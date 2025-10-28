from apps.cart.models import CartItem

def cart_context(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.total_price for item in cart_items)
        cart_count = cart_items.count()
    else:
        cart_items = []
        cart_total = 0
        cart_count = 0

    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count
    }
