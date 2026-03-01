from django.contrib import admin
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'upload_date']
    list_filter = ['upload_date', 'owner']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['upload_date']
    ordering = ['name']
