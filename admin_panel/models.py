from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()  # Will contain HTML with embedded images
    cover_image = models.ImageField(upload_to='blog_covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

