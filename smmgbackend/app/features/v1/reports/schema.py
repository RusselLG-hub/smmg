from pydantic import BaseModel, ConfigDict


class StatusBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pending_count: int
    confirmed_count: int
    completed_count: int
    cancelled_count: int
    total_count: int
    completion_rate_pct: float
    cancellation_rate_pct: float


class VolumePoint(BaseModel):
    date: str
    count: int


class DoctorReportRow(BaseModel):
    doctor_profile_id: str
    doctor_name: str
    specialty_name: str | None = None
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    pending_appointments: int
    confirmed_appointments: int
    completion_rate_pct: float


class ServiceUsageRow(BaseModel):
    service_id: str | None = None
    service_name: str
    specialty_name: str | None = None
    appointment_count: int
    completed_count: int
    cancelled_count: int
    percentage_of_total: float


class SpecialtyReportRow(BaseModel):
    specialty_id: str
    specialty_name: str
    doctor_count: int
    appointment_count: int
    service_count: int


class PeakTimeRow(BaseModel):
    label: str
    count: int


class PeakBookingTimes(BaseModel):
    busiest_days: list[PeakTimeRow]
    busiest_hours: list[PeakTimeRow]


class DemographicGroup(BaseModel):
    label: str
    count: int


class PatientDemographicSummary(BaseModel):
    gender_distribution: list[DemographicGroup]
    age_distribution: list[DemographicGroup]
    total_patients: int


class ReportsOverviewResponse(BaseModel):
    start_date: str
    end_date: str
    status_breakdown: StatusBreakdown
    volume_trend: list[VolumePoint]
    doctor_stats: list[DoctorReportRow]
    service_stats: list[ServiceUsageRow]
    specialty_stats: list[SpecialtyReportRow]
    peak_times: PeakBookingTimes
    demographics: PatientDemographicSummary


class DoctorPersonalReportResponse(BaseModel):
    doctor_name: str
    specialty_name: str | None = None
    start_date: str
    end_date: str
    status_breakdown: StatusBreakdown
    volume_trend: list[VolumePoint]
    service_stats: list[ServiceUsageRow]
    peak_times: PeakBookingTimes
