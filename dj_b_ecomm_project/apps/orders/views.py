from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.orders.models import Order , OrderItem
from django.contrib import messages
from apps.cart.models import CartItem
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
import json
from apps.shop.models import Product
from .forms import ProductForm
from django.shortcuts import render
from apps.orders.models import Order
from django.db.models import Prefetch
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@login_required
def my_orders_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        )
        .order_by('-created_at')
    )

    status_tabs = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]

    orders_by_status_list = [
        {'status': s, 'label': l, 'orders': orders.filter(status=s)}
        for s, l in status_tabs
    ]

    return render(request, 'orders/my_orders.html', {
        'orders_by_status_list': orders_by_status_list,
        'status_tabs': status_tabs,
    })



@login_required
def place_order_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # normal redirect for unauthenticated users

    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Optional demo payment fields
        name_on_card = request.POST.get('name_on_card', '')
        card_number = request.POST.get('card_number', '')
        expiry = request.POST.get('expiry', '')
        cvv = request.POST.get('cvv', '')

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart_total,
            status='pending'
        )

        # Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear cart
        cart_items.delete()

        # Redirect to "My Orders" page after placing order
        return redirect(reverse('my_orders'))  # replace 'my_orders' with your URL name

    return render(request, 'orders/place_order.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_items.count(),
    })

@login_required
@csrf_exempt
def update_order_status(request, order_id):
    """AJAX: update order status"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get("status")

            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()

            return JsonResponse({"success": True, "status": new_status})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})

@login_required
def update_ordered_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Recalculate totals for all orders containing this product
            orders_with_product = Order.objects.filter(items__product=product).distinct()
            updated_totals = {}
            for order in orders_with_product:
                total = sum(item.product.price * item.quantity for item in order.items.all()) # type: ignore
                order.total_amount = total # type: ignore
                order.save()
                updated_totals[order.id] = total # pyright: ignore[reportAttributeAccessIssue]

            # Correct AJAX check
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'updated_totals': updated_totals})

            messages.success(request, f'✅ {product.name} updated successfully!')
            return redirect('my_orders')
    else:
        form = ProductForm(instance=product)

    return render(request, 'orders/update_ordered_product.html', {'form': form, 'product': product})


@login_required
def delete_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



@login_required
def order_products_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    products = []

    for item in order.items.all():  # type: ignore # assuming a ForeignKey to Product
        product = item.product
        image_url = product.images.url if product.images else '/static/images/no-image.png'
        products.append({
            'name': product.name or 'Unknown Product',
            'price': float(product.price or 0),
            'quantity': item.quantity or 1,
            'image_url': image_url
        })

    return JsonResponse({'products': products})
