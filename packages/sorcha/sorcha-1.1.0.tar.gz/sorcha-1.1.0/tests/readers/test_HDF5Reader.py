import numpy as np
import pytest
from numpy.testing import assert_equal

from sorcha.readers.HDF5Reader import HDF5DataReader
from sorcha.utilities.dataUtilitiesForTests import get_test_filepath


@pytest.mark.parametrize("use_cache", [True, False])
def test_HDF5DataReader_read_rows(use_cache):
    """Test that we can read in the ephemeris data from an HDF5 file."""
    reader = HDF5DataReader(get_test_filepath("ephemtestoutput.h5"), cache_table=use_cache)
    ephem_data = reader.read_rows()
    assert len(ephem_data) == 9
    assert reader.get_reader_info() == "HDF5DataReader:" + get_test_filepath("ephemtestoutput.h5")

    expected_first_row = np.array(
        [
            "S00000t",
            379,
            59853.205174,
            283890475.515,
            -1.12,
            11.969664,
            -0.280799,
            -0.19939,
            -0.132793,
            426166274.581,
            77286024.759,
            6987943.309,
            -2.356,
            11.386,
            4.087,
            148449956.422,
            18409281.409,
            7975891.432,
            -4.574,
            27.377,
            11.699,
            2.030016,
        ],
        dtype="object",
    )
    assert_equal(expected_first_row, ephem_data.iloc[0].values)

    column_headings = np.array(
        [
            "ObjID",
            "FieldID",
            "fieldMJD_TAI",
            "Range_LTC_km",
            "RangeRate_LTC_km_s",
            "RA_deg",
            "RARateCosDec_deg_day",
            "Dec_deg",
            "DecRate_deg_day",
            "Obj_Sun_x_LTC_km",
            "Obj_Sun_y_LTC_km",
            "Obj_Sun_z_LTC_km",
            "Obj_Sun_vx_LTC_km_s",
            "Obj_Sun_vy_LTC_km_s",
            "Obj_Sun_vz_LTC_km_s",
            "Obs_Sun_x_km",
            "Obs_Sun_y_km",
            "Obs_Sun_z_km",
            "Obs_Sun_vx_km_s",
            "Obs_Sun_vy_km_s",
            "Obs_Sun_vz_km_s",
            "phase_deg",
        ],
        dtype=object,
    )
    assert_equal(column_headings, ephem_data.columns.values)

    # Read in rows 3, 4, 5, 6 + the header
    ephem_data = reader.read_rows(3, 4)
    assert len(ephem_data) == 4
    assert_equal(column_headings, ephem_data.columns.values)
    assert_equal("S000021", ephem_data.iloc[0].values[0])


@pytest.mark.parametrize("use_cache", [True, False])
def test_HDF5DataReader_read_objects(use_cache):
    """Test that we can read in the ephemeris data for specific object IDs only."""
    reader = HDF5DataReader(get_test_filepath("ephemtestoutput.h5"), cache_table=use_cache)
    ephem_data = reader.read_objects(["S000015", "S000044"])
    assert len(ephem_data) == 5

    # Check that we correctly loaded the header information.
    column_headings = np.array(
        [
            "ObjID",
            "FieldID",
            "fieldMJD_TAI",
            "Range_LTC_km",
            "RangeRate_LTC_km_s",
            "RA_deg",
            "RARateCosDec_deg_day",
            "Dec_deg",
            "DecRate_deg_day",
            "Obj_Sun_x_LTC_km",
            "Obj_Sun_y_LTC_km",
            "Obj_Sun_z_LTC_km",
            "Obj_Sun_vx_LTC_km_s",
            "Obj_Sun_vy_LTC_km_s",
            "Obj_Sun_vz_LTC_km_s",
            "Obs_Sun_x_km",
            "Obs_Sun_y_km",
            "Obs_Sun_z_km",
            "Obs_Sun_vx_km_s",
            "Obs_Sun_vy_km_s",
            "Obs_Sun_vz_km_s",
            "phase_deg",
        ],
        dtype=object,
    )
    assert_equal(column_headings, ephem_data.columns.values)

    # Check that the first row matches.
    expected_first_row = np.array(
        [
            "S000015",
            60,
            59853.050544,
            668175640.541,
            23.682,
            312.82599,
            -0.143012,
            -49.366779,
            0.060345,
            444295081.174,
            -301086798.179,
            -499254823.262,
            1.334,
            2.899,
            -0.966,
            148508007.817,
            18043717.331,
            7819571.632,
            -4.132,
            27.288,
            11.702,
            11.073412,
        ],
        dtype="object",
    )
    assert_equal(expected_first_row, ephem_data.iloc[0].values)

    # Check that the remaining rows have the correct IDs.
    assert_equal(ephem_data.iloc[1].values[0], "S000015")
    assert_equal(ephem_data.iloc[2].values[0], "S000044")
    assert_equal(ephem_data.iloc[3].values[0], "S000044")
    assert_equal(ephem_data.iloc[4].values[0], "S000044")

    # Read different object IDs.
    ephem_data2 = reader.read_objects(["S000021"])
    assert len(ephem_data2) == 1
    assert_equal(ephem_data2.iloc[0].values[0], "S000021")


def test_bad_format():
    """Test that we fail if we try to read a non-HDF5 file."""
    reader = HDF5DataReader(get_test_filepath("testcolour.txt"))
    with pytest.raises(RuntimeError):
        _ = reader.read_rows()
