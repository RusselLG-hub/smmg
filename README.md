# SSMG Healthcare Appointment Management System

SSMG is a role-based healthcare appointment management system with doctor discovery, database-backed specialties and services, schedule management, appointment workflows, notifications, reports, image uploads, and an AI-powered health and first-aid assistant.

> **Development only:** The accounts and infrastructure credentials below are local demonstration defaults. Replace them before exposing the system publicly, and never commit the generated `.env` file.

## Local URLs and User Credentials

### SSMG application

- **Application:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

All seeded doctor and staff accounts use the password `ChangeMe123!`.

### Administrator login

| Environment | Email | Password |
| --- | --- | --- |
| Staging prototype | `admin@gmail.com` | Use the private password configured as `ADMIN_PASSWORD` in the deployment secret |
| Local Docker Compose | Value of `ADMIN_EMAIL` in `.env` | Value of `ADMIN_PASSWORD` in `.env` |

The administrator password is deliberately not committed to this README. Share it with authorized client reviewers through a private channel or password manager, then rotate it after the prototype review.

| Role | Name | Email | Specialty |
| --- | --- | --- | --- |
| Doctor | Maria Santos | `maria.santos.doctor@example.com` | General Medicine |
| Doctor | Gabriel Reyes | `gabriel.reyes.doctor@example.com` | Pediatrics |
| Doctor | Isabella Cruz | `isabella.cruz.doctor@example.com` | Cardiology |
| Doctor | Miguel Garcia | `miguel.garcia.doctor@example.com` | Dermatology |
| Doctor | Sofia Mendoza | `sofia.mendoza.doctor@example.com` | Obstetrics and Gynecology |
| Staff | Angela Flores | `angela.flores.staff@example.com` | Not applicable |
| Staff | Paolo Navarro | `paolo.navarro.staff@example.com` | Not applicable |

The administrator account is created from the configured `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `ADMIN_NAME` values. Patient accounts are created from the registration page.

The backend startup process creates the administrator, five doctors, two staff accounts, five specialties, and five services. The seed scripts are idempotent, so existing records are not duplicated and user-changed passwords are not overwritten.

### MinIO dashboard

- **Console:** [http://localhost:9001](http://localhost:9001)
- **S3 API:** [http://localhost:9000](http://localhost:9000)
- **Username:** `minioadmin`
- **Password:** `minioadmin`
- **Application bucket:** `ssmg`

To inspect uploaded profile and service images:

1. Open [http://localhost:9001](http://localhost:9001).
2. Sign in with the MinIO credentials above.
3. Open **Object Browser**.
4. Select the `ssmg` bucket.

### PostgreSQL and pgAdmin

SSMG uses PostgreSQL, so its browser-based database dashboard is **pgAdmin**. phpMyAdmin is not included because it supports MySQL and MariaDB, not PostgreSQL.

Open [http://localhost:5050](http://localhost:5050) and sign in to pgAdmin:

| Setting | Value |
| --- | --- |
| Email | `admin@ssmg.example.com` |
| Password | `pgadmin` |

After signing in, register the SSMG PostgreSQL server:

1. Right-click **Servers** in the left sidebar.
2. Select **Register > Server**.
3. In **General**, enter `SSMG PostgreSQL` as the server name.
4. In **Connection**, enter the database credentials below.
5. Enable **Save password**, then select **Save**.

| PostgreSQL setting | Value |
| --- | --- |
| Host from pgAdmin in Docker | `postgres` |
| Host from your computer | `localhost` |
| Port | `5432` |
| Maintenance database | `ssmg` |
| Username | `postgres` |
| Password | `postgres` |

Use `postgres`, not `localhost`, in pgAdmin because both containers communicate through the Docker Compose network.

To open PostgreSQL directly through its container:

```bash
docker compose exec postgres psql -U postgres -d ssmg
```

Useful commands:

```sql
\dt
SELECT id, name, email, role, is_active FROM users;
SELECT appointment_reference, scheduled_at, status FROM appointments;
\q
```

## Docker Setup

### 1. Install Docker CLI and Docker Compose

SSMG uses Docker Engine and the Docker Compose CLI plugin. Docker Desktop is not required.

#### Windows 10 or Windows 11

The project uses Linux containers. Install WSL 2 by opening **PowerShell as Administrator** and running:

```powershell
wsl --install -d Ubuntu
wsl --update
```

Restart Windows if requested, then open **Ubuntu** from the Start menu. Run the remaining Git and Docker commands inside the Ubuntu terminal.

#### Ubuntu or Ubuntu on WSL 2

Install Docker Engine, the CLI, Buildx, and the Compose plugin from Docker's official repository:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Start Docker and enable it during system startup:

```bash
sudo systemctl enable --now docker
```

Verify the installation:

```bash
docker --version
docker compose version
docker info
```

If `docker info` reports a permission error, run Docker commands with `sudo` or configure Docker for non-root use using Docker's official Linux post-installation guide.

### 2. Clone and enter the project

```bash
mkdir -p ~/projects
cd ~/projects
git clone <repository-url>
cd ssmg
```

The repository root must contain `docker-compose.yml`, `ssmgbackend`, and `ssmgfrontend`.

### 3. Create the environment file

```bash
cp .env.example .env
```

Configure the administrator account, JWT secret, Resend settings, MinIO settings, and external AI provider values in `.env` before starting the system.

### 4. Build and start SSMG

```bash
docker compose up -d --build
```

Docker starts the Nuxt frontend, FastAPI backend, PostgreSQL, MinIO, and pgAdmin. Check their status:

```bash
docker compose ps
```

Follow backend startup and seed logs:

```bash
docker compose logs -f backend
```

Press `Ctrl+C` to stop following logs. The containers continue running.

### 5. Open and test the system

1. Open [http://localhost:3000](http://localhost:3000).
2. Sign in using a seeded account listed above.
3. Open [MinIO](http://localhost:9001) to inspect uploaded images.
4. Open [pgAdmin](http://localhost:5050) to inspect PostgreSQL records.
5. Open [FastAPI documentation](http://localhost:8000/docs) to inspect application endpoints.

## Common Docker Commands

```bash
# Show container status
docker compose ps

# Follow all service logs
docker compose logs -f

# Restart all services
docker compose restart

# Rebuild after source or dependency changes
docker compose up -d --build

# Stop containers while preserving data
docker compose down
```

To permanently remove the local PostgreSQL, MinIO, and pgAdmin data volumes:

```bash
docker compose down --volumes
```

> This operation permanently deletes local database records, uploaded objects, and saved pgAdmin configuration. Seed data is recreated during the next startup, but user-created data cannot be recovered.

## Architecture

- **Frontend:** Nuxt 4, Vue 3, TypeScript, Pinia, Tailwind CSS, and direct FastAPI requests
- **Backend:** FastAPI, Pydantic 2, asynchronous SQLAlchemy 2, JWT authentication, and role authorization
- **Database:** PostgreSQL 16
- **Object storage:** MinIO
- **Email:** Resend
- **AI:** External AI API behind a FastAPI provider
- **Rate limiting:** SlowAPI inside FastAPI
- **Local orchestration:** Docker Compose

```text
ssmg/
├── ssmgbackend/       # FastAPI application, models, providers, and seed scripts
├── ssmgfrontend/      # Nuxt application, stores, services, and shared types
├── docs/              # System documentation PDF and PNG diagrams
├── docker-compose.yml # Local service definitions
└── .env.example       # Development environment template
```

## Core Capabilities

- Role-specific dashboards for patients, doctors, staff, and administrators
- Database-backed doctors, specialties, services, schedules, and appointments
- Appointment booking, confirmation, rescheduling, cancellation, and completion
- Profile and service image storage through MinIO
- Email verification, appointment notices, and verified self-service password changes
- Administrator management for doctors, staff, catalog records, schedules, users, and reports
- AI-powered health and first-aid conversations with administrator monitoring
- Responsive dashboards, reports, tables, forms, and modal dialogs

## Documentation

- [System documentation overview](./docs/README.md)
- [System documentation PDF](./docs/system_documentation.pdf)
- [System architecture diagram](./docs/diagrams/ssmg-architecture.png)
- [Entity relationship diagram](./docs/diagrams/ssmg-erd.png)
- [Role capabilities diagram](./docs/diagrams/ssmg-use-case.png)
- [Appointment booking sequence](./docs/diagrams/ssmg-sequence.png)
- [Appointment lifecycle diagram](./docs/diagrams/ssmg-activity.png)
