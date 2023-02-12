from django.urls import path
from . import views
from django.urls import path, include
from registration.views import SignUpView


urlpatterns = [
    path('', views.frontpage, name="frontpage"),
    path('signup/', SignUpView.as_view(), name='signup'),    
]


