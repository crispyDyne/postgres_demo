import asyncio

from db_config import config, channels, connect_to_db, connect_to_postgres


async def destroy_then_create_database():
    conn = await connect_to_postgres()
    await conn.execute(f'DROP DATABASE IF EXISTS {config["database"]};')
    await conn.execute(f'CREATE DATABASE {config["database"]};')
    await conn.close()


async def setup_table(table_name):
    conn = await connect_to_db()

    channels_str = ", ".join([f"{channel} DOUBLE PRECISION" for channel in channels])
    await conn.execute(
        f"""
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            device_id integer NOT NULL default 1,
            {channels_str}
        );
        """
    )

    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION notify_update() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify(TG_TABLE_NAME, NEW.id::text);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    await conn.execute(
        f"""
        CREATE TRIGGER {table_name}_inserted
        AFTER INSERT ON {table_name}
        FOR EACH ROW
        EXECUTE FUNCTION notify_update();
        """
    )

    await conn.close()


async def main():
    await destroy_then_create_database()
    await setup_table("data_table")
    print("Database and table setup complete.")


if __name__ == "__main__":
    asyncio.run(main())
