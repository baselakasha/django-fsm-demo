from django.contrib import admin
from .models import MyUser, BlogPost

admin.site.register(MyUser)
admin.site.register(BlogPost)