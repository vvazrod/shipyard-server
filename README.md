# Shipyard

[![codecov](https://codecov.io/gh/Varrrro/shipyard-server/branch/master/graph/badge.svg?token=6I31QH122L)](https://codecov.io/gh/Varrrro/shipyard-server)

This system provides a simpler way of orchestrating real-time tasks in
distributed environments. Manage nodes, tasks and trigger deployments using
containers through a well-defined REST API.

## Installation

The recommended way of running this software is by using the
`varrrro/shipyard-server` Docker image. The server needs to connect to a Mondo
database whose URL is provided through an environment variable called `DB_HOST`.

You can also do a test deployment of the system with `docker-compose` using the
following example configuration. Please note that this example uses your user's
SSH configuration and keys.

```YAML
version: "3.0"

services:
  management:
    image: varrrro/shipyard-server
    depends_on:
    - db
    environment:
      DB_HOST: ${DB_HOST}
    volumes:
    - ~/.ssh:/root/.ssh
    ports:
    - 8000:8000

  db:
    image: mongo
```

## Usage

Although you could use the server's REST API directly, it is recommended to use
the official [CLI client](https://github.com/Varrrro/shipyard-cli) to interact
with the system.
