# ESG Backend Setup

## Prerequisites
- Python 3.9+
- PostgreSQL (or we'll set up in STEP 2)
- pip (Python package manager)

## Initial Setup

### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create .env file
```bash
# Copy the example
cp .env.example .env

# Edit .env with your database credentials
```

### 4. Run Migrations (STEP 3 onwards)
```bash
python manage.py migrate
```

### 5. Create Superuser (admin)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Server will be at: http://localhost:8000

### 7. Access Admin Panel
http://localhost:8000/admin
