Contributing to PHIdelity
Thank you for your interest in contributing to PHIdelity, a Python package for intelligently anonymizing Protected Health Information (PHI) in clinical notes. We welcome contributions from the community to enhance features, improve performance, fix bugs, or expand documentation. This guide outlines how to contribute effectively.
Code of Conduct
By participating in this project, you agree to abide by our Code of Conduct. Please ensure all interactions are respectful, inclusive, and professional.
How to Contribute
1. Getting Started

Explore Issues: Check the Issues page for open tasks. Look for labels like good first issue or help wanted to find beginner-friendly tasks.
Discuss Ideas: If you have a new feature or improvement in mind, open an issue to discuss it before starting work to align with the project’s goals.
Fork the Repository: Create a personal fork of the repository on GitHub to work on your changes.

2. Setting Up Your Environment

Clone Your Fork:
git clone https://github.com/your-username/phidelity.git
cd phidelity


Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Install Ollama:

Follow instructions at ollama.ai to set up a local Ollama server.
Start the server: ollama serve.
Pull the default model: ollama pull qwen3:4B.


Verify Setup:Test the package locally:
phidelity --help



3. Making Changes

Create a Branch:Use a descriptive branch name related to your contribution:
git checkout -b feature/add-new-phi-type


Follow Coding Standards:

Write clear, readable code with meaningful variable names.
Add docstrings to all functions using the Google Python Style Guide.
Ensure compatibility with Python 3.8+.
Keep changes focused; avoid unrelated modifications in a single pull request.


Test Your Changes:

Run the package locally to verify functionality:phidelity --input test_note.txt --phi-output phi.csv --anonymized-output anonymized.txt


Add or update tests if applicable (see tests/ directory when available).
Ensure no new errors or warnings are introduced.


Update Documentation:

Modify README.md or other docs if your changes affect usage or setup.
Add comments in code for complex logic.



4. Submitting Your Contribution

Commit Changes:Use clear commit messages:
git commit -m "Add support for new PHI type: email addresses"


Push to Your Fork:
git push origin feature/add-new-phi-type


Open a Pull Request (PR):

Go to the main PHIdelity repository.
Create a PR from your branch to the main branch.
Include in your PR description:
A summary of changes.
Reference to any related issues (e.g., Fixes #123).
Any testing steps or special instructions for reviewers.




Respond to Feedback:

Maintainers may request changes or clarifications.
Make updates to your branch and push them; they’ll automatically update the PR.



5. Types of Contributions
We welcome contributions in various forms, including:

Bug Fixes: Address issues reported in the issue tracker.
New Features: Enhance PHI detection, add new output formats, or improve performance.
Documentation: Improve README, add examples, or clarify instructions.
Tests: Add unit or integration tests to ensure reliability.
Code Refactoring: Optimize code for readability or efficiency.
Issue Triage: Help reproduce bugs or clarify issue reports.

6. Development Guidelines

Package Structure: Maintain the existing structure (clinical_anonymizer/ for core modules).
Dependencies: Avoid adding new dependencies unless necessary; discuss in an issue first.
Error Handling: Ensure robust error handling, especially for LLM interactions and file I/O.
Backward Compatibility: Avoid breaking changes to the CLI or public API unless justified.
License: All contributions must comply with the MIT License.

7. Review Process

Review Timeline: Maintainers aim to review PRs within 7 days, but this may vary.
Approval: PRs require at least one maintainer’s approval to be merged.
CI Checks: Ensure any automated checks (if set up) pass before merging.
Merging: Maintainers will merge approved PRs or guide you to resolve conflicts.

Questions or Support
If you have questions or need help:

Open an issue with the question label.
Reach out via GitHub Discussions (if enabled).
Contact (add maintainer’s email if desired).

Acknowledgments
Thank you for contributing to PHIdelity! Your efforts help make healthcare data anonymization more accessible and effective for everyone.

Last updated: June 11, 2025
