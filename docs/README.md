# SSMG System Documentation

This folder contains the maintained system documentation and diagrams for the current SSMG implementation.

## Document set

- [System documentation (PDF)](./system_documentation.pdf)
- [System architecture](./diagrams/ssmg-architecture.png)
- [Entity relationship diagram](./diagrams/ssmg-erd.png)
- [Role capabilities](./diagrams/ssmg-use-case.png)
- [Appointment booking sequence](./diagrams/ssmg-sequence.png)
- [Appointment lifecycle](./diagrams/ssmg-activity.png)

## System summary

SSMG is a role-based healthcare appointment management system for patients, doctors, staff, and administrators. The Nuxt application communicates directly with a FastAPI backend that applies JWT authentication and role authorization, persists healthcare scheduling data in PostgreSQL, stores images in MinIO, sends account and appointment emails through Resend, and accesses an external AI provider through a backend abstraction.

Patients can browse doctors, specialties, and services; manage their profile; book, reschedule, and cancel appointments; and use the health and first-aid assistant. Doctors manage their profile and view assigned appointments, schedules, and personal reports. Staff coordinate appointment operations, while administrators manage users, doctors, staff, catalog records, schedules, reports, and AI conversation monitoring.

## PDF regeneration

Regenerate the PDF with a Chrome-compatible browser:

```bash
google-chrome --headless --no-sandbox --disable-gpu \
  --print-to-pdf=docs/system_documentation.pdf \
  "file://$(pwd)/docs/system_documentation.html"
```
