"""HTML and Plain Text email templates for appointment notifications."""


def build_booking_confirmation_email(
    patient_name: str,
    reference: str,
    doctor_name: str,
    specialty_name: str | None,
    service_name: str | None,
    date_str: str,
    time_str: str,
) -> tuple[str, str]:
    subject = f"Appointment Request Received - Ref #{reference}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; color: #111827;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
        <div style="background-color: #0284c7; padding: 16px; border-radius: 8px; color: #ffffff; text-align: center;">
          <h2 style="margin: 0; font-size: 20px;">Appointment Request Received</h2>
        </div>
        <p style="margin-top: 20px;">Dear <strong>{patient_name}</strong>,</p>
        <p>Your appointment request has been received and is awaiting clinic confirmation. Please keep your reference number for future inquiries.</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f8fafc; border-radius: 8px; overflow: hidden;">
          <tr>
            <td style="padding: 12px; font-weight: bold; border-bottom: 1px solid #e2e8f0; width: 40%;">Reference Number:</td>
            <td style="padding: 12px; font-family: monospace; font-weight: bold; color: #0284c7; border-bottom: 1px solid #e2e8f0;">{reference}</td>
          </tr>
          <tr>
            <td style="padding: 12px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Doctor:</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">Dr. {doctor_name} {f'({specialty_name})' if specialty_name else ''}</td>
          </tr>
          {f'<tr><td style="padding: 12px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Service:</td><td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{service_name}</td></tr>' if service_name else ''}
          <tr>
            <td style="padding: 12px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Date & Time:</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;"><strong>{date_str}</strong> at <strong>{time_str}</strong></td>
          </tr>
        </table>

        <p style="font-size: 13px; color: #6b7280;">If you need to reschedule or cancel your appointment, please log into your SMMG patient portal at least 24 hours prior to your scheduled time.</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
        <p style="font-size: 12px; color: #9ca3af; text-align: center;">&copy; SMMG Healthcare Appointment Management System.</p>
      </div>
    </body>
    </html>
    """
    text = (
        f"Dear {patient_name},\n\n"
        f"Your appointment request has been received and is awaiting clinic confirmation.\n"
        f"Reference Number: {reference}\n"
        f"Doctor: Dr. {doctor_name}\n"
        f"Date & Time: {date_str} at {time_str}\n\n"
        f"Thank you for choosing SMMG Healthcare."
    )
    return subject, html, text


def build_status_confirmed_email(
    patient_name: str,
    reference: str,
    doctor_name: str,
    date_str: str,
    time_str: str,
) -> tuple[str, str, str]:
    subject = f"Appointment Confirmed - Ref #{reference}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; color: #111827;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
        <div style="background-color: #16a34a; padding: 16px; border-radius: 8px; color: #ffffff; text-align: center;">
          <h2 style="margin: 0; font-size: 20px;">Appointment Confirmed by Clinic</h2>
        </div>
        <p style="margin-top: 20px;">Dear <strong>{patient_name}</strong>,</p>
        <p>Clinic staff have confirmed your consultation appointment.</p>
        <p><strong>Reference:</strong> {reference}<br/><strong>Doctor:</strong> Dr. {doctor_name}<br/><strong>Schedule:</strong> {date_str} at {time_str}</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
        <p style="font-size: 12px; color: #9ca3af; text-align: center;">&copy; SMMG Healthcare Appointment Management System.</p>
      </div>
    </body>
    </html>
    """
    text = f"Dear {patient_name},\n\nYour appointment Ref #{reference} with Dr. {doctor_name} on {date_str} at {time_str} is now confirmed."
    return subject, html, text


def build_reschedule_email(
    patient_name: str,
    reference: str,
    doctor_name: str,
    old_date_str: str,
    new_date_str: str,
    new_time_str: str,
    pending_confirmation: bool = False,
) -> tuple[str, str, str]:
    subject = f"Appointment Rescheduled - Ref #{reference}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; color: #111827;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
        <div style="background-color: #2563eb; padding: 16px; border-radius: 8px; color: #ffffff; text-align: center;">
          <h2 style="margin: 0; font-size: 20px;">Appointment Rescheduled</h2>
        </div>
        <p style="margin-top: 20px;">Dear <strong>{patient_name}</strong>,</p>
        <p>Your appointment <strong>Ref #{reference}</strong> with Dr. {doctor_name} has been rescheduled.{" The new schedule is awaiting clinic confirmation." if pending_confirmation else ""}</p>

        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 16px; border-radius: 8px; margin: 20px 0;">
          <p style="margin: 0 0 8px 0; color: #1e40af;"><strong>New Schedule:</strong></p>
          <p style="margin: 0; font-size: 16px; font-weight: bold; color: #1e3a8a;">{new_date_str} at {new_time_str}</p>
        </div>

        <p style="font-size: 13px; color: #6b7280;">(Previous schedule: {old_date_str})</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
        <p style="font-size: 12px; color: #9ca3af; text-align: center;">&copy; SMMG Healthcare Appointment Management System.</p>
      </div>
    </body>
    </html>
    """
    confirmation_note = " The new schedule is awaiting clinic confirmation." if pending_confirmation else ""
    text = f"Dear {patient_name},\n\nYour appointment Ref #{reference} with Dr. {doctor_name} has been rescheduled to {new_date_str} at {new_time_str}.{confirmation_note}"
    return subject, html, text


def build_cancellation_email(
    patient_name: str,
    reference: str,
    doctor_name: str,
    date_str: str,
    time_str: str,
    cancellation_reason: str | None = None,
) -> tuple[str, str, str]:
    subject = f"Appointment Cancelled - Ref #{reference}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; color: #111827;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
        <div style="background-color: #dc2626; padding: 16px; border-radius: 8px; color: #ffffff; text-align: center;">
          <h2 style="margin: 0; font-size: 20px;">Appointment Cancelled</h2>
        </div>
        <p style="margin-top: 20px;">Dear <strong>{patient_name}</strong>,</p>
        <p>Your appointment <strong>Ref #{reference}</strong> scheduled for {date_str} at {time_str} with Dr. {doctor_name} has been cancelled.</p>

        {f'<div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 12px; border-radius: 8px; margin: 16px 0; color: #991b1b; font-size: 13px;"><strong>Cancellation Reason:</strong> {cancellation_reason}</div>' if cancellation_reason else ''}

        <p style="font-size: 13px; color: #6b7280;">You may log into the SMMG patient portal at any time to book a new appointment.</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
        <p style="font-size: 12px; color: #9ca3af; text-align: center;">&copy; SMMG Healthcare Appointment Management System.</p>
      </div>
    </body>
    </html>
    """
    text = f"Dear {patient_name},\n\nYour appointment Ref #{reference} for {date_str} at {time_str} has been cancelled."
    return subject, html, text


def build_reminder_email(
    patient_name: str,
    reference: str,
    doctor_name: str,
    specialty_name: str | None,
    service_name: str | None,
    date_str: str,
    time_str: str,
) -> tuple[str, str, str]:
    subject = f"Reminder: Tomorrow's Consultation - Ref #{reference}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; color: #111827;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
        <div style="background-color: #0284c7; padding: 16px; border-radius: 8px; color: #ffffff; text-align: center;">
          <h2 style="margin: 0; font-size: 20px;">Appointment Reminder</h2>
        </div>
        <p style="margin-top: 20px;">Dear <strong>{patient_name}</strong>,</p>
        <p>This is a friendly reminder of your upcoming healthcare consultation tomorrow.</p>

        <div style="background-color: #f0f9ff; border: 1px solid #bae6fd; padding: 16px; border-radius: 8px; margin: 20px 0;">
          <p style="margin: 0 0 4px 0;"><strong>Doctor:</strong> Dr. {doctor_name} {f'({specialty_name})' if specialty_name else ''}</p>
          {f'<p style="margin: 0 0 4px 0;"><strong>Service:</strong> {service_name}</p>' if service_name else ''}
          <p style="margin: 0 0 4px 0;"><strong>Reference:</strong> {reference}</p>
          <p style="margin: 8px 0 0 0; font-size: 16px; font-weight: bold; color: #0369a1;">{date_str} at {time_str}</p>
        </div>

        <p style="font-size: 13px; color: #6b7280;">Please arrive 10 minutes prior to your scheduled time.</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
        <p style="font-size: 12px; color: #9ca3af; text-align: center;">&copy; SMMG Healthcare Appointment Management System.</p>
      </div>
    </body>
    </html>
    """
    text = f"Dear {patient_name},\n\nReminder: You have an upcoming consultation with Dr. {doctor_name} tomorrow, {date_str} at {time_str}. Ref #{reference}."
    return subject, html, text
