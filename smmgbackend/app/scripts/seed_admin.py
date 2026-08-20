import asyncio
import sys

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import async_session
from app.features.v1.users import model as user_model
from app.features.v1.users import repository as user_repository


async def seed_admin():
    admin_email = settings.ADMIN_EMAIL.lower().strip()

    if not admin_email or not settings.ADMIN_PASSWORD:
        print("Error: ADMIN_EMAIL and ADMIN_PASSWORD must be configured.")
        sys.exit(1)

    async with async_session() as db:
        existing_user = await user_repository.get_by_email(db, admin_email)
        if existing_user:
            print("Admin user already exists.")
            return

        hashed_pw = hash_password(settings.ADMIN_PASSWORD)

        admin_user = user_model.User(
            email=admin_email,
            name=settings.ADMIN_NAME.strip(),
            hashed_password=hashed_pw,
            role="admin",
            is_active=True,
            is_email_verified=True,
        )

        db.add(admin_user)
        await db.commit()
        print("Admin user created successfully.")


def main():
    asyncio.run(seed_admin())


if __name__ == "__main__":
    main()
