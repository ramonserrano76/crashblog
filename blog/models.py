from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.core.validators import URLValidator

class Category(models.Model):
    
    name = models.TextField(max_length=255, verbose_name='Name')
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/%s/' % self.slug
    
class Post(models.Model):
    ACTIVE = 'active'
    DRAFT = 'draft'

    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DRAFT, 'Draft')
    )

    category = models.ForeignKey(Category, related_name='posts', verbose_name='Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=400, verbose_name="Title")    
    slug = models.SlugField(unique=True, blank=True)           
    intro = models.TextField(verbose_name="intro", max_length=20000)
    body = RichTextField(verbose_name="body", max_length=20000)
    status = models.CharField(max_length=10, verbose_name="Status", choices=CHOICES_STATUS, default=ACTIVE)
    image = models.ImageField(upload_to='uploads/', verbose_name="Image", blank=True, )
    clip = models.FileField(upload_to='uploads/%Y/%m/%d/',
                            verbose_name="Clip", blank=True, )
    remote_image_url = models.URLField(blank=True, validators=[URLValidator()])
    remote_clip_url = models.URLField(blank=True, validators=[URLValidator()])
    created_at = models.DateTimeField(auto_now_add=True)
    
        
    class Meta:        
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/%s' % (self.category.slug, self.slug)    

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = self.generate_unique_slug(base_slug)
        return super().save(*args, **kwargs)

    def generate_unique_slug(self, base_slug):
        slug = base_slug
        suffix = 1

        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        return slug
    # def delete_post(self, slug=None, using=None, keep_parents=False):
    #     if self.image:
    #         self.image.storage.delete(self.image.name)  # borrado fisico
    #         super().delete()
    #     else:
    #         if self.clip:
    #             self.clip.storage.delete(self.clip.name)  # borrado fisico
    #             super().delete()
    #         else:
    #             if not self.image and not self.clip:                    
    #                 post = get_object_or_404(Post, slug=slug)
    #                 post.delete()
    #                 return redirect(self, 'frontpage')



    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=False, null=True)
    body = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    # def __str__(self):
    #     return 'Comment {} by {}'.format(self.name, self.email)