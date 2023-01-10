from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200)
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=200
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    name = models.CharField(
        'Имя',
        max_length=60,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        'Ссылка',
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipts',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=255
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='static/recipe/',
        blank=True,
        null=True
    )
    text = models.TextField(
        'Описание рецепта'
    )
    cooking_time = models.BigIntegerField(
        'Время приготовления рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Recipts_Ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipts'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class Recipts_Ingredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipts'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')]


class Followers(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription')]

    def __str__(self):
        return f'Пользователь {self.user} -> автор {self.author}'


class Favorite_Recipe(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorite_recipe',
        verbose_name='Пользователь'
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    @receiver(post_save, sender=User)
    def create_favorite_recipe(
            sender, instance, created, **kwargs):
        if created:
            return Favorite_Recipe.objects.create(user=instance)


class Shopping(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        null=True,
        verbose_name='Пользователь'
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='shopping',
        verbose_name='Покупка'
    )

    @receiver(post_save, sender=User)
    def create_shopping_cart(
            sender, instance, created, **kwargs):
        if created:
            return Shopping.objects.create(user=instance)
