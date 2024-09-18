# Configuration should match the configuration in docker-compose.yml
import asyncpg

config = {
    "database": "demo_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}

channels = [
    'motor_curr_cmd' ,
    'motor_curr_act' ,
    'motor_vel_cmd' ,
    'motor_vel_act' ,
    'motor_pos_cmd' ,
    'motor_pos_act' ,
    'load_cell_load' ,
    'wec_current' ,
    'wec_voltage' ,
    'wec_heidenhain_pos' ,
    'wec_heidenhain_vel' ,
    'vesc_current' ,
    'vesc_voltage' ,
    'vesc_etc' 
    ]


async def connect_to_postgres():
    pg_config = config.copy()
    pg_config["database"] = "postgres"
    return await asyncpg.connect(**pg_config)


async def connect_to_db():
    return await asyncpg.connect(**config)
