
# 🚀 Onboardkit

Onboardkit is a Django-based onboarding toolkit built with Celery for asynchronous tasks and Redis as a message broker. It provides robust functionality for building modular, scalable onboarding workflows.

---

## 📁 Project Structure

```
Onboardkit/
├── your_project_name/          # Django project folder (with settings.py)
├── your_app_name/              # Main Django app
├── templates/                  # HTML templates
├── static/                     # Static files (CSS, JS)
├── venv/                       # Virtual environment (excluded from Git)
├── requirements.txt            # Python dependencies
└── manage.py                   # Django management script
```

---

## ⚙️ Tech Stack

- **Backend**: Django 5.2
- **Async Task Queue**: Celery 5.5
- **Message Broker**: Redis 6.2
- **Database**: PostgreSQL (psycopg2)
- **Frontend**: Django Templates + Bootstrap (crispy forms)

---

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Dhruv-Rana-47/Onboardkit.git
cd Onboardkit
```

### 2. Create and Activate a Virtual Environment

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root folder:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://username:password@localhost:5432/onboardkit
REDIS_URL=redis://localhost:6379
```

Use `python-decouple` or `dj-database-url` to load these in `settings.py`.

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

---

## 🧵 Running Celery

Open a new terminal and activate the same virtual environment, then run:

```bash
celery -A your_project_name worker --loglevel=info
```

Make sure Redis server is running locally on port `6379`.

---

## 📝 Features

- 🔄 Asynchronous task handling with Celery
- 🔐 Secure Django authentication
- 🧩 Modular onboarding tasks
- 📋 REST APIs (via Django REST Framework)
- 🌐 CORS support for frontend/backend integration

---

## 🧪 Testing

```bash
python manage.py test
```

---

## 👥 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Author

Made with 💻 by [Dhruv Rana](https://github.com/Dhruv-Rana-47)
