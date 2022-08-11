from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatechars


class UserProfile(models.Model):
    """ Расширение модели юзера дополнительными параметрами"""
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='age')
    city = models.CharField(max_length=40, default=None, null=True, blank=True)
    avatar = models.FileField(upload_to='img/', blank=True)
    subscribes = models.ManyToManyField(User, blank=True, related_name='subscribes')
    is_active = models.BooleanField(default=False)


class Photo(models.Model):
    """Моедль описания фотографии"""
    photo = models.FileField(upload_to='img/', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')

    class Meta:
        ordering = ['-created_at']


class PhotoComment(models.Model):
    """Модель комментраия для фотографий"""
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000, verbose_name='comment')
    name = models.CharField(max_length=50, blank=True, verbose_name='username')

    @property
    def short_text(self):
        return truncatechars(self.text, 40)
