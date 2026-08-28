# Intelligent Data Privacy Management System

Phase 1 provides the shared Flask project foundation for the team.

## Phase 2 database files

The MySQL table design and setup instructions are in [database/README.md](database/README.md).

## Phase 3: Connect Flask to MySQL

1. Make a local file named `.env` in this project folder. It is ignored by Git and must never be uploaded.
2. Copy the format from `.env.example`, replacing `YOUR_MYSQL_ROOT_PASSWORD` with your MySQL password.
3. Install the added dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Start the app and open `http://127.0.0.1:5000/database-status`.

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

When setup is correct, the status page returns `"connected"`. This phase only verifies a connection; no project features use the database yet.

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
