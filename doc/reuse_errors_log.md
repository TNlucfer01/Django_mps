# Module Reuse Guide - Error Log

This file tracks errors and issues encountered while following the `module_reuse_guide.md`.

## Error 1: `ModuleNotFoundError: No module named 'core'`
- **Step**: Step 8 — Set Up Tailwind CSS (`python manage.py tailwind init`)
- **Cause**: `settings.py` was updated in Step 7 with all apps in `INSTALLED_APPS` before the app folders were copied in Step 9.
- **Impact**: Blocked from initializing Tailwind CSS.
- **Fix/Workaround**: Skip to Step 9 to copy the app folders first, OR comment out the custom apps in `INSTALLED_APPS` until they ar2e copied.

## Error 2: `ModuleNotFoundError: No module named 'theme'`
- **Step**: Step 8 — Set Up Tailwind CSS (`python manage.py tailwind init`)
- **Cause**: `settings.py` includes `"theme"` in `INSTALLED_APPS`, but the `theme` app is only created *after* running `tailwind init`.
- **Impact**: Blocked from initializing Tailwind CSS.
- **Fix/Workaround**: Temporarily comment out `"theme"` in `INSTALLED_APPS` in `settings.py`, run `tailwind init`, and then uncomment it.

## Issue 3: Underspecified Prompts in Tailwind Init
- **Step**: Step 8 — Set Up Tailwind CSS (`python manage.py tailwind init`)
- **Observation**: The command prompts for:
  1. Tailwind version (Choice 1, 2, or 3).
  2. Inclusion of DaisyUI (y/n).
- **Impact**: The guide only says "When it asks for the app name, type: `theme`". It does not guide the user on the other prompts.
- **Recommendation**: Update guide to specify which choices to make.

## Issue 4: Missing Authentication Links in `base.html`
- **Step**: Step 9 — Copy the App Folders (specifically `templates/base.html`)
- **Observation**: The copied `templates/base.html` has a comment: `<!-- Removed user/login links as user authentication is disabled -->`.
- **Impact**: Users cannot log out or log in easily from the UI without manually typing URLs (and Logout is blocked on GET).
- **Recommendation**: Ensure the guide's templates include authentication links as described in Part 2 Module B.

## Error 5: `ImproperlyConfigured` for Cloudinary Storage
- **Step**: Step 11 — Verification (Checkout Flow)
- **Observation**: The `settings.py` template configures `cloudinary_storage` for media files. When uploading a payment screenshot during checkout, it crashes if Cloudinary credentials are not set.
- **Impact**: Checkout flow fails.
- **Fix/Workaround**: Change `STORAGES["default"]["BACKEND"]` to `"django.core.files.storage.FileSystemStorage"` for local storage.
