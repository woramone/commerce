from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models import Max


class User(AbstractUser):
    firstname = models.CharField(max_length=64, null=True)
    lastname = models.CharField(max_length=64, null=True)
    user_name = models.CharField(max_length=64, null=True)
    password = models.CharField(max_length=64, null=True)
    email = models.EmailField()

    def __str__(self):
       return self.username

class Listing(models.Model):
    CATEGORY_CHOICES = (
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Other', 'Other')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
           max_length=20,
           choices=CATEGORY_CHOICES
       )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', null=True, blank=True)
    image = models.CharField(max_length=5000, null=True, blank=True)

    def current_price(self):
        list = Bid.objects.filter(auction=self).aggregate(Max('amount'))
        return list

    def num_bids(self):
        return len(self.bids.all())

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    def __str__(self):
        return f'{self.amount} on {self.auction} by {self.user.username}'

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return f"{self.user}'s watchlist"

class Comment(models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f'{self.user}: {self.text}'