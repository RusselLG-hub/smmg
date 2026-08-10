import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.appointments import model as appt_model
from app.features.v1.notifications import templates
from app.providers import resend_provider
from app.features.v1.notifications import repository as notification_repository
from app.features.v1.notifications import schema as notification_schema
from app.features.v1.users import model as user_model

logger = logging.getLogger(__name__)


async def get_in_app_notifications(
    db: AsyncSession,
    current_user: user_model.User,
    limit: int = 12,
) -> list[notification_schema.InAppNotification]:
    """Build a small role-aware feed from existing appointment activity."""
    appointments = await notification_repository.list_for_user(
        db, user_id=current_user.id, role=current_user.role, limit=limit
    )
    href = (
        "/patient/appointments"
        if current_user.role == "patient"
        else "/doctor/appointments"
        if current_user.role == "doctor"
        else "/admin/appointments"
    )
    items: list[notification_schema.InAppNotification] = []

    for appointment in appointments:
        reference = appointment.appointment_reference
        patient_name = appointment.patient.user.name
        doctor_name = appointment.doctor.user.name
        status = appointment.status

        if current_user.role == "patient":
            titles = {
                "pending": "Appointment awaiting confirmation",
                "confirmed": "Appointment confirmed",
                "completed": "Appointment completed",
                "cancelled": "Appointment cancelled",
            }
            title = titles.get(status, "Appointment updated")
            message = f"{reference} with Dr. {doctor_name} is {status}."
        else:
            title = "Appointment activity"
            if status == "pending":
                title = "Appointment needs review"
            elif status == "cancelled":
                title = "Appointment cancelled"
            elif status == "completed":
                title = "Appointment completed"
            message = f"{patient_name}'s appointment {reference} with Dr. {doctor_name} is {status}."

        items.append(
            notification_schema.InAppNotification(
                id=f"{appointment.id}:{appointment.updated_at.isoformat()}:{status}",
                title=title,
                message=message,
                kind="status",
                created_at=appointment.updated_at,
                href=href,
            )
        )

    return items


def send_booking_notification(
    patient_email: str,
    patient_name: str,
    reference: str,
    doctor_name: str,
    specialty_name: str | None,
    service_name: str | None,
    date_str: str,
    time_str: str,
) -> None:
    try:
        subject, html, text = templates.build_booking_confirmation_email(
            patient_name=patient_name,
            reference=reference,
            doctor_name=doctor_name,
            specialty_name=specialty_name,
            service_name=service_name,
            date_str=date_str,
            time_str=time_str,
        )
        resend_provider.send_email(to=patient_email, subject=subject, html=html)
    except Exception as e:
        logger.error(f"Failed to send booking notification for Ref #{reference}: {e}")


def send_status_confirmed_notification(
    patient_email: str,
    patient_name: str,
    reference: str,
    doctor_name: str,
    date_str: str,
    time_str: str,
) -> None:
    try:
        subject, html, text = templates.build_status_confirmed_email(
            patient_name=patient_name,
            reference=reference,
            doctor_name=doctor_name,
            date_str=date_str,
            time_str=time_str,
        )
        resend_provider.send_email(to=patient_email, subject=subject, html=html)
    except Exception as e:
        logger.error(f"Failed to send status confirmation for Ref #{reference}: {e}")


def send_reschedule_notification(
    patient_email: str,
    patient_name: str,
    reference: str,
    doctor_name: str,
    old_date_str: str,
    new_date_str: str,
    new_time_str: str,
) -> None:
    try:
        subject, html, text = templates.build_reschedule_email(
            patient_name=patient_name,
            reference=reference,
            doctor_name=doctor_name,
            old_date_str=old_date_str,
            new_date_str=new_date_str,
            new_time_str=new_time_str,
        )
        resend_provider.send_email(to=patient_email, subject=subject, html=html)
    except Exception as e:
        logger.error(f"Failed to send reschedule notification for Ref #{reference}: {e}")


def send_cancellation_notification(
    patient_email: str,
    patient_name: str,
    reference: str,
    doctor_name: str,
    date_str: str,
    time_str: str,
    cancellation_reason: str | None = None,
) -> None:
    try:
        subject, html, text = templates.build_cancellation_email(
            patient_name=patient_name,
            reference=reference,
            doctor_name=doctor_name,
            date_str=date_str,
            time_str=time_str,
            cancellation_reason=cancellation_reason,
        )
        resend_provider.send_email(to=patient_email, subject=subject, html=html)
    except Exception as e:
        logger.error(f"Failed to send cancellation notification for Ref #{reference}: {e}")


def send_reminder_notification(
    patient_email: str,
    patient_name: str,
    reference: str,
    doctor_name: str,
    specialty_name: str | None,
    service_name: str | None,
    date_str: str,
    time_str: str,
) -> bool:
    try:
        subject, html, text = templates.build_reminder_email(
            patient_name=patient_name,
            reference=reference,
            doctor_name=doctor_name,
            specialty_name=specialty_name,
            service_name=service_name,
            date_str=date_str,
            time_str=time_str,
        )
        res = resend_provider.send_email(to=patient_email, subject=subject, html=html)
        return res is not None
    except Exception as e:
        logger.error(f"Failed to send reminder notification for Ref #{reference}: {e}")
        return False


async def process_appointment_reminders(db: AsyncSession) -> int:
    now_utc = datetime.now(timezone.utc)
    window_start = now_utc + timedelta(hours=20)
    window_end = now_utc + timedelta(hours=28)

    stmt = select(appt_model.Appointment).where(
        appt_model.Appointment.status.in_(["pending", "confirmed"]),
        appt_model.Appointment.reminder_sent_at.is_(None),
        appt_model.Appointment.scheduled_at >= window_start,
        appt_model.Appointment.scheduled_at <= window_end,
    )
    result = await db.execute(stmt)
    eligible_appts = list(result.scalars().all())

    sent_count = 0

    for appt in eligible_appts:
        try:
            patient_email = appt.patient.user.email
            patient_name = appt.patient.user.name
            doctor_name = appt.doctor.user.name
            specialty_name = appt.doctor.specialty.name if appt.doctor.specialty else None
            service_name = appt.service.name if appt.service else None

            date_str = appt.scheduled_at.strftime("%Y-%m-%d")
            time_str = appt.scheduled_at.strftime("%H:%M")

            success = send_reminder_notification(
                patient_email=patient_email,
                patient_name=patient_name,
                reference=appt.appointment_reference,
                doctor_name=doctor_name,
                specialty_name=specialty_name,
                service_name=service_name,
                date_str=date_str,
                time_str=time_str,
            )

            if success:
                appt.reminder_sent_at = datetime.now(timezone.utc)
                await db.commit()
                sent_count += 1
                logger.info(f"Reminder sent successfully for Ref #{appt.appointment_reference}")
        except Exception as e:
            logger.error(f"Error processing reminder for appointment {appt.id}: {e}")

    return sent_count
