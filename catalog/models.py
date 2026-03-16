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
    # Opciones predefinidas para el formato
    FORMAT_CHOICES = [
        ('NOVEL', 'Novel'),
        ('COMIC', 'Comic Book'),
        ('MANGA', 'Manga'),
        ('ANTHOLOGY', 'Anthology'),
    ]

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    genres = models.ManyToManyField(
        Genre, help_text="Select genres for this book")
    format_type = models.CharField(
        max_length=20, choices=FORMAT_CHOICES, default='NOVEL')

    # Sistema de seguimiento de lectura
    is_read = models.BooleanField(default=False)
    rating = models.IntegerField(
        null=True, blank=True, help_text="Rating from 1 to 5")

    # Para mangas o cómics, es útil saber el número del tomo
    volume_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.volume_number:
            return f"{self.title} - Vol. {self.volume_number}"
        return self.title
