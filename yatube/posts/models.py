from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CHAR_IN_POST = 15


class Group(models.Model):
    """Модель для работы с группами/сообществами."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        """Вывод на печать имени группы."""
        return self.title


class Post(models.Model):
    """Модель для работы с постами."""

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Сортировка по дате."""
        verbose_name = 'запись'
        verbose_name_plural = 'записи'
        ordering = ('-pub_date',)

    def __str__(self):
        """Вывод на печать 15 символов поста."""
        return self.text[:CHAR_IN_POST]


class Comment(models.Model):
    """Модель для работы с комментариями."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        """Сортировка по дате."""
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Модель для работы с подписками."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        """Проверка уникальности имен при подписке."""
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]
