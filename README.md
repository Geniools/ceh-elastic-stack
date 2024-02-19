# Elastic Stack: Honeypots
A docker-compose "project" to run several honeypots and log all the output in Elasticsearch. 
This is done part of the CEH minor at NHL Stenden University of Applied Sciences, Emmen, The Netherlands.

## Components
* Docker Compose
* Cowrie SSH/Telnet honeypot
* PyRdp honeypot (mitm tool)
* PyRdp honeypot (simulation) - *not working fully*
* DDosPot
* Elastic Stack
  * Elasticsearch
  * Kibana
  * Filebeat
  * Logstash

## System requirements
* 6-8GB RAM
* 40GB free Space

**Note!** This project was tested on Ubuntu 20.04

## How to build the environment
1. Update the package to the latest version

```bash
sudo apt update -y && sudo apt upgrade -y && sudo apt autoremove -y
```

2. Install Git

```bash
sudo apt install -y git
```

3. Install Docker

```bash
sudo apt install docker.io -y
```

4. Install Docker Compose

For Ubuntu use:

```bash
sudo apt install docker-compose -y
```

5. Clone this repository, and change to the directory

```bash
git clone https://github.com/Geniools/ceh-elastic-stack
cd Directory Name
```

### Configure Cowrie

1. **(Optional)** Change the port number when logging in via SSH **(only if you plan to run Cowrie on the default SSH port: 22)**

```bash
sudo vim /etc/ssh/sshd_config
```

Find the line where `#Port 22` is written, and rewrite it as `Port 22222`

Reload ssh.service to reflect the change

```bash
sudo systemctl reload ssh
```

2. Create the file `cowrie.json` inside the `cowrie/log` directory. Afterwards give it the right permissions.

```bash
sudo touch cowrie.json
sudo chmod o+w cowrie.json
```

### Configure Filebeat

8. Give the right permissions to `filebeat.yml` inside the `filebeat/config` directory.

```bash
sudo chmod go-w filebeat.yml
```

### Configure PyRDP

There are two honeypots meant for RDP connections.

1. 

The first one is runnig on the default port 3389, and requires an external Windows server with RDP enabled (for instance a Windows virtual machine).
Moreover, you will need to create a **.env** file at the root of the project and specify the IP address of the Windows server:

```dotenv
RDP_SERVER_IP=x.x.x.x
```

*Remember to replace with 'x.x.x.x' wit the real IP address of the server*

Afterwards, you can connect to the RDP server by specifying the IP address **of the linux server** running the hoenypot.
 
2. 

The second RDP honeypot will only display the login page of a fake Windows server, and then crash. Stil, some information of the 'attacker' will be logged and saved to elasticsearch.

This honeypot *does* **not** *require* and additional RDP windows server and runs on a custom port *3390*.

To connect to this honeypot, us the IP address of the Linux machine running the hoenypot, after which write the port 3390, such as:

```
x.x.x.x:3390
```

### Build the environment

1. Build and run containers

```bash
docker-compose up
```

You can run the containers as a daemon with the following command:

```bash
docker-compose up -d
```

2. Access Kibana in your browser

You can access Kibana by typing `http://127.0.0.1:5601` in your browser. 


## Test logging and honeypot's reaction

1. Install NMAP to to a quick test attack

```bash
sudo apt install nmap
```

*After all the containers started and kibana is running you can test the logging:*

```bash
sudo nmap -A -T4 0.0.0.0
sudo nmap -sU 0.0.0.0
```

2. Go to **Analytics -> Discover** in order to view the logged data:

Create a new data view for each honeypot *(on the right you'll see "patterns" with the initialls of the honeypot)*. Create one data view for each honeypot.

