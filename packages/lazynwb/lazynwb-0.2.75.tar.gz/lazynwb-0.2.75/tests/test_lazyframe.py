import logging

import polars as pl
import pytest

import h5py
import lazynwb
import lazynwb.tables

def test_polars_dtype_inference(local_hdf5_path):
    schema = lazynwb.tables.get_table_schema(
        local_hdf5_path,
        table_path='units',
    )
    assert schema['obs_intervals'] == pl.List(pl.Array(pl.Float64, shape=(2,))), f"Expected polars dtype for obs_intervals to be List[List[Float64]]: {schema['obs_intervals']=}"

@pytest.mark.parametrize(
    "nwb_fixture_name",
    [
        "local_hdf5_path",
        "local_hdf5_paths",
        "local_zarr_path",
        "local_zarr_paths",
    ],
)
def test_scan_nwb_sources(nwb_fixture_name, request):
    """Test scan_nwb with various NWB file/store inputs."""
    # Resolve the fixture name to its value (the path or list of paths)
    nwb_path_or_paths = request.getfixturevalue(nwb_fixture_name)

    # Test with trials table
    lf = lazynwb.scan_nwb(
        source=nwb_path_or_paths, table_path="/intervals/trials", disable_progress=True
    )

    # Check that we got a LazyFrame
    assert isinstance(lf, pl.LazyFrame), "scan_nwb should return a LazyFrame"

    # Execute the lazy frame and check we have data
    df = lf.collect()
    assert not df.is_empty(), f"DataFrame is empty for {nwb_fixture_name}"

    # Test that all expected internal columns are present
    for col in lazynwb.INTERNAL_COLUMN_NAMES:
        assert col in df.columns, f"Internal column {col!r} not found"


def test_scan_nwb_exclude_array_columns(local_hdf5_path):
    """Test scan_nwb with exclude_array_columns option."""
    # First get all columns including arrays
    lf_with_arrays = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/units",
        exclude_array_columns=False,
        disable_progress=True,
    )
    df_with_arrays = lf_with_arrays.collect()

    # Now exclude array columns
    lf_no_arrays = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/units",
        exclude_array_columns=True,
        disable_progress=True,
    )
    df_no_arrays = lf_no_arrays.collect()

    # Check that the version with arrays has more columns
    assert (
        df_with_arrays.width > df_no_arrays.width
    ), "DataFrame with arrays should have more columns"

    # Check for array columns like spike_times, waveform_mean, obs_intervals
    array_columns = {"spike_times", "waveform_mean", "obs_intervals"}
    for col in array_columns:
        assert (
            col in df_with_arrays.columns
        ), f"Array column {col!r} should be present when exclude_array_columns=False"
        assert (
            col not in df_no_arrays.columns
        ), f"Array column {col!r} should be excluded when exclude_array_columns=True"


def test_scan_nwb_schema_override(local_hdf5_path):
    """Test scan_nwb with schema overrides."""
    # Define schema overrides for specific columns
    schema_overrides = {"condition": pl.Categorical()}

    df = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/intervals/trials",
        schema_overrides=schema_overrides,
        disable_progress=True,
    ).collect()
    # Check that the schema override was applied
    assert (
        df.schema["condition"] == pl.Categorical
    ), f"Schema override for 'condition' column was not applied: {df.schema=}"
    
    # verify this works with predicate pushdown
    df = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/intervals/trials",
        schema_overrides=schema_overrides,
        disable_progress=True,
    ).filter(pl.col("start_time") > 2.0).collect()
    assert (
        df.schema["condition"] == pl.Categorical
    ), f"Schema override for 'condition' column was not applied when combined with filtering: {df.schema=}"

    # verify this works with projection 
    df = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/intervals/trials",
        schema_overrides=schema_overrides,
        disable_progress=True,
    ).select("start_time", "stop_time", "condition").collect()
    assert (
        df.schema["condition"] == pl.Categorical
    ), f"Schema override for 'condition' column was not applied when combined with projection: {df.schema=}"
    
    
def test_scan_nwb_predicate_pushdown(local_hdf5_path):
    """Test that scan_nwb correctly handles predicate pushdown optimizations."""
    # Create a query with a predicate
    lf = lazynwb.scan_nwb(
        source=local_hdf5_path, table_path="/intervals/trials", disable_progress=True
    )

    # Apply a predicate filter
    expr = pl.col("start_time") > 2.0
    filtered_lf = lf.filter(expr)

    # Execute and check results
    filtered_df = filtered_lf.collect()

    # Verify the filter was applied correctly
    assert (
        filtered_df["start_time"] > 2.0
    ).all(), "Predicate pushdown filter was not applied correctly"
    assert len(filtered_df) == len(lf.collect().filter(expr)), "Filtered DataFrame length does not match length when collecting and filtering separately"

    # Test filtering on internal columns
    internal_expr = pl.col(lazynwb.TABLE_INDEX_COLUMN_NAME) == 3
    filtered_internal_lf = lf.filter(internal_expr)

    # Execute and check results
    filtered_internal_df = filtered_internal_lf.collect()

    # Verify the filter was applied correctly
    assert (
        filtered_internal_df[lazynwb.TABLE_INDEX_COLUMN_NAME] == 3
    ).all(), "Predicate pushdown filter on internal column was not applied correctly"
    assert len(filtered_internal_df) == len(lf.collect().filter(internal_expr)), "Filtered DataFrame length does not match length when collecting and filtering separately"

def test_scan_nwb_raises_on_missing(local_hdf5_path):
    """Test that scan_nwb raises an error when the table is not found and raise_on_missing=True."""
    # Try with a non-existent table path
    with pytest.raises(KeyError):
        lf = lazynwb.scan_nwb(
            source=local_hdf5_path,
            table_path="/non_existent_table",
            raise_on_missing=True,
            disable_progress=True,
        )
        # Force execution to trigger the error
        lf.collect()


def test_scan_nwb_projection_pushdown(local_hdf5_path):
    """Test that scan_nwb correctly handles column projection optimizations."""
    # Create a query with column selection
    lf = lazynwb.scan_nwb(
        source=local_hdf5_path, table_path="/intervals/trials", disable_progress=True
    )

    # Select only specific columns
    selected_columns = ["start_time", "stop_time", "condition"]
    projected_lf = lf.select(selected_columns)

    # Execute and check results
    projected_df = projected_lf.collect()

    # Check that only the requested columns are present
    expected_columns = set(selected_columns)
    assert (
        set(projected_df.columns) == expected_columns
    ), f"LazyFrame Projection did not work correctly: {projected_df.columns=}, {expected_columns=}"

def test_sql_context(local_hdf5_path):
    """Test that scan_nwb can be used with SQL context."""
    # Create a SQL context
    sql_context = pl.SQLContext(eager=True)

    # Register the NWB table as a SQL table
    sql_context.register(
        "trials",
        lazynwb.scan_nwb(
            source=local_hdf5_path, table_path="/intervals/trials", disable_progress=True
        ),
    )

    result = sql_context.execute("SELECT * FROM trials WHERE start_time > 2.0")

    assert not result.is_empty(), "SQL query returned an empty result set"
    assert (result["start_time"] > 2.0).all(), "SQL query did not filter correctly"
    
def test_empty_scan(local_hdf5_path):
    """Ensure that filtering that returns no rows from a table doesn't break a query"""
    empty_expr = pl.col('stop_time') > 99
    trials = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/intervals/trials",
        disable_progress=True,
    )
    units = lazynwb.scan_nwb(
        source=local_hdf5_path,
        table_path="/units",
        disable_progress=True,
    )
    assert trials.filter(empty_expr).collect().is_empty(), "This filtering should return an empty DataFrame for trials table"
    assert not units.collect().is_empty(), "Units table should not be empty for this test"
    lf = trials.filter(empty_expr).join(units, on=lazynwb.NWB_PATH_COLUMN_NAME, how="left")
    assert lf.filter(empty_expr).collect().is_empty(), "Filtering should return an empty DataFrame"

    lf = trials.join(units, on=lazynwb.NWB_PATH_COLUMN_NAME, how="left").filter(empty_expr)
    assert lf.filter(empty_expr).collect().is_empty(), "Filtering should return an empty DataFrame, regardless of query order"
    lf = units.join(trials, on=lazynwb.NWB_PATH_COLUMN_NAME, how="inner").filter(empty_expr)
    assert lf.filter(empty_expr).collect().is_empty(), "Filtering should return an empty DataFrame, regardless of join method"

def test_timeseries_with_rate(local_hdf5_path):
    # without timestamps, the default TimeSeries object has two keys: 'data' and
    # 'starting_time' which is another Group.
    # get_df() interprets them as 'data': List[float], 'starting_time': float
    # it needs to be aware of this possibility and generate a timestamps column
    lf = lazynwb.scan_nwb(local_hdf5_path, "processing/behavior/running_speed_with_rate")
    schema = lf.collect_schema()
    assert 'timestamps' in schema, f"'trials' table should provide a 'timestamps' column"
    assert 'timestamps' in lf.collect().columns, f"'trials' table should provide a 'timestamps' column"

def test_unique_count(local_hdf5_paths):
    df = lazynwb.scan_nwb(local_hdf5_paths, 'units').select('structure').unique().collect()
    assert len(df) == 1, f"Unique count should return a single row for the 'structure' column - check internal columns (underscore prefix) aren't being counted: {df=}"
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__])
