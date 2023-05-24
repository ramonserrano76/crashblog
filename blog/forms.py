from .models import Category, Post, Comment
from django import forms
from ckeditor.fields import RichTextField



class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].disabled = False  # OJO
        self.fields['email'].disabled = False # OJO
        
       # OR set readonly widget attribute.
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        # self.fields['email'].widget.attrs['default'] = 'mail@mail.com' OJO 
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class PostForm(forms.ModelForm):  
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # self.fields['slug'].widget.attrs['readonly'] = True
        # self.fields['slug'].widget.attrs['editable'] = False
        # self.fields['slug'].disabled = True

    
    def clean_slug(self):
        return self.cleaned_data['title'].lower().replace(' ', '-')

    
    
    class Meta:
        model = Post
        fields = ['category', 'title', 'intro', 'body', 'status',
                  'image', 'clip', 'remote_image_url', 'remote_clip_url']
        
        # image = forms.FileField(label='image', help_text="Formats accepted: JPEG nd PNG", required=False, validators=[FileTypeValidator(allowed_types=['image/jpeg', 'image/png'])])
        # clip = forms.FileField(label='clip', help_text="Formats accepted: JPG nd WEBM", required=False, validators=[FileTypeValidator(allowed_types=['video/mp4', 'video/webm'])])
        
        
        widgets = {           
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file mt-3'}),
            'clip': forms.ClearableFileInput(attrs={'class ': 'form-control-file mt-3'}),                        
            }
        labels = {
            'category': 'category', 'title': 'Title', 'slug': 'Slug', 'intro': 'Intro', 'body': 'Body', 'status': 'Status', 'image': 'Image', 'clip': 'Clip', 'image': 'Image', 'clip': 'Clip'
        }
        
class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = Category
        fields = ['name']        
        labels = { 'name': 'Name', 'slug': 'Slug' }  
    
