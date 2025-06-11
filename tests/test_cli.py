import json

import pytest
from unittest.mock import patch, mock_open
import sys
from io import StringIO
from phidelity.cli import main

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


def test_cli_stdin_stdout(capsys):
    with patch("sys.stdin", StringIO(SAMPLE_NOTE)), \
            patch("phidelity.anonymizer.query_llm") as mock_query, \
            patch("phidelity.anonymizer.extract_phi_list") as mock_extract:
        mock_query.return_value = ("<think>Reasoning</think>" + json.dumps(SAMPLE_PHI_LIST), None)
        mock_extract.return_value = (SAMPLE_PHI_LIST, None)
        sys.argv = ["cli.py"]
        main()
        captured = capsys.readouterr()
        assert "[Patient Name]" in captured.out
        assert "[Date of Visit]" in captured.out


def test_cli_input_file_output_file(tmp_path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "anonymized.txt"
    phi_output = tmp_path / "phi_data.csv"
    input_file.write_text(SAMPLE_NOTE)

    with patch("phidelity.anonymizer.query_llm") as mock_query, \
            patch("phidelity.anonymizer.extract_phi_list") as mock_extract:
        mock_query.return_value = ("<think>Reasoning</think>" + json.dumps(SAMPLE_PHI_LIST), None)
        mock_extract.return_value = (SAMPLE_PHI_LIST, None)
        sys.argv = ["cli.py", "--input", str(input_file), "--anonymized-output", str(output_file), "--phi-output",
                    str(phi_output)]
        main()
        assert output_file.exists()
        assert phi_output.exists()
        with open(output_file, 'r') as f:
            content = f.read()
            assert "[Patient Name]" in content


def test_cli_llm_error(capsys):
    with patch("sys.stdin", StringIO(SAMPLE_NOTE)), \
            patch("phidelity.anonymizer.query_llm") as mock_query:
        mock_query.return_value = (None, "Connection error")
        sys.argv = ["cli.py"]
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert "Error: Connection error" in captured.err