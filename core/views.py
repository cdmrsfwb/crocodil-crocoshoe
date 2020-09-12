from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import *


class HomeView(ListView):
    paginate_by = 10
    template_name = 'home.html'

    def get_queryset(self):
        if 'size' in self.kwargs:
            return Item.objects.filter(size=self.kwargs['size'])
        return Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'size' in self.kwargs:
            context['size'] = self.kwargs['size']
        else:
            context['size'] = 'A'
        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, ordered=False)[0]
        return render(self.request, 'order_summary.html', {'order': order})


class ProfileView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        context = []
        for item in Item.objects.all():
            context.append({})
            context[-1]['item'] = item
            order_item_qs = OrderItem.objects.filter(user=self.request.user, item=item, ordered=True)
            if order_item_qs.exists():
                context[-1]['number_owned'] = order_item_qs[0].quantity
            else:
                context[-1]['number_owned'] = 0
        return render(self.request, 'profile.html', {'object_list': context})


def about(request):
    return render(request, 'about.html')


def clicky(request):
    return render(request, 'clicky.html', {'clicked': False})


def get_richer(request):
    request.user.player.credit += 100
    request.user.player.save()
    return redirect("core:iamrichnow")


def iamrichnow(request):
    return render(request, 'clicky.html', {'clicked': True})


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )

    # check if there already is an active order for the current user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # if yes, check if the item being ordered is already in the order. if yes, increase quantity
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.quantity < 10:
                order_item.quantity += 1
                order_item.save()
                messages.success(request, f"{order_item.item} was added to your cart.")
            else:
                messages.warning(request, "You cannot order more than 10 of these at once.")

        # if it isn't, add it
        else:
            order.items.add(order_item)
            messages.success(request, f"{order_item.item} was added to your cart.")

    # if there is no active order for the current user, create it
    else:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
        messages.success(request, f"{order_item.item} was added to your cart.")

    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    # check if there is an active order for the current user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # if yes, check if the item being deleted is in the order. if yes, delete it
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.success(request, f"{order_item.item} was removed from your cart.")
            order_item.delete()

    return redirect("core:order-summary")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    # check if there is an active order for the current user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # if yes, check if the item being deleted is in the order. if yes, delete it
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.success(request, f"{order_item.item} was removed from your cart.")
            else:
                order.items.remove(order_item)
                messages.success(request, f"{order_item.item} was removed from your cart.")
                order_item.delete()

    return redirect("core:order-summary")


@login_required
def checkout(request):
    current_order = Order.objects.get(user=request.user, ordered=False)
    if request.user.player.credit < current_order.subtotal():
        messages.warning(request, "Insufficient funds")
        return redirect("core:order-summary")
    return render(request, 'checkout-page.html')


@login_required
def buy(request):
    current_order = Order.objects.get(user=request.user, ordered=False)
    if request.user.player.credit < current_order.subtotal():
        messages.warning(request, "Insufficient funds")
        return redirect("core:order-summary")
    request.user.player.credit -= current_order.subtotal()
    request.user.player.save()
    order_qs = Order.objects.filter(user=request.user, ordered=True)
    current_order_items = OrderItem.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order_stash = order_qs[0]
        for current_order_item in current_order_items:
            order_item_stash, created = OrderItem.objects.get_or_create(
                item=current_order_item.item,
                user=current_order_item.user,
                ordered=True
            )
            order_item_stash.quantity += current_order_item.quantity
            if created:
                order_item_stash.quantity -= 1
                order_stash.items.add(order_item_stash)
            order_item_stash.save()
            current_order.items.remove(current_order_item)
            current_order_item.delete()
    else:
        for current_order_item in current_order_items:
            current_order_item.ordered = True
            current_order_item.save()
        current_order.ordered = True
        current_order.save()
        Order.objects.create(user=request.user)
    return redirect("core:home")
