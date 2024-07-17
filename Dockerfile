FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt install python3-pip python3-dev libpq-dev postgresql-contrib -y && \
    apt-get clean && \
    rm -rf /root/.cache

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# install local packages
RUN pip install -e llm_wrapper

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]