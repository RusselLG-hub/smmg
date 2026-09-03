import asyncio

from app.core.security import hash_password
from app.db.session import async_session
from app.features.v1.doctors import repository as doctor_repository
from app.features.v1.patients import repository as patient_repository
from app.features.v1.patients.schema import PatientProfileUpdate
from app.features.v1.specialties import repository as specialty_repository
from app.features.v1.users import model as user_model
from app.features.v1.users import repository as user_repository


DOCTORS = [
    {
        "name": "Maria Santos",
        "email": "maria.santos.doctor@example.com",
        "legacy_email": "maria.santos.doctor@smmg.local",
        "password": "ChangeMe123!",
        "specialty": "General Medicine",
        "title": "MD",
        "phone": "+639171000101",
        "bio": "Primary-care physician focused on preventive care and accessible community health services.",
    },
    {
        "name": "Gabriel Reyes",
        "email": "gabriel.reyes.doctor@example.com",
        "legacy_email": "gabriel.reyes.doctor@smmg.local",
        "password": "ChangeMe123!",
        "specialty": "Pediatrics",
        "title": "MD, DPPS",
        "phone": "+639171000102",
        "bio": "Pediatrician providing family-centered care for infants, children, and adolescents.",
    },
    {
        "name": "Isabella Cruz",
        "email": "isabella.cruz.doctor@example.com",
        "legacy_email": "isabella.cruz.doctor@smmg.local",
        "password": "ChangeMe123!",
        "specialty": "Cardiology",
        "title": "MD, FPCP",
        "phone": "+639171000103",
        "bio": "Cardiology physician interested in early cardiovascular risk detection and long-term heart health.",
    },
    {
        "name": "Miguel Garcia",
        "email": "miguel.garcia.doctor@example.com",
        "legacy_email": "miguel.garcia.doctor@smmg.local",
        "password": "ChangeMe123!",
        "specialty": "Dermatology",
        "title": "MD, FPDS",
        "phone": "+639171000104",
        "bio": "Dermatologist treating common skin, hair, and nail conditions across all age groups.",
    },
    {
        "name": "Sofia Mendoza",
        "email": "sofia.mendoza.doctor@example.com",
        "legacy_email": "sofia.mendoza.doctor@smmg.local",
        "password": "ChangeMe123!",
        "specialty": "Obstetrics and Gynecology",
        "title": "MD, FPOGS",
        "phone": "+639171000105",
        "bio": "OB-GYN physician supporting preventive, reproductive, and maternal healthcare needs.",
    },
]

STAFF = [
    {
        "name": "Angela Flores",
        "email": "angela.flores.staff@example.com",
        "legacy_email": "angela.flores.staff@smmg.local",
        "password": "ChangeMe123!",
    },
    {
        "name": "Paolo Navarro",
        "email": "paolo.navarro.staff@example.com",
        "legacy_email": "paolo.navarro.staff@smmg.local",
        "password": "ChangeMe123!",
    },
]

PATIENTS = [
    {
        "name": "Juan Dela Cruz",
        "email": "juan.delacruz.patient@example.com",
        "legacy_email": "juan.delacruz.patient@smmg.local",
        "password": "ChangeMe123!",
        "phone": "+639171000201",
        "gender": "Male",
        "date_of_birth": "1992-05-14",
        "address": "123 Mabini St, Manila",
    },
    {
        "name": "Maria Clara",
        "email": "maria.clara.patient@example.com",
        "legacy_email": "maria.clara.patient@smmg.local",
        "password": "ChangeMe123!",
        "phone": "+639171000202",
        "gender": "Female",
        "date_of_birth": "1995-10-24",
        "address": "456 Rizal Ave, Quezon City",
    },
]


async def _create_user_if_missing(
    db,
    *,
    name: str,
    email: str,
    legacy_email: str,
    role: str,
    password_hash: str,
) -> tuple[user_model.User, bool]:
    existing = await user_repository.get_by_email(db, email)
    if not existing:
        existing = await user_repository.get_by_email(db, legacy_email)
        if existing:
            if existing.role != role:
                raise RuntimeError(
                    f"Cannot seed {email}: existing account has role '{existing.role}'."
                )
            existing.email = email.lower()
            await db.commit()
            await db.refresh(existing)

    if existing:
        if existing.role != role:
            raise RuntimeError(
                f"Cannot seed {email}: existing account has role '{existing.role}'."
            )
        return existing, False

    user = user_model.User(
        email=email.lower(),
        name=name,
        hashed_password=password_hash,
        role=role,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user, True


async def seed_workforce() -> None:
    created_doctors = 0
    created_staff = 0

    async with async_session() as db:
        for item in DOCTORS:
            if len(item["password"]) < 8:
                raise RuntimeError(f"Seed password for {item['email']} is too short.")

            specialty = await specialty_repository.get_by_name(db, item["specialty"])
            if not specialty:
                raise RuntimeError(
                    f"Required specialty '{item['specialty']}' is missing. Run seed_catalog first."
                )

            user, user_created = await _create_user_if_missing(
                db,
                name=item["name"],
                email=item["email"],
                legacy_email=item["legacy_email"],
                role="doctor",
                password_hash=hash_password(item["password"]),
            )
            profile = await doctor_repository.get_by_user_id(db, user.id)
            if not profile:
                await doctor_repository.create(
                    db,
                    user_id=user.id,
                    specialty_id=specialty.id,
                    title=item["title"],
                    phone=item["phone"],
                    bio=item["bio"],
                    is_active=True,
                )
            if user_created:
                created_doctors += 1

        for item in STAFF:
            if len(item["password"]) < 8:
                raise RuntimeError(f"Seed password for {item['email']} is too short.")

            _, created = await _create_user_if_missing(
                db,
                name=item["name"],
                email=item["email"],
                legacy_email=item["legacy_email"],
                role="staff",
                password_hash=hash_password(item["password"]),
            )
            if created:
                created_staff += 1

        created_patients = 0
        for item in PATIENTS:
            if len(item["password"]) < 8:
                raise RuntimeError(f"Seed password for {item['email']} is too short.")

            user, user_created = await _create_user_if_missing(
                db,
                name=item["name"],
                email=item["email"],
                legacy_email=item["legacy_email"],
                role="patient",
                password_hash=hash_password(item["password"]),
            )
            profile = await patient_repository.get_by_user_id(db, user.id)
            if not profile:
                await patient_repository.update(
                    db,
                    user_id=user.id,
                    data=PatientProfileUpdate(
                        phone=item["phone"],
                        gender=item["gender"],
                        date_of_birth=item["date_of_birth"],
                        address=item["address"],
                    ),
                )
            if user_created:
                created_patients += 1

    print(
        f"Workforce & client seed complete: {created_doctors} doctors, "
        f"{created_staff} staff, and {created_patients} client accounts created."
    )


def main() -> None:
    asyncio.run(seed_workforce())


if __name__ == "__main__":
    main()
