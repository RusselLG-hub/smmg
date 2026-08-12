# SSMG

SSMG runs locally with Docker Compose. Start all services from the project root:

```bash
docker compose up -d
```

## MinIO dashboard

Open [http://localhost:9001](http://localhost:9001) and log in with:

```text
Username: minioadmin
Password: minioadmin
```

Port `9001` is the MinIO web dashboard. Port `9000` is the object-storage API used by the backend.

## pgAdmin

Open [http://localhost:5050](http://localhost:5050) and log in with:

```text
Email: admin@ssmg.example.com
Password: pgadmin
```

### Add the PostgreSQL server

After logging in to pgAdmin:

1. Right-click **Servers** in the left sidebar.
2. Select **Register > Server**.
3. In the **General** tab, enter `SSMG PostgreSQL` as the name.
4. In the **Connection** tab, enter:

   ```text
   Host name/address: postgres
   Port: 5432
   Maintenance database: ssmg
   Username: postgres
   Password: postgres
   ```

5. Enable **Save password**, then select **Save**.

Use `postgres` as the host—not `localhost`—because pgAdmin and PostgreSQL communicate through the Docker Compose network.

## Local service URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API documentation | http://localhost:8000/docs |
| MinIO dashboard | http://localhost:9001 |
| pgAdmin | http://localhost:5050 |

The credentials above are intended only for local demonstration and development.
