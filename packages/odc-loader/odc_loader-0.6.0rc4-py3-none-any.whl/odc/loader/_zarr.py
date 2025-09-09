"""
Reader Driver from in-memory xarray/zarr spec docs.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from typing import Any, Iterator, TypeAlias

import dask.array as da
import fsspec
import numpy as np
import xarray as xr
from dask import is_dask_collection
from dask.array.core import normalize_chunks
from dask.base import tokenize
from dask.delayed import Delayed, delayed
from fsspec.core import url_to_fs
from odc.geo.gcp import GCPGeoBox
from odc.geo.geobox import GeoBox, GeoBoxBase, GeoboxTiles
from odc.geo.xr import ODCExtensionDa, ODCExtensionDs, xr_coords, xr_reproject

from .types import (
    AuxBandMetadata,
    AuxDataSource,
    AuxLoadParams,
    AuxReader,
    BandKey,
    DaskRasterReader,
    FixedCoord,
    GlobalLoadContext,
    LocalLoadContext,
    MDParser,
    RasterBandMetadata,
    RasterGroupMetadata,
    RasterLoadParams,
    RasterSource,
    ReaderSubsetSelection,
)

# TODO: tighten specs for Zarr*
SomeDoc: TypeAlias = Mapping[str, Any]
ZarrSpec: TypeAlias = Mapping[str, Any]
ZarrSpecDict: TypeAlias = dict[str, Any]
# pylint: disable=too-few-public-methods


class XrMDPlugin:
    """
    Convert xarray.Dataset to RasterGroupMetadata.

    Implements MDParser interface.

    - Convert xarray.Dataset to RasterGroupMetadata
    - Driver data is xarray.DataArray for each band
    """

    def __init__(
        self,
        template: RasterGroupMetadata,
        fallback: xr.Dataset | None = None,
    ) -> None:
        self._template = template
        self._fallback = fallback

    def _resolve_src(self, md: Any, regen_coords: bool = False) -> xr.Dataset | None:
        return _resolve_src_dataset(
            md, regen_coords=regen_coords, fallback=self._fallback, chunks={}
        )

    def extract(self, md: Any) -> RasterGroupMetadata:
        """Fixed description of src dataset."""
        if isinstance(md, RasterGroupMetadata):
            return md

        if (src := self._resolve_src(md, regen_coords=False)) is not None:
            return raster_group_md(src, base=self._template)

        return self._template

    def driver_data(self, md: Any, band_key: BandKey) -> xr.DataArray | SomeDoc | None:
        """
        Extract driver specific data for a given band.
        """
        name, _ = band_key

        if isinstance(md, dict):
            if (spec_doc := extract_zarr_spec(md)) is not None:
                return spec_doc
            return md

        if isinstance(md, xr.DataArray):
            return md

        src = self._resolve_src(md, regen_coords=False)
        if src is None or name not in src.data_vars:
            return None

        return src.data_vars[name]


class Context:
    """Context shared across a single load operation."""

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        geobox: GeoBox,
        chunks: None | dict[str, int],
        fs: fsspec.AbstractFileSystem | None = None,
    ) -> None:
        gbt: GeoboxTiles | None = None
        if chunks is not None:
            cy, cx = (
                chunks.get(name, fallback)
                for name, fallback in zip(["y", "x"], geobox.shape.yx)
            )
            gbt = GeoboxTiles(geobox, (cy, cx))
        self.geobox = geobox
        self.chunks = chunks
        self.fs = fs
        self.gbt = gbt

    def with_env(self, env: dict[str, Any]) -> "Context":
        assert isinstance(env, dict)
        return Context(self.geobox, self.chunks, fs=self.fs)


def from_raster_source(
    src: RasterSource,
    ctx: Context,
    *,
    chunk_store: (
        fsspec.AbstractFileSystem | fsspec.FSMap | Mapping[str, Any] | None
    ) = None,
    geobox: GeoBoxBase | None = None,
    **kw,  # da.from_zarr options
) -> xr.DataArray:
    driver_data: xr.DataArray | xr.Dataset | SomeDoc = src.driver_data
    subdataset = src.subdataset

    if isinstance(driver_data, xr.DataArray):
        return driver_data

    if isinstance(driver_data, xr.Dataset):
        if subdataset is None:
            _first, *_ = driver_data.data_vars
            subdataset = str(_first)
        return driver_data.data_vars[subdataset]

    spec = extract_zarr_spec(driver_data)
    assert spec is not None

    # Chunk store resolution
    # 1. Use supplied chunk_store
    # 2. Use ctx.fs if available
    # 3. Use fsspec.get_mapper(src.uri)

    if chunk_store is None:
        if ctx.fs:
            chunk_store = ctx.fs
        else:
            chunk_store = fsspec.get_mapper(src.uri)

    if isinstance(chunk_store, fsspec.AbstractFileSystem):
        chunk_store = chunk_store.get_mapper(src.uri)

    # create unloadable xarray.Dataset
    ds = xr.open_zarr(
        spec, consolidated=False, decode_coords="all", chunks={}, chunk_store={}
    )
    assert subdataset is not None
    assert subdataset in ds.data_vars

    # recreate xr.DataArray with all the dims/coords/attrs
    # but this time loadable from chunk_store
    xx = ds.data_vars[subdataset]
    assert isinstance(xx.odc, ODCExtensionDa)

    # regen coords using geobox if available
    # 1. Geobox supplied by caller
    # 2. Geobox from xarray.DataArray metadata
    # 3. Geobox from RasterSource
    if geobox is None:
        geobox = xx.odc.geobox
        if geobox is None:
            geobox = src.geobox

    coords = {**xx.coords}
    if geobox is not None:
        assert isinstance(geobox, (GeoBox, GCPGeoBox))
        coords.update(xr_coords(geobox, dims=xx.odc.spatial_dims or ("y", "x")))

    xx = xr.DataArray(
        da.from_zarr(
            spec,
            component=subdataset,
            chunk_store=chunk_store,
            **kw,
        ),
        coords=coords,
        dims=xx.dims,
        name=xx.name,
        attrs=xx.attrs,
    )
    return xx


class XrMemReader:
    """
    Implements protocol for raster readers.

    - Read from in-memory xarray.Dataset
    - Read from zarr spec
    """

    def __init__(self, src: xr.DataArray) -> None:
        self._src = src

    def read(
        self,
        cfg: RasterLoadParams,
        dst_geobox: GeoBox,
        *,
        dst: np.ndarray | None = None,
        selection: ReaderSubsetSelection | None = None,
    ) -> tuple[tuple[slice, slice], np.ndarray]:
        src = _select_extra_dims(self._src, selection, cfg)

        warped = xr_reproject(src, dst_geobox, resampling=cfg.resampling)
        if is_dask_collection(warped):
            warped = warped.data.compute(scheduler="synchronous")
        else:
            warped = warped.data

        assert isinstance(warped, np.ndarray)

        if dst is None:
            dst = warped
        else:
            dst[...] = warped

        yx_roi = (slice(None), slice(None))
        return yx_roi, dst


class XrMemReaderDask:
    """
    Dask version of the reader.
    """

    def __init__(
        self,
        src: xr.DataArray | None = None,
        cfg: RasterLoadParams | None = None,
        layer_name: str = "",
    ) -> None:
        self._layer_name = layer_name
        self._xx = src
        self._cfg = cfg

    def read(
        self,
        dst_geobox: GeoBox,
        *,
        selection: ReaderSubsetSelection | None = None,
        idx: tuple[int, ...] = (),
    ) -> Delayed:
        assert self._xx is not None
        assert self._cfg is not None
        assert isinstance(idx, tuple)
        xx = self._xx
        assert isinstance(xx.odc, ODCExtensionDa)
        assert isinstance(xx.odc.geobox, GeoBox)
        assert xx.odc.spatial_dims is not None

        yx_roi = xx.odc.geobox.overlap_roi(dst_geobox)
        selection = _extra_dims_selector(selection, self._cfg)
        selection.update(zip(xx.odc.spatial_dims, yx_roi))

        xx = self._xx.isel(selection)
        out_key = (self._layer_name, *idx)
        fut = delayed(_with_roi)(xx.data, dask_key_name=out_key)

        return fut

    def open(
        self,
        src: RasterSource,
        cfg: RasterLoadParams,
        ctx: Context,
        *,
        layer_name: str,
        idx: int,
    ) -> DaskRasterReader:
        assert idx >= 0
        base, *_ = layer_name.rsplit("-", 1)
        _tk = tokenize(src, ctx)
        xx = from_raster_source(src, ctx, name=f"{base}-zarr-{_tk}")

        assert xx.odc.geobox is not None
        assert not any(map(math.isnan, xx.odc.geobox.transform[:6]))
        assert ctx.gbt is not None
        gbt = ctx.gbt
        assert isinstance(gbt.base, GeoBox)

        xx_warped = xr_reproject(
            xx,
            gbt.base,
            resampling=cfg.resampling,
            dst_nodata=cfg.fill_value,
            dtype=cfg.dtype,
            chunks=gbt.chunk_shape((0, 0)).yx,
        )

        return XrMemReaderDask(xx_warped, cfg, layer_name=layer_name)


class XrMemReaderAux:
    """
    Implements protocol for auxiliary readers.
    """

    def __init__(self) -> None:
        pass

    def read(
        self,
        srcs: Sequence[Sequence[AuxDataSource]],
        cfg: AuxLoadParams,
        used_names: set[str],
        available_coords: Mapping[str, xr.DataArray],
        ctx: GlobalLoadContext,
        *,
        dask_layer_name: str | None = None,
    ) -> xr.DataArray:
        assert (cfg, used_names, available_coords, ctx, dask_layer_name) is not None

        def _extract(srcs: Sequence[Sequence[AuxDataSource]]) -> Iterator[xr.DataArray]:
            for row in srcs:
                for src in row:
                    if isinstance(src.driver_data, xr.DataArray):
                        yield src.driver_data
                    else:
                        # TODO: parity with raster sources
                        raise NotImplementedError(
                            "Auxiliary readers only support in memory xarray.DataArray"
                        )

        xx = list(_extract(srcs))
        assert len(xx) > 0

        if len(xx) == 1:
            return xx[0]

        return xr.concat(xx, dim=xx[0].dims[0])


class XrMemReaderDriver:
    """
    Read from in memory xarray.Dataset or zarr spec document.

    Implements ReaderDriver interface.
    """

    def __init__(
        self,
        src: xr.Dataset | None = None,
        template: RasterGroupMetadata | None = None,
        fs: fsspec.AbstractFileSystem | None = None,
    ) -> None:
        if src is not None and template is None:
            template = raster_group_md(src)
        if template is None:
            template = RasterGroupMetadata({}, {}, {}, [])
        self.src = src
        self.template = template
        self.fs = fs

    def new_load(
        self,
        geobox: GeoBox,
        *,
        chunks: None | dict[str, int] = None,
    ) -> Context:
        return Context(geobox, chunks, fs=self.fs)

    def finalise_load(self, load_state: GlobalLoadContext) -> GlobalLoadContext:
        return load_state

    def capture_env(self) -> dict[str, Any]:
        return {}

    @contextmanager
    def restore_env(
        self, env: dict[str, Any], load_state: GlobalLoadContext
    ) -> Iterator[LocalLoadContext]:
        yield load_state.with_env(env)

    def open(self, src: RasterSource, ctx: LocalLoadContext) -> XrMemReader:
        return XrMemReader(from_raster_source(src, ctx))

    @property
    def md_parser(self) -> MDParser:
        return XrMDPlugin(self.template, fallback=self.src)

    @property
    def dask_reader(self) -> DaskRasterReader | None:
        return XrMemReaderDask()

    @property
    def aux_reader(self) -> AuxReader | None:
        return XrMemReaderAux()


def band_info(xx: xr.DataArray) -> RasterBandMetadata | AuxBandMetadata:
    """
    Extract band metadata from xarray.DataArray
    """
    oo: ODCExtensionDa = xx.odc

    if xx.ndim < 2:
        return AuxBandMetadata(
            data_type=str(xx.dtype),
            nodata=oo.nodata,
            units=xx.attrs.get("units", "1"),
            dims=(),
        )

    if xx.ndim > 2:
        ydim = oo.ydim
        dims = tuple(str(d) for d in xx.dims)
        dims = dims[:ydim] + ("y", "x") + dims[ydim + 2 :]
    else:
        dims = ()

    return RasterBandMetadata(
        data_type=str(xx.dtype),
        nodata=oo.nodata,
        units=xx.attrs.get("units", "1"),
        dims=dims,
    )


def _raster_band_coords(src: xr.Dataset) -> set[str]:
    coords: set[str] = set()
    for dv in src.data_vars.values():
        if dv.odc.geobox is not None:
            coords.update(map(str, dv.coords))

    return coords


def raster_group_md(
    src: xr.Dataset,
    *,
    base: RasterGroupMetadata | None = None,
    aliases: dict[str, list[BandKey]] | None = None,
    extra_coords: Sequence[FixedCoord] = (),
    extra_dims: dict[str, int] | None = None,
) -> RasterGroupMetadata:
    oo: ODCExtensionDs = src.odc
    sdims = oo.spatial_dims or ("y", "x")

    if base is None:
        base = RasterGroupMetadata(
            bands={},
            aliases=aliases or {},
            extra_coords=extra_coords,
            extra_dims=extra_dims or {},
        )

    bands = {**base.bands}
    bands.update({(str(k), 1): band_info(v) for k, v in src.data_vars.items()})

    edims = {**base.extra_dims}
    aliases: dict[str, list[BandKey]] = {**base.aliases}
    extra_coords: list[FixedCoord] = list(base.extra_coords)
    supplied_coords = set(coord.name for coord in extra_coords)

    for coord_name in _raster_band_coords(src):
        coord = src.coords[coord_name]
        if len(coord.dims) != 1 or coord.dims[0] in sdims:
            # Only 1-d non-spatial coords
            continue

        if coord.name in supplied_coords:
            continue

        edims.setdefault(str(coord.dims[0]), len(coord.values))

        extra_coords.append(
            FixedCoord(
                str(coord.name),
                coord.values.tolist(),
                dim=str(coord.dims[0]),
                units=coord.attrs.get("units", "1"),
            )
        )

    return RasterGroupMetadata(
        bands=bands,
        aliases=aliases,
        extra_dims=edims,
        extra_coords=extra_coords,
    )


def mk_zarr_chunk_refs(
    spec_doc: SomeDoc,
    href: str,
    *,
    bands: Sequence[str] | None = None,
    sep: str = ".",
    overrides: dict[str, Any] | None = None,
) -> Iterator[tuple[str, Any]]:
    """
    Generate chunk references for all bands in zarr spec pointing to href.

    Output is a sequence of tuples in the form:

    ``("{band}/0.0", (f"{href}/{band}/0.0",))``

    suitable for building a dictionary for fsspec reference filesystem.

    This was meant to support generating inline coords for spatial dimensions
    and fixed coords for which we know the values. But we ended up not using
    this and instead rely on xarray to generate coords filled with `nan` by
    giving it empty chunk store.
    """

    spec = extract_zarr_spec(spec_doc)
    assert spec is not None
    assert ".zgroup" in spec, "Not a zarr spec"

    href = href.rstrip("/")

    if bands is None:
        _bands = [k.rsplit("/", 1)[0] for k in spec if k.endswith("/.zarray")]
    else:
        _bands = list(bands)

    if overrides is None:
        overrides = {}

    for b in _bands:
        meta = spec[f"{b}/.zarray"]
        assert "chunks" in meta and "shape" in meta

        shape_in_blocks = tuple(
            map(len, normalize_chunks(meta["chunks"], shape=meta["shape"]))
        )

        for idx in np.ndindex(shape_in_blocks):
            if idx == ():
                k = f"{b}/0"
            else:
                k = f"{b}/{sep.join(map(str, idx))}"
            v = overrides.get(k, None)
            if v is None:
                v = (f"{href}/{k}",)

            yield (k, v)


def _with_roi(xx: np.ndarray) -> tuple[tuple[slice, slice], np.ndarray]:
    return (slice(None), slice(None)), xx


def _extra_dims_selector(
    selection: ReaderSubsetSelection, cfg: RasterLoadParams
) -> dict[str, Any]:
    if selection is None:
        return {}

    assert isinstance(selection, (slice, int)) or len(selection) == 1
    assert len(cfg.extra_dims) == 1
    (band_dim,) = cfg.extra_dims
    return {band_dim: selection}


def _select_extra_dims(
    src: xr.DataArray, selection: ReaderSubsetSelection, cfg: RasterLoadParams
) -> xr.DataArray:
    if selection is None:
        return src

    return src.isel(_extra_dims_selector(selection, cfg))


def extract_zarr_spec(src: SomeDoc) -> ZarrSpecDict | None:
    if ".zgroup" in src:
        return dict(src)

    if "zarr:metadata" in src:
        # TODO: handle zarr:chunks for reference filesystem
        return dict(src["zarr:metadata"])

    if "zarr_consolidated_format" in src:
        return dict(src["metadata"])

    if ".zmetadata" in src:
        return dict(json.loads(src[".zmetadata"])["metadata"])

    return None


def _from_zarr_spec(
    spec_doc: ZarrSpecDict,
    *,
    regen_coords: bool = False,
    chunk_store: fsspec.AbstractFileSystem | Mapping[str, Any] | None = None,
    chunks=None,
    target: str | None = None,
    fsspec_opts: dict[str, Any] | None = None,
    drop_variables: Sequence[str] = (),
) -> xr.Dataset:
    fsspec_opts = fsspec_opts or {}
    if target is not None:
        if chunk_store is None:
            fs, target = url_to_fs(target, **fsspec_opts)
            chunk_store = fs.get_mapper(target)
        elif isinstance(chunk_store, fsspec.AbstractFileSystem):
            chunk_store = chunk_store.get_mapper(target)

    # TODO: deal with coordinates being loaded at open time.
    #
    # When chunk store is supplied xarray will try to load index coords (i.e.
    # name == dim, coords)

    xx = xr.open_zarr(
        spec_doc,
        chunk_store=chunk_store,
        drop_variables=drop_variables,
        chunks=chunks,
        decode_coords="all",
        consolidated=False,
    )
    gbox = xx.odc.geobox
    if gbox is not None and regen_coords:
        # re-gen x,y coords from geobox
        xx = xx.assign_coords(xr_coords(gbox))

    return xx


def _resolve_src_dataset(
    md: Any,
    *,
    regen_coords: bool = False,
    fallback: xr.Dataset | None = None,
    **kw,
) -> xr.Dataset | None:
    if isinstance(md, dict) and (spec_doc := extract_zarr_spec(md)) is not None:
        return _from_zarr_spec(spec_doc, regen_coords=regen_coords, **kw)

    if isinstance(md, xr.Dataset):
        return md

    return fallback
