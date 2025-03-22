from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure the slug is unique
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='brands/')
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure the slug is unique
            original_slug = self.slug
            counter = 1
            while Brand.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unisex')], default='U')
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True) 
    is_featured = models.BooleanField(default=False)
    popularity = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank=True )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure the slug is unique
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def get_price(self):
        price = self.variants.aggregate(min_price=models.Min('price'))['min_price']
        return price if price else 0


    def __str__(self):
        return self.name

class Variant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    reserved_quantity = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.product.name} - {self.color}"
    
    def available_stock(self):
        return self.stock - self.reserved_quantity

class ProductImage(models.Model):
   

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.variant.product.name} - {self.image.name}"