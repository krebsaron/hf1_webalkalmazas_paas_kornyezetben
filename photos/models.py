from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    name = models.CharField(max_length=40, verbose_name='Photo name')
    image = models.ImageField(upload_to='photos/', verbose_name='Image file')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Upload date')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Owner'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self):
        return self.name
