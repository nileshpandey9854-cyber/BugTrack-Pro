# Agile + DevOps Notes — BugTrack Pro

## Product goal
Give a small software team one place to record defects, prioritize fixes, assign work, track status, and preserve issue discussion/history.

## Example product backlog

| ID | User story | Priority | Acceptance criteria |
|---|---|---|---|
| US-01 | As a tester, I want to create an issue so the team can investigate a defect. | High | Title and description are required; a new ID is created; issue appears in the list. |
| US-02 | As a developer, I want to change issue status so progress is visible. | High | Only supported statuses are accepted; changes appear in activity history. |
| US-03 | As a team member, I want to search/filter issues so I can find relevant work quickly. | High | Search and status/priority filters can be combined. |
| US-04 | As a lead, I want priority and severity fields so work can be triaged. | High | Both fields are validated and visible in dashboard/detail pages. |
| US-05 | As a team member, I want to comment on an issue so investigation notes stay with the issue. | Medium | Comment body is required and displayed with author/time. |
| US-06 | As a lead, I want to export issues as CSV for a report. | Medium | Export downloads issue fields in a spreadsheet-friendly format. |
| US-07 | As a developer, I want tests to run on pushes and pull requests so regressions are caught early. | High | GitHub Actions installs dependencies and reports test status. |

## Example two-sprint plan

### Sprint 1 — Issue basics
- Create/view/edit/delete issues
- Status and priority tracking
- Search, filters, and dashboard counts
- Acceptance review: create an issue, filter it, update status, and delete it

### Sprint 2 — Collaboration and quality
- Comments, activity history, CSV export
- Automated tests and GitHub Actions
- Responsive UI and documentation
- Acceptance review: tests pass locally and CI is green on a pull request

## Definition of Done
- Acceptance criteria met
- Invalid input handled
- Automated test added for meaningful behavior
- Changes reviewed and committed
- README updated if setup/behavior changed
- CI checks pass

## Example daily stand-up
- Yesterday: implemented issue creation and dashboard
- Today: add status updates and activity history
- Blocker: confirm how an older database should gain new columns

## DevOps flow

1. Developer creates a branch and changes code.
2. Developer pushes the branch to GitHub.
3. A pull request targets `main`.
4. GitHub Actions installs dependencies, checks Python syntax, and runs tests.
5. Team reviews the changes and merges only after checks pass.
6. Deployment is intentionally not automated in this learning project; configure it separately after choosing a hosting platform.

## Agile vs DevOps
- Agile helps the team plan and deliver useful increments in small cycles.
- DevOps connects development and operations with automation, testing, delivery, monitoring, and feedback.
- They complement one another; neither is just a tool or a single file.
