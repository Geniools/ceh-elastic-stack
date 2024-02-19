FROM python:2.7-alpine AS base

# Set the working directory in the container
WORKDIR /app

# Install build dependencies
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev

COPY requirements.txt /app/requirements.txt
COPY ./src /app/src

RUN pip install typing
RUN pip install -r requirements.txt
RUN pip install rdpy
RUN pip install cryptography==2.2.2

# Stage 2: Final runner image
FROM base AS runner

# Copy the scenarios directory into the final image
COPY ./scenarios /app/scenarios

EXPOSE 3389

CMD python src/main.py /app/scenarios/win7-enterprise.rss > logs/output.json
