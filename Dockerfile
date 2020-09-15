FROM python:3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
WORKDIR /app
RUN pip install wheel \
    hug \
    marshmallow \
    marshmallow-dataclass \
    pymongo \
    paramiko \
    multipart \
    docker

# Copy app code
COPY shipyard ./shipyard

# Create mount point for SSH keys
VOLUME [ "/root/.ssh" ]

# The server listens on this port
EXPOSE 8000

# Run server
CMD [ "hug", "-m", "shipyard" ]
