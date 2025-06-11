# PHIdelity

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The **PHIdelity** is a Python tool that intelligently anonymizes Protected Health Information (PHI) in clinical notes while preserving their contextual meaning. Unlike basic redaction methods that obscure data, this tool uses a local Large Language Model (LLM) via Ollama to identify PHI (e.g., names, dates, medical record numbers) and replace it with meaningful, generalized descriptions (e.g., `[Patient Name]`, `[Date of Visit]`). This contextualized anonymization ensures the anonymized notes remain useful for research, analysis, or sharing while complying with privacy regulations like HIPAA.

The tool extracts PHI into a structured CSV file and saves the anonymized note as a text file, making it ideal for healthcare professionals, researchers, and developers handling sensitive medical data.

## Key Features

- **Contextualized Anonymization**: Replaces PHI with descriptive placeholders that retain the note's meaning (e.g., "John Doe" becomes `[Patient Name]`), enhancing usability for downstream applications.
- **Advanced PHI Detection**: Leverages a local LLM (default: `qwen3:4B`) to identify a wide range of PHI, including names, dates, medical record numbers, and more.
- **Structured Output**: Saves PHI to a CSV file with unique IDs, types, values, and descriptions for easy tracking and auditing.
- **Anonymized Note Export**: Generates a text file with the anonymized clinical note, ready for secure sharing or analysis.
- **Configurable and Local**: Runs on a local Ollama server, ensuring data privacy and allowing customization of the LLM model and output paths.
- **Open Source**: Licensed under the MIT License, inviting community contributions and adoption.

## Why Contextualized Anonymization?

Traditional anonymization methods often replace PHI with generic markers (e.g., `[REDACTED]`) or random strings, which can obscure the note's meaning and reduce its value for research or clinical review. The Clinical Note Anonymizer addresses this by:

- **Preserving Semantics**: Descriptive placeholders like `[Attending Physician Name]` or `[Medical Record Number]` maintain the note's context, making it interpretable for humans and machines.
- **Supporting Use Cases**: Anonymized notes remain suitable for medical research, machine learning training, or educational purposes without compromising privacy.
- **Ensuring Compliance**: By removing identifiable information while retaining structure, the tool helps meet strict privacy standards like HIPAA.

## Prerequisites

- **Python**: Version 3.8 or higher.
- **Ollama**: A running Ollama server (default: `http://localhost:11434/`) with the `qwen3:4B` model installed. See [Ollama's documentation](https://ollama.ai/) for setup.
- **Dependencies**: Python packages listed in `requirements.txt`.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/clinical-note-anonymizer.git
   cd clinical-note-anonymizer
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and Configure Ollama**:
   - Install Ollama from [ollama.ai](https://ollama.ai/).
   - Start the Ollama server:
     ```bash
     ollama serve
     ```
   - Pull the required model:
     ```bash
     ollama pull qwen3:4B
     ```

5. **Verify Setup**:
   Confirm the Ollama server is running at `http://localhost:11434/`:
   ```bash
   curl http://localhost:11434/api/generate -d '{"model": "qwen3:4B", "prompt": "Test"}'
   ```

## Usage

1. **Prepare a Clinical Note**:
   The script includes a sample clinical note in `anonymizer.py`. Modify the `clinical_note` variable or provide your own note as a string.

2. **Run the Script**:
   Process the clinical note to detect PHI and generate outputs:
   ```bash
   python anonymizer.py
   ```

3. **Outputs**:
   - **PHI Data** (`phi_data.csv`): A CSV file with columns: `ID`, `type`, `value`, `description`.
   - **Anonymized Note** (`anonymized_note.txt`): A text file with PHI replaced by contextual placeholders.
   - **Console Output**: Shows the LLM's JSON output, the anonymized note, and status messages.

4. **Example Output**:
   - `phi_data.csv`:
     ```
     ID,type,value,description
     redacted_name_001,Name,John Doe,Patient Name
     redacted_date_001,Date,June 11, 2025,Date of Visit
     redacted_medical_record_number_001,Medical Record Number,123456,Medical Record Number
     redacted_name_002,Name,Dr. Jane Smith,Attending Physician Name
     ...
     ```
   - `anonymized_note.txt`:
     ```
     Radiation Oncology Clinical Note
     Date of Visit: [Date of Visit]
     Patient Information

     Name: [Patient Name]
     Age: 65 years old
     Medical Record Number: [Medical Record Number]
     ...
     Physician: [Attending Physician Name]
     ```

5. **Customize Configuration**:
   Edit `anonymizer.py` to adjust:
   - `OLLAMA_ENDPOINT`: Ollama server URL (default: `http://localhost:11434/`).
   - `OLLAMA_MODEL`: LLM model (default: `qwen3:4B`).
   - Output file paths in `generate_phi_csv` and `anonymize_clinical_note`.

## File Structure

```
clinical-note-anonymizer/
├── anonymizer.py          # Main script for PHI detection and anonymization
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation (this file)
├── phi_data.csv           # Output CSV file (generated)
├── anonymized_note.txt    # Output anonymized note (generated)
```

## Contributing

We welcome contributions to enhance the Clinical Note Anonymizer, especially improvements to contextualization, LLM integration, or output formats. To contribute:

1. **Fork the Repository**: Create a fork on GitHub.
2. **Create a Branch**: Use a descriptive name (e.g., `feature/improve-phi-detection`).
3. **Make Changes**: Implement and test your changes.
4. **Submit a Pull Request**: Include a clear description and reference related issues.

Review the [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting.

## Issues and Support

Encounter a problem? Please:
- Check the [Issues](https://github.com/your-username/clinical-note-anonymizer/issues) page for similar reports.
- Open a new issue with details, including error messages and reproduction steps.

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

## Acknowledgments

- Powered by [Ollama](https://ollama.ai/) for secure, local LLM inference.
- Motivated by the need for privacy-preserving tools in healthcare that balance compliance and data utility.

## Contact

For inquiries or collaboration, use [GitHub Issues](https://github.com/your-username/clinical-note-anonymizer/issues) or contact (add your email if desired).

---

*Last updated: June 11, 2025*