# pylint: disable=missing-function-docstring,missing-module-docstring,too-many-statements,too-many-locals
from __future__ import annotations

from math import isnan
from typing import Any

import numpy as np
import pytest
import rasterio
import xarray as xr
from dask import is_dask_collection
from numpy import ma
from numpy.testing import assert_array_equal
from odc.geo.geobox import GeoBox
from odc.geo.xr import xr_zeros

from ._reader import (
    ReaderDaskAdaptor,
    expand_selection,
    pick_overview,
    resolve_band_query,
    resolve_dst_dtype,
    resolve_dst_nodata,
    resolve_load_cfg,
    resolve_src_nodata,
    same_nodata,
)
from ._rio import RioDriver, configure_rio, get_rio_env, rio_read
from .testing.fixtures import FakeReaderDriver, with_temp_tiff
from .types import (
    AuxBandMetadata,
    AuxLoadParams,
    RasterBandMetadata,
    RasterGroupMetadata,
    RasterLoadParams,
    RasterSource,
)


def test_same_nodata() -> None:
    _nan = float("nan")
    assert same_nodata(None, None) is True
    assert same_nodata(_nan, _nan) is True
    assert same_nodata(1, None) is False
    assert same_nodata(_nan, None) is False
    assert same_nodata(None, _nan) is False
    assert same_nodata(10, _nan) is False
    assert same_nodata(_nan, 10) is False
    assert same_nodata(109, 109) is True
    assert same_nodata(109, 1) is False


def test_resolve_nodata() -> None:
    def _cfg(**kw):
        return RasterLoadParams("uint8", **kw)

    assert resolve_src_nodata(None, _cfg()) is None
    assert resolve_src_nodata(11, _cfg()) == 11
    assert resolve_src_nodata(None, _cfg(src_nodata_fallback=0)) == 0
    assert resolve_src_nodata(None, _cfg(src_nodata_fallback=11)) == 11
    assert resolve_src_nodata(11, _cfg(src_nodata_fallback=0)) == 11
    assert resolve_src_nodata(11, _cfg(src_nodata_override=-1)) == -1
    assert resolve_src_nodata(11, _cfg(src_nodata_override=0)) == 0

    nan = resolve_dst_nodata(np.dtype("float32"), _cfg(), 0)
    assert nan is not None
    assert isnan(nan)
    assert resolve_dst_nodata(np.dtype("uint16"), _cfg(), 0) == 0
    assert resolve_dst_nodata(np.dtype("uint16"), _cfg(fill_value=3), 5) == 3
    assert resolve_dst_nodata(np.dtype("float32"), _cfg(fill_value=3), 7) == 3


def test_resolve_dst_dtype() -> None:
    assert resolve_dst_dtype("uint8", RasterLoadParams()) == "uint8"
    assert resolve_dst_dtype("uint8", RasterLoadParams(dtype="float32")) == "float32"


def test_pick_overiew() -> None:
    assert pick_overview(2, []) is None
    assert pick_overview(1, [2, 4]) is None
    assert pick_overview(2, [2, 4, 8]) == 0
    assert pick_overview(3, [2, 4, 8]) == 0
    assert pick_overview(4, [2, 4, 8]) == 1
    assert pick_overview(7, [2, 4, 8]) == 1
    assert pick_overview(8, [2, 4, 8]) == 2
    assert pick_overview(20, [2, 4, 8]) == 2


@pytest.mark.parametrize(
    "n, dims, band, selection, expect",
    [
        (3, (), 1, None, 1),
        (3, (), 3, None, 3),
        (3, ("b", "y", "x"), 3, None, [3]),
        (3, ("b", "y", "x"), 1, None, [1]),
        (3, ("b", "y", "x"), 0, None, [1, 2, 3]),
        (4, ("b", "y", "x"), 0, np.s_[:2], [1, 2]),
        (4, ("b", "y", "x"), 0, (slice(1, 4),), [2, 3, 4]),
        (4, ("b", "y", "x"), 0, [1, 3], [1, 3]),
        (2, ("b", "y", "x"), 0, 1, [2]),
        (5, ("b", "y", "x"), 0, -1, [5]),
    ],
)
def test_resolve_band_query(
    n: int,
    dims: tuple[str, ...],
    band: int,
    selection: Any,
    expect: Any,
) -> None:
    src = RasterSource("", band=band, meta=RasterBandMetadata(dims=dims))
    assert resolve_band_query(src, n, selection) == expect


@pytest.mark.parametrize(
    "ydim, selection, expect",
    [
        (0, None, np.s_[:, :]),
        (0, np.s_[:4], np.s_[:, :, :4]),
        (1, np.s_[:3], np.s_[:3, :, :]),
        (1, np.s_[8], np.s_[8, :, :]),
        (0, np.s_[1:2, 3:4], np.s_[:, :, 1:2, 3:4]),
        (1, np.s_[1:2, 3:4], np.s_[1:2, :, :, 3:4]),
        (2, np.s_[1:2, 3:4], np.s_[1:2, 3:4, :, :]),
    ],
)
def test_expand_selection(ydim, selection, expect) -> None:
    assert expand_selection(selection, ydim) == expect


def test_rio_reader_env() -> None:
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(160, 320), tight=True)
    rdr = RioDriver()
    load_state = rdr.new_load(gbox)

    configure_rio(cloud_defaults=True, verbose=True)
    env = rdr.capture_env()
    assert isinstance(env, dict)
    assert env["GDAL_DISABLE_READDIR_ON_OPEN"] == "EMPTY_DIR"
    assert "GDAL_DATA" not in env

    configure_rio(cloud_defaults=False, verbose=True)
    env2 = rdr.capture_env()

    with rdr.restore_env(env, load_state):
        _env = get_rio_env(sanitize=False, no_session_keys=False)
        assert isinstance(_env, dict)
        assert _env["GDAL_DISABLE_READDIR_ON_OPEN"] == "EMPTY_DIR"

    with rdr.restore_env(env2, load_state):
        _env = get_rio_env(sanitize=False, no_session_keys=False)
        assert isinstance(_env, dict)
        assert "GDAL_DISABLE_READDIR_ON_OPEN" not in _env

    # test no-op old args
    configure_rio(client="", activate=True)

    rdr.finalise_load(load_state)


def test_rio_read() -> None:
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(160, 320), tight=True)

    non_zeros_roi = np.s_[30:47, 190:210]

    xx = xr_zeros(gbox, dtype="int16")
    xx.values[non_zeros_roi] = 333
    assert xx.odc.geobox == gbox

    cfg = RasterLoadParams()

    with with_temp_tiff(xx, compress=None) as uri:
        src = RasterSource(uri)

        # read whole
        roi, pix = rio_read(src, cfg, gbox)
        assert gbox[roi] == gbox
        assert pix.shape == gbox.shape
        assert_array_equal(pix, xx.values)

        # Going via RioReader should be the same
        rdr_driver = RioDriver()
        load_state = rdr_driver.new_load(gbox)
        with rdr_driver.restore_env(rdr_driver.capture_env(), load_state) as ctx:
            rdr = rdr_driver.open(src, ctx)
            _roi, _pix = rdr.read(cfg, gbox)
            assert roi == _roi
            assert (pix == _pix).all()
        rdr_driver.finalise_load(load_state)

        # read part
        _gbox = gbox[non_zeros_roi]
        roi, pix = rio_read(src, cfg, _gbox)
        assert _gbox[roi] == _gbox
        assert pix.shape == _gbox.shape
        assert (pix == 333).all()
        assert_array_equal(pix, xx.values[non_zeros_roi])

        # - in-place dst
        # - dtype change to float32
        # - remap nodata to nan
        _cfg = RasterLoadParams(src_nodata_fallback=0)
        expect = xx.values.astype("float32")
        expect[xx.values == _cfg.src_nodata_fallback] = np.nan

        _dst = np.ones(gbox.shape, dtype="float32")
        roi, pix = rio_read(src, _cfg, gbox, dst=_dst)
        assert pix.dtype == _dst.dtype
        assert_array_equal(expect, pix)
        assert np.nansum(pix) == xx.values.sum()

        # - in-place dst
        # - remap nodata 0 -> -99
        _cfg = RasterLoadParams(src_nodata_fallback=0, fill_value=-99)
        expect = xx.values.copy()
        expect[xx.values == _cfg.src_nodata_fallback] = _cfg.fill_value

        _dst = np.ones(gbox.shape, dtype=xx.dtype)
        roi, pix = rio_read(src, _cfg, gbox, dst=_dst)
        assert pix.dtype == _dst.dtype
        assert (pix == _cfg.fill_value).any()
        assert (pix != _cfg.src_nodata_fallback).all()
        assert_array_equal(expect, pix)
        assert ma.masked_equal(pix, _cfg.fill_value).sum() == xx.values.sum()

    # smaller src than dst
    # float32 with nan
    _roi = np.s_[2:-2, 3:-5]
    _xx = xx.astype("float32").where(xx != 0, np.nan)[_roi]
    assert np.nansum(_xx.values) == xx.values.sum()
    assert _xx.odc.geobox == gbox[_roi]

    with with_temp_tiff(_xx, compress=None, overview_levels=[]) as uri:
        src = RasterSource(uri)

        # read whole input, filling only part of output
        roi, pix = rio_read(src, cfg, gbox)
        assert pix.shape == gbox[roi].shape
        assert gbox[roi] != gbox
        assert (gbox[roi] | gbox) == gbox
        assert_array_equal(pix, _xx.values)

    # smaller src than dst
    # no src nodata
    # yes dst nodata
    _xx = xx[_roi]
    assert _xx.values.sum() == xx.values.sum()
    assert _xx.odc.geobox == gbox[_roi]

    with with_temp_tiff(_xx, compress=None, overview_levels=[]) as uri:
        _cfg = RasterLoadParams(fill_value=-99)
        src = RasterSource(uri)

        # read whole input, filling only part of output
        roi, pix = rio_read(src, _cfg, gbox)
        assert pix.shape == gbox[roi].shape
        assert gbox[roi] != gbox
        assert (gbox[roi] | gbox) == gbox
        assert (pix != _cfg.fill_value).all()
        assert_array_equal(pix, _xx.values)

        # non-pasting path
        _gbox = gbox.zoom_out(1.3)
        roi, pix = rio_read(src, _cfg, _gbox)
        assert pix.shape == gbox[roi].shape
        assert gbox[roi] != gbox


def test_reader_ovr() -> None:
    # smoke test only
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(512, 512), tight=True)

    non_zeros_roi = np.s_[30:47, 190:210]

    xx = xr_zeros(gbox, dtype="int16")
    xx.values[non_zeros_roi] = 333
    assert xx.odc.geobox == gbox

    cfg = RasterLoadParams()

    # whole image from 1/2 overview
    with with_temp_tiff(xx, compress=None, overview_levels=[2, 4]) as uri:
        src = RasterSource(uri)
        _gbox = gbox.zoom_out(2)
        roi, pix = rio_read(src, cfg, _gbox)
        assert pix.shape == _gbox[roi].shape
        assert _gbox[roi] == _gbox


@pytest.mark.parametrize("resamlpling", ["nearest", "bilinear", "cubic"])
@pytest.mark.parametrize("dims", [("y", "x", "band"), ("band", "y", "x")])
def test_rio_read_rgb(resamlpling, dims) -> None:
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(512, 512), tight=True)

    non_zeros_roi = np.s_[30:47, 190:210]

    xx = xr_zeros(gbox, dtype="uint8")
    xx.values[non_zeros_roi] = 255
    xx = xx.expand_dims("band", 2)
    xx = xr.concat([xx, xx, xx], "band").assign_coords(band=["r", "g", "b"])

    assert xx.odc.geobox == gbox

    cfg = RasterLoadParams(
        dtype="uint8",
        dims=dims,
        resampling=resamlpling,
    )
    gbox2 = gbox.zoom_to(237)

    # whole image from 1/2 overview
    with with_temp_tiff(xx, compress=None, overview_levels=[2, 4]) as uri:
        src = RasterSource(
            uri,
            band=0,
            meta=RasterBandMetadata(cfg.dtype, dims=cfg.dims),
        )
        assert src.ydim in (0, 1)

        for gb in [gbox, gbox2]:
            roi, pix = rio_read(src, cfg, gb)

            if src.ydim == 1:
                expect_shape = (3, *gb[roi].shape.yx)
                expect_shape_2 = (2, *gb[roi].shape.yx)
                _dst = np.zeros((3, *gb.shape.yx), dtype=pix.dtype)
            else:
                assert src.ydim == 0
                expect_shape = (*gb[roi].shape.yx, 3)
                expect_shape_2 = (*gb[roi].shape.yx, 2)
                _dst = np.zeros((*gb.shape.yx, 3), dtype=pix.dtype)

            assert len(roi) == 2
            assert pix.ndim == 3
            assert pix.shape == expect_shape

            # again but with dst=
            _roi, pix2 = rio_read(src, cfg, gb, dst=_dst)
            assert pix2.shape == _dst[(np.s_[:],) * src.ydim + _roi].shape

            # again but with selection
            roi_2, pix = rio_read(src, cfg, gb, selection=np.s_[:2])
            assert roi == roi_2
            assert pix.ndim == 3
            assert pix.shape == expect_shape_2


def test_reader_unhappy_paths() -> None:
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(160, 320), tight=True)
    xx = xr_zeros(gbox, dtype="int16")

    with with_temp_tiff(xx, compress=None) as uri:
        cfg = RasterLoadParams()
        src = RasterSource(uri, band=3)

        # no such band error
        with pytest.raises(ValueError):
            _, _ = rio_read(src, cfg, gbox)


def test_reader_fail_on_error() -> None:
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(160, 320), tight=True)
    xx = xr_zeros(gbox, dtype="int16")
    src = RasterSource("file:///no-such-path/no-such.tif")
    cfg = RasterLoadParams(dtype=str(xx.dtype), fail_on_error=True)

    # check that it raises error when fail_on_error=True
    with pytest.raises(rasterio.errors.RasterioIOError):
        _, _ = rio_read(src, cfg, gbox)

    # check that errors are suppressed when fail_on_error=False
    cfg = RasterLoadParams(dtype=str(xx.dtype), fail_on_error=False)
    roi, yy = rio_read(src, cfg, gbox)
    assert yy.shape == (0, 0)
    assert yy.dtype == cfg.dtype
    assert roi == np.s_[0:0, 0:0]

    roi, yy = rio_read(src, cfg, gbox, dst=xx.data)
    assert yy.shape == (0, 0)
    assert yy.dtype == cfg.dtype
    assert roi == np.s_[0:0, 0:0]


@pytest.mark.parametrize("dtype", ["int16", "float32"])
def test_dask_reader_adaptor(dtype: str) -> None:
    gbox = GeoBox.from_bbox((-180, -90, 180, 90), shape=(160, 320), tight=True)

    meta = RasterBandMetadata(dtype, 333)
    group_md = RasterGroupMetadata({(b, 1): meta for b in ("aa", "bb")})

    base_driver = FakeReaderDriver(group_md)
    driver = ReaderDaskAdaptor(base_driver)

    ctx = base_driver.new_load(gbox, chunks={"x": 64, "y": 64})

    src = RasterSource("mem://", meta=meta)
    cfg = RasterLoadParams.same_as(src)
    rdr = driver.open(src, cfg, ctx, layer_name="aa", idx=0)

    assert isinstance(rdr, ReaderDaskAdaptor)

    xx = rdr.read(gbox, idx=(0,))
    assert is_dask_collection(xx)
    assert xx.key == ("aa", 0)
    assert rdr.read(gbox, idx=(1,)).key == ("aa", 1)
    assert rdr.read(gbox, idx=(1, 2, 3)).key == ("aa", 1, 2, 3)

    yy = xx.compute(scheduler="synchronous")
    assert isinstance(yy, tuple)
    yx_roi, pix = yy
    assert pix.shape == gbox[yx_roi].shape.yx
    assert pix.dtype == dtype


def test_resolve_load_cfg() -> None:
    cfg = resolve_load_cfg(
        {
            "band": RasterBandMetadata("uint8", 255),
            "bb": RasterBandMetadata(),
            "aux": AuxBandMetadata("int16", -1),
        },
        resampling={"band": "bilinear", "*": "mode"},
    )
    assert "band" in cfg
    assert "aux" in cfg

    c = cfg["band"]
    assert isinstance(c, RasterLoadParams)
    assert c.dtype == "uint8"
    assert c.dims == ()
    assert c.resampling == "bilinear"
    assert c.fill_value == 255
    assert c.src_nodata_fallback is None
    assert c.src_nodata_override is None
    assert c.fail_on_error is True

    c = cfg["bb"]
    assert isinstance(c, RasterLoadParams)
    assert c.dtype == "float32"
    assert c.dims == ()
    assert c.resampling == "mode"
    assert c.fill_value is None
    assert c.src_nodata_fallback is None
    assert c.src_nodata_override is None
    assert c.fail_on_error is True

    c = cfg["aux"]
    assert isinstance(c, AuxLoadParams)
    assert c.dtype == "int16"
    assert c.fill_value == -1


def test_rio_driver_init() -> None:
    driver = RioDriver()
    assert driver.md_parser is None
    assert driver.aux_reader is None
    assert driver.dask_reader is None

    a, b, c = [object() for _ in range(3)]
    driver = RioDriver(md_parser=a, aux_reader=b, dask_reader=c)  # type: ignore
    assert driver.md_parser is a
    assert driver.aux_reader is b
    assert driver.dask_reader is c
