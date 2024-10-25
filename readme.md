# Yummypiv Django Project (Restaurant Management)

![Dev](https://img.shields.io/badge/Branch-stable-green) 

![Dev](https://img.shields.io/badge/Version-1.0.0-blue)

## Introduction Project

The Restaurant Management Web App is a software solution designed to help restaurant owners and managers efficiently manage daily operations. 
This application aims to enhance productivity, facilitate monitoring, and improve customer experience. 


## Live server

You can see deployment web on [yummypiv.com](https://yummypiv.com)

## Tools

- Python version 3.12 [download](https://python.org)
    
- Django version 4.2 [download](https://www.djangoproject.com)
    
- Pip version 24.0


# Setup project env and Installation
### Python env
```bash
# clone repository
git clone https://github.com/ipungg-junior/yummypiv.git

# Create python env inside repository
cd yummypiv/
python -m venv env

# activate python env
source penv/bin/activate

# install python package
pip install -r requirements.txt
```

### Project configuration
```bash
# Clone and fill project configuration  (mail server, firebase credentials and etc)
mv root_conf.json.example root_conf.json
nano root_conf.json
```

### Setting up static file and Database migrations
```bash
 # make db migrations
python manage.py makemigrations apps
python manage.py migrate apps
python manage.py migrate

 # collect static
mkdir staticfiles
python manage.py collectstatic
```

## Test and Running Web App

```bash
 # Run django web server on default port 8000
python manage.py runserver 
```

***

## Authors
#### Muhammad Thoyfur | Software Engineer

