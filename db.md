# Database Schema — django_Learn Project

> Auto-generated from source inspection. Apps: `accounts`, `core`, `cart`, `products`, `orders`, `reviews`.

---

## Apps With No Models

| App | Notes |
|---|---|
| `accounts` | Uses Django's built-in `User` model (`AUTH_USER_MODEL`). No custom model defined. |
| `core` | No models. View-only app (home, about, contact, partnership). |
| `cart` | No database model. Cart state is stored entirely in the **session** (`SESSION_ENGINE = signed_cookies`). |

---

## `products` App

### `Category`
> Hierarchical product categories (e.g. Electronics → Mobiles).

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | auto | — |
| `name` | CharField(100) | unique | — |
| `slug` | SlugField(120) | unique | Auto-generated from `name` on save if blank |
| `description` | TextField | blank=True | — |
| `parent` | ForeignKey → `self` | null, blank, SET_NULL | Enables nested categories |
| `image_url` | URLField(500) | blank=True | External URL only |
| `display_order` | IntegerField | default=0 | Used for sorting |
| `is_active` | BooleanField | default=True | — |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |

**Meta**: `ordering = ["display_order", "name"]`

**Relationships**:
- Self-referential FK (`parent`) → supports subcategories
- `children` reverse name → `Category.children.all()`
- `products` reverse name from `Product`

---

### `Tag`
> Short keyword labels for products.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | auto | — |
| `name` | CharField(50) | unique | — |
| `slug` | SlugField(60) | unique | Auto-generated on save |
| `description` | CharField(200) | blank=True | — |
| `is_active` | BooleanField | default=True | — |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |

**Meta**: `ordering = ["name"]`

---

### `Product`
> Full-featured product model for an electronics-style shop.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | auto | — |
| `sku` | CharField(50) | unique, null, blank | Auto-generated 8-char UUID on save |
| `name` | CharField(255) | required | — |
| `slug` | SlugField(255) | unique | Auto-generated from `name` |
| `brand` | CharField(100) | blank=True | — |
| `model_number` | CharField(100) | blank=True | — |
| `short_description` | CharField(500) | blank=True | — |
| `long_description` | TextField | blank=True | — |
| `price` | DecimalField(10,2) | required | Current selling price |
| `original_price` | DecimalField(10,2) | null, blank | Used to calculate discount |
| `currency` | CharField(3) | default="INR" | — |
| `stock_quantity` | PositiveIntegerField | default=0 | — |
| `availability_status` | CharField(20) | choices, default="In Stock" | In Stock / Out of Stock / Pre-Order / Discontinued |
| `category` | ForeignKey → `Category` | CASCADE | — |
| `tags` | ManyToManyField → `Tag` | blank=True | — |
| `image` | ImageField | upload_to="products/" | Legacy single image |
| `image_gallery` | JSONField | default=list | List of image URLs |
| `video_url` | URLField(500) | blank=True | — |
| `specifications` | JSONField | default=dict | Key-value spec pairs |
| `average_rating` | DecimalField(3,2) | default=0.00 | Updated by `update_rating()` |
| `review_count` | IntegerField | default=0 | Updated by `update_rating()` |
| `is_active` | BooleanField | default=True | — |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |

**Meta**: `ordering = ["-created_at"]`

**Properties**:
- `is_on_sale` → True if `original_price > price`
- `discount_percentage` → Calculated % off
- `is_available` → True if "In Stock" and `stock_quantity > 0`

**Methods**:
- `update_rating()` — recalculates `average_rating` and `review_count` from approved reviews

**Relationships**:
- `category` FK → `Category` (CASCADE)
- `tags` M2M → `Tag`
- `reviews` reverse from `Review`
- `orders` reverse from `OrderItem`

---

## `orders` App

### `Order`
> A placed customer order. Tied to a user and contains shipping + payment information.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | auto | — |
| `user` | ForeignKey → `AUTH_USER_MODEL` | CASCADE, related_name="orders" | — |
| `first_name` | CharField(100) | required | — |
| `last_name` | CharField(100) | required | — |
| `email` | EmailField | required | — |
| `phone` | CharField(20) | required | — |
| `address` | TextField | required | — |
| `city` | CharField(100) | required | — |
| `state` | CharField(100) | required | — |
| `postal_code` | CharField(20) | required | — |
| `country` | CharField(100) | required | — |
| `total_amount` | DecimalField(10,2) | required | Captured from cart at time of order |
| `status` | CharField(20) | choices, default="pending" | pending / confirmed / shipped / delivered / cancelled |
| `payment_method` | CharField(50) | choices=PAYMENT_CHOICES, default="upi_qr" | Only valid value: "upi_qr" |
| `is_paid` | BooleanField | default=False | ⚠️ Never set to True automatically |
| `utr_number` | CharField(100) | null, blank | UPI transaction reference |
| `payment_screenshot` | ImageField | upload_to="payment_proofs/", null, blank | Stored on Cloudinary |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |

**Meta**: `ordering = ["-created_at"]`

**Relationships**:
- `user` FK → `AUTH_USER_MODEL`
- `items` reverse from `OrderItem`

---

### `OrderItem`
> A single product line within an Order.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | auto | — |
| `order` | ForeignKey → `Order` | CASCADE, related_name="items" | — |
| `product` | ForeignKey → `Product` | CASCADE | ⚠️ CASCADE means deleting a product deletes all order history |
| `price` | DecimalField(10,2) | required | Price at time of purchase (snapshot) |
| `quantity` | PositiveIntegerField | default=1 | — |

**Properties**:
- `get_total` → `price × quantity`

---

## `reviews` App

### `Review`
> User review for a product. Supports moderation and helpfulness voting.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | auto | — |
| `product` | ForeignKey → `Product` | CASCADE, related_name="reviews" | — |
| `user` | ForeignKey → `AUTH_USER_MODEL` | CASCADE | — |
| `rating` | PositiveSmallIntegerField | choices=1–5 | — |
| `title` | CharField(200) | blank=True | Optional review title |
| `comment` | TextField | required | — |
| `is_approved` | BooleanField | default=False | Must be approved before showing |
| `helpful_count` | IntegerField | default=0 | No increment logic implemented |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |

**Meta**:
- `ordering = ["-created_at"]`
- `unique_together = ["product", "user"]` → one review per user per product

**Lifecycle hooks**:
- `save()` → calls `product.update_rating()` on every save
- `delete()` → calls `product.update_rating()` after deleting

---

## Entity Relationship Summary

```
AUTH_USER_MODEL (Django built-in)
    │
    ├── Order (FK user → orders)
    │       └── OrderItem (FK order → items)
    │               └── Product (FK product)
    │
    └── Review (FK user)
            └── Product (FK product → reviews)

Product ──FK──► Category
Product ──M2M─► Tag
Category ──FK──► Category (self, parent)
```

---

## Session Storage (Cart)

The cart is **not stored in the database**. It lives in a signed cookie session:

- **Session key**: `CART_SESSION_ID = "cart"`
- **Structure**: `{ "<product_id>": { "quantity": int, "price": str } }`
- **Engine**: `django.contrib.sessions.backends.signed_cookies`
- **Limit**: Signed cookies have a ~4KB limit. Large carts may silently truncate.
