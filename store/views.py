from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)
        subtotal = product.price * quantity
        total += subtotal

        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(
        request,
        'store/cart.html',
        {
            'products': products,
            'total': total
        }
    )


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        del cart[str(pk)]

    request.session['cart'] = cart
    return redirect('cart')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')

    else:
        form = UserCreationForm()

    return render(
        request,
        'store/register.html',
        {
            'form': form
        }
    )


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    products = []
    total = 0

    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)
        subtotal = product.price * quantity
        total += subtotal

        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total=total
        )

        for item in products:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        request.session['cart'] = {}
        return redirect('order_success')

    return render(
        request,
        'store/checkout.html',
        {
            'products': products,
            'total': total
        }
    )


def order_success(request):
    return render(request, 'store/order_success.html')


def remove_one(request, pk):
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        if cart[str(pk)] > 1:
            cart[str(pk)] -= 1
        else:
            del cart[str(pk)]

    request.session['cart'] = cart
    return redirect('cart')