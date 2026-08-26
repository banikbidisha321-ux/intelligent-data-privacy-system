# Intelligent Data Privacy Management System

Phase 1 provides the shared Flask project foundation for the team.

## Run locally

1. Create and activate the virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the project dependency:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the application:

   ```powershell
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in a browser.

## Collaboration rules

- Do not commit `.venv`, `.env`, or secret keys.
- Pull the latest shared branch before starting work.
- Create a separate branch for each task and open a pull request for review.
- Keep this repository as the single shared codebase.
