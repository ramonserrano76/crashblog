import base64
import hashlib
import secrets
from django.shortcuts import redirect
import random
import string
from crashblog.settings import DEFAULT_IMAGE_URL, REDIRECT_URI
from .models import Post, Category
import os
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from .forms import CommentForm, PostForm, CategoryForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import json
import requests
from django.contrib import messages
from django.contrib.sessions.models import SessionManager, Session
from django.contrib.sessions.backends.base import SessionBase
import urllib.parse
from urllib.parse import urlencode, urlparse, unquote, quote
import urllib.request
from blog.twitter_login import *
from blog.linkedin_login import *
from blog.instagram_login import *


def post_form(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            remote_image_url = form.cleaned_data['remote_image_url']
            remote_clip_url = form.cleaned_data['remote_clip_url']

            if remote_image_url:
                post.image = remote_image_url
                post.clip = None  # Limpiar el campo de archivo de clip

            if remote_clip_url:
                post.clip = remote_clip_url
                post.image = None  # Limpiar el campo de archivo de imagen

            post.save()
            return HttpResponse('uploads')
        else:
            print('Form not valid')
    else:
        form = PostForm()

    return render(request, "blog/post_form.html", {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('frontpage')


@method_decorator(staff_member_required, name='dispatch')
class PostUpdateView(UpdateView):
    template_name = 'blog/post_update_form.html'
    model = Post
    form_class = PostForm
    template_name_suffix = '_update_form'

    # def get_success_url(self):
    #     return reverse('update', args=[self.object.slug]) + '?ok'

    def get_object(self):
        return Post.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('update', args=[self.get_object().slug]) + '?ok'


@method_decorator(staff_member_required, name='dispatch')
class PostDeleteView(DeleteView):
    template_name = 'blog/post_confirm_delete.html'
    model = Post
    success_url = reverse_lazy('frontpage')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        posts = get_object_or_404(Post, slug=kwargs['slug'])
        # Elimina los archivos de imagen y video asociados al post
        if posts.image:
            image_path = os.path.join(
                settings.MEDIA_ROOT, posts.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
            posts.image.storage.delete(posts.image.name)  # borrado fisico

        if posts.clip:
            clip_path = os.path.join(
                settings.MEDIA_ROOT, posts.clip.name)
            if os.path.exists(clip_path):
                os.remove(clip_path)
            posts.image.storage.delete(posts.clip.name)  # borrado fisico

        posts.delete()
        return HttpResponseRedirect(success_url)


def post_detail(request, category_slug, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.ACTIVE)
    # define la variable slug
    slug = post.slug
    # guarda la variable slug en session para invocarla más adelante
    request.session['slug'] = slug
    # define la variable category_slug
    category_slug = post.category.slug
    # guarda la variable category_slug para invocarla más adelante
    request.session['category_slug'] = category_slug
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            return redirect('post_detail', category_slug=category_slug, slug=slug)
    else:
        form = CommentForm(initial={
            "name": request.user.username if request.user.is_authenticated else "request.user",
            "email": request.user.email if request.user.is_authenticated else "user@user.com"
        })
    return render(request, 'blog/post_detail.html', {'form': form, 'post': post})


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category, status=Post.ACTIVE).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'blog/category.html', {'category': category, 'posts': posts, 'categories': categories})


def search(request):
    query = request.GET.get('query', '')

    posts = Post.objects.filter(status=Post.ACTIVE).filter(
        Q(title__icontains=query) | Q(intro__icontains=query) | Q(body__icontains=query))

    return render(request, 'blog/search.html', {'posts': posts, 'query': query})