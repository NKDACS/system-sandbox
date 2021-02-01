from django.contrib import admin
from django.conf import settings

class MyAdminSite(admin.AdminSite):
    site_url = '/'
    if not settings.DEBUG:
        site_url = settings.PRODUCTION_URL_PREFIX + site_url
