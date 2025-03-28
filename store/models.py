from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# ------------------- Category Model ------------------- #
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)

    # Override save method to auto-generate slug if not provided
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique by adding a counter if needed
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


# ------------------- Brand Model ------------------- #
class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='brands/')
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)

    # Override save method to auto-generate slug if not provided
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique by adding a counter if needed
            original_slug = self.slug
            counter = 1
            while Brand.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


# ------------------- Product Model ------------------- #
class Product(models.Model):
    # Product basic fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)

    # Gender-specific product
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unisex')],
        default='U'
    )

    # Soft delete and other flags
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    # Product analytics
    popularity = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # Override save method to auto-generate slug if not provided
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique by adding a counter if needed
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    # Soft delete method - sets is_deleted flag and saves timestamp
    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()

    # Get the minimum price from available variants
    def get_price(self):
        price = self.variants.aggregate(min_price=models.Min('price'))['min_price']
        return price if price else 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']


# ------------------- Variant Model ------------------- #
class Variant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    reserved_quantity = models.PositiveIntegerField(default=0)

    # Return available stock after considering reserved quantity
    def available_stock(self):
        return self.stock - self.reserved_quantity

    def __str__(self):
        return f"{self.product.name} - {self.color}"

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variants"


# ------------------- Product Image Model ------------------- #
class ProductImage(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.variant.product.name} - {self.image.name}"

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
