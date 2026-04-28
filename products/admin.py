from django import forms
from django.contrib import admin
from .models import Product, ProductImage, Category, Tag
from .widgets import KeyValueWidget


class ProductAdminForm(forms.ModelForm):
    """Custom admin form that replaces the raw JSON textarea for
    specifications with a user-friendly key-value table widget."""

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "specifications": KeyValueWidget(),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "display_order", "is_active", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]
    list_filter = ["is_active", "parent"]
    list_editable = ["display_order", "is_active"]
    ordering = ["display_order", "name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]
    list_filter = ["is_active"]


class ProductImageInline(admin.TabularInline):
    """Inline image uploader — add/remove/reorder gallery images directly on the Product page."""
    model = ProductImage
    extra = 3                          # Show 3 blank upload slots by default
    fields = ["image", "order"]
    ordering = ["order"]
    show_change_link = False

    def get_extra(self, request, obj=None, **kwargs):
        # Don't show blank rows when editing an existing product with many images
        if obj and obj.gallery_images.count() >= 10:
            return 0
        return self.extra


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductImageInline]
    list_display = [
        "name", "brand", "sku", "category",
        "price", "original_price", "stock_quantity",
        "availability_status", "average_rating", "review_count",
        "is_active", "created_at",
    ]
    list_filter = ["category", "availability_status", "is_active", "brand", "created_at"]
    list_editable = ["price", "stock_quantity", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "brand", "sku", "model_number", "short_description"]
    raw_id_fields = ["category"]
    filter_horizontal = ["tags"]
    readonly_fields = ["average_rating", "review_count", "created_at", "updated_at"]
    fieldsets = (
        ("Identity", {
            "fields": ("name", "slug", "sku", "brand", "model_number", "category", "tags")
        }),
        ("Description", {
            "fields": ("short_description", "long_description")
        }),
        ("Pricing", {
            "fields": ("price", "original_price", "currency")
        }),
        ("Stock & Availability", {
            "description": "Set stock_quantity. availability_status auto-syncs: 0 → Out of Stock, >0 → In Stock. Set Pre-Order or Discontinued manually to bypass auto-sync.",
            "fields": ("stock_quantity", "availability_status", "is_active")
        }),
        ("Media", {
            "description": "Upload the main product image below. Use the 'Product Images' section further down to upload gallery images from your device.",
            "fields": ("image", "video_url")
        }),
        ("Specifications", {
            "fields": ("specifications",)
        }),
        ("Ratings (Read Only)", {
            "fields": ("average_rating", "review_count"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
