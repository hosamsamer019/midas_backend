"""Core app configuration."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Data Processing Layer'
    
    def ready(self):
        """
        Initialize the core app.
        This method is called when Django starts.
        """
        # Import signals or perform initialization here if needed
        pass
