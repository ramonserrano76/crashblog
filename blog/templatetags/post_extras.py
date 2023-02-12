from django import template
from blog.models import Post, Category

register = template.Library()


@register.simple_tag
def get_page_list():
    posts = Post.objects.all()
    return posts


@register.simple_tag
def get_category_list():
    categories = Category.objects.all()
    return categories
