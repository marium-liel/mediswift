#!/usr/bin/env python3
"""
Setup script for Medicine & Supplement Ordering Platform
Run this script to set up the development environment quickly
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running: {command}")
        print(f"Error: {e.stderr}")
        return None

def setup_backend():
    """Set up Django backend"""
    print("\n🔧 Setting up Django Backend...")
    
    backend_dir = "backend"
    
    # Create virtual environment
    print("Creating virtual environment...")
    run_command("python -m venv venv", cwd=backend_dir)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
        venv_pip = os.path.join(backend_dir, "venv", "Scripts", "pip.exe")
    else:  # Linux/Mac
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
        venv_pip = os.path.join(backend_dir, "venv", "bin", "pip")
    
    print("Installing Python dependencies...")
    run_command(f"{venv_pip} install -r requirements.txt", cwd=backend_dir)
    
    # Create .env file if it doesn't exist
    env_file = os.path.join(backend_dir, ".env")
    if not os.path.exists(env_file):
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("SECRET_KEY=django-insecure-development-key-change-in-production\n")
            f.write("DEBUG=True\n")
            f.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
    
    # Run migrations
    print("Running database migrations...")
    run_command(f"{venv_python} manage.py makemigrations", cwd=backend_dir)
    run_command(f"{venv_python} manage.py migrate", cwd=backend_dir)
    
    # Create superuser (optional)
    print("\n📝 To create an admin user, run:")
    print(f"cd {backend_dir}")
    if os.name == 'nt':
        print("venv\\Scripts\\activate")
    else:
        print("source venv/bin/activate")
    print("python manage.py createsuperuser")
    
    print("✅ Backend setup complete!")

def setup_frontend():
    """Set up React frontend"""
    print("\n⚛️ Setting up React Frontend...")
    
    frontend_dir = "frontend"
    
    # Check if Node.js is installed
    try:
        run_command("node --version")
        run_command("npm --version")
    except:
        print("❌ Node.js and npm are required but not found.")
        print("Please install Node.js from https://nodejs.org/")
        return False
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    print("✅ Frontend setup complete!")
    return True

def create_sample_data():
    """Create sample data for testing"""
    print("\n📊 Creating sample data...")
    
    backend_dir = "backend"
    if os.name == 'nt':
        venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
    
    # Create a simple data creation script
    sample_data_script = f"""
import os
import django
import sys

sys.path.append('{os.path.abspath(backend_dir)}')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_platform.settings')
django.setup()

from products.models import Category, Product
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()

# Create categories
categories = [
    {{'name': 'Pain Relief', 'description': 'Medicines for pain management'}},
    {{'name': 'Vitamins', 'description': 'Essential vitamins and minerals'}},
    {{'name': 'Antibiotics', 'description': 'Prescription antibiotics'}},
    {{'name': 'Supplements', 'description': 'Health supplements'}},
]

for cat_data in categories:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={{'description': cat_data['description']}}
    )
    if created:
        print(f"Created category: {{category.name}}")

# Create sample products
pain_relief = Category.objects.get(name='Pain Relief')
vitamins = Category.objects.get(name='Vitamins')

products = [
    {{
        'name': 'Paracetamol 500mg',
        'brand': 'MediSwift',
        'category': pain_relief,
        'product_type': 'medicine',
        'description': 'Effective pain relief and fever reducer',
        'dosage': '1-2 tablets every 4-6 hours',
        'precautions': 'Do not exceed 8 tablets in 24 hours',
        'price': 5.99,
        'stock_quantity': 100,
        'expiry_date': date.today() + timedelta(days=365),
        'requires_prescription': False
    }},
    {{
        'name': 'Vitamin D3 1000IU',
        'brand': 'HealthPlus',
        'category': vitamins,
        'product_type': 'supplement',
        'description': 'Essential vitamin D3 supplement',
        'dosage': '1 tablet daily with food',
        'precautions': 'Consult doctor if pregnant or nursing',
        'price': 12.99,
        'stock_quantity': 50,
        'expiry_date': date.today() + timedelta(days=730),
        'requires_prescription': False
    }},
]

for prod_data in products:
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        brand=prod_data['brand'],
        defaults=prod_data
    )
    if created:
        print(f"Created product: {{product.name}}")

print("Sample data created successfully!")
"""
    
    # Write and execute the sample data script
    script_path = os.path.join(backend_dir, "create_sample_data.py")
    with open(script_path, 'w') as f:
        f.write(sample_data_script)
    
    run_command(f"{venv_python} create_sample_data.py", cwd=backend_dir)
    
    # Clean up
    os.remove(script_path)
    
    print("✅ Sample data created!")

def main():
    """Main setup function"""
    print("🏥 Medicine & Supplement Ordering Platform Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the Medicine project root directory")
        sys.exit(1)
    
    # Setup backend
    setup_backend()
    
    # Setup frontend
    if not setup_frontend():
        return
    
    # Create sample data
    create_sample_data()
    
    print("\n🎉 Setup Complete!")
    print("\nTo start the development servers:")
    print("\n📱 Frontend (React):")
    print("cd frontend")
    print("npm start")
    print("\n🔧 Backend (Django):")
    print("cd backend")
    if os.name == 'nt':
        print("venv\\Scripts\\activate")
    else:
        print("source venv/bin/activate")
    print("python manage.py runserver")
    
    print("\n🌐 Access the application:")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:8000")
    print("Admin Panel: http://localhost:8000/admin")
    
    print("\n📚 Check README.md for detailed documentation!")

if __name__ == "__main__":
    main()
