import asyncio
import asyncpg

# should match the configuration in docker-compose.yml
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
    return await asyncpg.connect(
        **pg_config
    )

async def connect_to_db():
    return await asyncpg.connect(
        **config
    )

async def create_database():
    # Connect to the default 'postgres' database to create a new database
    conn = await connect_to_postgres()
    await conn.execute(f"DROP DATABASE IF EXISTS {config["database"]};")
    await conn.execute(f"CREATE DATABASE {config["database"]};")
    await conn.close()


async def setup_table():
    # Connect to the newly created database to create a new table
    conn = await connect_to_db()

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS data_table (
            id SERIAL PRIMARY KEY,
            time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            channel_1 DOUBLE PRECISION,
            channel_2 DOUBLE PRECISION,
            channel_3 DOUBLE PRECISION
        );
    """
    )

    # Create a function that notifies the 'data_channel' channel whenever a new row is inserted
    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION notify_trigger() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify('data_channel', NEW.id::text);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create a trigger that calls the 'notify_trigger' function after a new row is inserted
    await conn.execute(
        """
        CREATE TRIGGER data_insert_notify
        AFTER INSERT ON data_table
        FOR EACH ROW
        EXECUTE FUNCTION notify_trigger();
    """
    )

    await conn.close()


async def main():
    await create_database()
    await setup_table()
    print("Database and table setup complete.")


if __name__ == "__main__":
    asyncio.run(main())
