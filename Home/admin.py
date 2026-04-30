from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from.models import *
# Register your models here.

admin.site.register(Specialization)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Feedback)
admin.site.register(Bill)