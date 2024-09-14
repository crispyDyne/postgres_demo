import asyncio

from db_config import connect_to_db


async def fetch_and_print_data(conn, payload):
    # Fetch the data row based on the notification payload (which contains the row ID)
    row = await conn.fetchrow(
        """
        SELECT * FROM data_table WHERE id = $1;
        """,
        int(payload),
    )

    # Print the fetched row
    print(
        f"Fetched data: ID={row['id']}, Time={row['time']}, "
        f"Channel 1={row['channel_1']}, Channel 2={row['channel_2']}, Channel 3={row['channel_3']}"
    )


async def listen_notifications():
    # Connect to the database to listen for notifications
    conn = await connect_to_db()

    # Listen to the 'data_channel' channel
    async def on_notify(conn, pid, channel, payload):
        print(f"Got notification for ID: {payload}")
        await fetch_and_print_data(conn, payload)

    await conn.add_listener("data_channel", on_notify)
    print("Waiting for notifications...")

    try:
        while True:
            await asyncio.sleep(1)  # Keeps the loop running to receive notifications
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(listen_notifications())
