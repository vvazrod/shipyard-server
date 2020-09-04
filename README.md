# shipyard-server
Containerized real-time tasks deployment and management tool

# Usage
The recommended way of running this software is with [the container image
provided in Docker Hub](https://hub.docker.com/r/varrrro/shipyard-server). Note
that the MongoDB host URL is provided in an environment variable called
`DB_HOST`.

You can also do a test deployment of the system with `docker-compose` using the
following example configuration.

```YAML
version: "3.0"

services:
    management:
        image: varrrro/shipyard-server
        depends_on:
            - db
        environment:
            DB_HOST: ${DB_HOST}
        ports:
            - 8000:8000

    db:
        image: mongo
```
