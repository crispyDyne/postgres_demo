import asyncio
import random

from db0_setup_database import connect_to_db


async def add_data():
    # Connect to the database to insert data
    conn = await connect_to_db()
    # Insert random data into the 'data_table' table every 5 seconds
    try:
        while True:
            channel_1 = random.uniform(0, 100)
            channel_2 = random.uniform(0, 100)
            channel_3 = random.uniform(0, 100)

            await conn.execute(
                """
                INSERT INTO data_table (channel_1, channel_2, channel_3)
                VALUES ($1, $2, $3);
            """,
                channel_1,
                channel_2,
                channel_3,
            )

            print(f"Inserted data: {channel_1}, {channel_2}, {channel_3}")
            await asyncio.sleep(5)  # Insert data every 5 seconds

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_data())
