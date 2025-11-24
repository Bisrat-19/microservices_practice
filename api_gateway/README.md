# API Gateway Setup

This API Gateway uses Nginx to route requests to microservices and validate JWT tokens.

## Architecture

- **Nginx** acts as the API Gateway
- Validates JWT tokens using `auth_request` module
- Routes requests to appropriate microservices:
  - Auth Service: `localhost:8000`
  - Order Service: `localhost:8001`
  - Notification Service: `localhost:8002`

## Setup Instructions

### Option 1: Using Docker (Recommended)

1. Make sure Docker and Docker Compose are installed

2. Run the services:
```bash
# From the project root directory
docker-compose up -d
```

### Option 2: Manual Setup

1. Install Nginx:
```bash
sudo apt-get update
sudo apt-get install nginx
```

2. Copy the configuration file:
```bash
sudo cp api_gateway/nginx.conf /etc/nginx/sites-available/api_gateway
sudo ln -s /etc/nginx/sites-available/api_gateway /etc/nginx/sites-enabled/
```

3. Remove default Nginx site (optional):
```bash
sudo rm /etc/nginx/sites-enabled/default
```

4. Test Nginx configuration:
```bash
sudo nginx -t
```

5. Start/Restart Nginx:
```bash
sudo systemctl restart nginx
```

## Service Ports

Make sure your Django services are running on these ports:
- **Auth Service**: `8000`
- **Order Service**: `8001`
- **Notification Service**: `8002`
- **API Gateway (Nginx)**: `80`

## API Endpoints

All requests should go through the API Gateway at `http://localhost/api/`

### Public Endpoints (No Auth Required)
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Protected Endpoints (Require JWT Token)
- `GET /api/orders` - List user's orders
- `POST /api/orders` - Create a new order (user_id extracted from JWT)
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order
- `GET /api/notifications` - List user's notifications

## Usage Example

1. Register a user:
```bash
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123", "password2": "testpass123"}'
```

2. Login to get JWT token:
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

3. Create an order (use the access token from login):
```bash
curl -X POST http://localhost/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"product_name": "Laptop", "quantity": 1}'
```

Note: The `user_id` is automatically extracted from the JWT token by the API Gateway and passed to the order service. You don't need to include it in the request body.

## How It Works

1. Client sends request with JWT token in `Authorization` header
2. Nginx intercepts the request and calls `/api/auth/validate` (internal)
3. Auth service validates the JWT token and returns user info in headers
4. Nginx extracts `X-User-ID` and `X-Username` from validation response
5. Nginx forwards the request to the appropriate service with user info in headers
6. Order/Notification service uses the `X-User-ID` header to identify the user

## Troubleshooting

- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
- Check Nginx access logs: `sudo tail -f /var/log/nginx/access.log`
- Verify services are running on correct ports
- Ensure JWT secret keys match between services

