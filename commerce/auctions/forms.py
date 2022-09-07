from cProfile import label
from django import forms
from .models import Listing
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'category', 'image', 'price', 'starting_bid']

