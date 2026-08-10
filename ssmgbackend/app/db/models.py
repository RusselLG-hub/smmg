"""Central model registry used by migration metadata discovery."""

from app.features.v1.ai_integration.model import AIChatMessage, AIChatSession
from app.features.v1.appointments.model import Appointment
from app.features.v1.auth.model import VerificationCode
from app.features.v1.doctors.model import DoctorProfile
from app.features.v1.patients.model import PatientProfile
from app.features.v1.schedules.model import DoctorSchedule, DoctorScheduleOverride
from app.features.v1.services.model import Service
from app.features.v1.specialties.model import Specialty
from app.features.v1.users.model import User

__all__ = [
    "User",
    "VerificationCode",
    "Specialty",
    "Service",
    "DoctorProfile",
    "PatientProfile",
    "DoctorSchedule",
    "DoctorScheduleOverride",
    "Appointment",
    "AIChatSession",
    "AIChatMessage",
]
