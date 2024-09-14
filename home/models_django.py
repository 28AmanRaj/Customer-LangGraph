from django.db import models

class File(models.Model):
    original_filename = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    bucket = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    
    def __str__(self):
        return self.original_filename