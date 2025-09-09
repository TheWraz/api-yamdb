from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from titles.models import Title


class Review(models.Model):
    """Модель для хранения отзывов на произведения."""

    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
# Если related_name одинаковый для всех полей, то можно указать default_related_name.
# Тут и ниже.
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
# Величины ограничений берем из констант.
# Тут и далее.
# Параметром message, в каждом классе валидации, можно указать сообщение с причиной данной ошибки.
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
# огда объявляется коллекция, нужно верно выбрать между списком и кортежем(тут список). 
# Выбор нужно делать осознанно, потому что список изменяемый, а кортеж нет. 
# Если предполагается, что сюда будет вноситься изменения где то в коде, то нужен список, а если изменений никаких не будет то лучше кортеж.
# Тут и далее.
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв {self.author.username} на {self.title.name}'


class Comment(models.Model):
    """Модель для хранения комментариев к отзывам."""

    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Комментарий {self.author.username} к отзыву {self.review.id}'
