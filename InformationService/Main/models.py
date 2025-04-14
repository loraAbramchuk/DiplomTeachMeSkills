from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.PositiveIntegerField()
    genres = models.ManyToManyField(Genre)
    country = models.ManyToManyField(Country)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Serial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.PositiveIntegerField()
    genres = models.ManyToManyField(Genre)
    country = models.ManyToManyField(Country)
    episodes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

