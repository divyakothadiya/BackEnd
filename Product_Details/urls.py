from django.urls import path
from .views import ProductCreateView,ProductListView,PDUpdateView

urlpatterns = [
    path('product-create/', ProductCreateView.as_view(), name='product-create'),
    path('product-list/', ProductListView.as_view(), name='product-list'),
    path('product-update/', PDUpdateView.as_view(), name='product-update'),
]
