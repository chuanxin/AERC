FROM python:3.13.2-bookworm

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

# for migrations
COPY migrations .
COPY pyproject.toml .

COPY src/ .