from __future__ import annotations

import importlib
import importlib.util
from typing import TYPE_CHECKING, Callable, NamedTuple, cast

import pytest

# import tensorstore as ts
from ome_writers import (
    AcquireZarrStream,
    OMEStream,
    TensorStoreZarrStream,
    TifffileStream,
)

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np

    from ome_writers._auto import BackendName


class AvailableBackend(NamedTuple):
    name: BackendName
    cls: type[OMEStream]
    file_ext: str
    read_data: Callable[[Path], np.ndarray]


def _read_zarr(output_path: Path) -> np.ndarray:
    try:
        import tensorstore as ts

        spec = {
            "driver": "zarr3",
            "kvstore": {"driver": "file", "path": str(output_path / "0")},
        }
        store = ts.open(spec).result()
        return store.read().result()  # type: ignore
    except ImportError:
        try:
            import zarr  # type: ignore

            z = zarr.open(str(output_path / "0"), mode="r")
            return z[:]
        except ImportError as e:
            raise pytest.skip("zarr or tensorstore is not installed") from e


def _read_tiff(output_path: Path) -> np.ndarray:
    try:
        import tifffile  # type: ignore

        return tifffile.imread(str(output_path))
    except ImportError as e:
        raise pytest.skip("tifffile is not installed") from e


# Test configurations for each backend
BACKENDS: list[AvailableBackend] = []
if importlib.util.find_spec("tensorstore") is not None:
    BACKENDS.append(
        AvailableBackend("tensorstore", TensorStoreZarrStream, ".ome.zarr", _read_zarr)
    )
if importlib.util.find_spec("acquire_zarr") is not None:
    BACKENDS.append(
        AvailableBackend("acquire-zarr", AcquireZarrStream, ".ome.zarr", _read_zarr)
    )
if importlib.util.find_spec("tifffile") is not None:
    BACKENDS.append(AvailableBackend("tiff", TifffileStream, ".ome.tiff", _read_tiff))


@pytest.fixture(params=BACKENDS, ids=lambda b: b.name)
def backend(request: pytest.FixtureRequest) -> AvailableBackend:
    """Fixture to provide an available backend based on the test parameter."""
    return cast("AvailableBackend", request.param)
