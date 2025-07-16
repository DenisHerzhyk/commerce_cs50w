from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("all/", views.all, name="all"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories/", views.categories, name="categories"),
    path("category/<category>/", views.category, name="category"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist_add/<int:listing_id>/", views.watchlist_add, name="watchlist_add"),
    path("watchlist_remove/<int:listing_id>/", views.watchlist_remove, name="watchlist_remove"),
    path("create/", views.create, name="create"),
    path("listing/<int:listing_id>/", views.listing, name="listing"),
    path("bid/<int:listing_id>/", views.bid, name="bid"),
    path("comment/<int:listing_id>/", views.comment, name="comment"),
    path("unactivate/<int:listing_id>/", views.unactivate, name="unactivate"),
]
