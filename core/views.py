from django.shortcuts import render
from django.contrib import messages
from products.models import Product, Category


def home(request):
    products = Product.objects.filter(is_active=True).order_by("-average_rating")[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    return render(request, "core/home.html", {
        "products": products,
        "categories": categories
    })


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        messages.success(request, f"Thank you {name}! Your message has been sent.")
        return render(request, "core/contact.html")
    return render(request, "core/contact.html")


def partnership(request):
    if request.method == "POST":
        business_name = request.POST.get("business_name")
        contact_person = request.POST.get("contact_person")
        messages.success(request, f"Thank you {contact_person}! Your partnership inquiry for {business_name} has been received. We will contact you shortly.")
        return render(request, "core/partnership.html")
    return render(request, "core/partnership.html")
