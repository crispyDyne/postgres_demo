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

