# E-commerce Module Reuse Guide

This guide explains how to extract and reuse the modular components of this Django project (Cart, Products, Orders, Reviews, Accounts) in other e-commerce websites.

## General Principles

All apps in this project are designed to be as **decoupled** as possible. To reuse an app:
1.  **Copy the app folder** to your new project.
2.  **Add it to `INSTALLED_APPS`**.
3.  **Configure required settings** in your `settings.py`.
4.  **Include app URLs** in your root `urls.py`.
5.  **Adjust templates and imports** to match your new project structure.

---

## 1. Shopping Cart Module (`cart`)

A session-based cart with no database overhead.

-   **Dependencies**: `django.contrib.sessions`, `products.models.Product` (can be swapped).
-   **Key Setting**: `CART_SESSION_ID = "cart"`.
-   **Integration**: Add `cart.cart.cart_context` to `TEMPLATES["OPTIONS"]["context_processors"]`.
-   **Reuse Tip**: If your product model is in a different app, update the imports in `cart/cart.py` and `cart/views.py`.

## 2. Product Catalogue Module (`products`)

Handles categories, tags, and rich product data.

-   **Dependencies**: `django.db.models.JSONField` (requires PostgreSQL or modern SQLite).
-   **Key Features**: Hierarchical categories, automatic slug/SKU generation, review aggregate fields.
-   **Reuse Tip**: To use without the `reviews` app, simply keep the `average_rating` and `review_count` fields as static fields or remove them. The `update_rating()` method is safe to keep.

## 3. Order & Checkout Module (`orders`)

Manages checkout flow, UPI payments, and Google Sheets sync.

-   **Dependencies**: `cart`, `products`, `requests` (for Sheets sync), `cloudinary` (for screenshots).
-   **Key Settings**: `UPI_ID`, `PAYEE_NAME`, `GOOGLE_SCRIPT_URL`.
-   **Reuse Tip**: To disable Google Sheets sync, set `GOOGLE_SCRIPT_URL = ""`. To use local storage instead of Cloudinary, change the `payment_screenshot` field to a standard `ImageField`.

## 4. Review System Module (`reviews`)

Product reviews with moderation and automatic rating updates.

-   **Dependencies**: `products`, `django.dispatch` (Signals).
-   **Architecture**: Uses **Signals** (`reviews/signals.py`) to trigger `product.update_rating()` when reviews are saved or deleted.
-   **Reuse Tip**: Ensure your product model has an `update_rating()` method. If not, modify `reviews/signals.py` to perform the logic you need.

## 5. User Accounts Module (`accounts`)

Simple, clean registration and login flow.

-   **Dependencies**: `django.contrib.auth`.
-   **Key Feature**: Extended `UserCreationForm` to capture email.
-   **Reuse Tip**: The login view uses raw POST data for simplicity. For more robust validation, swap it for Django's `AuthenticationForm`.

---

## The Modularity Pattern

This project follows a "Signal-based Decoupling" pattern:
-   **App A (e.g., Reviews)** knows about **App B (e.g., Products)**.
-   Instead of App A calling App B directly in the model's `save()` method, it uses **Signals**.
-   This allows App B to remain "unaware" of App A's specific implementation details, making it easier to swap or disable modules.

## Cross-App Imports

When reusing modules, always check for cross-app imports at the top of:
-   `models.py`
-   `views.py`
-   `signals.py`
-   `cart.py`

Update these to match your new project's app structure.
