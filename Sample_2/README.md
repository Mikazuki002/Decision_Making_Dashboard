# Office DTR System

A Django-based **Daily Time Record** system for a small office. Built-in
SQLite database ships with sample departments, employees, and 14 days of
attendance records so you can explore the UI immediately.

## Features

- 👥 **Employees** — directory sorted alphabetically (last name, first name)
- 📋 **Attendance** — master DTR list with quick time-in / time-out buttons
- 🔎 **Live search** — instant client-side filtering as you type (plus
  server-side query for downloads)
- 🔄 **Auto-update** — every edit re-renders the affected row; the changed
  cell flashes yellow
- ⬇️ **Download** — CSV and Excel (.xlsx) exports honour the current
  filters
- 🗄️ **Built-in database** — `db.sqlite3` ships with 7 departments,
  12 employees, ~90 attendance rows
- 📊 **Decision-making dashboard** — 4 charts (hours-per-employee bar,
  status doughnut, daily-trend line, department comparison) + 4 quick
  insight cards (completion rate, top performer, late leader, busiest day)
- 🔁 **Self-updating charts** — page polls every 5s; if data changed
  (version hash flipped), charts and insights re-render automatically
- 📤 **Excel round-trip** — Download Excel → edit → Upload Modified Excel
  → DB updates → charts refresh on next poll

## Run it

```bash
pip install django openpyxl
python manage.py migrate              # creates db.sqlite3
python manage.py seed_dtr             # fills sample data (idempotent)
python manage.py createsuperuser      # optional, for admin / login
python manage.py runserver
```

Open http://127.0.0.1:8000/ → the Attendance page.

## URLs

| Path | What it does |
|---|---|
| `/` | Attendance list (alphabetical, live search, downloads) |
| `/attendance/` | Same view |
| `/employees/` | Employee directory (alphabetical) |
| `/employees/new/` | Add employee |
| `/employees/<id>/` | Per-employee DTR history |
| `/employees/<id>/edit/` | Edit employee |
| `/employees/<id>/download.csv` | Per-employee CSV |
| `/download/csv/` | Whole-DTR CSV (honours `?q=&date_from=&date_to=`) |
| `/download/excel/` | Whole-DTR Excel |
| `/admin/` | Django admin |
| `/login/`, `/logout/` | Auth (only needed for adding/editing) |
| `/dashboard/` | Decision-making dashboard with 4 auto-updating charts |
| `/dashboard/data.json` | JSON payload powering the charts (with a `version` hash) |
| `/dashboard/upload/` | Upload a modified Excel to refresh the data |

## File map

```
office_dtr/                  Django project (settings, urls)
dtr/
  models.py                  Department, Employee, Attendance
  views.py                   list / search / edit / time-in/out / downloads
  forms.py                   EmployeeForm, AttendanceForm
  urls.py
  admin.py
  management/commands/
    seed_dtr.py              Built-in sample data loader
  templates/dtr/             base, login, attendance_list, employee_*
  static/dtr/                styles.css, app.js (live-search + flash)
  migrations/
db.sqlite3                   Built-in SQLite database (created by migrate + seed_dtr)
```

## How the requirements map to code

| Requirement | Implementation |
|---|---|
| Data downloadable | `views.download_csv`, `views.download_excel`, `views.download_employee_csv` |
| Change one part → auto-update | Every POST redirects back to the same list; the row re-renders with the new value and flashes yellow (`static/dtr/js/app.js`) |
| Search function | `#live-search` filters rows on the client; server-side `?q=` filters for downloads and reloads |
| Always alphabetical | `models.Meta.ordering = ['last_name', 'first_name']` on Employee + explicit `order_by('employee__last_name', 'employee__first_name')` in every view |
| Built-in database | `db.sqlite3` is committed-ready; `python manage.py seed_dtr` populates sample data |
| Python + Django | Django 5.2, Python 3.13 |