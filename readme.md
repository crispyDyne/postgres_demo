## Postgres Setup
[Install docker desktop (Windows)](https://docs.docker.com/desktop/install/windows-install/)

[Setup TimescaleDB Docker Image](https://docs.timescale.com/self-hosted/latest/install/installation-docker/)
- There are any number of ways to run a PostgreSQL database, but for this example I'm using a Docker container and a TimescaleDB image.
- The image I'm using: timescale/timescaledb-ha:pg16
- TimescaleDB is an extension of PostgreSQL, so you can use any PostgreSQL client to connect to it.
- The examples here do not use any timescale specific features, so you can use any PostgreSQL database to run the examples.

Things most likely to go wrong:
- Port is not exposed. The default port for PostgreSQL is 5432. If you're running the container on your local machine, you'll need to expose this port.
- User name or password is incorrect. The default user name is 'postgres' and the default password is 'password'. You can change these in the docker run command.
- Database name is incorrect. The default database name is 'postgres'. You can change this in the docker run command.


## Running the examples
- db0_setup_database.py: This script will create a database and a table in the database as well as notifications for the table.
    - Run this script first. It only needs to be run once.
- db1_add_data.py: This script will insert data into the table.
    - Run this script after running db0_setup_database.py.
- db2_listen.py: This script will listen for notifications from the table.
    - Run this script while db1_add_data.py is running. It will print out the notifications to the console.
- dbt_timescale_setup.py: Similar to db0_setup_database.py, but sets up TimescaleDB specific features. Specifically, it sets up a continuous aggregates, which  pre-compute statistics like averages, sums, etc. over specified time intervals (1 second, 1 minute, 1 hour, etc.).
    - Run this script first, instead of db0_setup_database.py, if you want to use TimescaleDB specific features. It only needs to be run once.
    - The other scripts will work with or without TimescaleDB specific features.


# Setting Up TimescaleDB in Docker on Ubuntu

## Prerequisites
1. **Docker**: 

    ```bash
    sudo apt-get update
    sudo apt-get install docker.io
    ```

2. **Docker Compose Plugin**


    ```bash
    sudo apt update
    sudo apt install docker-compose-v2
    ```

3. **Install psql**:

    ```bash
    sudo apt-get install postgresql-client
    ```

## Run a TimescaleDB Container
    
```bash
sudo docker compose up -d
```

This command does the following:
- `docker-compose up`: Starts the container.
- `-d`: Runs the container in detached mode (background).

The configuration for the TimescaleDB container is defined in the `docker-compose.yml` file. You can customize this file to change the container's settings, such as the port mapping, environment variables, and volumes.

## Other Useful Commands

### List Running Containers

```bash
sudo docker ps
```

### Stop the Container

```bash
sudo docker stop timescaledb
```

Assumes the container is named `timescaledb` (as defined in the `docker-compose.yml` file).