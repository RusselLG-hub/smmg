import asyncio

from app.db.session import async_session
from app.features.v1.services import repository as service_repository
from app.features.v1.services import schema as service_schema
from app.features.v1.specialties import repository as specialty_repository
from app.features.v1.specialties import schema as specialty_schema


SPECIALTIES = [
    {
        "name": "General Medicine",
        "description": "Primary care for common illnesses, preventive care, and overall health concerns.",
    },
    {
        "name": "Pediatrics",
        "description": "Medical care for infants, children, and adolescents, including growth and development concerns.",
    },
    {
        "name": "Cardiology",
        "description": "Evaluation and care for heart health, blood pressure, and cardiovascular conditions.",
    },
    {
        "name": "Dermatology",
        "description": "Diagnosis and treatment of conditions affecting the skin, hair, and nails.",
    },
    {
        "name": "Obstetrics and Gynecology",
        "description": "Women's reproductive health, pregnancy care, and gynecological consultations.",
    },
]

SERVICES = [
    {
        "name": "General Medical Consultation",
        "specialty": "General Medicine",
        "description": "A general health assessment for symptoms, routine concerns, and appropriate treatment or referral.",
    },
    {
        "name": "Child Wellness Consultation",
        "specialty": "Pediatrics",
        "description": "Routine pediatric consultation covering growth, development, nutrition, and common childhood concerns.",
    },
    {
        "name": "Heart Health Assessment",
        "specialty": "Cardiology",
        "description": "Evaluation of cardiovascular symptoms and risk factors, including blood pressure and heart-health review.",
    },
    {
        "name": "Skin Condition Consultation",
        "specialty": "Dermatology",
        "description": "Clinical assessment for acne, rashes, irritation, infections, and other skin-related concerns.",
    },
    {
        "name": "Women's Health Consultation",
        "specialty": "Obstetrics and Gynecology",
        "description": "Consultation for reproductive health, prenatal concerns, menstrual health, and preventive care.",
    },
]


async def seed_catalog() -> None:
    async with async_session() as db:
        specialty_ids: dict[str, str] = {}
        created_specialties = 0
        created_services = 0

        for item in SPECIALTIES:
            specialty = await specialty_repository.get_by_name(db, item["name"])
            if not specialty:
                specialty = await specialty_repository.create(
                    db,
                    specialty_schema.SpecialtyCreate(
                        name=item["name"],
                        description=item["description"],
                        is_active=True,
                    ),
                )
                created_specialties += 1
            specialty_ids[item["name"]] = specialty.id

        for item in SERVICES:
            service = await service_repository.get_by_name(db, item["name"])
            if service:
                continue
            await service_repository.create(
                db,
                service_schema.ServiceCreate(
                    name=item["name"],
                    description=item["description"],
                    specialty_id=specialty_ids[item["specialty"]],
                    image_url=None,
                    is_active=True,
                ),
            )
            created_services += 1

        print(
            f"Catalog seed complete: {created_specialties} specialties and "
            f"{created_services} services created."
        )


def main() -> None:
    asyncio.run(seed_catalog())


if __name__ == "__main__":
    main()
