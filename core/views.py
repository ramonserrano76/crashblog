from django.http.response import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from urllib.parse import urlparse, urlunparse
from blog.models import Post
from django.urls import reverse
from django.views.generic import View

class RedirectDomainView(View):
    FROM_DOMAIN = 'yourusername.pythonanywhere.com'
    TO_DOMAIN = 'www.yourdomain.com'

    def dispatch(self, request, *args, **kwargs):
        if request.get_host() == self.FROM_DOMAIN:
            return redirect(f"{self.TO_DOMAIN}{request.path}", permanent=True)
        return super().dispatch(request, *args, **kwargs)
    
def frontpage(request):
    posts = Post.objects.filter(status=Post.ACTIVE)

    return render(request, 'core/frontpage.html', {'posts': posts})

def about(request):
    return render(request, 'core/about.html')

def robots_txt(request):
    text = [
        "User-Agent: *",
        "Disallow: /admin/",
    ]
    return HttpResponse("\n".join(text), content_type="text/plain")


