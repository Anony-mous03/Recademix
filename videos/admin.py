from django.contrib import admin
from .models import Course, UserCourse, Topic, Field, VideoProgress
# Register your models here.
admin.site.site_header = "RecademiX"
class Courseslist(admin.ModelAdmin):
    list_display = ("title", "field", "created_at", "description", "image")
admin.site.register(Course, Courseslist)
class Userlist(admin.ModelAdmin):
    list_display = ("user", "course")
admin.site.register(UserCourse, Userlist)
class Topiclist(admin.ModelAdmin):
    list_display = ("course", "name", "url", "is_recommended", "uploaded", "description", "video_id")
admin.site.register(Topic, Topiclist)
class Fieldlist(admin.ModelAdmin):
    list_display = ("name", "description")
admin.site.register(Field, Fieldlist)
admin.site.register(VideoProgress)


