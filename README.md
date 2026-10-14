# BugTrack Pro

A beginner-friendly, portfolio-ready issue tracking application built with Flask and SQLite. It demonstrates practical Agile issue management plus a basic DevOps CI pipeline using GitHub Actions.

## Features

- Dashboard with total, open, in-progress, and active high-priority issue counts
- Create, view, edit, update status, and delete issues
- Search across title, description, assignee, and labels
- Filter by status and priority; sort by newest, oldest, recent update, or priority
- Priority, severity, assignee, labels, and due date fields
- Comments and issue activity history
- CSV export for spreadsheet/reporting use
- Input validation, parameterized SQL, readable error pages, and responsive layout
- SQLite schema migration so a basic older BugTrack Lite database can gain new fields
- Unit/integration tests and GitHub Actions CI
- Dockerfile for a consistent local container environment

## Run locally (Windows PowerShell)

1. Extract the ZIP and open the `BugTrack-Agile-DevOps` folder in VS Code.
2. Open the VS Code terminal in that folder.
3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the application:

   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser. The `bugs.db` SQLite database is created automatically.

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.\.venv\Scripts\python.exe app.py` without activating the environment.

## Run tests

```powershell
python -m pytest -v
```

Tests use a temporary SQLite database, so they do not need to use your normal `bugs.db`.

## GitHub Actions CI

Workflow file: `.github/workflows/ci.yml`

When code is pushed to `main`, or a pull request targets `main`, GitHub Actions checks out the repository, installs Python 3.12 and dependencies, checks Python syntax, and runs the test suite. See GitHub → repository → **Actions** to view logs and results. The workflow does not deploy the app; deployment is a separate future step.

## Docker (optional)

```powershell
docker build -t bugtrack-pro .
docker run --rm -p 5000:5000 -e DATABASE_PATH=/tmp/bugs.db bugtrack-pro
```

## Project structure

```text
BugTrack-Agile-DevOps/
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
├── AGILE_DOCUMENTATION.md
├── .github/workflows/ci.yml
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── bug_form.html
│   ├── detail.html
│   └── error.html
├── static/style.css
└── tests/test_app.py
```

## Important scope and production notes

This is a learning/portfolio project, not a fully secured multi-user production service. It currently has no authentication, role-based access, CSRF protection, or production hosting configuration. Before public deployment, add those controls, use a strong `SECRET_KEY` environment variable, configure a production WSGI server, and review logging/backups. Do not expose sensitive real bug reports in a public demo.

## Agile demonstration

Suggested sprint: build issue CRUD, dashboard and filters first; then add comments/activity; then strengthen tests and CI. Keep a backlog, write acceptance criteria, estimate work, review the increment, and record retrospective improvements. See `AGILE_DOCUMENTATION.md`.
