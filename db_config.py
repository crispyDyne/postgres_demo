# Configuration should match the configuration in docker-compose.yml
import asyncpg

config = {
    "database": "demo_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}


async def connect_to_postgres():
    pg_config = config.copy()
    pg_config["database"] = "postgres"
    return await asyncpg.connect(**pg_config)


async def connect_to_db():
    return await asyncpg.connect(**config)
