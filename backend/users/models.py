from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Класс кастомных пользователей."""
    MAX_LENGTH_EMAIL = 254
    MAX_LENGTH_OTHER_FIELDS = 150
    REDEX = r'^[\w.@+-]+$'

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта',
        help_text='Обязательное поле',
        unique=True,
        blank=False,
        null=False,
    )
    username = models.CharField(
        max_length=MAX_LENGTH_OTHER_FIELDS,
        verbose_name='Никнейм',
        help_text='Обязательное поле',
        unique=True,
        blank=False,
        null=False,
        validators=[RegexValidator(
            regex=REDEX,
            message='Неверный формат Никнейма.'),
                    validate_username,
                    ]
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_OTHER_FIELDS,
        verbose_name='Имя',
        help_text='Обязательное поле',
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_OTHER_FIELDS,
        verbose_name='Фамилия',
        help_text='Обязательное поле',
        blank=False,
        null=False,
    )
    password = models.CharField(
        max_length=MAX_LENGTH_OTHER_FIELDS,
        verbose_name='Пароль',
        help_text='Обязательное поле',
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Follower(models.Model):
    """Класс для подписки на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
