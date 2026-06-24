from django.db import models
from django.urls import reverse


class Department(models.Model):
    """Office department — e.g. HR, Accounting, IT."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']  # always alphabetical

    def __str__(self):
        return self.name


class Employee(models.Model):
    """An office employee tracked by the DTR system."""
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees'
    )
    position = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Always alphabetical — sort by last_name then first_name.
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('dtr:employee_detail', args=[self.pk])


class Attendance(models.Model):
    """A single day's time record for an employee.

    time_in / time_out are stored as DateTime so we can compute total
    hours accurately (including half-days and overtime).
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default listing is alphabetical by employee last name, then by date desc.
        ordering = ['employee__last_name', 'employee__first_name', '-date']
        unique_together = [('employee', 'date')]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['employee', 'date']),
        ]

    def __str__(self):
        return f"{self.employee} — {self.date}"

    @property
    def total_hours(self):
        """Decimal hours worked, or None if not yet timed out."""
        if not self.time_in or not self.time_out:
            return None
        delta = self.time_out - self.time_in
        return round(delta.total_seconds() / 3600.0, 2)

    @property
    def status(self):
        if not self.time_in:
            return 'Absent'
        if not self.time_out:
            return 'Timed In'
        return 'Complete'
