import os
import tempfile
import unittest

import app as bugtrack


class BugTrackProTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        bugtrack.app.config.update(TESTING=True, DATABASE_PATH=os.path.join(self.temp_dir.name, "test.db"))
        self.client = bugtrack.app.test_client()
        with bugtrack.app.app_context():
            bugtrack.init_db()

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_issue(self, title="Login button broken", **extra):
        data = {"title": title, "description": "Button does not respond when clicked.", "priority": "High", "severity": "Major", "assignee": "Aditi", "labels": "frontend, login", "due_date": ""}
        data.update(extra)
        return self.client.post("/bugs/new", data=data, follow_redirects=True)

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Issue dashboard", response.data)

    def test_create_issue_and_detail(self):
        response = self.create_issue()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login button broken", response.data)
        self.assertIn(b"Issue #1 created successfully.", response.data)

    def test_title_and_description_required(self):
        response = self.client.post("/bugs/new", data={"title": "", "description": ""}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"required", response.data)

    def test_search_and_priority_filter(self):
        self.create_issue()
        response = self.client.get("/?q=Login&priority=High")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login button broken", response.data)
        response = self.client.get("/?q=not-a-real-issue")
        self.assertNotIn(b"Login button broken", response.data)

    def test_status_update_records_activity(self):
        self.create_issue()
        response = self.client.post("/bugs/1/update-status", data={"status": "In Progress"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"In Progress", response.data)
        self.assertIn(b"Status changed", response.data)

    def test_invalid_status_is_rejected(self):
        self.create_issue()
        response = self.client.post("/bugs/1/update-status", data={"status": "Made Up"}, follow_redirects=True)
        self.assertIn(b"valid status", response.data)

    def test_comments_are_saved(self):
        self.create_issue()
        response = self.client.post("/bugs/1/comments", data={"author": "Ravi", "body": "I can reproduce this."}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"I can reproduce this", response.data)

    def test_csv_export(self):
        self.create_issue()
        response = self.client.get("/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"text/csv", response.content_type.encode())
        self.assertIn(b"Login button broken", response.data)

    def test_missing_issue_returns_404(self):
        self.assertEqual(self.client.get("/bugs/999").status_code, 404)

    def test_delete_issue(self):
        self.create_issue()
        response = self.client.post("/bugs/1/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Login button broken", response.data)


if __name__ == "__main__":
    unittest.main()
