from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView # what are these  values are even do 
from django.db.models import Q
from .models import Product, Category


class ProductListView(ListView): # why do we create a class is there any need for this to even happen
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12 
#  what does the above line even do 
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        category_slug = self.kwargs.get("categoryz_slug")
        search_query = self.request.GET.get("q")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            context["current_category"] = get_object_or_404(Category, slug=category_slug)
        return context

#   how does this even work ?
class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            from reviews.models import Review
            context["user_review"] = Review.objects.filter(
                product=self.object, user=self.request.user
            ).first()
        return context

#  i still don't understand these  .    

class CategoryListView(ListView): 
    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"
