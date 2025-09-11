from __future__ import annotations

import contextlib
import dataclasses
import logging
import typing
from typing import Literal

import h5py
import numpy as np
import zarr

import lazynwb.exceptions
import lazynwb.file_io
import lazynwb.types_
import lazynwb.utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TimeSeries:
    _file_path: lazynwb.types_.PathLike
    _table_path: str

    @property
    def _file(self) -> lazynwb.file_io.FileAccessor:
        return lazynwb.file_io._get_accessor(self._file_path)

    @property
    def data(self) -> h5py.Dataset | zarr.Array:
        try:
            return self._file[f"{self._table_path}/data"]
        except KeyError:
            if self._table_path not in self._file:
                raise lazynwb.exceptions.InternalPathError(
                    f"{self._table_path} not found in file"
                ) from None
            raise AttributeError(
                f"{self._table_path} has no data: use event timestamps alone"
            )

    @property
    def timestamps(self) -> h5py.Dataset | zarr.Array:
        try:
            return self._file[f"{self._table_path}/timestamps"]
        except KeyError:
            if self._table_path not in self._file:
                raise lazynwb.exceptions.InternalPathError(
                    f"{self._table_path} not found in file"
                ) from None
            rate = self.rate
            starting_time = self._starting_time
            if rate is None or starting_time is None:
                raise AssertionError(
                    f"Not enough information to calculate timestamps for {self._table_path}: need rate and starting_time"
                ) from None
            return (np.arange(len(self.data)) / rate) + starting_time

    @property
    def conversion(self) -> float | None:
        return self.data.attrs.get("conversion", None)

    @property
    def description(self) -> str | None:
        return self._file[f"{self._table_path}"].attrs.get("description", None)

    @property
    def offset(self) -> float | None:
        return self.data.attrs.get("offset", None)

    @property
    def rate(self) -> float | None:
        if (_starting_time := self._starting_time) is not None:
            return _starting_time.attrs.get("rate", None)
        return None

    @property
    def resolution(self) -> float | None:
        return self.data.attrs.get("resolution", None)

    @property
    def _starting_time(self) -> h5py.Dataset | zarr.Array | None:
        try:
            return self._file[f"{self._table_path}/starting_time"]
        except KeyError:
            if self._table_path not in self._file:
                raise lazynwb.exceptions.InternalPathError(
                    f"{self._table_path} not found in file"
                ) from None
            return None

    @property
    def starting_time(self) -> float:
        return self.timestamps[0]

    @property
    def timestamps_unit(self) -> str | None:
        with contextlib.suppress(KeyError):
            return self._file[self._table_path].attrs["timestamps_unit"]
        with contextlib.suppress(KeyError):
            return self._file[f"{self._table_path}/timestamps"].attrs.get("unit", None)
        with contextlib.suppress(KeyError):
            return self._file[f"{self._table_path}/starting_time"].attrs.get(
                "unit", None
            )
        raise AttributeError(
            f"Cannot find timestamps unit for {self._table_path}: no timestamps or starting_time found"
        )

    @property
    def unit(self):
        return self.data.attrs.get("unit", None)


@typing.overload
def get_timeseries(
    nwb_path: lazynwb.types_.PathLike,
    search_term: str | None = None,
    exact_path: bool = False,
    match_all: Literal[True] = True,
) -> dict[str, TimeSeries]: ...


@typing.overload
def get_timeseries(
    nwb_path: lazynwb.types_.PathLike,
    search_term: str | None = None,
    exact_path: bool = False,
    match_all: Literal[False] = False,
) -> TimeSeries: ...


def get_timeseries(
    nwb_path: lazynwb.types_.PathLike,
    search_term: str | None = None,
    exact_path: bool = False,
    match_all: bool = False,
) -> dict[str, TimeSeries] | TimeSeries:
    """
    Retrieve a TimeSeries object from an NWB file.
    This function searches for TimeSeries in an NWB file and returns either a specific
    TimeSeries object or a dictionary of all TimeSeries objects if `match_all` is True.

    Parameters
    ----------
    nwb_path : PathLike
        Path to an NWB file. Can be an hdf5 or zarr NWB.
    search_term : str or None, default=None
        String to search for specific TimeSeries. If the search term exactly matches a path,
        only that TimeSeries will be returned. If it partially matches multiple paths,
        the first match will be returned with a warning.
    exact_path: bool, default=False
        If True, the search term must exactly match the path of the TimeSeries. This is preferred
        as it is faster and less ambiguous.
    match_all : bool, default=False
        If True, returns all TimeSeries in the NWB as a dictionary regardless of search_term.

    Returns
    -------
    dict[str, TimeSeries] or TimeSeries
        If match_all is True, returns a dictionary mapping paths to TimeSeries objects.
        Otherwise, returns a single TimeSeries object, which is a dataclass, with attributes common
        to all NWB TimeSeries objects exposed, e.g. data, timestamps, rate, unit.
        For specialized TimeSeries objects, other attributes may be accessed via the h5py/zarr
        accessor using the `file` and `path` attributes, e.g. `ts.file[ts.path + '/data']`

    Raises
    ------
    ValueError
        If neither search_term is provided nor match_all is set to True.

    Notes
    -----
    The function identifies TimeSeries by looking for paths ending with "/data"
    or "/timestamps", which are characteristic of TimeSeries objects in NWB files.
    """
    if not (search_term or match_all):
        raise ValueError(
            "Either `search_term` must be specified or `match_all` must be set to True"
        )

    def _format(name: str) -> str:
        return name.removesuffix("/data").removesuffix("/timestamps")

    file = lazynwb.file_io._get_accessor(nwb_path)
    is_in_file = search_term in file
    if exact_path and not is_in_file:
        raise lazynwb.exceptions.InternalPathError(
            f"Exact path {search_term!r} not found in file {file._path.as_posix()}"
        )
    elif not match_all and search_term and is_in_file:
        return TimeSeries(_file_path=nwb_path, _table_path=_format(search_term))
    else:
        path_to_accessor = {
            _format(k): TimeSeries(_file_path=nwb_path, _table_path=_format(k))
            for k in lazynwb.utils._traverse_internal_paths(file._file)
            if k.split("/")[-1] in ("data", "timestamps")
            and (not search_term or search_term in k)
            # regular timeseries will be a dir with /data and optional /timestamps
            # eventseries will be a dir with /timestamps only
        }
        if match_all:
            return path_to_accessor
        if len(path_to_accessor) > 1:
            logger.warning(
                f"Found multiple timeseries matching {search_term!r}: {list(path_to_accessor.keys())} - returning first"
            )
        return next(iter(path_to_accessor.values()))


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
