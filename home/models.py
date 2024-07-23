from django.db import models

class File(models.Model):
    original_filename = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    bucket = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    
    def __str__(self):
        return self.original_filename
    
# MONGO DB MODELS

from mongoengine import Document, StringField, URLField

class Query(Document):
    query = StringField(max_length=500)  # Use StringField with a reasonable max_length

class Company(Document):
    name = StringField(max_length=122)
    url = URLField(max_length=122)
