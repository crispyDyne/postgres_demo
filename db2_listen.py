import asyncio

from db_config import connect_to_db


async def fetch_and_print_data(conn, payload, table_name):
    # Fetch the data row based on the notification payload (which contains the row ID)
    if payload == "updated":
        # the timescale example does not use a row id, so we fetch the latest row instead
        print("Fetching the latest row...")
        row = await conn.fetchrow(
            f"""
            SELECT * FROM {table_name} ORDER BY time DESC LIMIT 1;
            """
        )
    else:
        row = await conn.fetchrow(
            f"""
            SELECT * FROM {table_name} WHERE id = $1;
            """,
            int(payload),
        )

    # Print the fetched row
    print(row)


async def listen_notifications(table_name):
    # Connect to the database to listen for notifications
    conn = await connect_to_db()

    # Listen to the 'data_channel' channel
    async def on_notify(conn, pid, channel, payload):
        await fetch_and_print_data(conn, payload, table_name)

    await conn.add_listener(f"{table_name}", on_notify)
    print("Waiting for notifications...")

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the loop running to receive notifications
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(listen_notifications("data_table"))
