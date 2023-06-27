from django.db import models

# Create your models here.


class NewsLetter(models.Model):
    email = models.EmailField(max_length=254)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
