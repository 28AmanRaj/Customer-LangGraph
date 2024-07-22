from mongoengine import Document, StringField, URLField

class Query(Document):
    query = StringField(max_length=500)  # Use StringField with a reasonable max_length

class Company(Document):
    name = StringField(max_length=122)
    url = URLField(max_length=122)
