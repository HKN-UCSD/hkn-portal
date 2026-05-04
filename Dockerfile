FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /hkn-portal

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Node and build frontend
RUN apt-get update && apt-get install -y nodejs npm
COPY frontend/package.json frontend/
RUN cd frontend && npm install
COPY frontend/ frontend/
RUN cd frontend && npm run build

COPY . .