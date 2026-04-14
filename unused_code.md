# Unused Code Audit — django_Learn Project

> Dead code, unreachable code, imported-but-unused symbols, and inert model fields across every file.

---

## `accounts` App

### `accounts/models.py`
```python
from django.db import models  # ← Imported but no model is defined. Entire file is effectively empty.
```
The file imports `models` and has a comment `# Create your models here.` but defines nothing. The file can either be left as a placeholder or populated with a custom `UserProfile` model.

---

### `accounts/views.py`
```python
from django.contrib.auth.decorators import login_required  # ← Used only by profile()
```
- `profile()` view — renders `accounts/profile.html` but **passes no context**. The template has nothing to display unless it uses `{{ user }}` from the global auth context processor. The view body is effectively a pass-through.

---

## `core` App

### `core/models.py`
```python
from django.db import models  # ← Imported but nothing is defined.
```
Entire file is unused boilerplate.

---

### `core/views.py`
The following local variables are assigned but **never used** (only interpolated into a success message string):

| View | Variable | Line |
|---|---|---|
| `contact()` | `name` | 21 |
| `contact()` | `email` | 22 |
| `contact()` | `subject` | 23 |
| `contact()` | `message` | 24 |
| `partnership()` | `business_name` | 32 |
| `partnership()` | `contact_person` | 33 |

```python
# contact() — these are read from POST but never emailed, logged, or saved
name = request.POST.get("name")       # unused beyond f-string
email = request.POST.get("email")     # unused
subject = request.POST.get("subject") # unused
message = request.POST.get("message") # unused
```

```python
# partnership() — same pattern
business_name = request.POST.get("business_name")   # unused beyond f-string
contact_person = request.POST.get("contact_person") # unused beyond f-string
```

Also: the POST branch of `contact()` and `partnership()` both call `render(...)` instead of `redirect(...)` after success — this means refreshing the page will re-submit the form (missing POST-redirect-GET pattern).

---

## `cart` App

### `cart/models.py`
```python
from django.db import models  # ← Imported but no model is defined.
```
File is empty placeholder.

### `cart/admin.py`
```python
from django.contrib import admin  # ← Imported but nothing is registered.
```
File is empty placeholder.

---

## `products` App

### `products/views.py`
```python
from django.shortcuts import render, get_object_or_404
```
- `render` — **never used**. All views in this file are class-based (`ListView`, `DetailView`). The `render` import is dead.

```python
class CategoryListView(ListView):  # ← View is defined and URL-routed but never linked in any template.
```
`CategoryListView` (line 120) and its URL (`products/categories/`) exist but are orphaned — no navigation link points to this page.

---

### `products/models.py`

```python
image = models.ImageField(upload_to="products/", blank=True)   # Legacy single image
```
Marked as "Legacy" in a comment, but still active in admin `fieldsets`. Code that uses the product image should migrate fully to `image_gallery` (a JSONField list of URLs). The `image` field is half-deprecated dead weight.

The `uuid` import inside `Product.save()`:
```python
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.name)
    if not self.sku:
        import uuid                          # ← Import inside a method body (non-standard)
        self.sku = str(uuid.uuid4())[:8].upper()
```
`uuid` is imported inside the method body instead of at the top of the file. Not unused, but bad practice.

---

## `orders` App

### `orders/views.py`

```python
from django.views.decorators.http import require_POST  # ← Imported but never used in this file.
```
`@require_POST` is imported but not applied to any view in `orders/views.py`.

```python
# Debug print statements — should be removed
print(f"\n[DEBUG] Order #{order.id} — items count: {len(items)}")
print(f"[DEBUG]   → {line}")
print(f"[DEBUG] products_str = '{products_str}'\n")
print(f"[DEBUG] ERROR building products_str: {e}\n")
```
Temporary debug prints are still present and will pollute production logs.

---

### `orders/admin.py`

The `OrderItemAdmin` (line 39) is registered but has minimal config:
```python
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "price", "quantity"]
```
`OrderItem` is already visible via the `OrderItemInline` inside `OrderAdmin`. Having a separate top-level `OrderItemAdmin` is redundant and creates duplicate admin entries for the same data.

---

## `reviews` App

### `reviews/models.py`

```python
helpful_count = models.IntegerField(default=0)
```
The `helpful_count` field is defined and shown in admin (`readonly_fields`) but there is **no view, URL, or form** that increments it. It is a completely inert field — always 0 for every review.

---

## `tes/urls.py` (Root URLs)

```python
from django.conf.urls.static import static
...
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
In production (Vercel), `DEBUG=False` so this block is skipped — correct. But since `STORAGES["default"]` points to Cloudinary, `MEDIA_ROOT` is never really used even in development. This block is technically harmless but effectively dead in a Cloudinary-backed setup.

---

## Summary Table

| File | Type | Symbol |
|---|---|---|
| `accounts/models.py` | Unused import | `models` |
| `core/models.py` | Unused import | `models` |
| `cart/models.py` | Unused import | `models` |
| `cart/admin.py` | Unused import | `admin` |
| `core/views.py` | Unused variables | `name`, `email`, `subject`, `message`, `business_name`, `contact_person` |
| `products/views.py` | Unused import | `render` |
| `products/views.py` | Orphan class | `CategoryListView` (no nav link) |
| `products/models.py` | Half-deprecated field | `image` |
| `products/models.py` | Import inside method | `uuid` |
| `orders/views.py` | Unused import | `require_POST` |
| `orders/views.py` | Debug prints | 4× `print(f"[DEBUG]...")` |
| `orders/admin.py` | Redundant registration | `OrderItemAdmin` (duplicates inline) |
| `reviews/models.py` | Inert field | `helpful_count` |
