from django.db import models
from django.contrib.auth.models import User

class Field(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='courses', default="null")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)  
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)


    def __str__(self):
        return self.title

class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics', default=1)
    name = models.CharField(max_length=255)
    url = models.URLField()
    is_recommended = models.BooleanField(default=False)
    uploaded = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)  # Added description field
    video_id = models.CharField(max_length=20, blank=True, null=True)  # Store YouTube video ID
    
    def save(self, *args, **kwargs):
        # Extract video_id from URL if not provided
        if not self.video_id and 'youtube.com/embed/' in self.url:
            self.video_id = self.url.split('youtube.com/embed/')[1]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.name}"

class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class VideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    watched_date = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    watch_duration = models.IntegerField(default=0)  # Store seconds watched
    
    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-watched_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"