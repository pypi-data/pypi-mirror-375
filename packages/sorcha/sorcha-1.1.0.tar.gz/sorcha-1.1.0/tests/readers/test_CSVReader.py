import numpy as np
import os
import pandas as pd
import pytest
from numpy.testing import assert_equal
from pandas.testing import assert_frame_equal
import tempfile

from sorcha.readers.CSVReader import CSVDataReader
from sorcha.utilities.dataUtilitiesForTests import get_test_filepath


@pytest.mark.parametrize("use_cache", [True, False])
def test_CSVDataReader_ephem(use_cache):
    """Test that we can read in the ephemeris data from a CSV.

    This test does not perform any transformations, filtering, or validation of the data.
    It just loads it directly from a CSV.
    """
    csv_reader = CSVDataReader(get_test_filepath("ephemtestoutput.csv"), "csv", cache_table=use_cache)
    assert csv_reader.header_row == 0
    assert csv_reader.get_reader_info() == "CSVDataReader:" + get_test_filepath("ephemtestoutput.csv")

    # Read in all 9 rows.
    ephem_data = csv_reader.read_rows()
    assert len(ephem_data) == 9

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
    ephem_data = csv_reader.read_rows(3, 4)
    assert len(ephem_data) == 4
    assert_equal(column_headings, ephem_data.columns.values)
    assert_equal("S000021", ephem_data.iloc[0].values[0])


def test_CSVDataReader_ephemeris_header():
    """Test that we can read in the ephemeris data from a CSV when the header is NOT at row 0."""
    csv_reader = CSVDataReader(get_test_filepath("ephemtestoutput_comment.csv"), "csv")
    assert csv_reader.header_row == 2

    # Read in all 9 rows.
    ephem_data = csv_reader.read_rows()
    assert len(ephem_data) == 9

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
    ephem_data = csv_reader.read_rows(3, 4)
    assert len(ephem_data) == 4
    assert_equal(column_headings, ephem_data.columns.values)
    assert_equal("S000021", ephem_data.iloc[0].values[0])

    # Everything still works if we manually provide the header line.
    csv_reader2 = CSVDataReader(get_test_filepath("ephemtestoutput_comment.csv"), "csv", header=2)
    ephem_data2 = csv_reader2.read_rows()
    assert len(ephem_data2) == 9

    # Check that we fail if we provide the wrong header line number (skip the true header)
    with pytest.raises(SystemExit) as e1:
        _ = CSVDataReader(get_test_filepath("ephemtestoutput_comment.csv"), "csv", header=4)
    assert e1.type == SystemExit

    with pytest.raises(SystemExit) as e1:
        _ = CSVDataReader(get_test_filepath("ephemtestoutput_comment.csv"), "csv", header=1)
    assert e1.type == SystemExit


@pytest.mark.parametrize("use_cache", [True, False])
def test_CSVDataReader_specific_ephem(use_cache):
    """Test that we can read in the ephemeris data for specific object IDs only."""
    csv_reader = CSVDataReader(get_test_filepath("ephemtestoutput.csv"), "csv", cache_table=use_cache)
    ephem_data = csv_reader.read_objects(["S000015", "S000044"])
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
    ephem_data2 = csv_reader.read_objects(["S000021"])
    assert len(ephem_data2) == 1
    assert_equal(ephem_data2.iloc[0].values[0], "S000021")


def test_CSVDataReader_orbits():
    """Test that we can read in the orbit data.

    This test does not perform any transformations, filtering, or validation of the orbit data.
    It just loads it directly from a CSV.
    """
    orbit_des_reader = CSVDataReader(get_test_filepath("testorb.des"), "whitespace")
    assert orbit_des_reader.header_row == 0
    orbit_des = orbit_des_reader.read_rows()

    orbit_csv_reader = CSVDataReader(get_test_filepath("testorb.csv"), "csv")
    assert orbit_csv_reader.header_row == 0
    orbit_csv = orbit_des_reader.read_rows()

    # Check that the two files are the same.
    assert_frame_equal(orbit_csv, orbit_des)

    # Check that the column names and first row match expectations.
    expected_first_row = np.array(
        [
            "S00000t",
            "COM",
            0.952105479028,
            0.504888475701,
            4.899098347472,
            148.881068605772,
            39.949789586436,
            54486.32292808,
            54466.0,
        ],
        dtype=object,
    )

    expected_columns = np.array(
        [
            "ObjID",
            "FORMAT",
            "q",
            "e",
            "inc",
            "node",
            "argPeri",
            "t_p_MJD_TDB",
            "epochMJD_TDB",
        ],
        dtype=object,
    )
    assert_equal(expected_first_row, orbit_des.iloc[0].values)
    assert_equal(expected_columns, orbit_des.columns.values)
    assert len(orbit_des) == 5

    with pytest.raises(SystemExit) as e2:
        bad_reader = CSVDataReader(get_test_filepath("testorb.csv"), "whitespace")
        _ = bad_reader.read_rows()
    assert e2.type == SystemExit


def test_CSVDataReader_parameters():
    """Test that we can read in the parameters data.

    This test does not perform any transformations, filtering, or validation of the parameters data.
    It just loads it directly from a CSV.
    """
    # Only read in the first two lines.
    txt_reader = CSVDataReader(get_test_filepath("testcolour.txt"), "whitespace")
    assert txt_reader.header_row == 0
    params_txt = txt_reader.read_rows(0, 2)
    assert len(params_txt) == 2

    csv_reader = CSVDataReader(get_test_filepath("testcolour.csv"), "csv")
    assert csv_reader.header_row == 0
    params_csv = csv_reader.read_rows(0, 2)
    assert len(params_txt) == 2

    expected_first_line = np.array(["S00000t", 17.615, 0.3, 0.0, 0.1, 0.15], dtype=object)
    expected_columns = np.array(["ObjID", "H_r", "g-r", "i-r", "z-r", "GS"], dtype=object)
    assert_frame_equal(params_txt, params_csv)

    assert_equal(params_txt.iloc[0].values, expected_first_line)
    assert_equal(params_txt.columns.values, expected_columns)

    # Check a bad read.
    with pytest.raises(SystemExit) as e1:
        bad_reader = CSVDataReader(get_test_filepath("testcolour.txt"), "csv")
        _ = bad_reader.read_rows()
    assert e1.type == SystemExit

    # Test reading the full text file.
    params_txt2 = txt_reader.read_rows()
    assert len(params_txt2) == 5


def test_CSVDataReader_parameters_objects():
    """Test that we can read in the parameters data by object ID."""
    # Only read in the first two lines.
    txt_reader = CSVDataReader(get_test_filepath("testcolour.txt"), "whitespace")
    params_txt = txt_reader.read_objects(["S000015", "NonsenseID"])
    assert len(params_txt) == 1

    expected_first_line = np.array(["S000015", 22.08, 0.3, 0.0, 0.1, 0.15], dtype=object)
    expected_columns = np.array(["ObjID", "H_r", "g-r", "i-r", "z-r", "GS"], dtype=object)
    assert_equal(params_txt.iloc[0].values, expected_first_line)
    assert_equal(params_txt.columns.values, expected_columns)


def test_CSVDataReader_comets():
    reader = CSVDataReader(get_test_filepath("testcomet.txt"), "whitespace")
    observations = reader.read_rows(0, 1)

    expected = pd.DataFrame({"ObjID": ["67P/Churyumov-Gerasimenko"], "afrho1": [1552], "k": [-3.35]})
    assert_frame_equal(observations, expected)

    # Check reading with a bad format specification.
    with pytest.raises(SystemExit) as e1:
        reader = CSVDataReader(get_test_filepath("testcomet.txt"), "csv")
        _ = reader.read_rows(0, 1)
    assert e1.type == SystemExit


def test_CSVDataReader_delims():
    """Test that we check and match the delimiter during reader creation."""
    _ = CSVDataReader(get_test_filepath("testcolour.txt"), "whitespace")

    # Wrong delim type.
    with pytest.raises(SystemExit) as e1:
        _ = CSVDataReader(get_test_filepath("testcolour.txt"), "csv")
    assert e1.type == SystemExit

    # Invalid delim type.
    with pytest.raises(SystemExit) as e1:
        _ = CSVDataReader(get_test_filepath("testcolour.txt"), "many_commas")
    assert e1.type == SystemExit

    # Empty delim type.
    with pytest.raises(SystemExit) as e2:
        _ = CSVDataReader(get_test_filepath("testcolour.txt"), "")
    assert e2.type == SystemExit


def test_CSVDataReader_blank_lines():
    """Test that we fail if the input file has blank lines."""
    with tempfile.TemporaryDirectory() as dir_name:
        file_name = os.path.join(dir_name, "test.ecsv")
        with open(file_name, "w") as output:
            output.write("# My comment\n")
            output.write("ObjID,b,c\n")
            output.write("0,1,2\n")
            output.write("1,1,2\n")
            output.write("2,1,2\n")

        # The checks pass.
        reader = CSVDataReader(file_name, sep="csv", cache_table=False)
        data = reader.read_objects(["1", "2"])
        assert len(data) == 2

        with open(file_name, "a") as output:
            output.write("3,1,2\n")
            output.write("\n")  # add another blank line
            output.write("\n")  # add another blank line

        # The code now fails by default.
        reader2 = CSVDataReader(file_name, sep="csv", cache_table=False)
        with pytest.raises(SystemExit):
            _ = reader2.read_objects(["1", "2"])
