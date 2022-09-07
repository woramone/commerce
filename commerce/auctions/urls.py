from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("create", views.create_listing, name="create"),
    path("listing/<int:auction_id>", views.listing, name="listing"),

    path('add_watchlist/<int:auction_id>/', views.add_watchlist, name='add_watchlist'),
    path('watchlist/', views.watchlist, name='watchlist'),
    
    path('bid_update/<int:auction_id>/', views.bid_update, name='bid_update'),
    path('close_bid/<int:auction_id>/', views.close_bid, name='close_bid'),

    path('comment/<int:auction_id>', views.comment, name='comment'),
    
    path('category/<path:category>', views.category, name='category'),
]
