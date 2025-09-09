import pytest
import numpy as np
import zarr
import zarr.storage

import figpack
from figpack.spike_sorting.views.Autocorrelograms import Autocorrelograms
from figpack.spike_sorting.views.CrossCorrelograms import CrossCorrelograms


@pytest.mark.spikeinterface
def test_autocorrelograms_with_si():
    """Test Autocorrelograms with real spikeinterface data"""
    import spikeinterface.extractors as se

    # Create toy example data
    recording, sorting = se.toy_example(
        num_units=4,  # Use fewer units for faster tests
        duration=10,  # Shorter duration for faster tests
        seed=0,
        num_segments=1,
    )

    # Create view from sorting
    view = Autocorrelograms.from_sorting(sorting)

    # Basic validation
    assert len(view.autocorrelograms) == 4  # One for each unit

    # Check attributes of each autocorrelogram
    for item in view.autocorrelograms:
        assert isinstance(item.unit_id, str)
        assert isinstance(item.bin_edges_sec, np.ndarray)
        assert isinstance(item.bin_counts, np.ndarray)
        assert item.bin_edges_sec.dtype == np.float32
        assert item.bin_counts.dtype == np.int32
        assert len(item.bin_counts) == len(item.bin_edges_sec) - 1

    # Test Zarr storage
    store = zarr.storage.MemoryStore()
    root = zarr.group(store=store)
    group = figpack.Group(root.create_group("test"))
    view._write_to_zarr_group(group)

    # Verify stored data
    assert group.attrs["view_type"] == "Autocorrelograms"
    assert group.attrs["num_autocorrelograms"] == 4

    # Check bin edges dataset
    assert "bin_edges_sec" in group
    assert group["bin_edges_sec"].dtype == np.float32

    # Check bin counts dataset
    assert "bin_counts" in group
    assert group["bin_counts"].dtype == np.int32
    assert group["bin_counts"].shape[0] == 4  # num_autocorrelograms rows
    assert group["bin_counts"].shape[1] == len(
        view.autocorrelograms[0].bin_counts
    )  # num_bins columns

    # Check metadata
    metadata = group.attrs["autocorrelograms"]
    assert len(metadata) == 4

    for i, meta in enumerate(metadata):
        assert "unit_id" in meta
        assert "index" in meta
        assert meta["index"] == i  # Verify indices are sequential
        assert "num_bins" in meta
        assert meta["num_bins"] == len(view.autocorrelograms[0].bin_counts)


@pytest.mark.spikeinterface
def test_cross_correlograms_with_si():
    """Test CrossCorrelograms with real spikeinterface data"""
    import spikeinterface.extractors as se

    # Create toy example data
    recording, sorting = se.toy_example(
        num_units=4,  # Use fewer units for faster tests
        duration=10,  # Shorter duration for faster tests
        seed=0,
        num_segments=1,
    )

    # Create view from sorting
    view = CrossCorrelograms.from_sorting(sorting)

    # Basic validation - should have cross-correlograms for each pair
    n_units = len(sorting.get_unit_ids())
    expected_pairs = (n_units * (n_units + 1)) // 2  # Including diagonal
    assert len(view.cross_correlograms) == expected_pairs

    # Check attributes of each cross-correlogram
    for item in view.cross_correlograms:
        assert isinstance(item.unit_id1, str)
        assert isinstance(item.unit_id2, str)
        assert isinstance(item.bin_edges_sec, np.ndarray)
        assert isinstance(item.bin_counts, np.ndarray)
        assert item.bin_edges_sec.dtype == np.float32
        assert item.bin_counts.dtype == np.int32
        assert len(item.bin_counts) == len(item.bin_edges_sec) - 1

    # Test Zarr storage
    store = zarr.storage.MemoryStore()
    root = zarr.group(store=store)
    group = figpack.Group(root.create_group("test"))
    view._write_to_zarr_group(group)

    # Verify stored data
    assert group.attrs["view_type"] == "CrossCorrelograms"
    assert group.attrs["num_cross_correlograms"] == expected_pairs
    assert "hide_unit_selector" in group.attrs

    # Check bin edges dataset
    assert "bin_edges_sec" in group
    assert group["bin_edges_sec"].dtype == np.float32

    # Check bin counts dataset
    assert "bin_counts" in group
    assert group["bin_counts"].dtype == np.int32
    assert group["bin_counts"].shape[0] == expected_pairs  # num_cross_correlograms rows
    assert group["bin_counts"].shape[1] == len(
        view.cross_correlograms[0].bin_counts
    )  # num_bins columns

    # Check metadata
    metadata = group.attrs["cross_correlograms"]
    assert len(metadata) == expected_pairs

    for i, meta in enumerate(metadata):
        assert "unit_id1" in meta
        assert "unit_id2" in meta
        assert "index" in meta
        assert meta["index"] == i  # Verify indices are sequential
        assert "num_bins" in meta
        assert meta["num_bins"] == len(view.cross_correlograms[0].bin_counts)


@pytest.mark.spikeinterface
def test_cross_correlograms_from_widget():
    """Test creating CrossCorrelograms directly from widget"""
    import spikeinterface.extractors as se
    import spikeinterface.widgets as sw

    # Create toy example data
    recording, sorting = se.toy_example(
        num_units=4, duration=10, seed=0, num_segments=1
    )

    # Create the widget
    W = sw.CrossCorrelogramsWidget(sorting)

    # Create view from widget
    view = CrossCorrelograms.from_spikeinterface_widget(W)

    # Validate view contents
    n_units = len(sorting.get_unit_ids())
    expected_pairs = (n_units * (n_units + 1)) // 2  # Including diagonal
    assert len(view.cross_correlograms) == expected_pairs

    # Test Zarr storage
    store = zarr.storage.MemoryStore()
    root = zarr.group(store=store)
    group = figpack.Group(root.create_group("test"))
    view._write_to_zarr_group(group)

    # Verify data is stored correctly
    assert group.attrs["num_cross_correlograms"] == expected_pairs
