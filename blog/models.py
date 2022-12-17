from django.db import models
from ckeditor.fields import RichTextField
from django.template.defaultfilters import slugify
class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True)
            
    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % self.slug

class Post(models.Model):
    ACTIVE = 'active'
    DRAFT = 'draft'

    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DRAFT, 'Draft')
    )

    category = models.ForeignKey(Category, related_name='posts', verbose_name="Category", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(verbose_name="Slug", null=False, unique=True)
    intro = models.TextField(verbose_name="Intro")
    body = models.TextField(verbose_name="Body")
    status = models.CharField(max_length=10, verbose_name="Status", choices=CHOICES_STATUS, default=ACTIVE)
    image = models.ImageField(upload_to='uploads/', verbose_name="Image", blank=True, null=True)
    clip = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name="Clip", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/%s' % (self.category.slug, self.slug)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    body = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    # def __str__(self):
    #     return 'Comment {} by {}'.format(self.name, self.email)