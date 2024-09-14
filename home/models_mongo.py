# MONGO DB MODELS
from mongoengine import Document, StringField, URLField

class Query(Document):
    query = StringField(max_length=500)  # Use StringField with a reasonable max_length
    thread_id = StringField(max_length=36)  # Store thread ID
class Company(Document):
    name = StringField(max_length=122)
    url = URLField(max_length=122)
