from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True,verbose_name='Аватар')
    phone_number = models.CharField(max_length=10,blank=True,null=True)
    class Meta:
        db_table = 'user' # В бд
        verbose_name = 'Пользователя'  # Ед. в адм панель
        verbose_name_plural = 'Пользователи'  # Мн. в адм панель
    def __str__(self):
        return self.username