"""BugTrack Pro: a small issue tracker built with Flask and SQLite."""
from __future__ import annotations

import csv
import io
import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, Response, abort, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
STATUSES = ["Open", "In Progress", "Testing", "Closed"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
SEVERITIES = ["Minor", "Major", "Critical", "Blocker"]

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-key-change-before-deploying"),
    DATABASE_PATH=os.environ.get("DATABASE_PATH", str(BASE_DIR / "bugs.db")),
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
)


def get_db() -> sqlite3.Connection:
    """Return one SQLite connection for the current request."""
    if "db" not in g:
        db_path = app.config["DATABASE_PATH"]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create tables and add newer columns to an older BugTrack Lite database."""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            severity TEXT NOT NULL DEFAULT 'Major',
            status TEXT NOT NULL DEFAULT 'Open',
            assignee TEXT NOT NULL DEFAULT '',
            labels TEXT NOT NULL DEFAULT '',
            due_date TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    existing = {row["name"] for row in db.execute("PRAGMA table_info(bugs)").fetchall()}
    migrations = {
        "severity": "TEXT NOT NULL DEFAULT 'Major'",
        "labels": "TEXT NOT NULL DEFAULT ''",
        "due_date": "TEXT NOT NULL DEFAULT ''",
        "updated_at": "TEXT NOT NULL DEFAULT ''",
    }
    for column, definition in migrations.items():
        if column not in existing:
            db.execute(f"ALTER TABLE bugs ADD COLUMN {column} {definition}")
    db.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE
        )
    """)
    db.commit()


def log_activity(bug_id: int, action: str, details: str = "") -> None:
    get_db().execute(
        "INSERT INTO activity (bug_id, action, details) VALUES (?, ?, ?)",
        (bug_id, action, details),
    )


def get_bug_or_404(bug_id: int) -> sqlite3.Row:
    bug = get_db().execute("SELECT * FROM bugs WHERE id = ?", (bug_id,)).fetchone()
    if bug is None:
        abort(404)
    return bug


@app.before_request
def ensure_db() -> None:
    init_db()


@app.route("/")
def index():
    db = get_db()
    search = request.args.get("q", "").strip()[:100]
    status_filter = request.args.get("status", "")
    priority_filter = request.args.get("priority", "")
    sort = request.args.get("sort", "newest")
    conditions, params = [], []
    if search:
        conditions.append("(title LIKE ? OR description LIKE ? OR assignee LIKE ? OR labels LIKE ?")
        params.extend([f"%{search}%"] * 4)
        # Labels and free text are searched together with the other issue fields.
        conditions[-1] += ")"
    if status_filter in STATUSES:
        conditions.append("status = ?")
        params.append(status_filter)
    if priority_filter in PRIORITIES:
        conditions.append("priority = ?")
        params.append(priority_filter)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    order_by = {"oldest": "id ASC", "priority": "CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, id DESC", "updated": "updated_at DESC, id DESC"}.get(sort, "id DESC")
    bugs = db.execute(f"SELECT * FROM bugs{where} ORDER BY {order_by}", params).fetchall()
    counts = {row["status"]: row["count"] for row in db.execute("SELECT status, COUNT(*) AS count FROM bugs GROUP BY status")}
    total = db.execute("SELECT COUNT(*) FROM bugs").fetchone()[0]
    critical = db.execute("SELECT COUNT(*) FROM bugs WHERE priority IN ('High', 'Critical') AND status != 'Closed'").fetchone()[0]
    return render_template("index.html", bugs=bugs, statuses=STATUSES, priorities=PRIORITIES,
                           counts=counts, total=total, critical=critical, search=search,
                           status_filter=status_filter, priority_filter=priority_filter, sort=sort)


@app.route("/bugs/new", methods=["GET", "POST"])
def create_bug():
    values = {key: "" for key in ("title", "description", "assignee", "labels", "due_date")}
    values.update(priority="Medium", severity="Major")
    if request.method == "POST":
        for key in values:
            values[key] = request.form.get(key, "").strip()
        if not values["title"] or not values["description"]:
            flash("Title aur description required hain.", "error")
        elif len(values["title"]) > 120 or len(values["description"]) > 5000:
            flash("Title 120 aur description 5000 characters se chhota rakho.", "error")
        elif values["priority"] not in PRIORITIES or values["severity"] not in SEVERITIES:
            flash("Please valid priority aur severity select karo.", "error")
        elif values["due_date"] and not valid_date(values["due_date"]):
            flash("Due date valid date honi chahiye.", "error")
        else:
            db = get_db()
            cursor = db.execute("""INSERT INTO bugs
                (title, description, priority, severity, assignee, labels, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (values["title"], values["description"], values["priority"], values["severity"],
                 values["assignee"][:80], values["labels"][:160], values["due_date"]))
            bug_id = cursor.lastrowid
            log_activity(bug_id, "Issue created", f"Priority: {values['priority']}")
            db.commit()
            flash(f"Issue #{bug_id} created successfully.", "success")
            return redirect(url_for("bug_detail", bug_id=bug_id))
    return render_template("bug_form.html", page_title="Create issue", button_text="Create issue",
                           values=values, priorities=PRIORITIES, severities=SEVERITIES)


def valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


@app.route("/bugs/<int:bug_id>")
def bug_detail(bug_id: int):
    bug = get_bug_or_404(bug_id)
    comments = get_db().execute("SELECT * FROM comments WHERE bug_id = ? ORDER BY id DESC", (bug_id,)).fetchall()
    activity = get_db().execute("SELECT * FROM activity WHERE bug_id = ? ORDER BY id DESC LIMIT 20", (bug_id,)).fetchall()
    return render_template("detail.html", bug=bug, comments=comments, activity=activity,
                           statuses=STATUSES, priorities=PRIORITIES, severities=SEVERITIES)


@app.route("/bugs/<int:bug_id>/edit", methods=["GET", "POST"])
def edit_bug(bug_id: int):
    bug = get_bug_or_404(bug_id)
    values = dict(bug)
    if request.method == "POST":
        for key in ("title", "description", "assignee", "labels", "due_date"):
            values[key] = request.form.get(key, "").strip()
        values["priority"] = request.form.get("priority", "")
        values["severity"] = request.form.get("severity", "")
        if not values["title"] or not values["description"]:
            flash("Title aur description required hain.", "error")
        elif len(values["title"]) > 120 or len(values["description"]) > 5000:
            flash("Title 120 aur description 5000 characters se chhota rakho.", "error")
        elif values["priority"] not in PRIORITIES or values["severity"] not in SEVERITIES:
            flash("Invalid priority ya severity.", "error")
        elif values["due_date"] and not valid_date(values["due_date"]):
            flash("Due date valid date honi chahiye.", "error")
        else:
            db = get_db()
            db.execute("""UPDATE bugs SET title=?, description=?, priority=?, severity=?, assignee=?,
                labels=?, due_date=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                (values["title"], values["description"], values["priority"], values["severity"],
                 values["assignee"][:80], values["labels"][:160], values["due_date"], bug_id))
            log_activity(bug_id, "Issue edited", "Issue details updated")
            db.commit()
            flash(f"Issue #{bug_id} updated.", "success")
            return redirect(url_for("bug_detail", bug_id=bug_id))
    return render_template("bug_form.html", page_title=f"Edit issue #{bug_id}", button_text="Save changes",
                           values=values, priorities=PRIORITIES, severities=SEVERITIES)


@app.route("/bugs/<int:bug_id>/update-status", methods=["POST"])
def update_status(bug_id: int):
    bug = get_bug_or_404(bug_id)
    status = request.form.get("status", "")
    if status not in STATUSES:
        flash("Please valid status choose karo.", "error")
    else:
        db = get_db()
        db.execute("UPDATE bugs SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, bug_id))
        log_activity(bug_id, "Status changed", f"{bug['status']} → {status}")
        db.commit()
        flash("Status update ho gaya.", "success")
    return redirect(url_for("bug_detail", bug_id=bug_id))


@app.route("/bugs/<int:bug_id>/comments", methods=["POST"])
def add_comment(bug_id: int):
    get_bug_or_404(bug_id)
    author = request.form.get("author", "").strip()[:80] or "Team member"
    body = request.form.get("body", "").strip()
    if not body or len(body) > 2000:
        flash("Comment required hai aur 2000 characters se chhota hona chahiye.", "error")
    else:
        db = get_db()
        db.execute("INSERT INTO comments (bug_id, author, body) VALUES (?, ?, ?)", (bug_id, author, body))
        log_activity(bug_id, "Comment added", f"Comment by {author}")
        db.commit()
        flash("Comment add ho gaya.", "success")
    return redirect(url_for("bug_detail", bug_id=bug_id) + "#comments")


@app.route("/bugs/<int:bug_id>/delete", methods=["POST"])
def delete_bug(bug_id: int):
    get_bug_or_404(bug_id)
    db = get_db()
    db.execute("DELETE FROM bugs WHERE id = ?", (bug_id,))
    db.commit()
    flash(f"Issue #{bug_id} deleted.", "success")
    return redirect(url_for("index"))


@app.route("/export.csv")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Description", "Status", "Priority", "Severity", "Assignee", "Labels", "Due date", "Created", "Updated"])
    rows = get_db().execute("SELECT * FROM bugs ORDER BY id DESC").fetchall()
    for bug in rows:
        writer.writerow([bug["id"], bug["title"], bug["description"], bug["status"], bug["priority"], bug["severity"], bug["assignee"], bug["labels"], bug["due_date"], bug["created_at"], bug["updated_at"]])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=bugtrack-issues.csv"})


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="Issue nahi mila ya page exist nahi karta."), 404


@app.errorhandler(413)
def too_large(_error):
    return render_template("error.html", code=413, message="Request bahut badi hai. Chhota input try karo."), 413


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
