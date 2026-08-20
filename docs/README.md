# SMMG System Documentation

This folder contains the maintained system documentation and diagrams for the current SMMG implementation.

## Document set

- [System documentation (PDF)](./system_documentation.pdf)
- [Prototype explanation (PDF)](./SMMG_Prototype_Explanation.pdf)
- [System architecture](./diagrams/smmg-architecture.png)
- [Entity relationship diagram](./diagrams/smmg-erd.png)
- [Role capabilities](./diagrams/smmg-use-case.png)
- [Appointment booking sequence](./diagrams/smmg-sequence.png)
- [Appointment lifecycle](./diagrams/smmg-activity.png)

## System summary

SMMG is a role-based healthcare appointment management system for patients, doctors, staff, and administrators. The Nuxt application communicates directly with a FastAPI backend that applies JWT authentication and role authorization, persists healthcare scheduling data in PostgreSQL, stores images in MinIO, sends account and appointment emails through Resend, and accesses an external AI provider through a backend abstraction.

Patients can browse doctors, specialties, and services; manage their profile; book, reschedule, and cancel appointments; and use the health and first-aid assistant. Doctors manage their profile and view assigned appointments, schedules, and personal reports. Staff coordinate appointment operations, while administrators manage users, doctors, staff, catalog records, schedules, reports, and AI conversation monitoring.

## PDF regeneration

Regenerate the system documentation PDF with a Chrome-compatible browser:

```bash
google-chrome --headless --no-sandbox --disable-gpu \
  --print-to-pdf=docs/system_documentation.pdf \
  "file://$(pwd)/docs/system_documentation.html"
```

Regenerate the prototype explanation PDF with weasyprint:

```bash
pip install weasyprint
weasyprint docs/SMMG_Prototype_Explanation.html docs/SMMG_Prototype_Explanation.pdf
```
