from django.contrib import admin

# Register your models here.
from .models import Person, Publisher, Thesis

admin.site.register(Person)
admin.site.register(Publisher)
admin.site.register(Thesis)