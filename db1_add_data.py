import asyncio
import asyncpg
import random


async def add_data():
    conn = await asyncpg.connect(
        database="demo_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    )

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

    await conn.close()


if __name__ == "__main__":
    asyncio.run(add_data())
