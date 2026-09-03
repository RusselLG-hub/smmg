import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.core.exceptions import ConflictException, ServiceUnavailableException
from app.features.v1.auth import schema as auth_schema
from app.features.v1.auth import service as auth_service
from app.providers import resend_provider


class AuthServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_register_cleans_up_created_user_when_verification_code_fails(self):
        db = AsyncMock()
        mock_user = SimpleNamespace(
            id="user-new",
            email="newuser@example.com",
            name="New User",
            is_email_verified=False,
            role="patient",
        )

        register_data = auth_schema.RegisterRequest(
            email="newuser@example.com",
            name="New User",
            password="Password123!",
        )

        with (
            patch.object(auth_service.user_repository, "get_by_email", AsyncMock(return_value=None)),
            patch.object(auth_service.user_repository, "create_user", AsyncMock(return_value=mock_user)),
            patch.object(
                auth_service,
                "send_verification_code",
                AsyncMock(side_effect=ServiceUnavailableException(detail="Email failed")),
            ),
        ):
            with self.assertRaises(ServiceUnavailableException):
                await auth_service.register(db, register_data)

        # Ensure the newly created user was deleted from the database
        db.delete.assert_awaited_once_with(mock_user)
        db.commit.assert_awaited()

    async def test_register_unverified_existing_user_updates_and_resends_code(self):
        db = AsyncMock()
        existing_user = SimpleNamespace(
            id="user-pending",
            email="pending@example.com",
            name="Old Name",
            hashed_password="old-hash",
            is_email_verified=False,
            role="patient",
        )

        register_data = auth_schema.RegisterRequest(
            email="pending@example.com",
            name="Updated Name",
            password="NewPassword123!",
        )

        with (
            patch.object(auth_service.user_repository, "get_by_email", AsyncMock(return_value=existing_user)),
            patch.object(auth_service, "send_verification_code", AsyncMock()) as send_code_mock,
        ):
            result = await auth_service.register(db, register_data)

        self.assertIs(result, existing_user)
        self.assertEqual(existing_user.name, "Updated Name")
        db.commit.assert_awaited()
        db.refresh.assert_awaited_with(existing_user)
        send_code_mock.assert_awaited_once_with(db, user=existing_user)

    async def test_register_already_verified_user_raises_conflict(self):
        db = AsyncMock()
        existing_user = SimpleNamespace(
            id="user-active",
            email="active@example.com",
            name="Active User",
            is_email_verified=True,
            role="patient",
        )

        register_data = auth_schema.RegisterRequest(
            email="active@example.com",
            name="Active User",
            password="Password123!",
        )

        with patch.object(auth_service.user_repository, "get_by_email", AsyncMock(return_value=existing_user)):
            with self.assertRaises(ConflictException) as ctx:
                await auth_service.register(db, register_data)

        self.assertIn("already registered", ctx.exception.detail)


class PasswordStrengthValidationTests(unittest.TestCase):
    def test_password_strength_rules(self):
        # Too short (<8 chars)
        with self.assertRaises(ValueError):
            auth_schema.validate_password_strength("Pass1!")

        # Missing uppercase
        with self.assertRaises(ValueError):
            auth_schema.validate_password_strength("password123!")

        # Missing lowercase
        with self.assertRaises(ValueError):
            auth_schema.validate_password_strength("PASSWORD123!")

        # Missing number
        with self.assertRaises(ValueError):
            auth_schema.validate_password_strength("Password!!!!")

        # Missing special character
        with self.assertRaises(ValueError):
            auth_schema.validate_password_strength("Password1234")

        # Valid password meets all criteria
        self.assertEqual(auth_schema.validate_password_strength("Password123!"), "Password123!")

    def test_register_schema_enforces_password_strength(self):
        # Fails schema validation with weak password
        with self.assertRaises(Exception):
            auth_schema.RegisterRequest(
                name="Test User",
                email="test@example.com",
                password="weak",
            )

        # Passes schema validation with strong password
        req = auth_schema.RegisterRequest(
            name="Test User",
            email="test@example.com",
            password="StrongPassword123!",
        )
        self.assertEqual(req.password, "StrongPassword123!")


class ResendProviderTests(unittest.TestCase):
    def test_placeholder_key_detection(self):
        self.assertTrue(resend_provider._is_placeholder_api_key(None))
        self.assertTrue(resend_provider._is_placeholder_api_key(""))
        self.assertTrue(resend_provider._is_placeholder_api_key("your_resend_api_key"))
        self.assertTrue(resend_provider._is_placeholder_api_key("your_api_key_here"))
        self.assertTrue(resend_provider._is_placeholder_api_key("dummy"))
        self.assertTrue(resend_provider._is_placeholder_api_key("mock"))
        self.assertFalse(resend_provider._is_placeholder_api_key("re_1234567890abcdef"))

    def test_send_email_simulates_in_dev_with_placeholder_key(self):
        with patch.object(resend_provider.settings, "RESEND_API_KEY", "your_resend_api_key"):
            result = resend_provider.send_email(
                to="test@example.com",
                subject="Test Subject",
                html="<p>Test</p>",
            )
        self.assertEqual(result.get("status"), "simulated")

    def test_send_email_simulates_in_dev_when_resend_throws(self):
        with (
            patch.object(resend_provider.settings, "RESEND_API_KEY", "re_test_key"),
            patch.object(resend_provider.settings, "EMAIL_FROM", "noreply@example.com"),
            patch.object(resend_provider.settings, "ENVIRONMENT", "development"),
            patch("resend.Emails.send", side_effect=Exception("API key invalid")),
        ):
            result = resend_provider.send_email(
                to="test@example.com",
                subject="Test Subject",
                html="<p>Test</p>",
            )
        self.assertEqual(result.get("status"), "simulated")

    def test_send_email_raises_in_production_when_resend_throws(self):
        with (
            patch.object(resend_provider.settings, "RESEND_API_KEY", "re_real_key_123"),
            patch.object(resend_provider.settings, "EMAIL_FROM", "noreply@example.com"),
            patch.object(resend_provider.settings, "ENVIRONMENT", "production"),
            patch("resend.Emails.send", side_effect=Exception("Connection refused")),
        ):
            with self.assertRaises(resend_provider.EmailProviderError):
                resend_provider.send_email(
                    to="test@example.com",
                    subject="Test Subject",
                    html="<p>Test</p>",
                )


if __name__ == "__main__":
    unittest.main()
