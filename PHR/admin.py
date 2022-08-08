from django.contrib import admin
from .models import Patient, User


admin.site.register(User)
admin.site.register(Patient)
# Register your models here.
