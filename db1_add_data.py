import asyncio
import random

from db_config import connect_to_db, channels


async def add_data(table_name):
    # Connect to the database to insert data
    conn = await connect_to_db()
    # Insert random data every 5 seconds
    try:
        channel_str = ", ".join(channels)
        channel_sql = ", ".join([f"${i}" for i in range(1, len(channels) + 1)])
        while True:
            channel_data = []
            for _ in channels:
                channel_data.append(random.uniform(0, 100))

            await conn.execute(
                f"""
                INSERT INTO {table_name} ({channel_str})
                VALUES ({channel_sql});
                """,
                *channel_data,
            )

            data_str = "".join(
                [
                    f"{channel}: {data:.2f}, "
                    for (channel, data) in zip(channels, channel_data)
                ]
            )
            data_str = data_str[:-2]  # Remove the trailing comma
            print(f"Inserted data - {data_str}")
            await asyncio.sleep(5)  # Insert data every 5 seconds

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_data("data_table"))
