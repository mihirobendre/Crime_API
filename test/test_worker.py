
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from api import (
    all_values_for,
    top_5_values,
    hist_plotter,
    line_plotter,
    worker
)


@pytest.fixture
def sample_data():
    # Sample data for testing
    data = [
        {"param": "value1"},
        {"param": "value2"},
        {"param": "value1"},
        {"param": "value3"},
        {"param": "value2"},
        {"param": "value1"},
        {"param": "value4"},
        {"param": "value5"}
    ]
    return data


def test_all_values_for(sample_data):
    # Test all_values_for function
    param = "param"
    result = all_values_for(param, sample_data)
    expected_result = {
        "value1": 3,
        "value2": 2,
        "value3": 1,
        "value4": 1,
        "value5": 1
    }
    assert result == expected_result


def test_top_5_values(sample_data):
    # Test top_5_values function
    data_dict = {
        "value1": 3,
        "value2": 2,
        "value3": 1,
        "value4": 1,
        "value5": 1
    }
    result = top_5_values(data_dict)
    expected_result = {
        "value1": 3,
        "value2": 2,
        "value3": 1,
        "value4": 1,
        "value5": 1
    }
    assert result == expected_result


@patch('api.rd.keys')
def test_hist_plotter(mock_keys):
    # Test hist_plotter function
    mock_keys.return_value = ['key1', 'key2']
    with patch('api.rd.get') as mock_get:
        mock_get.return_value = json.dumps({"param": "value"})
        hist_plotter("param")
    # Assert some conditions after the plot is made


@patch('api.rd.keys')
def test_line_plotter(mock_keys):
    # Test line_plotter function
    mock_keys.return_value = ['key1', 'key2']
    with patch('api.rd.get') as mock_get:
        mock_get.return_value = json.dumps({"occ_date": "2023-01-01", "crime_type": "Theft"})
        line_plotter()
    # Assert some conditions after the plot is made


def test_worker():
    # Test worker function
    job_data = {
        "id": "some_id",
        "status": "submitted",
        "job_type": "histogram",
        "params": {"param": "value"}
    }
    with patch('api.get_job_by_id') as mock_get_job_by_id:
        mock_get_job_by_id.return_value = job_data
        with patch('api.hist_plotter') as mock_hist_plotter:
            worker("some_id")
            mock_hist_plotter.assert_called_once_with("value")


