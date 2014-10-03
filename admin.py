from django.contrib import admin
from django.conf import settings

# Autoload
# !!! NOTE : Let's check in settings to be sure we want this behavoir
from django.db.models import get_models, get_app
from django.contrib.admin.sites import AlreadyRegistered
 
from simple_history.admin import SimpleHistoryAdmin
 
def autoregister(*app_list):
    
    # Register All Models In Each App
    for app_name in app_list:
        app_models = get_app(app_name)
        for model in get_models(app_models):
            
            try:
                # Register The Model
                admin.site.register(model,SimpleHistoryAdmin)
            except AlreadyRegistered:
                pass

# Run the Register
autoregister(*settings.REST_EASY_APPS)
