"""Aggregation helpers for the dashboard.

The dashboard view calls `compute_dashboard_payload()` to build the JSON
that the chart UI consumes. The payload includes a `version` field — a
short hash of the underlying data — so the front-end can detect when
something has changed and re-render only then (cheap auto-update).
"""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from datetime import timedelta
from statistics import mean

from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone

from .models import Attendance, Employee, Department


def _hours(record) -> float:
    if record.time_in and record.time_out:
        return (record.time_out - record.time_in).total_seconds() / 3600.0
    return 0.0


def _status(record) -> str:
    if not record.time_in:
        return 'Absent'
    if not record.time_out:
        return 'Timed In'
    return 'Complete'


def compute_dashboard_payload() -> dict:
    """Build the full dashboard dataset + a version hash for change detection."""
    today = timezone.localdate()
    last_14 = today - timedelta(days=14)

    qs = (
        Attendance.objects
        .select_related('employee', 'employee__department')
        .filter(date__gte=last_14, date__lte=today)
    )

    records = list(qs)
    employees = list(Employee.objects.select_related('department').all())

    # ---------- 1) Hours per employee (bar chart) ----------
    per_emp_hours = defaultdict(float)
    per_emp_days = defaultdict(int)
    per_emp_late = defaultdict(int)
    for r in records:
        if r.time_in and r.time_out:
            per_emp_hours[r.employee.full_name] += _hours(r)
            per_emp_days[r.employee.full_name] += 1
            # Late if time-in is past 09:00
            if r.time_in.time().hour > 9 or (r.time_in.time().hour == 9 and r.time_in.time().minute > 0):
                per_emp_late[r.employee.full_name] += 1

    hours_sorted = sorted(per_emp_hours.items(), key=lambda x: x[1], reverse=True)
    employee_names = [n for n, _ in hours_sorted]
    employee_hours = [round(h, 2) for _, h in hours_sorted]

    # ---------- 2) Status pie chart ----------
    status_count = defaultdict(int)
    for r in records:
        status_count[_status(r)] += 1
    status_labels = list(status_count.keys())
    status_values = list(status_count.values())

    # ---------- 3) Daily total-hours trend (line chart) ----------
    per_day = defaultdict(float)
    per_day_attendance = defaultdict(int)
    for r in records:
        if r.time_in and r.time_out:
            per_day[r.date.isoformat()] += _hours(r)
            per_day_attendance[r.date.isoformat()] += 1
    # Build contiguous date range
    day_labels, day_values, day_counts = [], [], []
    d = last_14
    while d <= today:
        iso = d.isoformat()
        day_labels.append(d.strftime('%b %d'))
        day_values.append(round(per_day.get(iso, 0.0), 2))
        day_counts.append(per_day_attendance.get(iso, 0))
        d += timedelta(days=1)

    # ---------- 4) Department comparison (horizontal bar) ----------
    per_dept = defaultdict(lambda: {'hours': 0.0, 'records': 0})
    for r in records:
        dept = r.employee.department.name if r.employee.department else 'Unassigned'
        per_dept[dept]['hours'] += _hours(r)
        per_dept[dept]['records'] += 1
    dept_labels = sorted(per_dept.keys())
    dept_hours = [round(per_dept[d]['hours'], 2) for d in dept_labels]
    dept_records = [per_dept[d]['records'] for d in dept_labels]

    # ---------- Quick insights (decision-making) ----------
    total_records = len(records)
    complete = status_count.get('Complete', 0)
    absent = status_count.get('Absent', 0)
    timed_in = status_count.get('Timed In', 0)
    avg_daily = round(mean(employee_hours), 2) if employee_hours else 0
    busiest_day_iso = max(per_day, key=per_day.get, default=None)
    busiest_day_label = (
        timezone.datetime.fromisoformat(busiest_day_iso).strftime('%b %d, %Y')
        if busiest_day_iso else 'N/A'
    )
    top_employee = hours_sorted[0][0] if hours_sorted else 'N/A'
    late_leader = (
        max(per_emp_late, key=per_emp_late.get) if per_emp_late else 'N/A'
    )
    late_count_leader = per_emp_late.get(late_leader, 0)

    insights = {
        'total_records': total_records,
        'complete': complete,
        'absent': absent,
        'timed_in': timed_in,
        'completion_rate': round((complete / total_records) * 100, 1) if total_records else 0,
        'avg_hours_per_employee': avg_daily,
        'busiest_day': busiest_day_label,
        'top_employee': top_employee,
        'late_leader': late_leader,
        'late_count_leader': late_count_leader,
    }

    payload = {
        'generated_at': timezone.now().isoformat(),
        'window': {'from': last_14.isoformat(), 'to': today.isoformat()},
        'employees': {
            'labels': employee_names,
            'hours': employee_hours,
            'late_count': [per_emp_late[n] for n in employee_names],
        },
        'status': {
            'labels': status_labels,
            'values': status_values,
        },
        'trend': {
            'labels': day_labels,
            'hours': day_values,
            'counts': day_counts,
        },
        'departments': {
            'labels': dept_labels,
            'hours': dept_hours,
            'records': dept_records,
        },
        'insights': insights,
    }

    # ---------- Version hash ----------
    # Hash the underlying numbers (not the timestamp) so two payloads
    # with the same data have the same version even if generated seconds
    # apart. The client compares this hash and re-fetches only on change.
    fingerprint = json.dumps(
        [employee_hours, status_values, day_values, dept_hours, dept_records],
        sort_keys=True,
    ).encode()
    payload['version'] = hashlib.md5(fingerprint).hexdigest()[:12]
    return payload
