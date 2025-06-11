# PHIdelity

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![PyPI version](https://badge.fury.io/py/phidelity.svg)](https://pypi.org/project/phidelity/)

## Overview

**PHIdelity** is a Python package designed to intelligently anonymize Protected Health Information (PHI) in clinical notes while preserving their contextual meaning. Unlike traditional redaction tools that simply obscure data, PHIdelity leverages a local Large Language Model (LLM) via [Ollama](https://ollama.ai/) to detect PHI (e.g., names, dates, medical record numbers) and replace it with meaningful, generalized placeholders (e.g., `[Patient Name]`, `[Date of Visit]`). This approach ensures that anonymized notes remain valuable for research, analysis, or sharing, all while adhering to privacy standards like HIPAA.

PHIdelity offers a flexible command-line interface (CLI) and importable Python functions, extracting PHI into structured CSV files and saving anonymized notes as text files. It’s an ideal tool for healthcare professionals, researchers, and developers working with sensitive medical data.

## Key Features

- **Contextualized Anonymization**: Replaces PHI with descriptive placeholders (e.g., "John Doe" → `[Patient Name]`), maintaining the note’s usability.
- **Advanced PHI Detection**: Uses a local LLM (default: `qwen3:4B`) to identify diverse PHI types, including names, dates, and medical record numbers.
- **Structured Output**: Exports PHI details to a CSV file with unique IDs, types, values, and descriptions for tracking and auditing.
- **Anonymized Note Export**: Saves the anonymized note as a text file, ready for secure use.
- **Local and Configurable**: Operates on a local Ollama server for data privacy, with customizable LLM models and output paths.
- **Open Source**: Released under the MIT License, encouraging community contributions.

## Why Contextualized Anonymization?

Traditional methods often replace PHI with generic markers (e.g., `[REDACTED]`) or random strings, stripping notes of their meaning and utility. PHIdelity improves on this by:

- **Preserving Semantics**: Placeholders like `[Attending Physician Name]` or `[Medical Record Number]` keep the note interpretable.
- **Supporting Use Cases**: Enables research, machine learning, and education with privacy intact.
- **Ensuring Compliance**: Removes identifiable data while retaining structure, aligning with regulations like HIPAA.

## Installation

PHIdelity is available on PyPI and can be installed easily with pip.

### Steps

1. **Install PHIdelity**:
   ```bash
   pip install phidelity
   ```

2. **Prerequisites**:
   - **Python**: Version 3.8 or higher.
   - **Ollama**: A running Ollama server (default: `http://localhost:11434/`) with the `qwen3:4B` model installed.

3. **Set Up Ollama**:
   - Install Ollama from [ollama.ai](https://ollama.ai/).
   - Start the server:
     ```bash
     ollama serve
     ```
   - Pull the default model:
     ```bash
     ollama pull qwen3:4B
     ```
   - Verify it’s running:
     ```bash
     curl http://localhost:11434/api/generate -d '{"model": "qwen3:4B", "prompt": "Test"}'
     ```

## Usage

PHIdelity can be used via its command-line interface (CLI) or as a Python module.

### Command-Line Interface (CLI)

The CLI provides a straightforward way to anonymize clinical notes.

#### Basic Commands

- **Anonymize a File**:
  ```bash
  phidelity --input clinical_note.txt --phi-output phi_data.csv --anonymized-output anonymized_note.txt
  ```
- **Anonymize from stdin**:
  ```bash
  echo "Clinical note text" | phidelity
  ```

#### Options

- `--input`: Path to the input clinical note (default: stdin).
- `--phi-output`: Path for the PHI CSV output (default: none).
- `--anonymized-output`: Path for the anonymized note (default: stdout).
- `--endpoint`: Ollama server URL (default: `http://localhost:11434/`).
- `--model`: LLM model (default: `qwen3:4B`).

Run `phidelity --help` for full details.

### Python Module

Use PHIdelity programmatically in your Python projects.

#### Example

```python
from phidelity import generate_prompt, query_llm, extract_phi_list, anonymize_note

# Define a clinical note
note = """
Radiation Oncology Clinical Note
Date of Visit: June 11, 2025
Patient Information
Name: John Doe
"""

# Process the note
prompt = generate_prompt(note)
response, error = query_llm(prompt)
if not error:
    phi_list, error = extract_phi_list(response)
    if not error:
        anonymized_note = anonymize_note(note, phi_list)
        print(anonymized_note)
else:
    print(f"Error: {error}")
```

#### Output Example

- **Anonymized Note**:
  ```
  Radiation Oncology Clinical Note
  Date of Visit: [Date of Visit]
  Patient Information
  Name: [Patient Name]
  ```
- **PHI CSV** (if saved):
  ```
  ID,type,value,description
  redacted_name_001,Name,John Doe,Patient Name
  redacted_date_001,Date,June 11, 2025,Date of Visit
  ```

## Configuration

- **Ollama Settings**: Customize the endpoint and model via CLI options (`--endpoint`, `--model`) or function parameters.
- **Output Paths**: Specify paths with `--phi-output` and `--anonymized-output` in the CLI; defaults to stdout for the note and no CSV if unspecified.

## Contributing

Contributions are welcome! To get started:

1. Fork the repository on GitHub.
2. Create a branch (e.g., `feature/better-phi-detection`).
3. Make and test your changes.
4. Submit a pull request with a clear description.

See [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for more details.

## Issues and Support

If you encounter issues:
- Check the [Issues](https://github.com/your-username/phidelity/issues) page.
- Submit a new issue with details like error messages and steps to reproduce.

## License

PHIdelity is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

## Acknowledgments

- Built with [Ollama](https://ollama.ai/) for local LLM inference.
- Inspired by the need for privacy-preserving healthcare tools that retain data utility.

## Contact

For questions or collaboration, use [GitHub Issues](https://github.com/your-username/phidelity/issues) or reach out at (add your email if desired).

---

*Last updated: June 11, 2025*