import pytest
import json
import csv
from unittest.mock import patch, mock_open

import requests

from phidelity.anonymizer import query_llm, extract_phi_list, generate_phi_csv, anonymize_note, generate_prompt

# Sample clinical note for testing
SAMPLE_NOTE = """
Patient: John Doe
Date: June 11, 2025
MRN: 123456
Physician: Dr. Jane Smith
"""

SAMPLE_PHI_LIST = [
    {"type": "Name", "text": "John Doe", "description": "Patient Name"},
    {"type": "Date", "text": "June 11, 2025", "description": "Date of Visit"},
    {"type": "Medical Record Number", "text": "123456", "description": "Medical Record Number"},
    {"type": "Name", "text": "Dr. Jane Smith", "description": "Attending Physician Name"}
]

def test_query_llm_success():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "Mocked response"}
        response, error = query_llm("Test prompt")
        assert response == "Mocked response"
        assert error is None
        mock_post.assert_called_once()

def test_query_llm_failure():
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        response, error = query_llm("Test prompt")
        assert response is None
        assert error == "Error communicating with Ollama server: Connection error"

def test_extract_phi_list_valid():
    raw_response = "<think>Reasoning</think>" + json.dumps(SAMPLE_PHI_LIST)
    phi_list, error = extract_phi_list(raw_response)
    assert phi_list == SAMPLE_PHI_LIST
    assert error is None

def test_extract_phi_list_no_think_tag():
    raw_response = json.dumps(SAMPLE_PHI_LIST)
    phi_list, error = extract_phi_list(raw_response)
    assert phi_list is None
    assert error == "No </think> tag found in response"

def test_extract_phi_list_invalid_json():
    raw_response = "<think>Reasoning</think>{invalid json}"
    phi_list, error = extract_phi_list(raw_response)
    assert phi_list is None
    assert error.startswith("Failed to parse JSON")

def test_extract_phi_list_non_list():
    raw_response = "<think>Reasoning</think>" + json.dumps({"not": "a list"})
    phi_list, error = extract_phi_list(raw_response)
    assert phi_list is None
    assert error == "Parsed content is not a list"

def test_generate_phi_csv_success(tmp_path):
    output_file = tmp_path / "phi_data.csv"
    success, message = generate_phi_csv(SAMPLE_PHI_LIST, str(output_file))
    assert success is True
    assert message == f"PHI data saved to '{output_file}'"
    with open(output_file, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 5  # Header + 4 data rows
        assert rows[0] == ["ID", "type", "value", "description"]
        assert rows[1][0].startswith("redacted_name_001")
        assert rows[1][1] == "Name"
        assert rows[1][2] == "John Doe"
        assert rows[1][3] == "Patient Name"
        assert rows[2][0].startswith("redacted_date_001")
        assert rows[2][1] == "Date"
        assert rows[2][2] == "June 11, 2025"
        assert rows[2][3] == "Date of Visit"
        assert rows[3][0].startswith("redacted_medical_record_number_001")
        assert rows[3][1] == "Medical Record Number"
        assert rows[3][2] == "123456"
        assert rows[3][3] == "Medical Record Number"
        assert rows[4][0].startswith("redacted_name_002")
        assert rows[4][1] == "Name"
        assert rows[4][2] == "Dr. Jane Smith"
        assert rows[4][3] == "Attending Physician Name"

def test_generate_phi_csv_failure(tmp_path):
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        success, message = generate_phi_csv(SAMPLE_PHI_LIST, str(tmp_path / "phi_data.csv"))
        assert success is False
        assert message == "Failed to save CSV: Permission denied"

def test_anonymize_note():
    anonymized = anonymize_note(SAMPLE_NOTE, SAMPLE_PHI_LIST)
    assert "[Patient Name]" in anonymized
    assert "[Date of Visit]" in anonymized
    assert "[Medical Record Number]" in anonymized
    assert "[Attending Physician Name]" in anonymized
    assert "John Doe" not in anonymized

def test_anonymize_note_empty():
    anonymized = anonymize_note("", SAMPLE_PHI_LIST)
    assert anonymized == ""

def test_anonymize_note_no_phi():
    anonymized = anonymize_note(SAMPLE_NOTE, [])
    assert anonymized == SAMPLE_NOTE

def test_generate_prompt():
    prompt = generate_prompt(SAMPLE_NOTE)
    assert "Please identify all protected health information (PHI)" in prompt
    assert SAMPLE_NOTE in prompt
    assert "<think> reasoning </think>" in prompt