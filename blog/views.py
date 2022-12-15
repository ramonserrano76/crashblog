from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .forms import CommentForm, PostForm
from .models import Post, Category
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

# def handle_uploaded_file(f):
#     with open('uploads/'+f.name, 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)

def post_form(request):    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse('uploads')
        print ('Form not valid')
    else:
        form = PostForm()    
    return render(request, "blog/post_form.html", {'form': form})

@method_decorator(staff_member_required, name='dispatch')
class PostDeleteView(DeleteView):
    template_name = 'blog/post_confirm_delete.html'
    model = Post
    success_url = reverse_lazy('frontpage')

@method_decorator(staff_member_required, name='dispatch')
class PostUpdateView(UpdateView):
    template_name = 'blog/post_update_form.html'
    model = Post
    form_class = PostForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('update', args=[self.object.slug]) + '?ok'

@method_decorator(staff_member_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('frontpage')


def post_detail(request, category_slug, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.ACTIVE)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            return redirect('post_detail',  category_slug=category_slug, slug=slug)
    else:
        user = request.user
        form = CommentForm()  #initial={"name": user.username, "email": user.email})
        return render(request, 'blog/post_detail.html', {'post': post, 'form': form})


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status=Post.ACTIVE).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'blog/category.html', {'category': category, 'posts': posts, 'categories': categories})


def search(request):
    query = request.GET.get('query', '')

    posts = Post.objects.filter(status=Post.ACTIVE).filter(
        Q(title__icontains=query) | Q(intro__icontains=query) | Q(body__icontains=query))

    return render(request, 'blog/search.html', {'posts': posts, 'query': query})


# def home_view(request):
#     context = {}
#     if request.method == "POST":
#         form = GeeksForm(request.POST, request.FILES)
#         if form.is_valid():
#             name = form.cleaned_data.get("name")
#             img = form.cleaned_data.get("geeks_field")
#             obj = GeeksModel.objects.create(
#                 title=name,
#                 img=img
#             )
#             obj.save()
#             print(obj)
#     else:
#         form = GeeksForm()
#     context['form'] = form
#     return render(request, "home.html", context)
