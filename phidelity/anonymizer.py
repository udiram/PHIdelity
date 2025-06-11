import requests
import json
import csv
from collections import defaultdict

DEFAULT_ENDPOINT = "http://localhost:11434/"
DEFAULT_MODEL = "qwen3:4B"

def query_llm(prompt, endpoint=DEFAULT_ENDPOINT, model=DEFAULT_MODEL):
    """Query the LLM with a given prompt and return the response."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(f"{endpoint}/api/generate", json=payload,
                                 headers={"Content-Type": "application/json"})
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received"), None
    except requests.exceptions.RequestException as e:
        return None, f"Error communicating with Ollama server: {str(e)}"

def extract_phi_list(raw_response):
    """Extract the JSON content after the </think> tag."""
    try:
        think_end = raw_response.find("</think>")
        if think_end == -1:
            return None, "No </think> tag found in response"
        json_part = raw_response[think_end + len("</think>"):].strip()
        phi_list = json.loads(json_part)
        if not isinstance(phi_list, list):
            return None, "Parsed content is not a list"
        return phi_list, None
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def generate_phi_csv(phi_list, output_file):
    """Convert a list of PHI items to CSV with description and save to a file."""
    try:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "type", "value", "description"])
            type_counts = defaultdict(int)

            for item in phi_list:
                type_ = item["type"]
                text = item["text"]
                description = item.get("description", "")

                type_counts[type_] += 1
                count = type_counts[type_]
                type_lower = type_.lower().replace(" ", "_")
                id_ = f"redacted_{type_lower}_{count:03d}"

                writer.writerow([id_, type_, text, description])
        return True, f"PHI data saved to '{output_file}'"
    except Exception as e:
        return False, f"Failed to save CSV: {str(e)}"

def anonymize_note(clinical_note, phi_list):
    """Anonymize the clinical note by replacing PHI with [description]."""
    # Sort PHI items by length of 'text' in descending order to avoid partial replacements
    phi_list.sort(key=lambda x: len(x["text"]), reverse=True)
    anonymized_note = clinical_note
    for item in phi_list:
        text = item["text"]
        description = item["description"]
        anonymized_note = anonymized_note.replace(text, f"[{description}]")
    return anonymized_note

def generate_prompt(clinical_note):
    """Generate a prompt for the LLM to identify PHI in the clinical note."""
    return f"""
Please identify all protected health information (PHI) in the following clinical note. PHI includes all names and name variations (full names, first names only, last names with titles like 'Mr.', 'Ms.', or 'Dr.', or any other references to an individual, including patients and physicians), addresses, email addresses, phone numbers, social security numbers, medical record numbers, dates related to the individual (such as birth dates, admission dates, or appointment dates), and any other information that can be used to identify an individual.

For each piece of PHI, provide a 'description' field that explains its context or role in the clinical note without including specific names or other PHI. For names, use 'Patient Name' for the patient, 'Attending Physician Name' for the attending physician, 'Follow-up Physician Name' for the follow-up physician, etc., and ensure that all references to the same individual have the same description, regardless of how the name is presented. For other PHI, use descriptions like 'Date of Visit', 'Medical Record Number', 'Clinic Address', etc.

Provide the results as a JSON array, where each object has 'type', 'text', and 'description' fields, like this: [{{"type": "Name", "text": "John Doe", "description": "Patient Name"}}, {{"type": "Date", "text": "2023-01-01", "description": "Admission Date"}}, ...]. Ensure all references to individuals (patients and physicians) are included as separate 'Name' entries with appropriate generalized descriptions. Do not include any additional text in the response, only the JSON array wrapped in <think> reasoning </think> tags.

Clinical Note:
{clinical_note}
"""