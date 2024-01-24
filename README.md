# Elastic Stack: Cowrie, PyRDP Honeypots
A docker-compose "project" to run 3 honeypots and log all the output in Elasticsearch. 
This is done part of the CEH minor at NHL Stenden University of Applied Sciences, Emmen, The Netherlands.

## Configuration
* Docker Compose
* Cowrie SSH/Telnet honeypot
* PyRdp honeypot
* DDosPot
* Elastic Stack
  * Elasticsearch
  * Kibana
  * Filebeat
  * Logstash

## System requirements
* 6-8GB RAM
* 40GB free Space

**Note!** This project was tested on the above mentioend characteristics, on Ubuntu 20.04.

## How to build the environment
1. Update the package to the latest version

```bash
sudo apt update -y && sudo apt upgrade -y && sudo apt autoremove -y
```

2. **(Optional)** Change the port number when logging in via SSH **(only if you plan to run Cowrie on the default SSH port: 22)**

```bash
sudo vim /etc/ssh/sshd_config
```

Find the line where `#Port 22` is written, and rewrite it as `Port 22222`

Reload ssh.service to reflect the change

```bash
sudo systemctl reload ssh
```

3. Install Git

```bash
sudo apt install -y git
```

4. Install Docker (Linux)

```bash
sudo apt install docker.io -y
```

5. Install Docker Compose

Please see here: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

For Ubuntu use:

```bash
sudo apt install docker-compose -y
```

6. Clone this repository, and change to the directory

```bash
git clone https://github.com/Geniools/ceh-elastic-stack
cd Directory Name
```

7. Create the file `cowrie.json` inside the `cowrie/log` directory. Afterwards give it the right permissions.

```bash
sudo touch cowrie.json
sudo chmod o+w cowrie.json
```

8. Give the right permissions to `filebeat.yml` inside the `filebeat/config` directory.

```bash
sudo chmod go-w filebeat.yml
```

9. Build and run containers

```bash
docker-compose up
```

You can run the containers as a daemon with the following command:

```bash
docker-compose up -d
```

10. Access Kibana in your browser

You can access Kibana by typing `http://127.0.0.1:5601` in your browser. 


11. Install NMAP to to a quick test attack

```bash
sudo apt install nmap
```

**After all the containers started and kibana is running you can test the logging:**

```bash
sudo nmap -A -T4 0.0.0.0
sudo nmap -sU 0.0.0.0
```

12. Go to Analytics -> Discover:

Create a new data view for each honeypot *(on the right you'll see "patterns" with the initialls of the honeypot)*. Create one data view for each honeypot.

