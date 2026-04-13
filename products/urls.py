from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"), # hat are these name parameter even do ?
    path("category/<slug:category_slug>/", views.ProductListView.as_view(), name="category_detail"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
]