"""Seed built-in sample data for the Office DTR system.

Idempotent: re-running is safe — it skips records that already exist.
Usage:
    python manage.py seed_dtr
    python manage.py seed_dtr --reset   # wipe and re-seed
"""
from datetime import date, datetime, time, timedelta
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from dtr.models import Department, Employee, Attendance


DEPARTMENTS = [
    'Accounting',
    'Administration',
    'Human Resources',
    'Information Technology',
    'Marketing',
    'Operations',
    'Sales',
]

# (employee_id, first, last, dept, position)
EMPLOYEES = [
    ('EMP-001', 'Ana',     'Reyes',      'Accounting',            'Senior Accountant'),
    ('EMP-002', 'Ben',     'Cruz',       'Information Technology','IT Specialist'),
    ('EMP-003', 'Carlo',   'Bautista',   'Operations',            'Operations Lead'),
    ('EMP-004', 'Diana',   'Garcia',     'Human Resources',       'HR Officer'),
    ('EMP-005', 'Edward',  'Lopez',      'Marketing',             'Marketing Coordinator'),
    ('EMP-006', 'Faith',   'Mendoza',    'Sales',                 'Sales Executive'),
    ('EMP-007', 'Gabriel', 'Santos',     'Information Technology','System Administrator'),
    ('EMP-008', 'Hannah',  'Villanueva', 'Administration',        'Office Manager'),
    ('EMP-009', 'Ian',     'Del Rosario','Accounting',            'Bookkeeper'),
    ('EMP-010', 'Julia',   'Aquino',     'Human Resources',       'Recruiter'),
    ('EMP-011', 'Kenneth', 'Ramos',      'Operations',            'Logistics Coordinator'),
    ('EMP-012', 'Lara',    'Fernandez',  'Marketing',             'Graphic Designer'),
]


class Command(BaseCommand):
    help = 'Seed built-in sample data (departments, employees, DTR records).'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Wipe data first.')

    def handle(self, *args, **opts):
        if opts['reset']:
            self.stdout.write('Wiping existing DTR data…')
            Attendance.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()

        # Departments
        dept_map = {}
        for name in DEPARTMENTS:
            obj, created = Department.objects.get_or_create(name=name)
            dept_map[name] = obj
        self.stdout.write(self.style.SUCCESS(f"Departments ready: {len(dept_map)}"))

        # Employees
        emp_objs = []
        for eid, first, last, dept, pos in EMPLOYEES:
            obj, _ = Employee.objects.get_or_create(
                employee_id=eid,
                defaults=dict(
                    first_name=first,
                    last_name=last,
                    department=dept_map[dept],
                    position=pos,
                    is_active=True,
                ),
            )
            emp_objs.append(obj)
        self.stdout.write(self.style.SUCCESS(f"Employees ready: {len(emp_objs)}"))

        # DTR records for the last 14 weekdays
        today = timezone.localdate()
        records_created = 0
        rng = random.Random(42)  # deterministic
        days_back = 0
        target = 14
        while records_created < target * len(emp_objs) // 2 and days_back < 30:
            d = today - timedelta(days=days_back)
            days_back += 1
            if d.weekday() >= 5:  # skip weekends
                continue
            for emp in emp_objs:
                if Attendance.objects.filter(employee=emp, date=d).exists():
                    continue
                if rng.random() < 0.08:  # ~8% absent days
                    Attendance.objects.create(employee=emp, date=d)
                    continue
                in_hour = rng.randint(0, 1)  # 8 or 9
                in_min = rng.randint(0, 59)
                out_hour = 17 + rng.randint(0, 1)
                out_min = rng.randint(0, 59)
                time_in = timezone.make_aware(datetime.combine(d, time(in_hour + 8, in_min)))
                time_out = timezone.make_aware(datetime.combine(d, time(out_hour, out_min)))
                Attendance.objects.create(
                    employee=emp, date=d,
                    time_in=time_in, time_out=time_out,
                    remarks='',
                )
                records_created += 1
        self.stdout.write(self.style.SUCCESS(f"Attendance records created: {records_created}"))
        self.stdout.write(self.style.SUCCESS('Seed complete.'))
