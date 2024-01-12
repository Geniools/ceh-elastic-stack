FROM alpine:edge

# Install prerequisites
RUN apk --update --no-cache add python3 python3-dev build-base libcap py3-pip git

# Create new user and group under which ddospot will run
RUN addgroup -g 1000 ddospot && adduser -D -s /sbin/nologin -u 1000 -G ddospot ddospot

# Create DDoSPot directory and copy source
COPY . /ddospot

# Create and activate virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python requirements
RUN pip install --upgrade pip
RUN pip install -r /ddospot/requirements.txt

# Fix permissions
RUN chown ddospot.ddospot -R /ddospot/*

# Enable capabilities on Python interpreter in the virtualenv to bind on privileged ports
# RUN setcap 'cap_net_bind_service=+ep' /venv/bin/python

# Expose relevant UDP ports
EXPOSE 19/udp 53/udp 123/udp 161/udp 1900/udp

# Start DDoSPot
USER ddospot
WORKDIR /ddospot
CMD ["python", "ddospot.py", "-n"]

