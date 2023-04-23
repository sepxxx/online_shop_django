from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('orders/', views.userOrders, name='orders'),
    path('detail/<int:prod_id>', views.detail, name='detail'),
    path('aboutbrand/', views.aboutbrand, name='aboutbrand'),
    path('faq/', views.faq, name='faq'),
]