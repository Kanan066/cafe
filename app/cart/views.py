from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order, ORDER_STATUS, MenuItem

# Check if user is staff
def is_staff_user(user):
    return user.is_staff

# ------------------- STAFF VIEWS -------------------

# Staff dashboard view
@login_required
@user_passes_test(is_staff_user)
def staff_dashboard(request):
    orders = Order.objects.all().order_by('-created_at')  # Show newest first
    return render(request, 'cart/staff_dashboard.html', {'orders': orders})

# Update order status view
@login_required
@user_passes_test(is_staff_user)
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    if status in dict(ORDER_STATUS).keys():
        order.status = status
        order.save()
    return redirect('staff_dashboard')


# ------------------- CUSTOMER VIEWS -------------------

@login_required
def customer_order_status(request):
    orders = Order.objects.filter(customer_name=request.user.username).order_by('-created_at')
    return render(request, 'cart/customer_order_status.html', {'orders': orders})

@login_required
def place_order(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))

        item = get_object_or_404(MenuItem, id=item_id)

        Order.objects.create(
            customer_name=request.user.username,
            menu_item=item,
            quantity=quantity,
            status='pending'
        )

        return redirect('customer_order_status')  # or a success page

    return redirect('menu')  # fallback


def cart_summary(request):
    cart = request.session.get('cart', {})
    items = []
    total_price = 0

    for item_id, quantity in cart.items():
        item = get_object_or_404(MenuItem, id=item_id)
        items.append({
            'item': item,
            'quantity': quantity,
            'subtotal': item.price * quantity
        })
        total_price += item.price * quantity

    return render(request, "cart/cart_summary.html", {
        'cart_items': items,
        'total_price': total_price
    })


# ------------------- CART ACTIONS -------------------

def cart_add(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if item_id in cart:
            cart[item_id] += quantity
        else:
            cart[item_id] = quantity

        request.session['cart'] = cart
        return redirect('cart_summary')


def cart_delete(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart = request.session.get('cart', {})

        if item_id in cart:
            del cart[item_id]
            request.session['cart'] = cart

        return redirect('cart_summary')


def cart_update(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if item_id in cart:
            if quantity > 0:
                cart[item_id] = quantity
            else:
                del cart[item_id]
            request.session['cart'] = cart

        return redirect('cart_summary')
