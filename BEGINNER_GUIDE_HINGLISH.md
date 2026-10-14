# BugTrack Pro — Beginner Guide (Hinglish)

## 1. App ka kaam kya hai?
BugTrack Pro ek chhota issue/bug tracker hai. Jab kisi software mein problem milti hai, team us problem ko issue ke roop mein save kar sakti hai, priority set kar sakti hai, responsible person ka naam daal sakti hai, status update kar sakti hai, comments likh sakti hai aur CSV report export kar sakti hai.

## 2. Laptop par kaise chalana hai?

Windows PowerShell mein VS Code terminal kholo, aur confirm karo ki terminal isi project folder mein hai (jahan `app.py` aur `requirements.txt` hain).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Browser mein `http://127.0.0.1:5000` kholo. Terminal ko chalta rehne do; server band karne ke liye terminal mein `Ctrl+C` press karo.

Agar PowerShell environment activate karne se roke, direct venv Python use kar sakte ho:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## 3. App use karne ka practical workflow

1. **New issue** par click karo.
2. Title aur description likho. Example: `Login button not working`.
3. Priority choose karo: Low, Medium, High, Critical.
4. Severity choose karo: Minor, Major, Critical, Blocker. Priority aur severity alag concepts hain: priority batati hai kitni jaldi kaam karna hai; severity problem ka impact batati hai.
5. Assignee, labels aur due date optional hain.
6. Issue create karne ke baad detail page khulega.
7. Status ko Open → In Progress → Testing → Closed jaise workflow mein update karo. Team apne process ke mutabik status choose kar sakti hai.
8. Comments section mein investigation notes add karo.
9. Activity history mein status/details ke recorded changes dekho.
10. Dashboard par search, status/priority filters aur sorting try karo. Export CSV se spreadsheet file download karo.

## 4. Kaunsi file kya karti hai?

- `app.py`: Flask routes, input validation, SQLite queries, comments/activity aur CSV export. Yeh application ka Python brain hai.
- `templates/base.html`: Common page frame, navigation, footer aur flash messages.
- `templates/index.html`: Dashboard cards, filters aur issue table.
- `templates/bug_form.html`: New/edit issue form.
- `templates/detail.html`: Single issue, status form, comments aur activity history.
- `templates/error.html`: Friendly error page.
- `static/style.css`: Colours, spacing, layout, responsive/mobile styling.
- `bugs.db`: SQLite data file, first run par automatically banti hai. Is file ko delete karoge to local issue data chala jayega; pehle backup lena.
- `tests/test_app.py`: Automated tests, jo create/search/status/comments/export/delete jaise flows check karte hain.
- `.github/workflows/ci.yml`: GitHub par push/PR ke baad automated checks chalata hai.
- `Dockerfile`: Container image build karne ke instructions.
- `AGILE_DOCUMENTATION.md`: Example backlog, sprints aur Definition of Done.

## 5. GitHub Actions practical workflow

1. Project ko Git repository mein commit aur GitHub par push karo.
2. Repository ke **Actions** tab par jao.
3. `BugTrack Pro CI` workflow run khulega.
4. Workflow Python set up karta hai, dependencies install karta hai, syntax check karta hai aur tests chalata hai.
5. Green tick ka matlab configured checks pass hue; red cross ka matlab logs mein failure dekhna hai.
6. Is workflow mein automatic deployment nahi hai. CI aur deployment alag cheezein hain.

## 6. Tests locally kaise chalane hain?

```powershell
python -m pytest -v
```

Tests ek temporary database use karte hain, isliye normal `bugs.db` ko test data se overwrite nahi karna chahiye.

## 7. Learning note / limitations

Yeh educational portfolio project hai. Abhi login, multi-user permissions, CSRF protection, production server, monitoring aur automatic deployment included nahi hain. Public internet par production ke liye deploy karne se pehle security features aur production configuration add karna zaroori hai. `SECRET_KEY` ko public repository mein real secret ke roop mein kabhi commit mat karna; deployment par environment variable set karna.
