# Microservices Project - Quick Start Guide

## Prerequisites
- Python 3.12+
- Nginx (for API Gateway)
- RabbitMQ (for message broker)
- Docker & Docker Compose (optional, for containerized setup)

## Local Development Setup

### 1. Start RabbitMQ
```bash
# Using Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management-alpine

# Or install locally and start the service
```

### 2. Start Django Services

Open 4 terminal windows:

**Terminal 1 - Auth Service:**
```bash
cd auth_service
source venv/bin/activate  # or use your virtual environment
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
# Or run from project root:
# python -m notification_service.notifications.consumer
```

### 3. Setup Nginx API Gateway (ONE-TIME SETUP)

**IMPORTANT:** You can do this in ANY terminal (doesn't need to be a new one). Nginx runs as a background service, so after setup, it keeps running automatically.

**Option A: Using Docker (Easiest - Recommended)**

Open a terminal (can be any terminal, even one you're already using) and run:

```bash
# Navigate to project root if not already there
cd ~/Projects/microservices_project

# Run Nginx in Docker (runs in background)
docker run -d \
  --name api_gateway \
  -p 80:80 \
  -v $(pwd)/api_gateway/nginx.conf:/etc/nginx/conf.d/default.conf \
  --network host \
  nginx:alpine

# Verify it's running
docker ps | grep api_gateway
```

That's it! Nginx is now running. You can close this terminal - Nginx will keep running.

**Option B: Manual Setup (Install Nginx on your system)**

Open a terminal and run these commands ONE TIME:

```bash
# 1. Install Nginx
sudo apt-get update
sudo apt-get install nginx

# 2. Navigate to project root
cd ~/Projects/microservices_project

# 3. Copy configuration file
sudo cp api_gateway/nginx.local.conf /etc/nginx/sites-available/api_gateway

# 4. Enable the site
sudo ln -s /etc/nginx/sites-available/api_gateway /etc/nginx/sites-enabled/

# 5. Remove default site (optional, but recommended)
sudo rm /etc/nginx/sites-enabled/default

# 6. Test configuration (make sure no errors)
sudo nginx -t

# 7. Start Nginx (runs in background)
sudo systemctl restart nginx

# 8. Check if Nginx is running
sudo systemctl status nginx
```

**After setup:** Nginx runs automatically in the background. You don't need to keep the terminal open. It will start automatically when you reboot your computer too.

**To stop Nginx later (if needed):**
- Docker: `docker stop api_gateway`
- Manual: `sudo systemctl stop nginx`

**To start Nginx again:**
- Docker: `docker start api_gateway`
- Manual: `sudo systemctl start nginx`

## Testing the API Gateway

### 1. Register a User
```bash
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

### 2. Login and Get JWT Token
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Response will include `access` and `refresh` tokens. Copy the `access` token.

### 3. Create an Order (with JWT)
```bash
curl -X POST http://localhost/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "product_name": "Laptop",
    "quantity": 1
  }'
```

**Note:** The `user_id` is automatically extracted from the JWT token by the API Gateway. You don't need to include it in the request.

### 4. Get User's Orders
```bash
curl -X GET http://localhost/api/orders \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 5. Get User's Notifications
```bash
curl -X GET http://localhost/api/notifications \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Using Docker Compose (All-in-One)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture Flow

1. **Client** → API Gateway (Nginx) with JWT token
2. **API Gateway** → Validates JWT via Auth Service `/users/validate/`
3. **API Gateway** → Extracts `user_id` from validated JWT
4. **API Gateway** → Forwards request to Order/Notification Service with `X-User-ID` header
5. **Order Service** → Creates order with `user_id` from header
6. **Order Service** → Publishes event to RabbitMQ
7. **Notification Consumer** → Listens to RabbitMQ and creates notification

## Troubleshooting

- **Nginx 502 Bad Gateway**: Check if Django services are running on correct ports
- **401 Unauthorized**: Verify JWT token is valid and not expired
- **No notifications**: Ensure RabbitMQ is running and notification consumer is active
- **Connection refused**: Check service ports and firewall settings

## Service Ports

- API Gateway (Nginx): `80`
- Auth Service: `8000`
- Order Service: `8001`
- Notification Service: `8002`
- RabbitMQ: `5672` (AMQP), `15672` (Management UI)

