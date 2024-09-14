import asyncio

from db_config import config, channels, connect_to_db, connect_to_postgres


async def create_database():
    conn = await connect_to_postgres()
    await conn.execute(f'DROP DATABASE IF EXISTS {config["database"]};')
    await conn.execute(f'CREATE DATABASE {config["database"]};')
    await conn.close()


async def setup_table():
    conn = await connect_to_db()

    channels_str = ", ".join([f"{channel} DOUBLE PRECISION" for channel in channels])
    await conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS data_table (
            id SERIAL PRIMARY KEY,
            time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            {channels_str}
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
