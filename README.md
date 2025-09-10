# 🛍️ Kastomy Shop - Backend API

This repository contains the **official Django backend API** for the Kastomy Shop application.  
It provides all the necessary endpoints to support the frontend, including authentication, product management, and order handling.

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally for development or testing.

---

### ✅ Prerequisites

Make sure you have the following installed:

- **Python** 3.8+
- **pip** (Python package manager)
- **Django** & **Django REST Framework**
- **Celery**
- **Docker** & **Docker Compose**
- **Git**

---

### ⚙️ Installation & Running Locally

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kastomy-shop-backend

    Create and activate a virtual environment

python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows

Install dependencies

pip install -r requirements.txt

Apply migrations

python manage.py migrate

Run the development server

    python manage.py runserver

🌍 Environment Variables

Create a .env file in the project root with the following keys (example values provided):

# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/shop_db

# Celery / Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# JWT
JWT_SECRET=your-jwt-secret
JWT_ACCESS_EXP=3600
JWT_REFRESH_EXP=86400

    ⚠️ Make sure .env is listed in your .gitignore file so sensitive data is not committed.

🐳 Running with Docker

Build and start the containers

docker-compose up --build

The API will be available at:
👉 http://localhost:8000
⚡ Running Celery

To enable background tasks, run Celery worker and optionally Celery beat:

# Start Celery worker
celery -A core worker -l info

# Start Celery beat (for periodic tasks)
celery -A core beat -l info

If using Docker, these services are already defined in the docker-compose.yml.
🧪 Running Tests

To run the test suite:

# Using Django's test runner
python manage.py test

# Or if pytest is installed
pytest




## 📂 Project Structure


```plaintext
castomy-shop/
│
├── accounts/        → ثبت‌نام، لاگین، OTP، JWT، مدیریت احراز هویت
├── adminpanel/      → API مخصوص پنل مدیریت (مدیرکل پلتفرم)
├── cart/            → مدیریت سبد خرید کاربران
├── categories/      → دسته‌بندی محصولات (درختی، چند سطحی)
├── core/            → مدل پایه (BaseModel)، Soft Delete، ابزارهای مشترک
├── orders/          → سفارش‌ها، وضعیت سفارش، مدیریت فاکتورها
├── payments/        → درگاه پرداخت، تراکنش‌ها، کیف پول احتمالی
├── products/        → محصولات، ویژگی‌ها، تنوع محصول (variation)
├── reviews/         → نظرات و امتیاز کاربران روی محصولات/فروشنده‌ها
├── stores/          → اطلاعات فروشندگان و فروشگاه‌ها
├── users/           → پروفایل کاربر، آدرس‌ها، نقش‌ها (مشتری/فروشنده)
│
├── config/         → تنظیمات اصلی پروژه (settings, urls, wsgi, asgi)
└── manage.py
```


📌 Features

    🔐 User authentication (JWT)

    🛒 Product & order management

    📦 RESTful API endpoints

    ⚡ Celery for async tasks

    🐳 Dockerized for easy setup

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
📜 License

This project is licensed under the MIT License