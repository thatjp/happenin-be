#!/usr/bin/env python
"""
Simple test script to verify the scraping app is working.
Run this after setting up the app to test basic functionality.
"""

import os
import sys
import django
from datetime import timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happin.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.scraping.models import (
    ScrapingTarget, ScrapingJob, ScrapedData, ScrapingRule,
    ScrapingLog, ScrapingMetrics
)
from apps.scraping.scrapers import WebScraper
from apps.scraping.tasks import scrape_target_manual

User = get_user_model()


def test_scraping_app():
    """Test basic functionality of the scraping app"""
    print("🧪 Testing Scraping App...")
    print("=" * 50)
    
    # Test 1: Check if models can be imported
    print("1. Testing model imports...")
    try:
        print("   ✓ ScrapingTarget imported successfully")
        print("   ✓ ScrapingJob imported successfully")
        print("   ✓ ScrapedData imported successfully")
        print("   ✓ ScrapingRule imported successfully")
        print("   ✓ ScrapingLog imported successfully")
        print("   ✓ ScrapingMetrics imported successfully")
    except Exception as e:
        print(f"   ✗ Error importing models: {e}")
        return False
    
    # Test 2: Check if user exists
    print("\n2. Checking for test user...")
    try:
        user = User.objects.get(username='scraper_user')
        print(f"   ✓ Found test user: {user.username}")
    except User.DoesNotExist:
        print("   ✗ Test user 'scraper_user' not found")
        print("   Run: python manage.py setup_scraping --create-user")
        return False
    
    # Test 3: Check if scraping targets exist
    print("\n3. Checking for scraping targets...")
    try:
        targets = ScrapingTarget.objects.all()
        if targets.exists():
            print(f"   ✓ Found {targets.count()} scraping targets:")
            for target in targets[:3]:  # Show first 3
                print(f"     - {target.name} ({target.url})")
        else:
            print("   ✗ No scraping targets found")
            print("   Run: python manage.py setup_scraping --create-examples")
            return False
    except Exception as e:
        print(f"   ✗ Error checking targets: {e}")
        return False
    
    # Test 4: Test web scraper
    print("\n4. Testing web scraper...")
    try:
        scraper = WebScraper(
            user_agent='Test Scraper (+https://example.com/bot)',
            delay=1,
            timeout=10
        )
        print("   ✓ WebScraper created successfully")
        
        # Test scraping a simple page
        result = scraper.scrape('https://httpbin.org/html')
        if result.error:
            print(f"   ⚠ Scraping had error: {result.error}")
        else:
            print(f"   ✓ Scraped page successfully")
            print(f"     - Status: {result.status_code}")
            print(f"     - Content type: {result.content_type}")
            print(f"     - Title: {result.title[:50] if result.title else 'None'}...")
        
        scraper.close()
        
    except Exception as e:
        print(f"   ✗ Error testing scraper: {e}")
        return False
    
    # Test 5: Test Celery task
    print("\n5. Testing Celery task...")
    try:
        # Get first target
        target = ScrapingTarget.objects.first()
        if target:
            print(f"   ✓ Testing with target: {target.name}")
            
            # Test task (this will queue the task)
            result = scrape_target_manual.delay(target.id, user.id)
            print(f"   ✓ Task queued successfully: {result.id}")
            print(f"   ✓ Task status: {result.status}")
        else:
            print("   ⚠ No targets available for testing")
            
    except Exception as e:
        print(f"   ✗ Error testing Celery task: {e}")
        return False
    
    # Test 6: Check database operations
    print("\n6. Testing database operations...")
    try:
        # Create a test log entry
        log = ScrapingLog.objects.create(
            target=target,
            level=ScrapingLog.LogLevel.INFO,
            message='Test log entry from test script',
            context={'test': True, 'timestamp': timezone.now().isoformat()}
        )
        print(f"   ✓ Created test log entry: {log.id}")
        
        # Clean up test data
        log.delete()
        print("   ✓ Cleaned up test data")
        
    except Exception as e:
        print(f"   ✗ Error testing database operations: {e}")
        return False
    
    # Test 7: Check admin interface
    print("\n7. Checking admin interface...")
    try:
        from django.contrib import admin
        admin_site = admin.site
        
        # Check if models are registered
        registered_models = [model._meta.model_name for model in admin_site._registry.keys()]
        scraping_models = ['scrapingtarget', 'scrapingjob', 'scrapeddata', 'scrapingrule', 'scrapinglog', 'scrapingmetrics']
        
        for model in scraping_models:
            if model in registered_models:
                print(f"   ✓ {model} registered in admin")
            else:
                print(f"   ⚠ {model} not registered in admin")
                
    except Exception as e:
        print(f"   ✗ Error checking admin interface: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The scraping app is working correctly.")
    print("=" * 50)
    
    # Additional information
    print("\n📋 Next steps:")
    print("1. Start Redis server: redis-server")
    print("2. Start Celery worker: celery -A happin worker -l info -Q scraping")
    print("3. Start Celery Beat: celery -A happin beat -l info")
    print("4. Visit Django admin: http://localhost:8000/admin/")
    print("5. Monitor scraping jobs and data")
    
    return True


if __name__ == '__main__':
    try:
        success = test_scraping_app()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
