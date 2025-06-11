import argparse
import sys
from phidelity.anonymizer import query_llm, extract_phi_list, generate_phi_csv, anonymize_note, generate_prompt

def main():
    parser = argparse.ArgumentParser(description="Anonymize clinical notes using an LLM")
    parser.add_argument("--input", help="Input clinical note file (default: stdin)", default=None)
    parser.add_argument("--phi-output", help="Output CSV file for PHI data (default: none)", default=None)
    parser.add_argument("--anonymized-output", help="Output file for anonymized note (default: stdout)", default=None)
    parser.add_argument("--endpoint", help="Ollama server endpoint", default="http://localhost:11434/")
    parser.add_argument("--model", help="LLM model to use", default="qwen3:4B")
    parser.add_argument("--version", action="version", version="phidelity 0.1.0")
    args = parser.parse_args()

    # Read clinical note from file or stdin
    if args.input:
        with open(args.input, 'r') as f:
            clinical_note = f.read()
    else:
        clinical_note = sys.stdin.read()

    # Process the note
    prompt = generate_prompt(clinical_note)
    raw_response, error = query_llm(prompt, args.endpoint, args.model)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    phi_list, error = extract_phi_list(raw_response)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    anonymized_note = anonymize_note(clinical_note, phi_list)

    # Save PHI CSV if specified
    if args.phi_output:
        success, message = generate_phi_csv(phi_list, args.phi_output)
        if not success:
            print(f"Error: {message}", file=sys.stderr)
            sys.exit(1)
        print(f"PHI data saved to {args.phi_output}")

    # Output anonymized note to file or stdout
    if args.anonymized_output:
        with open(args.anonymized_output, 'w') as f:
            f.write(anonymized_note)
        print(f"Anonymized note saved to {args.anonymized_output}")
    else:
        print(anonymized_note)

if __name__ == "__main__":
    main()