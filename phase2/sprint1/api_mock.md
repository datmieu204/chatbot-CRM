Authorization: Bearer <token>
Content-Type: application/json

# 1. Create new Lead
POST /api/v1/Lead

{
    "firstName": "John",
    "lastName": "Doe",
    "emailAddress": "john@example.com",
    "phoneNumber": "+84123456789"
}

# 2. Create new Account

POST /api/v1/Account
{
    "name": "ABC Corp",
    "industry": "Technology",
    "website": "https://abc.com"
}

# 3. Create new Order

POST /api/v1/Order
{
    "orderNumber": "ORD12345",
    "customerId": "abc123",
    "totalAmount": 100.5,
    "currency": "USD"
}

