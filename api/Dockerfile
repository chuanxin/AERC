# pull official base image
FROM python:3.13.3-alpine

# set work directory
RUN mkdir app
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

# install system dependencies for compiling packages
RUN apk add --no-cache \
    build-base \
    linux-headers \
    clang-dev \
    fontconfig \
    ttf-dejavu \
    wqy-zenhei

# copy requirements files
COPY requirements.txt .
COPY requirements-dev.txt .

# install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r requirements-dev.txt \
    && rm -rf /root/.cache/pip

# for migrations
COPY migrations .
COPY pyproject.toml .

# copy project
COPY src/ .