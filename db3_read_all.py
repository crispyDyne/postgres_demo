import asyncio

from db_config import connect_to_db


async def read_all_data():
    conn = await connect_to_db()
    rows = await conn.fetch("SELECT * FROM data_table;")
    for row in rows:
        print(row)
    await conn.close()


if __name__ == "__main__":
    asyncio.run(read_all_data())
