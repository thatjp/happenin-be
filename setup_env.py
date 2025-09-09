#!/usr/bin/env python3
"""
Setup script to create .env file from template
"""
import os
import shutil

def setup_environment():
    """Create .env file from template if it doesn't exist"""
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    if os.path.exists('env_template.txt'):
        shutil.copy('env_template.txt', '.env')
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your actual values")
    else:
        print("❌ env_template.txt not found")
        return
    
    print("\n🔧 Next steps:")
    print("1. Edit .env file with your actual Twilio credentials")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python manage.py runserver")

if __name__ == "__main__":
    setup_environment()
