from django.apps import AppConfig


class ScrapingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.scraping'
    verbose_name = 'Web Scraping'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.scraping.signals
