from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    """Модель для хранения отзывов на произведения."""
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.IntegerField(verbose_name='ID автора')
    # Заглушка для User.id
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    title_id = models.IntegerField(verbose_name='ID произведения')
    # Заглушка для Title.id

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title_id'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв {self.author} на произведение {self.title_id}'


class Comment(models.Model):
    """Модель для хранения комментариев к отзывам."""
    text = models.TextField(verbose_name='Текст комментария')
    author = models.IntegerField(verbose_name='ID автора')
    # Заглушка для User.id
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    review_id = models.IntegerField(verbose_name='ID отзыва')
    # Заглушка для Review.id

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Комментарий {self.author} к отзыву {self.review_id}'
