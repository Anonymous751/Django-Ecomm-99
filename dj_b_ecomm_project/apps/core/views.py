from django.shortcuts import render
from . import forms
from apps.shop.models import Product
from apps.cart.models import CartItem



def home_view(request):
    # Separate selected categories for each section
    featured_category = request.GET.get('featured_category')
    trending_category = request.GET.get('trending_category')
    newcomers_category = request.GET.get('newcomers_category')

    search_query = request.GET.get('search')

    # Start with all products
    products = Product.objects.all()

    # Featured Products filter
    featured_products = Product.objects.filter(is_featured=True)
    if featured_category:
        featured_products = featured_products.filter(category=featured_category)
    if search_query:
        featured_products = featured_products.filter(name__icontains=search_query)

    # Trending Products filter
    trending_products = Product.objects.filter(is_trending=True)
    if trending_category:
        trending_products = trending_products.filter(category=trending_category)
    if search_query:
        trending_products = trending_products.filter(name__icontains=search_query)
        
    # New Comers filter
    new_comers = Product.objects.all()
    if newcomers_category:
        new_comers = new_comers.filter(category=newcomers_category)
    if search_query:
        new_comers = new_comers.filter(name__icontains=search_query)
    new_comers = new_comers.order_by('-created_at')[:10]

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
        'featured_category': featured_category,
        'trending_category': trending_category,
        'newcomers_category': newcomers_category,
        'search_query': search_query,
        'Product': Product,  # for CATEGORY_CHOICES
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
