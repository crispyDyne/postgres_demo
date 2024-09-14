import asyncio

from db_config import connect_to_db


async def read_all_data():
    conn = await connect_to_db()
    rows = await conn.fetch("SELECT * FROM data_table;")
    for row in rows:
        print(
            f"ID={row['id']}, Time={row['time']}, "
            f"Channel 1={row['channel_1']}, Channel 2={row['channel_2']}, Channel 3={row['channel_3']}"
        )
    await conn.close()


if __name__ == "__main__":
    asyncio.run(read_all_data())
