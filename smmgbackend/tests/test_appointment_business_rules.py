import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, patch

from app.core.exceptions import BadRequestException, ForbiddenException
from app.features.v1.appointments import schema, service


def user(role: str, user_id: str = "user-1") -> SimpleNamespace:
    return SimpleNamespace(id=user_id, role=role, email="patient@example.com", name="Patient")


def appointment(status: str = "pending", doctor_id: str = "doctor-1") -> SimpleNamespace:
    patient_user = SimpleNamespace(email="patient@example.com", name="Patient")
    doctor_user = SimpleNamespace(name="Doctor")
    return SimpleNamespace(
        id="appointment-1",
        patient_profile_id="patient-1",
        doctor_profile_id=doctor_id,
        status=status,
        appointment_reference="APT-TEST",
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
        patient=SimpleNamespace(user=patient_user),
        doctor=SimpleNamespace(user=doctor_user),
        reminder_sent_at=None,
    )


class AppointmentBusinessRuleTests(unittest.IsolatedAsyncioTestCase):
    async def test_patient_booking_is_created_pending(self):
        created = appointment()
        doctor = SimpleNamespace(id="doctor-1", is_active=True, specialty=None, user=SimpleNamespace(name="Doctor"))
        with (
            patch.object(service.patient_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="patient-1"))),
            patch.object(service.doctor_repository, "get_by_id", AsyncMock(return_value=doctor)),
            patch.object(service, "_validate_slot_against_schedule", AsyncMock(return_value=(created.scheduled_at, 30))),
            patch.object(service.appointment_repository, "check_active_conflict", AsyncMock(return_value=False)),
            patch.object(service.appointment_repository, "get_by_reference", AsyncMock(return_value=None)),
            patch.object(service.appointment_repository, "create_appointment", AsyncMock(return_value=created)) as create,
            patch.object(service.notification_service, "send_booking_notification"),
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=created),
        ):
            result = await service.create_appointment(
                AsyncMock(), user("patient"),
                schema.AppointmentCreate(doctor_profile_id="doctor-1", date="2099-01-01", time="09:00"),
            )
        self.assertIs(result, created)
        self.assertEqual(create.await_args.kwargs["status"], "pending")

    async def test_non_patient_cannot_book(self):
        with self.assertRaises(ForbiddenException):
            await service.create_appointment(
                AsyncMock(), user("staff"),
                schema.AppointmentCreate(doctor_profile_id="doctor-1", date="2099-01-01", time="09:00"),
            )

    async def test_service_specialty_must_match_doctor(self):
        doctor = SimpleNamespace(
            id="doctor-1", is_active=True, specialty_id="specialty-a",
            specialty=None, user=SimpleNamespace(name="Doctor"),
        )
        clinic_service = SimpleNamespace(
            id="service-1", is_active=True, specialty_id="specialty-b", name="Cardiology",
        )
        with (
            patch.object(service.patient_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="patient-1"))),
            patch.object(service.doctor_repository, "get_by_id", AsyncMock(return_value=doctor)),
            patch.object(service.clinic_service_repository, "get_by_id", AsyncMock(return_value=clinic_service)),
            patch.object(service, "_validate_slot_against_schedule", AsyncMock()) as validate_slot,
        ):
            with self.assertRaises(BadRequestException):
                await service.create_appointment(
                    AsyncMock(), user("patient"),
                    schema.AppointmentCreate(
                        doctor_profile_id="doctor-1", service_id="service-1",
                        date="2099-01-01", time="09:00",
                    ),
                )
        validate_slot.assert_not_awaited()

    async def test_available_date_override_replaces_weekly_schedule(self):
        override = SimpleNamespace(
            is_available=True, start_time="09:00", end_time="11:00"
        )
        with (
            patch.object(service.schedule_repository, "get_override_by_date", AsyncMock(return_value=override)),
            patch.object(service.schedule_repository, "get_by_doctor_and_day", AsyncMock()) as weekly,
        ):
            scheduled_at, duration = await service._validate_slot_against_schedule(
                AsyncMock(), "doctor-1", "2099-01-01", "09:30"
            )
        self.assertEqual(scheduled_at.strftime("%H:%M"), "09:30")
        self.assertEqual(duration, 30)
        weekly.assert_not_awaited()

    async def test_staff_can_confirm_pending(self):
        appt = appointment("pending")
        updated = appointment("confirmed")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.appointment_repository, "update_status", AsyncMock(return_value=updated)) as update,
            patch.object(service.notification_service, "send_status_confirmed_notification"),
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=updated),
        ):
            await service.update_appointment_status(
                AsyncMock(), user("staff"), appt.id, schema.AppointmentStatusUpdate(status="confirmed")
            )
        update.assert_awaited_once_with(ANY, appt.id, "confirmed")

    async def test_staff_cannot_complete_confirmed(self):
        with patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appointment("confirmed"))):
            with self.assertRaises(BadRequestException):
                await service.update_appointment_status(
                    AsyncMock(), user("staff"), "appointment-1", schema.AppointmentStatusUpdate(status="completed")
                )

    async def test_assigned_doctor_can_complete_confirmed(self):
        appt = appointment("confirmed")
        updated = appointment("completed")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.doctor_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="doctor-1"))),
            patch.object(service.appointment_repository, "update_status", AsyncMock(return_value=updated)) as update,
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=updated),
        ):
            await service.update_appointment_status(
                AsyncMock(), user("doctor"), appt.id, schema.AppointmentStatusUpdate(status="completed")
            )
        self.assertEqual(update.await_args.args[2], "completed")

    async def test_doctor_cannot_complete_pending(self):
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appointment("pending"))),
            patch.object(service.doctor_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="doctor-1"))),
        ):
            with self.assertRaises(BadRequestException):
                await service.update_appointment_status(
                    AsyncMock(), user("doctor"), "appointment-1", schema.AppointmentStatusUpdate(status="completed")
                )

    async def test_doctor_cannot_update_another_doctors_appointment(self):
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appointment("confirmed", "doctor-2"))),
            patch.object(service.doctor_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="doctor-1"))),
        ):
            with self.assertRaises(ForbiddenException):
                await service.update_appointment_status(
                    AsyncMock(), user("doctor"), "appointment-1", schema.AppointmentStatusUpdate(status="completed")
                )

    async def test_patient_cannot_use_staff_status_workflow(self):
        with patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appointment("pending"))):
            with self.assertRaises(ForbiddenException):
                await service.update_appointment_status(
                    AsyncMock(), user("patient"), "appointment-1", schema.AppointmentStatusUpdate(status="confirmed")
                )

    async def test_patient_reschedule_returns_to_pending(self):
        appt = appointment("confirmed")
        db = AsyncMock()
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.patient_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="patient-1"))),
            patch.object(service, "_validate_slot_against_schedule", AsyncMock(return_value=(appt.scheduled_at + timedelta(days=1), 30))),
            patch.object(service.appointment_repository, "check_active_conflict", AsyncMock(return_value=False)),
            patch.object(service.appointment_repository, "reschedule", AsyncMock(return_value=appt)) as reschedule,
            patch.object(service.notification_service, "send_reschedule_notification"),
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=appt),
        ):
            await service.reschedule_appointment(
                db, user("patient"), appt.id, schema.AppointmentReschedule(date="2099-01-02", time="10:00")
            )
        self.assertEqual(reschedule.await_args.kwargs["new_status"], "pending")

    async def test_staff_reschedule_preserves_status(self):
        appt = appointment("confirmed")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service, "_validate_slot_against_schedule", AsyncMock(return_value=(appt.scheduled_at + timedelta(days=1), 30))),
            patch.object(service.appointment_repository, "check_active_conflict", AsyncMock(return_value=False)),
            patch.object(service.appointment_repository, "reschedule", AsyncMock(return_value=appt)) as reschedule,
            patch.object(service.notification_service, "send_reschedule_notification"),
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=appt),
        ):
            await service.reschedule_appointment(
                AsyncMock(), user("staff"), appt.id, schema.AppointmentReschedule(date="2099-01-02", time="10:00")
            )
        self.assertEqual(reschedule.await_args.kwargs["new_status"], "confirmed")

    async def test_doctor_cannot_reschedule(self):
        with patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appointment("confirmed"))):
            with self.assertRaises(ForbiddenException):
                await service.reschedule_appointment(
                    AsyncMock(), user("doctor"), "appointment-1",
                    schema.AppointmentReschedule(date="2099-01-02", time="10:00"),
                )

    async def test_doctor_can_only_cancel_assigned_appointment(self):
        appt = appointment("confirmed", "doctor-2")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.doctor_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="doctor-1"))),
        ):
            with self.assertRaises(ForbiddenException):
                await service.cancel_appointment(
                    AsyncMock(), user("doctor"), appt.id, schema.AppointmentCancel()
                )

    async def test_patient_cannot_cancel_within_24_hours(self):
        appt = appointment("confirmed")
        appt.scheduled_at = datetime.now(timezone.utc) + timedelta(hours=12)
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.patient_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="patient-1"))),
        ):
            with self.assertRaises(BadRequestException):
                await service.cancel_appointment(
                    AsyncMock(), user("patient"), appt.id, schema.AppointmentCancel()
                )

    async def test_staff_can_cancel_active_appointment(self):
        appt = appointment("pending")
        cancelled = appointment("cancelled")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.appointment_repository, "update_status", AsyncMock(return_value=cancelled)) as update,
            patch.object(service.notification_service, "send_cancellation_notification"),
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=cancelled),
        ):
            await service.cancel_appointment(
                AsyncMock(), user("staff"), appt.id,
                schema.AppointmentCancel(cancellation_reason="Clinic unavailable"),
            )
        update.assert_awaited_once_with(
            ANY, appt.id, status="cancelled", cancellation_reason="Clinic unavailable"
        )

    async def test_patient_can_cancel_own_appointment_more_than_24_hours_ahead(self):
        appt = appointment("confirmed")
        cancelled = appointment("cancelled")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.patient_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="patient-1"))),
            patch.object(service.appointment_repository, "update_status", AsyncMock(return_value=cancelled)) as update,
            patch.object(service.notification_service, "send_cancellation_notification"),
            patch.object(service.appointment_schema.AppointmentRead, "model_validate", return_value=cancelled),
        ):
            await service.cancel_appointment(
                AsyncMock(), user("patient"), appt.id, schema.AppointmentCancel()
            )
        self.assertEqual(update.await_args.kwargs["status"], "cancelled")

    async def test_patient_cannot_view_another_patients_appointment(self):
        appt = appointment("pending")
        appt.patient_profile_id = "patient-2"
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.patient_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="patient-1"))),
        ):
            with self.assertRaises(ForbiddenException):
                await service.get_appointment_details(AsyncMock(), user("patient"), appt.id)

    async def test_doctor_cannot_view_another_doctors_appointment(self):
        appt = appointment("confirmed", "doctor-2")
        with (
            patch.object(service.appointment_repository, "get_by_id", AsyncMock(return_value=appt)),
            patch.object(service.doctor_repository, "get_by_user_id", AsyncMock(return_value=SimpleNamespace(id="doctor-1"))),
        ):
            with self.assertRaises(ForbiddenException):
                await service.get_appointment_details(AsyncMock(), user("doctor"), appt.id)


if __name__ == "__main__":
    unittest.main()
