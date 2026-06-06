# Brim Project Setup Guide

Complete setup for Brim network with Django backend, Tailwind CSS frontend, and Rust integration via PyO3.

---

## Phase 1: Django Backend Setup

### 1. Initialize Project
```bash
mkdir brim && cd brim
```

### 2. Create Virtual Environment
```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install django djangorestframework
```

### 4. Create Django Project
```bash
django-admin startproject brim .
```

### 5. Create Django App
```bash
python manage.py startapp brimapi
```

### 6. Configure Django Settings

Edit `brim/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'brimapi',
]
```

### 7. Run Migrations
```bash
python manage.py makemigrations brimapi
python manage.py migrate
```

---

## Phase 2: Frontend Setup (Tailwind CSS)

### 1. Initialize Frontend Directory
```bash
mkdir frontend && cd frontend
npm init -y
```

### 2. Install Tailwind CSS
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. Configure Tailwind

Create `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../brimapi/templates/**/*.html",
    "./src/**/*.{html,js}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Create `src/input.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. Build CSS
```bash
npx tailwindcss -i ./src/input.css -o ./dist/output.css --watch
```

---

## Phase 3: Django Templates

### 1. Create Base Template

mkdir -p brimapi/templates/brimapi
touch brimapi/templates/brimapi/base.html
# Add this content to brimapi/templates/brimapi/base.html:
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Brim Network{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. Configure Static Files

In `brim/settings.py`:
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'dist',
]
```

---

## Phase 4: Rust Integration (PyO3)

### 1. Create Rust Library

From project root:
```bash
cargo new --lib rust-ext
cd rust-ext
```

### 2. Configure Cargo.toml

Edit `rust-ext/Cargo.toml`:
```toml
[package]
name = "rust-ext"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_ext"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.24", features = ["extension-module"] }
```

### 3. Write Rust Code

Edit `rust-ext/src/lib.rs`:
```rust
use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_ext(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
```

### 4. Create pyproject.toml

Create `rust-ext/pyproject.toml`:
```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "rust-ext"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Rust",
    "Programming Language :: Python :: Implementation :: CPython",
]
```

### 5. Build and Install Rust Package

```bash
# Install maturin
pip install maturin

# Build the Rust extension
maturin develop

# Or build wheel for distribution
maturin build
```

---

## Phase 5: Python Bridge Script

Create `brimbridge.py` in project root:
```python
import rust_ext

# Test the Rust function
result = rust_ext.sum_as_string(5, 7)
print(f"Result from Rust: {result}")
```

Run it:
```bash
python brimbridge.py
```

---

## Phase 6: Integration with Existing Brim Node

### 1. Link Existing Rust Node

Create a symlink or update `Cargo.toml` to reference your existing rust-node:

```bash
ln -s /Users/theredferret03/brim/rust-node rust-ext/src/core
```

Or in `rust-ext/Cargo.toml`:
```toml
[dependencies]
brim-veracity = { path = "../rust-node" }
```

### 2. Create PyO3 Wrappers for Existing Code

Add to `rust-ext/src/lib.rs`:
```rust
use pyo3::prelude::*;
use brim_veracity::User;

#[pyfunction]
fn create_user(username: String, password: String) -> PyResult<String> {
    // Wrapper for existing User creation
    Ok(format!("User {} created", username))
}

#[pymodule]
fn rust_ext(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_user, m)?)?;
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
```

---

## Quick Start Commands

```bash
# 1. Setup everything
cd /Users/theredferret03/brim
source venv/bin/activate

# 2. Run Django server
python manage.py runserver

# 3. In another terminal, build Tailwind
cd frontend && npx tailwindcss -i ./src/input.css -o ./dist/output.css --watch

# 4. Rebuild Rust extension (when needed)
cd rust-ext && maturin develop

# 5. Run the bridge
python brimbridge.py
```

---

## Directory Structure

```
brim/
├── venv/                          # Python virtual environment
├── brim/                          # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── brimapi/                       # Django REST API app
│   ├── migrations/
│   ├── templates/brimapi/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── frontend/                      # Tailwind CSS frontend
│   ├── src/
│   │   ├── input.css
│   │   └── index.html
│   ├── dist/
│   └── tailwind.config.js
├── rust-ext/                      # PyO3 Rust extension
│   ├── src/
│   │   └── lib.rs
│   ├── Cargo.toml
│   └── pyproject.toml
├── rust-node/                     # Existing Brim Rust node
│   └── ...
├── python-node/                   # Existing Python CLI
│   └── ...
├── brimbridge.py                  # Python-Rust bridge script
└── manage.py                      # Django management
```

---

## Troubleshooting

### Issue: `cargo` not found
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### Issue: `rust_ext` module not found
```bash
cd rust-ext
maturin develop --release
```

### Issue: Tailwind styles not updating
Make sure the watch command is running:
```bash
npx tailwindcss -i ./src/input.css -o ./dist/output.css --watch
```

### Issue: Django static files not serving
```bash
python manage.py collectstatic
```

---

## Next Steps

1. ✅ Set up Django backend with REST API
2. ✅ Configure Tailwind CSS frontend
3. ✅ Integrate existing Rust node via PyO3
4. 🔄 Create API endpoints for Brim network operations
5. 🔄 Build frontend UI for user/claims management
6. 🔄 Connect Python CLI to Django backend
