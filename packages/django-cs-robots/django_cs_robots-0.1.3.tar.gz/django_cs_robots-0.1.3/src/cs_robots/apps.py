# src/cs_robots/apps.py
from django.apps import AppConfig

class CSRobotsConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cs_robots' 
    verbose_name = 'Robots.txt editor'