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
    multipart

# Copy app code
COPY shipyard ./shipyard

# The server listens on this port
EXPOSE 8000

# Run server
CMD [ "hug", "-m", "shipyard" ]
