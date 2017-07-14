<div align="center">

  <br />

  <a align="center" href=""> <img height="300" width="500" src="https://user-images.githubusercontent.com/18141485/28209680-78d39b40-688b-11e7-983b-be5b76c897a2.gif" alt="A Feedback-driven GUI master/actuator orchestration framework for the OpenC2 language, written in Python. Works in remote security management. Loves to travel. Enjoys meeting new people. Good listener."/>

  <h1 align="center">Reactor Relay</h1>

  <strong>A Feedback-driven GUI master / actuator orchestration framework for the OpenC2 language, written in Python</strong>
  
</div>

<br />

<div align="center">
  <a href=""> <img src="https://img.shields.io/badge/python-2.7-blue.svg?style=flat-square" alt="python versions" />
  </a>
  <!-- Stage -->
  <a href=""> <img src="https://img.shields.io/badge/stage-dev-yellow.svg?style=flat-square" alt="build stage" />
  </a>
</div>    

---

## Foreword

This project is proof of concept code to show how OpenC2 can be deployed on geographically disparate networks. Please report bugs via git issues, pull requests are welcome.


## History

This project is built on top of OrchID's code base: 

[OrchID](https://github.com/OpenC2-org/OrchID) is an OpenC2 proxy built in [Django](https://www.djangoproject.com/) 1.10.2. OrchID aims to provide a simple, modular API to begin accepting OpenC2 commands and converting them into Python actions.

OpenC2 OrchID was built by [Adam Bradbury](#creator) (Zepko Architect), so is used extensively in Zepko's response architecture. This document explains the usage for the onboarded profiles for this version of OrchID, for general documentation on how OrchID functions you should refer to the official [repository](https://github.com/OpenC2-org/OrchID).


## Purpose

This codebase provides a modified version of OrchID that can be administrated by non-technical staff. It allows the end user to link profile code, to OpenC2 commands and actuators, and handles credential storage.

The relay is called by an upstream Orchestrator (See [ReactorMaster](https://github.com/OpenC2-org/ReactorMaster)), the idea is, that an MSSP has multiple sites and clients, with different capabilities and network layouts, buy allowing engineers to create a topology of "Relays" commands can be routed to multiple sites from a central server, without the need for that central server to connect into each actuator directly. _(e.g. Remoting in as root to a webserver from the internet)._

Relays provide a way for us to define specific use cases and actuators per client, and provide a secure ip-locked TLS channel to execute those actions.


## Installation _(CentOS 7.3)_

### 1. Install dependencies 

    ```shell
    yum install -y git wget python-pip python-devel gcc mariadb mariadb-server mariadb-devel MySQL-python libffi-devel
    ```

### 2. Configure the database 

```shell
systemctl status mariadb.service
systemctl start mariadb.service
systemctl enable mariadb.service

mysql_secure_installation
  ```

  ```shell
  
  NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
        SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!
  
  In order to log into MariaDB to secure it, we'll need the current
  password for the root user.  If you've just installed MariaDB, and
  you haven't set the root password yet, the password will be blank,
  so you should just press enter here.
  
  Enter current password for root (enter for none):
  ```
> Press enter for first time installs

  ```shell
  Change the root password? [Y/n]
  ```
> It's recommended that you set a strong password for the root account
> By default the password for Reactor is `correcthorsebatterystaple`

  ```shell
  Remove anonymous users? [Y/n]
  ```
> It is recommended that all anonymous remote logins be disabled

  ```shell
  Disallow root login remotely? [Y/n]
  ```
> It is recommended that the root account only login from `localhost`

  ```shell
  Remove test database and access to it? [Y/n]
  ```
> It is recommended that the test database is removed for security

  ```shell
  Reload privilege tables now? [Y/n]
  ```
> Choose Y to apply the new settings

  ```shell
  Cleaning up...
  
  All done!  If you've completed all of the above steps, your MariaDB
  installation should now be secure.
  
  Thanks for using MariaDB!
  ```

### 3. Configure the firewall _(`firewall-cmd` on CentOS 7.3)_

> Either create port rules for the necessary ports required by Reactor, or disable the firewall altogether *(not recommended)*

##### _(Optional)_ Disable firewall

```shell
systemctl stop firewall-cmd
systemctl disable firewall-cmd
```

##### Enable firewall

```shell
firewall-cmd --state
running
```

```
systemctl status firewall-cmd
systemctl start firewall-cmd
systemctl enable firewall-cmd
```

##### Create firewall port rules

```shell
firewall-cmd --add-port=8000/tcp --zone=public --permanent   # ReactorRelay

firewall-cmd --reload
```

### 4. Configure the project environment(s)  

```shell
git clone https://User:Token@github.com/User/ReactorRelay.git
```

> OR...

```shell
git clone https://github.com/User/ReactorRelay.git

Enter username and password...
```

##### Familiarise yourself with the code base. If you're familiar with Django projects then this will be very familiar.
  
  ```shell
  cd ReactorRelay && ls
  
  LICENSE  main  manage.py  reactor_relay  README.md  requirements.txt  samples  static
  ```

##### Upgrade pip

```shell
pip install --upgrade pip
```

##### Install *virtualenv* package

```shell
pip install virtualenv
```

##### Create a new virtual environment

> If you are testing both ReactorRelay and ReactorMaster on the same system, you can use one virtual environment for both

```shell
virtualenv env/ -p python --prompt="[ReactorRelay]"
```

##### Activate virtual environment

```shell
source env/bin/activate
```

##### Deactivate virtual environment

```shell
deactivate
```

### 5. Set up the application (must be in virtual environment) 

##### Install dependencies

```shell
pip install -r requirements.txt
```

##### Configure Django

> For database migrations, you may need to first create the schema specified on line 90 in `main/settings.py`

```shell
mysql -uroot -p   # provide password when prompted
```

```mysql
MariaDB [(none)]> show schemas;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
3 rows in set (0.00 sec)

create schema reactor_relay;
Query OK, 1 row affected (0.00 sec)

MariaDB [(none)]> show schemas;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| reactor_relay      |
+--------------------+
4 rows in set (0.00 sec)

exit
Bye
```

##### Update database to latest schema

```shell
python manage.py migrate   # configures database according to models and previous migrations

Operations to perform:
  Apply all migrations: admin, auth, contenttypes, reactor_relay, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying reactor_relay.0001_initial... OK
  Applying sessions.0001_initial... OK
```

##### Load the starting data into the database

```shell
python manage.py loaddata reactor_relay/fixtures/initial_data.json
```

##### Create a superuser to manage the project

```shell
python manage.py createsuperuser
```

##### Launch the server

```shell
python manage.py runserver 0.0.0.0:8000   # relay
```

> Now check that you can visit it in the browser, and login as the super-user you created.

The relay's web interface is accessible on:

`http://<ip_addr>:8000/`

It's OpenC2 API is accessible on:

`http://<ip_addr>:8000/openc2/`

<div align="center">
  <a><img alt="ReactorRelay fresh dashboard" src="https://user-images.githubusercontent.com/18141485/28184970-749a5434-680d-11e7-9d7a-bed296e5895f.PNG"/>
  </a>
</div>

> It is recommended you put this behind an SSL reverse proxy such as [NGINX](http://hg.nginx.org/nginx/) as commands can contain sensitive information, and connections to this box should be IP locked to known and trusted upstream orchestrators.

---

## Usage

### [ReactorRelay](https://github.com/OpenC2-org/ReactorRelay)   -   `:8000`

##### Actuator Creation

The first step is to define the actuators you need this relay to control. Credentials can be specified if you need them in your code profiles. (Example: SSH login credentials)

<div align="center">
  <a><img alt="ReactorRelay create actuator" src="https://user-images.githubusercontent.com/18141485/28185075-e1b79004-680d-11e7-8c4d-80d56918b015.PNG"/>
  </a>

  <a><img alt="ReactorRelay actuator created" height="300" width="800" src="https://user-images.githubusercontent.com/18141485/28185107-ff8d712a-680d-11e7-97e3-a826f86d3b9e.PNG"/>
  </a>
</div>

##### Profile Creation

Some example profiles are found in `./reactor_relay/profiles` - these are the code that translates OpenC2 code into vendor commands specific to your estate.

This relay has three really simple profiles to get you started, if you are running this code on a linux machine, they should all work:

##### `address_ping.py`

  This uses a local ping executable to ping a target address. `action:SCAN,actuator:process-network-scanner,target:cybox:Address`

##### `address_drop_ips.py`

  This connects to a remote linux machine via SSH and executes an iptables command to drop an IP address, the revoke code is also in this profile aswell. `action:DENY/ALLOW,actuator:network-ips,target:cybox:Address`

##### `address_whois.py`

  This uses a local whois executable to perform a whois query for an IP. `action:QUERY,actuator:process,target:cybox:Address`

##### Capability Creation

Capabilities are what the relay will disclose to the upstream orchestrator. Capabilities link an Acutuator and code profile, and specify what type of target it requires to execute e.g: `Cybox:NetworkConnection`

<div align="center">
  <a><img alt="ReactorRelay create capability" src="https://user-images.githubusercontent.com/18141485/28185174-401ffdde-680e-11e7-8eac-f93a644899ed.PNG"/>
  </a>

  <a><img alt="ReactorRelay capability created" height="150" width="800" src="https://user-images.githubusercontent.com/18141485/28185176-42cc5758-680e-11e7-9fc0-e95e26d1bba4.PNG"/>
  </a>
</div>

Once this is done, you must configure the Master and sync each relay's capabilities.

<div align="center">
  <a><img alt="ReactorRelay capabilities synced" src="https://user-images.githubusercontent.com/18141485/28039086-f320e8ce-65b8-11e7-8906-8ca7cb5c9582.PNG"/>
  </a>
</div>

Follow the documentation for [ReactorMaster](https://github.com/OpenC2-org/ReactorMaster) until you are ready to send jobs.

##### Job Execution

The relay shows the details for jobs it has received from its master along with their status. Once a job is complete, the relay will send the outcome back to the master.

If the master does not appear to be receiving responses for jobs it has requested, check the relays themselves to determine whether the jobs are succeeding locally or not.

<div align="center">
  <a><img alt="ReactorRelay job results" src="https://user-images.githubusercontent.com/18141485/28185312-c56ec2cc-680e-11e7-83c6-a89fba9c5bae.PNG"/>
  </a>
</div>

---

### Creator

<div align="center">
  <p style="color:blue;font-size:28px;"><strong>Adam Bradbury</strong></p>
  </br>
</div>
<div align="center">
  <a href="https://github.com/AdamTheAnalyst"> <img alt="AdamTheAnalyst" height="50" width="50" src="https://user-images.githubusercontent.com/18141485/28211297-cac67320-6893-11e7-98ae-5c0825229fe5.png"/>
  </a>
  <a href="https://twitter.com/adamtheanalyst"> <img alt="AdamTheAnalyst" height="50" width="50" src="https://user-images.githubusercontent.com/18141485/28211298-cac99276-6893-11e7-818f-3f7873b5d09a.png"/>
  </a>
</div>

---

## Appendices

### Reactor and OpenC2 architectural overview

```
    ┌────────┐              ┌───────┐            ┌──────────┐
    | Master ├─ manages a ─→| Relay ├─ has an ──→| Actuator |
    └─┬────┬─┘              └───────┘            └────┬─────┘
      |    |                                          |
      |    └──── defines                           can use
      |             |                                 |
  specifies         ↓                                 ↓
      |          ┌─────┐                        ┌────────────┐
      |          | Job |←───────── used by  ────┤ Capability │
      |          └──┬──┘                        └────────────┘
      ↓             |
  ┌────────┐      targets
  │ Target |←───────┘
  └────────┘
```

### Reactor project deployment file overview

```shell
.
├── LICENSE
├── README.md
├── main
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── reactor_relay
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── fixtures
│   │   └── initial_data.json
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── profiles
│   │   ├── __init__.py
│   │   ├── address_drop_ips.py
│   │   ├── address_ping.py
│   │   ├── email_send_office365_email.py
│   │   ├── response.py
│   │   └── uri_virustotal_lookup.py
│   ├── response.py
│   ├── templates
│   │   └── reactor_relay
│   ├── tests.py
│   ├── validators.py
│   └── views.py
├── requirements.txt
├── samples
│   └── response_ack.json
└── static
    └── theme
        ├── css
        ├── font-awesome
        ├── fonts
        └── js
```


<br/>

<a href="#top">↥ back to top</a>


---

<div align="center">
  <h3 align="center">License</h3>
  <!-- MIT License -->
  <a href=""> <img src="https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square" alt="MIT License" />
  </a>
</div>
