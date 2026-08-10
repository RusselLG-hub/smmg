from datetime import datetime, time, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.features.v1.doctors import repository as doctor_repository
from app.features.v1.reports import repository as reports_repository
from app.features.v1.reports import schema as reports_schema
from app.features.v1.users import model as user_model

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _parse_date_range(
    start_date: str | None, end_date: str | None
) -> tuple[datetime, datetime, str, str]:
    now_utc = datetime.now(timezone.utc)

    if not end_date:
        end_d = now_utc.date()
    else:
        try:
            end_d = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise BadRequestException(detail="Invalid end_date format. Expected YYYY-MM-DD.")

    if not start_date:
        start_d = end_d - timedelta(days=30)
    else:
        try:
            start_d = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise BadRequestException(detail="Invalid start_date format. Expected YYYY-MM-DD.")

    if start_d > end_d:
        raise BadRequestException(detail="start_date must be less than or equal to end_date.")

    start_dt = datetime.combine(start_d, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(end_d, time.max, tzinfo=timezone.utc)

    return start_dt, end_dt, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")


async def get_reports_overview(
    db: AsyncSession, start_date: str | None = None, end_date: str | None = None
) -> reports_schema.ReportsOverviewResponse:
    start_dt, end_dt, s_str, e_str = _parse_date_range(start_date, end_date)

    # 1. Status Breakdown
    st_counts = await reports_repository.get_status_counts(db, start_dt, end_dt)
    tot = sum(st_counts.values())
    comp_rate = round((st_counts["completed"] / tot * 100), 1) if tot > 0 else 0.0
    canc_rate = round((st_counts["cancelled"] / tot * 100), 1) if tot > 0 else 0.0

    status_breakdown = reports_schema.StatusBreakdown(
        pending_count=st_counts["pending"],
        confirmed_count=st_counts["confirmed"],
        completed_count=st_counts["completed"],
        cancelled_count=st_counts["cancelled"],
        total_count=tot,
        completion_rate_pct=comp_rate,
        cancellation_rate_pct=canc_rate,
    )

    # 2. Volume Trend
    vol_rows = await reports_repository.get_volume_trend(db, start_dt, end_dt)
    volume_trend = [
        reports_schema.VolumePoint(date=d.strftime("%Y-%m-%d"), count=cnt)
        for d, cnt in vol_rows
    ]

    # 3. Doctor Stats
    doc_rows = await reports_repository.get_doctor_stats(db, start_dt, end_dt)
    doctor_stats = []
    for r in doc_rows:
        d_tot = r["total_appointments"]
        d_comp_rate = round((r["completed_appointments"] / d_tot * 100), 1) if d_tot > 0 else 0.0
        doctor_stats.append(
            reports_schema.DoctorReportRow(
                doctor_profile_id=r["doctor_profile_id"],
                doctor_name=r["doctor_name"],
                specialty_name=r["specialty_name"],
                total_appointments=d_tot,
                completed_appointments=r["completed_appointments"],
                cancelled_appointments=r["cancelled_appointments"],
                pending_appointments=r["pending_appointments"],
                confirmed_appointments=r["confirmed_appointments"],
                completion_rate_pct=d_comp_rate,
            )
        )

    # 4. Service Stats
    srv_rows, grand_total_srv = await reports_repository.get_service_stats(db, start_dt, end_dt)
    service_stats = []
    for r in srv_rows:
        pct = round((r["appointment_count"] / grand_total_srv * 100), 1) if grand_total_srv > 0 else 0.0
        service_stats.append(
            reports_schema.ServiceUsageRow(
                service_id=r["service_id"],
                service_name=r["service_name"],
                specialty_name=r["specialty_name"],
                appointment_count=r["appointment_count"],
                completed_count=r["completed_count"],
                cancelled_count=r["cancelled_count"],
                percentage_of_total=pct,
            )
        )

    # 5. Specialty Stats
    spec_rows = await reports_repository.get_specialty_stats(db, start_dt, end_dt)
    specialty_stats = [
        reports_schema.SpecialtyReportRow(
            specialty_id=r["specialty_id"],
            specialty_name=r["specialty_name"],
            doctor_count=r["doctor_count"],
            appointment_count=r["appointment_count"],
            service_count=r["service_count"],
        )
        for r in spec_rows
    ]

    # 6. Peak Times
    p_days = await reports_repository.get_peak_days(db, start_dt, end_dt)
    p_hours = await reports_repository.get_peak_hours(db, start_dt, end_dt)

    busiest_days = [
        reports_schema.PeakTimeRow(label=DAY_NAMES[int(dow)], count=cnt)
        for dow, cnt in p_days
        if 0 <= int(dow) < 7
    ]
    busiest_hours = [
        reports_schema.PeakTimeRow(label=f"{int(hr):02d}:00", count=cnt)
        for hr, cnt in p_hours
    ]

    peak_times = reports_schema.PeakBookingTimes(
        busiest_days=busiest_days, busiest_hours=busiest_hours
    )

    # 7. Demographics
    demo_dict = await reports_repository.get_demographic_stats(db)
    demographics = reports_schema.PatientDemographicSummary(
        gender_distribution=[
            reports_schema.DemographicGroup(**g) for g in demo_dict["gender_distribution"]
        ],
        age_distribution=[
            reports_schema.DemographicGroup(**a) for a in demo_dict["age_distribution"]
        ],
        total_patients=demo_dict["total_patients"],
    )

    return reports_schema.ReportsOverviewResponse(
        start_date=s_str,
        end_date=e_str,
        status_breakdown=status_breakdown,
        volume_trend=volume_trend,
        doctor_stats=doctor_stats,
        service_stats=service_stats,
        specialty_stats=specialty_stats,
        peak_times=peak_times,
        demographics=demographics,
    )


async def get_doctor_personal_report(
    db: AsyncSession,
    current_user: user_model.User,
    start_date: str | None = None,
    end_date: str | None = None,
) -> reports_schema.DoctorPersonalReportResponse:
    doctor_prof = await doctor_repository.get_by_user_id(db, current_user.id)
    if not doctor_prof:
        raise NotFoundException(detail="Doctor profile not found.")

    start_dt, end_dt, s_str, e_str = _parse_date_range(start_date, end_date)

    st_counts = await reports_repository.get_status_counts(
        db, start_dt, end_dt, doctor_id=doctor_prof.id
    )
    tot = sum(st_counts.values())
    comp_rate = round((st_counts["completed"] / tot * 100), 1) if tot > 0 else 0.0
    canc_rate = round((st_counts["cancelled"] / tot * 100), 1) if tot > 0 else 0.0

    status_breakdown = reports_schema.StatusBreakdown(
        pending_count=st_counts["pending"],
        confirmed_count=st_counts["confirmed"],
        completed_count=st_counts["completed"],
        cancelled_count=st_counts["cancelled"],
        total_count=tot,
        completion_rate_pct=comp_rate,
        cancellation_rate_pct=canc_rate,
    )

    vol_rows = await reports_repository.get_volume_trend(
        db, start_dt, end_dt, doctor_id=doctor_prof.id
    )
    volume_trend = [
        reports_schema.VolumePoint(date=d.strftime("%Y-%m-%d"), count=cnt)
        for d, cnt in vol_rows
    ]

    srv_rows, grand_total_srv = await reports_repository.get_service_stats(
        db, start_dt, end_dt, doctor_id=doctor_prof.id
    )
    service_stats = [
        reports_schema.ServiceUsageRow(
            service_id=r["service_id"],
            service_name=r["service_name"],
            specialty_name=r["specialty_name"],
            appointment_count=r["appointment_count"],
            completed_count=r["completed_count"],
            cancelled_count=r["cancelled_count"],
            percentage_of_total=round((r["appointment_count"] / grand_total_srv * 100), 1)
            if grand_total_srv > 0
            else 0.0,
        )
        for r in srv_rows
    ]

    p_days = await reports_repository.get_peak_days(
        db, start_dt, end_dt, doctor_id=doctor_prof.id
    )
    p_hours = await reports_repository.get_peak_hours(
        db, start_dt, end_dt, doctor_id=doctor_prof.id
    )

    peak_times = reports_schema.PeakBookingTimes(
        busiest_days=[
            reports_schema.PeakTimeRow(label=DAY_NAMES[int(dow)], count=cnt)
            for dow, cnt in p_days
            if 0 <= int(dow) < 7
        ],
        busiest_hours=[
            reports_schema.PeakTimeRow(label=f"{int(hr):02d}:00", count=cnt)
            for hr, cnt in p_hours
        ],
    )

    specialty_name = doctor_prof.specialty.name if doctor_prof.specialty else None

    return reports_schema.DoctorPersonalReportResponse(
        doctor_name=current_user.name,
        specialty_name=specialty_name,
        start_date=s_str,
        end_date=e_str,
        status_breakdown=status_breakdown,
        volume_trend=volume_trend,
        service_stats=service_stats,
        peak_times=peak_times,
    )
