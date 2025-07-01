# Virtual Quantum Network (VQN)

This repository contains the codebase and deployment artifacts for a research project on **Software Virtualization and Resource Allocation in Quantum Networks**. The system is designed to efficiently allocate optical switch channels to users in a scalable, distributed, and cloud-native environment, with support for asynchronous processing and notification.

---

## Table of Contents

- [Virtual Quantum Network (VQN)](#virtual-quantum-network-vqn)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [System Architecture](#system-architecture)
  - [Features](#features)
  - [Technology Stack](#technology-stack)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Local Development](#local-development)
    - [Kubernetes Deployment](#kubernetes-deployment)
  - [API Documentation](#api-documentation)
  - [Testing](#testing)
  - [Research Context](#research-context)
  - [Acknowledgements](#acknowledgements)

---

## Overview

This project implements a **cloud-native resource allocation service** for quantum network testbeds. It provides:

- A RESTful API for users to request, view, and manage channel allocations.
- Asynchronous request processing using Redis as a distributed queue.
- Notification via AWS SES when resources are allocated.
- A React-based frontend for user interaction.
- Kubernetes manifests for scalable deployment.

The code and design are intended to support reproducible research and experimentation in quantum networking resource management.

---

## System Architecture

**Components:**

- **Frontend**: React SPA for user signup, login, resource requests, and admin views ([frontend/src](frontend/src)).
- **Backend**: FastAPI application for API endpoints, business logic, and async workers ([backend/](backend/)).
- **Database**: MySQL for persistent storage of users, switches, channels, and requests.
- **Redis**: Used for request queuing and pub/sub notification.
- **Notification**: AWS SES integration for user email notifications ([backend/notification.py](backend/notification.py)).
- **Deployment**: Docker Compose for local development, Kubernetes YAMLs for production.

---

## Features

- **User Management**: Signup, login, and authentication with JWT ([backend/api/auth_api.py](backend/api/auth_api.py)).
- **Resource Allocation**: Request and allocate optical switch channels, with support for prioritization and async processing ([backend/allocation.py](backend/allocation.py)).
- **Admin Views**: View all resources, delete allocations, and add switches.
- **Notifications**: Automatic email notification to users when their request is fulfilled.
- **Scalability**: Designed for horizontal scaling with Kubernetes and Redis-based queuing.
- **Testing**: Pytest-based unit and integration tests ([backend/test/](backend/test/)).

---

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, aioredis, aioboto3, MySQL
- **Frontend**: React, Axios, React Router
- **Queue/Cache**: Redis
- **Notifications**: AWS SES
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Node.js (for frontend)
- AWS SES account (for email notifications)
- Kubernetes cluster (for production deployment)

### Local Development

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/resource-allocation-quantum-networks.git
   cd resource-allocation-quantum-networks
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your AWS credentials.

3. **Start all services:**
   ```sh
   docker-compose up --build
   ```
   - Backend: [http://localhost:8000](http://localhost:8000)
   - Frontend: [http://localhost](http://localhost)

4. **Seed the database (optional for testing):**
   ```sh
   docker exec -it <backend_container_name> python backend/test/seed.py
   ```

### Kubernetes Deployment

1. **Apply manifests:**
   ```sh
   kubectl apply -f mysql-deployment.yaml
   kubectl apply -f redis-deployment.yaml
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f frontend-deployment.yaml
   ```

2. **Set up AWS credentials as Kubernetes secrets for SES.**

---

## API Documentation

The backend exposes a RESTful API. Key endpoints include:

- `POST /api/user/signup` — User registration
- `POST /api/auth/token` — Obtain JWT token
- `GET /api/channel/get/all` — List all channels
- `POST /api/channel/allocate` — Request channel allocation
- `POST /api/switch/create` — Add a new switch

See [backend/api/](backend/api/) for implementation details.

---

## Testing

- **Backend**: Run tests with
  ```sh
  docker exec -it <backend_container_name> pytest backend/test/
  ```
---

## Research Context

This codebase supports experiments and evaluation for the research:

> **"Software Virtualization and Resource Allocation in Quantum Networks"**

The system is designed to be extensible for future research, including:
- Evaluation of different allocation algorithms.
- Integration with real quantum hardware.
- Performance benchmarking (see [locust.py](locust.py) for load testing).

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [AWS SES](https://aws.amazon.com/ses/)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)

---

For questions, contributions, or collaboration, please open an issue or contact the maintainer.
