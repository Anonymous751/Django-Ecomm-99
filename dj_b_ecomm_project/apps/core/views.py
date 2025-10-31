from django.shortcuts import render
from . import forms
from apps.shop.models import Product
from apps.cart.models import CartItem



def home_view(request):
    selected_category = request.GET.get('category')
    search_query = request.GET.get('search')

    # Start with all products
    products = Product.objects.all()

    # Filter by category
    if selected_category:
        products = products.filter(category=selected_category)

    # Filter by search query
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Group products for sliders
    featured_products = products.filter(is_featured=True)
    trending_products = products.filter(is_trending=True)
    new_comers = products.order_by('-created_at')[:10]

    # Cart info
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.total_price for item in cart_items)
        cart_count = cart_items.count()
    else:
        cart_items = []
        cart_total = 0
        cart_count = 0

    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'new_comers': new_comers,
        'selected_category': selected_category,
        'search_query': search_query,
        'products': products,  # ✅ fixed
        'Product': Product,    # for CATEGORY_CHOICES if needed
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }

    return render(request, 'home.html', context)


def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {
                'form': forms.ContactForm(),  # empty form after saving
                'success': True
            })
    else:
        form = forms.ContactForm()

    # ✅ Always return a response, even for GET
    return render(request, 'contact.html', {'form': form})