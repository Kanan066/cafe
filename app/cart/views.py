from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order, ORDER_STATUS, MenuItem
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q


# Check if user is staff
def is_staff_user(user):
    return user.is_staff
def staff_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('staff_dashboard')  # Redirect to the dashboard
            else:
                messages.error(request, 'You are not authorized as staff.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'cart/staff_login.html', {'form': form})
def staff_dashboard(request):
    query = request.GET.get('q', '')
    orders = Order.objects.select_related('customer', 'menu_item')

    if query:
        orders = orders.filter(
            Q(customer__username__icontains=query) |
            Q(menu_item__name__icontains=query)
        )

    context = {
        'orders': orders.order_by('-id'),
        'new_orders_count': orders.filter(status='pending').count(),
    }
    return render(request, 'cart/staff_dashboard.html', context)


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




def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # Get user profile if logged in
    profile = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None

    return render(request, "checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "profile": profile,  # Pass profile to template
    })

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
