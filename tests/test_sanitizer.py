import pytest
import json
from unittest.mock import patch, mock_open

import requests
import sanitizer

# Sample clinical note and PHI list
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
        response = sanitizer.query_llm("Test prompt")
        assert response == "Mocked response"

def test_query_llm_failure():
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        response = sanitizer.query_llm("Test prompt")
        assert response.startswith("Error communicating with Ollama server")

def test_extract_json_after_think_valid():
    raw_response = "<think>Reasoning</think>" + json.dumps(SAMPLE_PHI_LIST)
    phi_list, error = sanitizer.extract_json_after_think(raw_response)
    assert phi_list == SAMPLE_PHI_LIST
    assert error is None

def test_extract_json_after_think_no_think_tag():
    raw_response = json.dumps(SAMPLE_PHI_LIST)
    phi_list, error = sanitizer.extract_json_after_think(raw_response)
    assert phi_list is None
    assert error == "No </think> tag found in response"

def test_generate_phi_csv_success(tmp_path):
    output_file = tmp_path / "phi_data.csv"
    success, message = sanitizer.generate_phi_csv(SAMPLE_PHI_LIST, str(output_file))
    assert success is True
    assert message == f"PHI data saved to '{output_file}'"
    with open(output_file, 'r') as f:
        content = f.read()
        assert "redacted_name_001,Name,John Doe,Patient Name" in content

def test_anonymize_clinical_note_success(tmp_path):
    csv_file = tmp_path / "phi_data.csv"
    sanitizer.generate_phi_csv(SAMPLE_PHI_LIST, str(csv_file))
    anonymized_note, error, message = sanitizer.anonymize_clinical_note(SAMPLE_NOTE, str(csv_file), str(tmp_path / "anonymized.txt"))
    assert error is None
    assert "[Patient Name]" in anonymized_note
    assert message.startswith("Anonymized note saved to")

def test_anonymize_clinical_note_csv_not_found(tmp_path):
    anonymized_note, error, message = sanitizer.anonymize_clinical_note(SAMPLE_NOTE, str(tmp_path / "nonexistent.csv"))
    assert anonymized_note is None
    assert error is None
    assert message.startswith("CSV file")