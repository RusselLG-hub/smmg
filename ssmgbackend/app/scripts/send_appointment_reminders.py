import asyncio
import logging
import sys

from app.db.session import async_session
from app.features.v1.notifications import service as notification_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("send_appointment_reminders")


async def main():
    logger.info("Starting appointment reminder process...")
    async with async_session() as db:
        try:
            sent_count = await notification_service.process_appointment_reminders(db)
            logger.info(f"Reminder process completed successfully. {sent_count} reminders sent.")
        except Exception as e:
            logger.error(f"Error during appointment reminder execution: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
