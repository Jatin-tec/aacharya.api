from django.db import models
from authentication.models import User

class Topic(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='topics')
    category = models.CharField(max_length=50)
    category_id = models.IntegerField()
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    addedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Topic: {self.category} - {self.username} - {self.video.videoId}'

    class Meta:
        ordering = ['-addedAt']

class Video(models.Model):
    videoId = models.CharField(max_length=50)
    transcript = models.TextField()
    description = models.TextField()
    addedAt = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    visual_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.videoId
    
    class Meta:
        ordering = ['-addedAt']
        
class Conversation(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    videoId = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='conversations')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f'Conversation: {self.videoId} - {self.username}'
    
class Note(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    videoId = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='notes')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    notes = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'Note: {self.videoId} - {self.username}'
