from django.db import models

class Categories(models.Model):
    name = models.CharField(max_length=150, unique= True, verbose_name = 'Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name = 'URL')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    class Meta:
        db_table = 'category' # В бд
        verbose_name = 'Категорию'  # Ед. в адм панель
        verbose_name_plural = 'Категории'  # Мн. в адм панель
    def __str__(self):
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='URl')
    image = models.ImageField(upload_to='images', blank=True, null=True, verbose_name='Изображение')
    price = models.DecimalField(default=0.00, max_digits=9,decimal_places=2, verbose_name='Цена')
    description = models.TextField(blank=True,null=True, verbose_name='Описание')
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE, verbose_name='Категория')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')

    class Meta:
        db_table = 'product' # В бд
        verbose_name = 'Продукт'  # Ед. в адм панель
        verbose_name_plural = 'Продукты'  # Мн. в адм панель
        ordering = ('id',)
    def __str__(self):
        return self.name

    def display_id(self):
        return f"{self.id:05}"

    def sell_price(self):
        return self.price