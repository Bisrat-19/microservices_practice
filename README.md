# Microservices E-Commerce System

A distributed microservices application demonstrating authentication, order management, and event-driven notifications using Django, Nginx, RabbitMQ, and Docker.

## Overview

This project implements a microservices architecture where users can register, authenticate, create orders, and receive notifications. The system consists of:

- **API Gateway (Nginx)**: Single entry point with JWT validation
- **Auth Service**: User registration, login, and JWT token management
- **Order Service**: Order creation and management
- **Notification Service**: Stores and retrieves user notifications
- **Notification Consumer**: Background worker processing RabbitMQ events
- **RabbitMQ**: Message broker for asynchronous event processing

When a user creates an order, the order service publishes an event to RabbitMQ, which triggers the notification consumer to create a notification automatically.

## Technology Stack

- Django 5.2 + Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Nginx (API Gateway with auth_request module)
- RabbitMQ 3.13
- Docker & Docker Compose
- Python 3.12

## Setup

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access Points:**
- API Gateway: `http://localhost`
- RabbitMQ Management: `http://localhost:15672` (guest/guest)

### Option 2: Manual Setup

#### 1. Start RabbitMQ

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management-alpine
```

#### 2. Start Django Services

Open 4 separate terminals:

**Terminal 1 - Auth Service:**
```bash
cd auth_service
source venv/bin/activate
python manage.py runserver 8000
```

**Terminal 2 - Order Service:**
```bash
cd order_service
source venv/bin/activate
python manage.py runserver 8001
```

**Terminal 3 - Notification Service:**
```bash
cd notification_service
source venv/bin/activate
python manage.py runserver 8002
```

**Terminal 4 - Notification Consumer:**
```bash
cd notification_service
source venv/bin/activate
python notifications/consumer.py
```

#### 3. Setup API Gateway

**Using Docker:**
```bash
docker run -d --name api_gateway -p 80:80 \
  -v $(pwd)/api_gateway/nginx.local.conf:/etc/nginx/conf.d/default.conf \
  --network host nginx:alpine
```

**Or install Nginx locally:**
```bash
# Install Nginx
sudo apt-get update && sudo apt-get install nginx

# Copy configuration
sudo cp api_gateway/nginx.local.conf /etc/nginx/sites-available/api_gateway
sudo ln -s /etc/nginx/sites-available/api_gateway /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and start
sudo nginx -t
sudo systemctl restart nginx
```

## API Endpoints

### Authentication (Public)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT tokens

### Orders (Protected - Requires JWT)
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Get order details
- `PUT /api/orders/{id}/` - Update order
- `DELETE /api/orders/{id}/` - Delete order

### Notifications (Protected - Requires JWT)
- `GET /api/notifications/` - List user's notifications
- `GET /api/notifications/{id}/` - Get notification details

## Quick Test

```bash
# 1. Register
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"pass123","password2":"pass123"}'

# 2. Login (copy the access token from response)
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'

# 3. Create Order (replace YOUR_TOKEN with access token from step 2)
curl -X POST http://localhost/api/orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Laptop","quantity":2}'

# 4. Get Notifications
curl -X GET http://localhost/api/notifications \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Service Ports

- API Gateway: `80`
- Auth Service: `8000`
- Order Service: `8001`
- Notification Service: `8002`
- RabbitMQ AMQP: `5672`
- RabbitMQ Management: `15672`
