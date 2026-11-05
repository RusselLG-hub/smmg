import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.db.session import get_db
from app.features.v1.appointments import router as appointment_router
from app.features.v1.auth.dependencies import get_current_user


def appointment_response(status: str = "pending") -> dict:
    now = datetime.now(timezone.utc)
    user_fields = {
        "profile_image_url": None,
        "is_active": True,
        "is_email_verified": True,
        "created_at": now,
        "updated_at": now,
    }
    return {
        "id": "appointment-1",
        "appointment_reference": "APT-TEST",
        "patient_profile_id": "patient-1",
        "doctor_profile_id": "doctor-1",
        "service_id": None,
        "scheduled_at": now + timedelta(days=3),
        "slot_duration_minutes": 30,
        "status": status,
        "reason": None,
        "cancellation_reason": None,
        "reminder_sent_at": None,
        "created_at": now,
        "updated_at": now,
        "patient": {
            "id": "patient-1", "user_id": "patient-user", "date_of_birth": None,
            "gender": None, "phone": None, "address": None, "profile_image_url": None,
            "created_at": now, "updated_at": now,
            "user": {"id": "patient-user", "email": "patient@example.com", "name": "Patient", "role": "patient", **user_fields},
        },
        "doctor": {
            "id": "doctor-1", "user_id": "doctor-user", "specialty_id": None,
            "title": None, "phone": None, "bio": None, "profile_image_url": None,
            "is_active": True, "created_at": now, "updated_at": now, "specialty": None,
            "user": {"id": "doctor-user", "email": "doctor@example.com", "name": "Doctor", "role": "doctor", **user_fields},
        },
        "service": None,
    }


class AppointmentApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = FastAPI()
        register_exception_handlers(self.app)
        self.app.include_router(appointment_router.router)

        async def override_db():
            yield None

        self.role = "patient"

        async def override_user():
            return SimpleNamespace(
                id=f"{self.role}-user", role=self.role, email=f"{self.role}@example.com",
                name=self.role.title(), is_active=True, is_email_verified=True,
            )

        self.app.dependency_overrides[get_db] = override_db
        self.app.dependency_overrides[get_current_user] = override_user
        self.transport = httpx.ASGITransport(app=self.app)
        self.client = httpx.AsyncClient(transport=self.transport, base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_all_appointment_routes_and_methods_are_registered(self):
        expected = {
            ("/v1/appointments", "POST"),
            ("/v1/appointments/me", "GET"),
            ("/v1/appointments/doctor/me", "GET"),
            ("/v1/appointments", "GET"),
            ("/v1/appointments/{appointment_id}", "GET"),
            ("/v1/appointments/{appointment_id}/cancel", "PATCH"),
            ("/v1/appointments/{appointment_id}/reschedule", "PATCH"),
            ("/v1/appointments/{appointment_id}/status", "PATCH"),
        }
        actual = {
            (route.path, method)
            for route in self.app.routes
            for method in getattr(route, "methods", set())
        }
        self.assertTrue(expected.issubset(actual))

    async def test_patient_can_create_and_list_own_appointments(self):
        response_data = appointment_response()
        with (
            patch.object(appointment_router.appointment_service, "create_appointment", AsyncMock(return_value=response_data)),
            patch.object(appointment_router.appointment_service, "list_my_appointments", AsyncMock(return_value=[response_data])),
        ):
            created = await self.client.post(
                "/v1/appointments",
                json={"doctor_profile_id": "doctor-1", "date": "2099-01-01", "time": "09:00"},
            )
            listed = await self.client.get("/v1/appointments/me?type=upcoming")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["status"], "pending")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

    async def test_non_patient_cannot_create_or_list_patient_appointments(self):
        self.role = "staff"
        created = await self.client.post(
            "/v1/appointments",
            json={"doctor_profile_id": "doctor-1", "date": "2099-01-01", "time": "09:00"},
        )
        listed = await self.client.get("/v1/appointments/me")
        self.assertEqual(created.status_code, 403)
        self.assertEqual(listed.status_code, 403)

    async def test_doctor_can_list_assigned_appointments(self):
        self.role = "doctor"
        with patch.object(
            appointment_router.appointment_service,
            "list_doctor_appointments",
            AsyncMock(return_value=[appointment_response("confirmed")]),
        ):
            response = await self.client.get("/v1/appointments/doctor/me?status=confirmed")
        self.assertEqual(response.status_code, 200)

    async def test_patient_cannot_list_doctor_or_admin_appointments(self):
        doctor_list = await self.client.get("/v1/appointments/doctor/me")
        admin_list = await self.client.get("/v1/appointments")
        self.assertEqual(doctor_list.status_code, 403)
        self.assertEqual(admin_list.status_code, 403)

    async def test_staff_and_admin_can_list_all_appointments(self):
        for role in ("staff", "admin"):
            with self.subTest(role=role):
                self.role = role
                with patch.object(
                    appointment_router.appointment_service,
                    "list_admin_appointments",
                    AsyncMock(return_value=[appointment_response()]),
                ):
                    response = await self.client.get("/v1/appointments?status=pending")
                self.assertEqual(response.status_code, 200)

    async def test_status_endpoint_allows_operational_roles_and_rejects_patient(self):
        for role in ("doctor", "staff", "admin"):
            with self.subTest(role=role):
                self.role = role
                with patch.object(
                    appointment_router.appointment_service,
                    "update_appointment_status",
                    AsyncMock(return_value=appointment_response("cancelled")),
                ):
                    response = await self.client.patch(
                        "/v1/appointments/appointment-1/status", json={"status": "cancelled"}
                    )
                self.assertEqual(response.status_code, 200)
        self.role = "patient"
        response = await self.client.patch(
            "/v1/appointments/appointment-1/status", json={"status": "confirmed"}
        )
        self.assertEqual(response.status_code, 403)

    async def test_detail_cancel_and_reschedule_endpoints_are_wired(self):
        response_data = appointment_response()
        with (
            patch.object(appointment_router.appointment_service, "get_appointment_details", AsyncMock(return_value=response_data)),
            patch.object(appointment_router.appointment_service, "cancel_appointment", AsyncMock(return_value={**response_data, "status": "cancelled"})),
            patch.object(appointment_router.appointment_service, "reschedule_appointment", AsyncMock(return_value=response_data)),
        ):
            detail = await self.client.get("/v1/appointments/appointment-1")
            cancel = await self.client.patch(
                "/v1/appointments/appointment-1/cancel", json={"cancellation_reason": "Changed plans"}
            )
            reschedule = await self.client.patch(
                "/v1/appointments/appointment-1/reschedule",
                json={"date": "2099-01-02", "time": "10:00"},
            )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(cancel.status_code, 200)
        self.assertEqual(reschedule.status_code, 200)

    async def test_invalid_endpoint_payloads_return_422(self):
        bad_booking = await self.client.post(
            "/v1/appointments",
            json={"doctor_profile_id": "doctor-1", "date": "01-01-2099", "time": "25:00"},
        )
        self.role = "staff"
        bad_status = await self.client.patch(
            "/v1/appointments/appointment-1/status", json={"status": "approved"}
        )
        self.assertEqual(bad_booking.status_code, 422)
        self.assertEqual(bad_status.status_code, 422)

    async def test_all_appointment_endpoints_require_authentication(self):
        del self.app.dependency_overrides[get_current_user]
        requests = (
            ("POST", "/v1/appointments", {"doctor_profile_id": "doctor-1", "date": "2099-01-01", "time": "09:00"}),
            ("GET", "/v1/appointments/me", None),
            ("GET", "/v1/appointments/doctor/me", None),
            ("GET", "/v1/appointments", None),
            ("GET", "/v1/appointments/appointment-1", None),
            ("PATCH", "/v1/appointments/appointment-1/cancel", {}),
            ("PATCH", "/v1/appointments/appointment-1/reschedule", {"date": "2099-01-02", "time": "10:00"}),
            ("PATCH", "/v1/appointments/appointment-1/status", {"status": "confirmed"}),
        )
        for method, url, payload in requests:
            with self.subTest(method=method, url=url):
                response = await self.client.request(method, url, json=payload)
                self.assertEqual(response.status_code, 401)


    async def test_appointment_create_rejects_non_descriptive_reason(self):
        # BUG-003: "0..." or strings without meaningful descriptive words must fail schema validation
        response = await self.client.post(
            "/v1/appointments",
            json={
                "doctor_profile_id": "doctor-1",
                "date": "2099-01-01",
                "time": "09:00",
                "reason": "0...",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_patient_profile_update_schema_validations(self):
        from app.features.v1.patients.schema import PatientProfileUpdate

        # BUG-001: Invalid birthdate 01/01/0001
        with self.assertRaises(Exception):
            PatientProfileUpdate(date_of_birth="0001-01-01")

        # BUG-001: Invalid address "00"
        with self.assertRaises(Exception):
            PatientProfileUpdate(address="00")

        # BUG-002: Invalid phone "."
        with self.assertRaises(Exception):
            PatientProfileUpdate(phone=".")

        # BUG-002: Invalid address "."
        with self.assertRaises(Exception):
            PatientProfileUpdate(address=".")

        # Valid profile update passes
        valid = PatientProfileUpdate(
            name="Juan Dela Cruz",
            date_of_birth="1995-10-24",
            phone="09123456789",
            address="123 Health Ave, Sorsogon City",
        )
        self.assertEqual(valid.phone, "+639123456789")


if __name__ == "__main__":
    unittest.main()
