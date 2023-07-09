from django.urls import path
from .views import PostCreateView, PostUpdateView, PostDeleteView
from . import views
from django.urls.conf import include

url_patterns = [    
    path('search/', views.search, name='search'),
    path('create/', PostCreateView.as_view(), name='create'),
    path('update/<slug:slug>', PostUpdateView.as_view(), name='update'),
    path('delete-post/<slug:slug>', PostDeleteView.as_view(), name='delete'),
    path('<slug:category_slug>/<slug:slug>', views.post_detail, name='post_detail'),
    path('<slug:slug>', views.category, name='category_detail'),
    path('handle_linkedin_response/<code>', views.handle_linkedin_response, name='handle_linkedin_response'),
    path('login-linkedin/', views.login_linkedin, name='login_linkedin'),
    path('redirect_uri/', views.redirect_uri, name='redirect_uri'),
    path('redirect_uri/handle_code/', views.handle_linkedin_response, name='handle_code'),    
    path('twitter_login/', views.twitter_login, name='twitter_login'),
    path('redirect_uri2/', views.handle_resp, name='redirect_uri2'),    
    path('redirect_uri2/handle_twitter_code/', views.twitter_callback, name='handle_twitter_code'),   
]