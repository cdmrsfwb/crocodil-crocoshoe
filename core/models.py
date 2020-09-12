from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import inflect
p = inflect.engine()


class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    image = models.CharField(max_length=30)
    image_desc = models.CharField(max_length=50)
    price = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1_000_000)])
    slug = models.SlugField()

    size = models.CharField(
        max_length=1,
        choices=(('S', 'Small'), ('M', 'Medium'), ('B', 'Big')),
        default='S',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={'slug': self.slug})

    class Meta:
        ordering = ['price']


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}pcs"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.items.count()} {p.plural('item', self.items.count())}"

    def subtotal(self):
        return sum([oi.quantity * oi.item.price for oi in self.items.all()])


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1_000_000)], default=2_000)

    def __str__(self):
        return self.user.username


def create_player_and_order(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        player = Player(user=user)
        player.save()
        order = Order(user=user)
        order.save()


post_save.connect(create_player_and_order, sender=User)
