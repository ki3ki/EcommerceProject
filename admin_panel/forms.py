from django import forms
from .models import Blog
from store.models import Product, Variant, ProductImage, Category, Brand
from .custom_widgets import MultipleFileInput

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'gender', 'is_featured']

class VariantForm(forms.ModelForm):
    image1 = forms.ImageField(label='Image 1', required=True)
    image2 = forms.ImageField(label='Image 2', required=True)
    image3 = forms.ImageField(label='Image 3', required=True)

    class Meta:
        model = Variant
        fields = ['color', 'stock', 'price']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'image']

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'slug', 'content', 'cover_image']

        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }