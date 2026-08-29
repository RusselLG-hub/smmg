import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.core.exceptions import NotFoundException
from app.features.v1.schedules import service


class PanelFeatureQaTests(unittest.IsolatedAsyncioTestCase):
    async def test_available_override_uses_fixed_duration_without_override_field(self):
        now = datetime.now(timezone.utc)
        override = SimpleNamespace(
            id="override-1", doctor_profile_id="doctor-1", is_available=True,
            start_time="09:00", end_time="10:00", created_at=now, updated_at=now,
        )
        with (
            patch.object(service.doctor_repository, "get_by_id", AsyncMock(return_value=SimpleNamespace(is_active=True))),
            patch.object(service.schedule_repository, "get_override_by_date", AsyncMock(return_value=override)),
            patch.object(service.appointment_repository, "get_active_appointments_for_doctor_date", AsyncMock(return_value=[])),
        ):
            result = await service.get_doctor_availability(
                AsyncMock(), "doctor-1", "2099-01-01"
            )
        self.assertEqual([slot.start_time for slot in result.slots], ["09:00", "09:30"])
        self.assertTrue(all(slot.end_time in {"09:30", "10:00"} for slot in result.slots))

    async def test_monthly_availability_rejects_unknown_doctor_even_for_past_month(self):
        with patch.object(
            service.doctor_repository, "get_by_id", AsyncMock(return_value=None)
        ):
            with self.assertRaises(NotFoundException):
                await service.get_doctor_monthly_availability(
                    AsyncMock(), "missing-doctor", 2000, 1
                )


if __name__ == "__main__":
    unittest.main()
