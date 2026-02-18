FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /hkn-portal

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .