# Bug Report — django_Learn Project

> Full codebase audit. Issues ranked: 🔴 Critical, 🟡 Medium, 🔵 Minor.

---

## `orders` App

### 🔴 BUG-01 — `is_paid` Never Set to True
**File**: `orders/views.py` — `checkout()` view

When a UPI order is placed (the only payment method), `is_paid` is never set to `True`. The user uploads a payment screenshot and UTR number, but the order is saved with `is_paid=False`. This also flows to Google Sheets, making the payment status column always say "Unpaid".

**Fix**: Set `is_paid=True` when `payment_method == "upi_qr"` and a screenshot is uploaded, or allow admin to set it manually and trigger a webhook/re-sync to Sheets.

---

### 🔴 BUG-02 — No Server-Side Form Validation
**File**: `orders/views.py` — `checkout()` view (lines 35–63)

All form fields are read with `request.POST.get(...)` and written directly to the DB with no validation. If any required field is empty (e.g. `first_name`, `email`, `address`), `None` or `""` is stored. The HTML `required` attribute can be bypassed with any API client or browser dev tools.

**Fix**: Validate all required fields before `Order.objects.create(...)` and return the form with error messages.

---

### 🔴 BUG-03 — `total_amount` Can Be Zero (Empty Cart Bypass)
**File**: `orders/views.py` — `checkout()` view

The only cart check is `if not cart:` (line 30), which calls `Cart.__len__`. If a product is added to the cart and then deleted from the database, `Cart.__iter__` skips it silently (because `Product.objects.filter(id__in=...)` returns nothing), but `Cart.__len__` still counts the stale session entry. The result: the order is created with `total_amount=0` and no `OrderItem` records.

Evidence from Google Sheets: Orders #5, #7, #9 all show `total_amount=0` with no products.

**Fix**: After iterating the cart to create `OrderItem`s, check `if order.items.count() == 0: order.delete(); show_error()`.

---

### 🟡 BUG-04 — `OrderItem.product` Uses CASCADE — Historical Data Loss
**File**: `orders/models.py` line 45

`product = models.ForeignKey(Product, on_delete=models.CASCADE)`

Deleting a product from the admin silently deletes all `OrderItem` rows referencing it. Historical orders lose their line items permanently.

**Fix**: Change to `on_delete=models.PROTECT` to prevent deletion, or `on_delete=models.SET_NULL, null=True` to preserve order history.

---

### 🟡 BUG-05 — Debug Print Statements Left in Production Code
**File**: `orders/views.py` lines 86–97

`print(f"[DEBUG] Order ...")` statements added for debugging are still present. These will output to production server logs if not removed.

**Fix**: Remove all `[DEBUG]` print lines or replace with proper `import logging; logger.debug(...)`.

---

### 🔵 BUG-06 — Double URL Prefix Risk (orders)
**File**: `orders/urls.py` vs `tes/urls.py`

`orders/urls.py` is included at `path("orders/", include("orders.urls"))`. Inside `orders/urls.py`, two URLs use names that imply double-nesting: `path("orders/", ...)` and `path("order/...")`. The actual effective URLs are `/orders/orders/` and `/orders/order/<id>/` — the second one is fine but the first produces a redundant `orders/orders/` path.

---

## `core` App

### 🟡 BUG-07 — Contact & Partnership Forms Do Nothing
**File**: `core/views.py` — `contact()` and `partnership()` views

Both views collect form data (name, email, subject, message / business_name, contact_person) but do absolutely nothing with it. No email is sent, no database entry is made, no logging happens. The success message is shown regardless, creating a false impression that the message was received.

**Fix**: Implement email sending via Django's `send_mail()` or save to a database model.

---

### 🔵 BUG-08 — Unused Variables in contact/partnership Views
**File**: `core/views.py` lines 21–23, 32–33

```python
name = request.POST.get("name")        # Never used after assignment
email = request.POST.get("email")      # Never used
subject = request.POST.get("subject")  # Never used
message = request.POST.get("message")  # Never used
business_name = request.POST.get("business_name")    # Never used
contact_person = request.POST.get("contact_person")  # Never used
```

All of these are assigned and only used in the `messages.success(...)` string. None are stored or acted upon.

---

## `accounts` App

### 🟡 BUG-09 — `logout_view` Doesn't Require POST
**File**: `accounts/views.py` line 44

```python
def logout_view(request):
    logout(request)
```

The logout view accepts `GET` requests. This is a **CSRF vulnerability** — any link on any page can log the user out (e.g. `<img src="/accounts/logout/">` on a malicious page). Django recommends logout only via POST.

**Fix**: Add `@require_POST` decorator or check `if request.method == "POST"`.

---

### 🔵 BUG-10 — Uses Django's Default `UserCreationForm` (No Email Field)
**File**: `accounts/views.py` line 15

The default `UserCreationForm` has no `email` field. Users register with just username + password. The `Order` model stores `email` from the checkout form, not from the user account — these can be different.

**Fix**: Create a custom form that extends `UserCreationForm` and adds `email`.

---

## `reviews` App

### 🟡 BUG-11 — `helpful_count` Has No Increment Logic
**File**: `reviews/models.py` line 17

`helpful_count = models.IntegerField(default=0)` is defined but there is no view, URL, or any code that increments it. The field is completely inert.

**Fix**: Either remove the field or implement a `mark_helpful` view with a URL.

---

### 🟡 BUG-12 — `add_review` Accepts Any Integer as Rating (No Validation)
**File**: `reviews/views.py` line 14

```python
rating = request.POST.get("rating")
```

The rating is read from POST and passed directly to `Review.objects.create(rating=rating)`. While `RATING_CHOICES` is defined on the model, Django does not enforce `choices` at the database level — any integer (or even a string) can be submitted via a crafted POST request.

**Fix**: Validate that `rating` is in `[1, 2, 3, 4, 5]` before creating the review.

---

## `products` App

### 🔵 BUG-13 — `CategoryListView` Not Linked From Any URLs
**File**: `products/views.py` line 120, `products/urls.py` line 10

`CategoryListView` is defined and registered at `path("categories/", ...)` but it's never linked from any template navigation. It's an orphan page.

---

### 🔵 BUG-14 — `Product.image` Described as "Legacy" But Still Active
**File**: `products/models.py` line 104

```python
image = models.ImageField(upload_to="products/", blank=True)   # Legacy single image
```

The comment says "Legacy" but the field is still in the admin (`fieldsets` includes it). This creates confusion about whether `image` or `image_gallery` should be used.

---

## `settings.py`

### 🔴 BUG-15 — `ALLOWED_HOSTS = ["*"]` on Production
**File**: `tes/settings.py` line 27

Wildcard `ALLOWED_HOSTS` is a security risk in production. Any domain can be used to host the app.

**Fix**: Set explicitly to your Vercel domain: `ALLOWED_HOSTS = ["your-app.vercel.app"]`.

---

### 🟡 BUG-16 — SESSION_COOKIE_SECURE = True Breaks Local HTTP
**File**: `tes/settings.py` line 123

`SESSION_COOKIE_SECURE = True` means session cookies will only be sent over HTTPS. On a local `runserver` (HTTP), the session cookie is never sent, which can silently break cart and login functionality locally.

**Fix**: Conditionally set it:
```python
SESSION_COOKIE_SECURE = not DEBUG
```

---

### 🔵 BUG-17 — `MEDIA_URL` Missing Leading Slash
**File**: `tes/settings.py` line 164

```python
MEDIA_URL = "media/"
```

Standard Django convention is `MEDIA_URL = "/media/"` (with leading slash). Without it, relative file serving may break on some configurations.

---

## Google Apps Script (External)

### 🔴 BUG-18 — Typo `data.products_orderedodtc` (now fixed)
**File**: Google Apps Script (external)

Typo `data.products_orderedodtc` caused the Products column in Sheets to be blank for every order. Fixed by renaming Django payload key to `products` and updating the Apps Script to `data.products`.
