import requests
import json
import csv
import sys
from collections import defaultdict

# Configuration for LLM endpoint and model
OLLAMA_ENDPOINT = "http://localhost:11434/"
OLLAMA_MODEL = "qwen3:4B"

def query_llm(prompt):
    """Query the LLM with a given prompt and return the response."""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(f"{OLLAMA_ENDPOINT}/api/generate", json=payload,
                                 headers={"Content-Type": "application/json"})
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama server: {str(e)}"

def extract_json_after_think(raw_response):
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

def generate_phi_csv(phi_list, output_file="phi_data.csv"):
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

def anonymize_clinical_note(clinical_note, csv_file="phi_data.csv", output_file="anonymized_note.txt"):
    """Anonymize the clinical note by replacing PHI with [description] and save to a text file."""
    try:
        # Load PHI data from CSV
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            phi_items = list(reader)

        # Sort PHI items by length of 'value' in descending order to avoid partial replacements
        phi_items.sort(key=lambda x: len(x["value"]), reverse=True)

        # Perform replacements
        anonymized_note = clinical_note
        for item in phi_items:
            value = item["value"]
            description = item["description"]
            anonymized_note = anonymized_note.replace(value, f"[{description}]")

        # Save anonymized note to text file
        with open(output_file, 'w') as txtfile:
            txtfile.write(anonymized_note)

        return anonymized_note, None, f"Anonymized note saved to '{output_file}'"
    except FileNotFoundError:
        return None, None, f"CSV file '{csv_file}' not found"
    except Exception as e:
        return None, None, f"Error anonymizing note: {str(e)}"

# Example clinical note
clinical_note = """
Radiation Oncology Clinical Note
Date of Visit: June 11, 2025
Patient Information

Name: John Doe  
Age: 65 years old  
Medical Record Number: 123456

Reason for Visit

Follow-up after completing radiation therapy for prostate cancer

Medical History

Diagnosed with prostate cancer (stage T2c, Gleason 7) two years ago  
Underwent radical prostatectomy  
Received adjuvant radiation therapy (66 Gy in 33 fractions) completed six months ago  
Pre-treatment PSA: 12 ng/mL  
Post-prostatectomy PSA: 0.2 ng/mL  
Post-radiation PSA: undetectable

Physical Examination

Vital Signs: BP 120/80 mmHg, HR 70 bpm, RR 16 breaths/min, Temp 98.6°F  
General Appearance: Well-nourished, no distress  
Findings: No lymphadenopathy; no radiation dermatitis or other skin changes; no complaints of urinary or bowel symptoms

Assessment and Plan

Assessment: Mr. Doe is a 65-year-old male with a history of prostate cancer, status post radical prostatectomy and adjuvant radiation therapy. Currently doing well, with no evidence of disease recurrence. PSA remains undetectable. No significant treatment-related side effects.  
Plan: Continue with regular follow-up visits every six months, with PSA testing at each visit. Next visit scheduled for December 11, 2025.

Physician: Dr. Jane Smith, MD
"""

# Construct the prompt for the LLM
prompt = f"""
Please identify all protected health information (PHI) in the following clinical note. PHI includes all names and name variations (full names, first names only, last names with titles like 'Mr.', 'Ms.', or 'Dr.', or any other references to an individual, including patients and physicians), addresses, email addresses, phone numbers, social security numbers, medical record numbers, dates related to the individual (such as birth dates, admission dates, or appointment dates), and any other information that can be used to identify an individual.

For each piece of PHI, provide a 'description' field that explains its context or role in the clinical note without including specific names or other PHI. For names, use 'Patient Name' for the patient, 'Attending Physician Name' for the attending physician, 'Follow-up Physician Name' for the follow-up physician, etc., and ensure that all references to the same individual have the same description, regardless of how the name is presented. For other PHI, use descriptions like 'Date of Visit', 'Medical Record Number', 'Clinic Address', etc.

Provide the results as a JSON array, where each object has 'type', 'text', and 'description' fields, like this: [{{"type": "Name", "text": "John Doe", "description": "Patient Name"}}, {{"type": "Date", "text": "2023-01-01", "description": "Admission Date"}}, ...]. Ensure all references to individuals (patients and physicians) are included as separate 'Name' entries with appropriate generalized descriptions. Do not include any additional text in the response, only the JSON array wrapped in <think> reasoning </think> tags.

Clinical Note:
{clinical_note}
"""

# Query the LLM and process the response
raw_response = query_llm(prompt)
phi_list, error = extract_json_after_think(raw_response)
if phi_list is not None:
    print("LLM JSON output:", json.dumps(phi_list, indent=2))  # Debug output
    success, message = generate_phi_csv(phi_list)
    if success:
        print(message)
        anonymized_note, error, save_message = anonymize_clinical_note(clinical_note)
        if anonymized_note is not None:
            print("\nAnonymized Clinical Note:")
            print(anonymized_note)
            print(save_message)
        else:
            print(f"Error: {error}", file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
else:
    print(f"Error: {error}", file=sys.stderr)
    print("Raw response from LLM:", raw_response, file=sys.stderr)