      Quick summary of important info below:
      When you start working on this repo
      1. create your own branch from the main
      2. write unit tests for new code
      3. check that all your unit tests cover your code and run locally
      4. when you want to commit to your branch, run locally pre-commit:
            pre-commit run --all-files
      pre-commit automatically triggers style & linting tools, which adjust the style of the code
      7. if it fails, fix the errors
      8. when pre-commit passed all tests, push the changes to the remote feature branch
      9. merge-squash to the dev branch

2. Coding Standards
PEP 8 Compliance: Follow the PEP 8 style guide for Python code. This includes naming conventions, indentation, line length, and more.

Docstrings: Use clear and descriptive docstrings for all functions and classes. Follow the PEP 257 guidelines.

Type Annotations: Include type annotations for function arguments and return types to enhance code readability and facilitate debugging.

Modular Code: Write modular code with functions and classes in the tools directory. Avoid putting complex logic directly
in Jupyter notebooks—keep notebooks focused on using and combining functions for analysis.

Dependencies: add all the dependencies to the requirements.txt file. When choosing not a standard package,
make sure that it is maintained and doesn't have weird dependencies.

3. Version Control Best Practices
Branching Strategy:

Main Branch: The main branch should always be stable and ready for production. Only well-tested code should be merged here.
Feature Branches: For new features or bug fixes, create a separate branch (feature/feature-name or bugfix/bug-description) and submit a pull request for review. After the work on the feature branch is done, merge-squash the branch to dev.
Pull Requests (PRs): Before merging a PR, ensure it is reviewed by at least one other team member. Use descriptive titles and include a summary of changes.

Commit Messages:

Use clear and concise commit messages.
Follow the format: Type: Short description (fixes #issue-number)

4. Documentation
Notebooks:

Each notebook should start with a markdown cell that outlines its purpose, data sources, and any relevant background information.
Use markdown cells within notebooks to explain the steps and logic used in the analysis.
Avoid duplicating code in notebooks—use functions from the tools directory.
Notebooks should not contain definitions of the functions.

In-Line Comments:

Use in-line comments sparingly to explain complex or non-obvious code sections.

5. Testing
Unit Tests:

Write unit tests for all functions in the tools directory. Store tests in the tests/ directory.
Use pytest for testing and ensure that tests cover a range of possible inputs, including edge cases.
Run tests locally before pushing changes to ensure nothing is broken.

You can conveniently run the test suite in the commandline using
`make test`

6. Pre-Commit
Code Style and Data Security:
This repository is configured with a pre-commit hook that enforces code style and data security. Before every commit, the hooks run isort for import sorting, black for code formatting, flake8 for linting, and detect_emails.py to check for emails in CSV files and that CSV files are readable. To manually run the pre-commit checks on all files, you can use the following command:

`pre-commit run --all-files`

7. Continuous Integration (CI)
This repository is equipped with automatic workflows that enforce checks before every commit. These workflows ensure that our code adheres to the standards we are trying to defend.

