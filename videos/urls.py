from . import views
from django.urls import path

urlpatterns = [
    path('course-registration/', views.course_registration, name='course_registration'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('edit-courses/', views.edit_courses, name='edit_courses'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('refresh-videos/<int:course_id>/', views.refresh_course_videos, name='refresh_videos'),
    path('track-progress/', views.track_video_progress, name='track_progress'),
    path('courses/<int:course_id>/topics/', views.course_topics, name='course_topics'),
]
