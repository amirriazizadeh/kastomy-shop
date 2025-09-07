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
   git clone <your-repository-url>
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

🐳 Running with Docker

    Build and start the containers

docker-compose up --build

The API will be available at:
👉 http://localhost:8000
⚡ Running Celery

To enable background tasks, you need to run Celery worker and optionally Celery beat:

# Start Celery worker
celery -A core worker -l info

# Start Celery beat (for periodic tasks)
celery -A core beat -l info

If using Docker, these services are already defined in the docker-compose.yml.
📂 Project Structure

shop_backend/
│
├── config/
│
├── core/
│
├── accounts/             
│   ├── models.py         # CustomUser, Profile, Address, OTP
│   └── ...
│
├── products/             
│   ├── models.py         # Product, Category
│   └── ...
│
├── reviews/              
│   ├── models.py         # Review (با GenericForeignKey)
│   └── ...
│
├── cart/
│   └── ...
│
├── orders/
│   └── ...
│
├── store/
│   └── ...
│
├── manage.py
└── requirements.txt

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