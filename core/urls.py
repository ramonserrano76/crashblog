from django.urls import path
from . import views
from django.urls import path, include
from registration.views import SignUpView
from views import RedirectDomainView

urlpatterns = [
    path('', RedirectDomainView.as_view(), name='home'), 
    path('', views.frontpage, name="frontpage"),
    path('signup/', SignUpView.as_view(), name='signup'),
     
]


