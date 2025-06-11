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


def group_names_by_person(phi_list, clinical_note):
    """
    Group names that refer to the same person, distinguishing patients from physicians.
    """
    name_items = [item for item in phi_list if item["type"] == "Name"]
    non_name_items = [item for item in phi_list if item["type"] != "Name"]

    def extract_name_parts(name, description):
        name = name.strip()
        words = name.split()
        if not words:
            return "", "", False
        is_physician = "dr." in name.lower() or "physician" in description.lower()
        if is_physician:
            if len(words) == 1:
                return "", "", True
            surname = words[-1].lower()
            first_name = words[1].lower() if len(words) > 2 else ""
        else:
            if len(words) == 1:
                return words[0].lower(), "", False
            if words[0].lower() in ["mr.", "ms.", "mrs."]:
                surname = words[-1].lower()
                first_name = words[1].lower() if len(words) > 2 else ""
            else:
                surname = words[-1].lower()
                first_name = words[0].lower()
        return first_name, surname, is_physician

    name_info = []
    for item in name_items:
        first_name, surname, is_physician = extract_name_parts(item["text"], item.get("description", ""))
        name_info.append({
            "item": item,
            "first_name": first_name,
            "surname": surname,
            "is_physician": is_physician,
            "original_index": len(name_info)
        })

    patient_names = [info for info in name_info if not info["is_physician"]]
    physician_names = [info for info in name_info if info["is_physician"]]

    patient_groups = defaultdict(list)
    for idx, info in enumerate(patient_names):
        key = info["surname"] if info["surname"] else info["first_name"]
        if key:
            patient_groups[key].append(idx)

    patient_final_groups = []
    used_patient_indices = set()
    for key, indices in patient_groups.items():
        if not indices:
            continue
        group = set(indices)
        for idx in indices:
            info = patient_names[idx]
            first_name = info["first_name"]
            if first_name and first_name != key:
                for other_key, other_indices in patient_groups.items():
                    if other_key != key:
                        for other_idx in other_indices:
                            if patient_names[other_idx]["first_name"] == first_name:
                                group.update(other_indices)
        if group and not group.issubset(used_patient_indices):
            patient_final_groups.append(list(group))
            used_patient_indices.update(group)

    for idx, info in enumerate(patient_names):
        if idx not in used_patient_indices and (info["first_name"] or info["surname"]):
            for group in patient_final_groups:
                for g_idx in group:
                    if patient_names[g_idx]["first_name"] == info["first_name"] and info["first_name"]:
                        group.append(idx)
                        used_patient_indices.add(idx)
                        break
            else:
                patient_final_groups.append([idx])
                used_patient_indices.add(idx)

    physician_groups = [[i] for i in range(len(physician_names))]

    final_groups = patient_final_groups + physician_groups

    for item in phi_list:
        item["person_id"] = ""

    person_counter = 1
    for group in final_groups:
        person_id = f"person_{person_counter:03d}"
        for idx in group:
            if group in patient_final_groups:
                name_items[patient_names[idx]["original_index"]]["person_id"] = person_id
            else:
                name_items[physician_names[idx]["original_index"]]["person_id"] = person_id
        person_counter += 1

    return name_items + non_name_items


def generate_phi_csv(phi_list, output_file="phi_data.csv"):
    """
    Convert a list of PHI items to CSV with description and person_id, and save to a file.
    """
    try:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "type", "value", "description", "person_id"])
            type_counts = defaultdict(int)

            for item in phi_list:
                type_ = item["type"]
                text = item["text"]
                description = item.get("description", "")
                person_id = item.get("person_id", "")

                type_counts[type_] += 1
                count = type_counts[type_]
                type_lower = type_.lower().replace(" ", "_")
                id_ = f"redacted_{type_lower}_{count:03d}"

                writer.writerow([id_, type_, text, description, person_id])
        return True, f"PHI data saved to '{output_file}'"
    except Exception as e:
        return False, f"Failed to save CSV: {str(e)}"


# Clinical note derived from your CSV data
clinical_note = """
Patient John Doe, residing at 123 Main St, Anytown, USA, with phone number 555-123-4567 and email johndoe@example.com, was admitted on 2023-01-01.
Mr. Doe complained of headache and nausea when he presented. John said he had just come back from a trip to south africa.
Dr. Kole saw the patient on 06/10/2025 with a planned follow up by Dr. Hoyle and the IR team on 06/12/2025
"""

# Construct the prompt for the LLM with updated instructions for generalized descriptions
prompt = f"""
Please identify all protected health information (PHI) in the following clinical note. PHI includes all names and name variations (full names, first names only, last names with titles like 'Mr.', 'Ms.', or 'Dr.', or any other references to an individual, including patients and physicians), addresses, email addresses, phone numbers, social security numbers, medical record numbers, dates related to the individual (such as birth dates, admission dates, or appointment dates), and any other information that can be used to identify an individual.

For each piece of PHI, provide a 'description' field that explains its context or role in the clinical note without including specific names or other PHI. Use generalized terms like "Patient's Full Name," "Attending Physician," or "Follow-up Physician" for names, and specify the purpose of dates without referencing individuals (e.g., "Date of Visit with Attending Physician," "Follow-up Appointment Date with Follow-up Physician"). For addresses, indicate whether it is the patient's home address or the clinic's address (e.g., "Patient's Home Address," "Clinic Address").

Provide the results as a JSON array, where each object has 'type', 'text', and 'description' fields, like this: [{{"type": "Name", "text": "John Doe", "description": "Patient's Full Name"}}, {{"type": "Date", "text": "2023-01-01", "description": "Admission Date"}}, ...]. Ensure all references to individuals (patients and physicians) are included as separate 'Name' entries with appropriate generalized descriptions. Do not include any additional text in the response, only the JSON array wrapped in <think> reasoning </think> tags.

Clinical Note:
{clinical_note}
"""

# Query the LLM and get the response
raw_response = query_llm(prompt)

# Extract and process the JSON
phi_list, error = extract_json_after_think(raw_response)
if phi_list is not None:
    print("LLM JSON output:", json.dumps(phi_list, indent=2))  # Debug output
    phi_list = group_names_by_person(phi_list, clinical_note)
    success, message = generate_phi_csv(phi_list)
    if success:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)
else:
    print(f"Error: {error}", file=sys.stderr)
    print("Raw response from LLM:", raw_response, file=sys.stderr)