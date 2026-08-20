from pydantic import BaseModel
from app.features.v1.appointments.schema import AppointmentRead


class PatientDashboardSummary(BaseModel):
    upcoming_appointment: AppointmentRead | None = None
    upcoming_count: int
    completed_count: int


class DoctorDashboardSummary(BaseModel):
    today_count: int
    upcoming_count: int
    today_appointments: list[AppointmentRead]
    schedule_count: int


class StaffDashboardSummary(BaseModel):
    today_count: int
    pending_count: int
    confirmed_count: int
    completed_count: int
    cancelled_count: int
    today_appointments: list[AppointmentRead]


class AdminDashboardSummary(BaseModel):
    total_users: int
    total_patients: int
    total_doctors: int
    total_staff: int
    active_doctors_count: int
    today_appointments_count: int
    pending_count: int
    confirmed_count: int
    completed_count: int
    cancelled_count: int
    total_specialties: int
    total_services: int
