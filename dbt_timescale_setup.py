import asyncio

from db0_setup_database import destroy_then_create_database
from db_config import connect_to_db, channels


async def destroy_then_create_devices_table(conn):
    await conn.execute(
        """
        DROP TABLE IF EXISTS devices CASCADE
        """
    )
    await conn.execute(
        """
        CREATE TABLE devices(
            id integer GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            name text NOT NULL,
            serial_number text,
            installation_date timestamptz default now()
        )
        """
    )


async def add_device(conn, name, serial_number):
    await conn.execute(
        """
        INSERT INTO devices (name, serial_number)
        VALUES ($1, $2)
        """,
        name,
        serial_number,
    )


async def make_hypertable(conn, table):
    table_name = table["table_name"]
    create_hypertable = f"""
        SELECT create_hypertable('{table_name}', by_range('time'), if_not_exists => TRUE)
        """
    await conn.execute(create_hypertable)


def aggregate_columns(name: str, most_granular: bool) -> list[str]:
    columns = []

    func_names = ["stats", "min", "max"]
    if most_granular:
        funcs = ["stats_agg", "min", "max"]
    else:
        funcs = ["rollup", "min", "max"]

    for func_name, func in zip(func_names, funcs):
        # Adjust the argument to use the appropriate name from the previous aggregate
        if most_granular:
            arg = name
        else:
            arg = f"{name}_{func_name}"

        # Generate the SQL aggregation function string
        column = f"{func}({arg}) as {name}_{func_name}"
        columns.append(column)

    return columns


async def create_aggregates(conn, table):
    durations = ["second", "minute", "hour", "day"]

    table_name = table["table_name"]
    columns = table["table_columns"]

    for dur_index, duration in enumerate(durations):
        # Define aggregate columns
        agg_columns = []
        for channel in columns:
            agg_col = aggregate_columns(channel, dur_index == 0)
            agg_columns.extend(agg_col)

        agg_columns = ", ".join(agg_columns)

        last_duration = (
            table_name
            if dur_index == 0
            else f"{table_name}_{durations[dur_index - 1]}s"
        )

        create_aggregate = f"""
            CREATE MATERIALIZED VIEW {table_name}_{duration}s
            WITH (timescaledb.continuous)
            AS SELECT \
            device_id,
            time_bucket('1 {duration}', time) AS time,
            {agg_columns}
            FROM {last_duration}
            GROUP BY (device_id, time_bucket('1 {duration}', {last_duration}.time));\
            """

        await conn.execute(create_aggregate)

        # Create the refresh policy
        await conn.execute(
            f"""
            SELECT add_continuous_aggregate_policy(
                '{table_name}_{duration}s',
                start_offset => NULL,
                end_offset => INTERVAL '1 {duration}' + INTERVAL '1 minute',
                schedule_interval => INTERVAL '1 {duration}'
            );
            """
        )


async def setup_table_with_timescale(conn, table):

    table_name = table["table_name"]
    columns = table["table_columns"]

    durations = ["second", "minute", "hour", "day"]
    for duration in durations:
        await conn.execute(
            f"""
            DROP MATERIALIZED VIEW IF EXISTS {table_name}_{duration}s CASCADE
            """
        )

    await conn.execute(
        f"""
        DROP TABLE IF EXISTS {table_name} CASCADE;
        """
    )

    channels_str = ", ".join([f"{column} float NOT NULL" for column in columns])

    await conn.execute(
        f"""
        CREATE TABLE {table_name} (
            time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            device_id integer NOT NULL default 1,
            {channels_str},
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
        """
    )

    await conn.execute(
        f"""
        CREATE TRIGGER {table_name}_inserted AFTER INSERT ON {table_name} EXECUTE FUNCTION notify_update();

        """
    )


async def create_notify_update_function(conn):
    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION notify_update() RETURNS trigger AS $$
        BEGIN
            PERFORM pg_notify(TG_TABLE_NAME, 'updated');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


I_WANT_TO_DELETE_THE_DATABASE = True


async def main():

    if I_WANT_TO_DELETE_THE_DATABASE:
        await destroy_then_create_database()

    conn = await connect_to_db()
    if I_WANT_TO_DELETE_THE_DATABASE:
        await destroy_then_create_devices_table(conn)
        await create_notify_update_function(conn)
        await add_device(conn, "device_1", "12345")

    table = {
        "table_name": "data_table",
        "table_columns": channels,
    }

    await setup_table_with_timescale(conn, table)
    await make_hypertable(conn, table)
    await create_aggregates(conn, table)


if __name__ == "__main__":
    asyncio.run(main())
