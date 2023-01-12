from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Юзернэйм',
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписка на',
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name="unique subscription"),
        ]
