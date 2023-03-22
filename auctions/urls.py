from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("greeting", views.greeting, name="greeting"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("category", views.categories, name="categories"),
    path("category/<str:name>", views.category, name="category"),
    path("listing/<str:id>", views.listing, name="listing"),
    path("removefromWatchlist/<str:id>", views.removefromWatchlist, name="removefromWatchlist"),
    path("addtoWatchlist/<str:id>", views.addtoWatchlist, name="addtoWatchlist"),
    path("watchlist", views.display_watchlist, name="display_watchlist"),
    path("addComment/<str:id>", views.addComment, name="addComment"),
    path("addBid/<str:id>", views.addBid, name="addBid"),
    path("closeAuction/<str:id>", views.closeAuction, name="closeAuction"),
]
