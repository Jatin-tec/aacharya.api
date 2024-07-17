from django.db import models

class Topic(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    addedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-addedAt']

class Video(models.Model):
    videoId = models.CharField(max_length=50)
    transcript = models.TextField()
    description = models.TextField()
    addedAt = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)

    def __str__(self):
        return self.videoId
    
    class Meta:
        ordering = ['-addedAt']