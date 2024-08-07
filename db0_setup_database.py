import asyncio
import asyncpg


async def create_database():
    conn = await asyncpg.connect(
        database="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    )
    await conn.execute("DROP DATABASE IF EXISTS demo_db;")
    await conn.execute("CREATE DATABASE demo_db;")
    await conn.close()


async def setup_table():
    conn = await asyncpg.connect(
        database="demo_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    )

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
