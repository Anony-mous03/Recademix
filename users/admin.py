from django.contrib import admin
from .models import ContactForm

admin.site.site_header = "RecademiX"
# Register your models here.
class ContactFormAdmin(admin.ModelAdmin):
   list_display = ('name', 'email', 'message')
admin.site.register(ContactForm, ContactFormAdmin)
