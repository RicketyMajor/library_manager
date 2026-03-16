from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=100, help_text="e.g., Science Fiction, Fantasy, Cyberpunk")

    def __str__(self):
        return self.name


class Book(models.Model):
    FORMAT_CHOICES = [
        ('NOVEL', 'Novel'),
        ('COMIC', 'Comic Book'),
        ('MANGA', 'Manga'),
        ('ANTHOLOGY', 'Anthology'),
    ]

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    genres = models.ManyToManyField(Genre)
    format_type = models.CharField(
        max_length=20, choices=FORMAT_CHOICES, default='NOVEL')
    is_read = models.BooleanField(default=False)

    publisher = models.CharField(
        max_length=200, null=True, blank=True)  # Editorial

    # Sistema de control para Cómics/Mangas
    is_series = models.BooleanField(default=False)
    total_volumes = models.IntegerField(null=True, blank=True)
    owned_volumes = models.CharField(
        max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
