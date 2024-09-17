import asyncio

from db0_setup_database import create_database
from db_config import connect_to_db, channels


async def make_hypertable(conn, table_name):
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


async def create_aggregates(conn, base_table_name):
    durations = ["second", "minute", "hour", "day"]

    for dur_index, duration in enumerate(durations):
        # Define aggregate columns
        agg_columns = []
        for channel in channels:
            agg_col = aggregate_columns(channel, dur_index == 0)
            agg_columns.extend(agg_col)

        agg_columns = ", ".join(agg_columns)

        last_duration = (
            base_table_name
            if dur_index == 0
            else f"{base_table_name}_{durations[dur_index - 1]}s"
        )

        create_aggregate = f"""
            CREATE MATERIALIZED VIEW {base_table_name}_{duration}s
            WITH (timescaledb.continuous)
            AS SELECT
                time_bucket('1 {duration}', time) AS time,
                {agg_columns}
            FROM {last_duration}
            GROUP BY time_bucket('1 {duration}', time);
            """

        await conn.execute(create_aggregate)

        # Create the refresh policy
        await conn.execute(
            f"""
            SELECT add_continuous_aggregate_policy(
                '{base_table_name}_{duration}s',
                start_offset => NULL,
                end_offset => INTERVAL '1 {duration}' + INTERVAL '1 minute',
                schedule_interval => INTERVAL '1 {duration}'
            );
            """
        )


async def setup_table_with_timescale(conn, table_name):

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

    channels_str = ", ".join([f"{channel} DOUBLE PRECISION" for channel in channels])

    await conn.execute(
        f"""
        CREATE TABLE data_table (
            id SERIAL,
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


async def main():
    await create_database()
    conn = await connect_to_db()
    await setup_table_with_timescale(conn, "data_table")
    await make_hypertable(conn, "data_table")
    await create_aggregates(conn, "data_table")


if __name__ == "__main__":
    asyncio.run(main())
