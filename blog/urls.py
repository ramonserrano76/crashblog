from django.urls import path
from .views import PostCreateView, PostUpdateView, PostDeleteView
from . import views

url_patterns = [
    path('search/', views.search, name='search'),
    path('create/', PostCreateView.as_view(), name='create'),
    path('update/<slug:slug>', PostUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', PostDeleteView.as_view(), name='delete'),
    path('<slug:category_slug>/<slug:slug>', views.post_detail, name='post_detail'),
    path('<slug:slug>', views.category, name='category_detail'),
    
]
