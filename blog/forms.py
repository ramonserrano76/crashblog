from .models import Category, Post
from django import forms
from ckeditor.fields import RichTextField
from .models import Comment
from upload_validator import FileTypeValidator

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].disabled = False
        self.fields['email'].disabled = False

       # OR set readonly widget attribute.
        # self.fields['name'].widget.attrs['readonly'] = True
        # self.fields['email'].widget.attrs['readonly'] = True

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__" #['category', 'title', 'slug', 'intro', 'body', 'status', 'image', 'clip']
        # image = forms.FileField(label='image', help_text="Formats accepted: JPEG nd PNG", required=False, validators=[FileTypeValidator(allowed_types=['image/jpeg', 'image/png'])])
        # clip = forms.FileField(label='clip', help_text="Formats accepted: JPG nd WEBM", required=False, validators=[FileTypeValidator(allowed_types=['video/mp4', 'video/webm'])])
        
        widgets = {
        #     'category': forms.ModelChoiceField(queryset=Category.objects.all(), to_field_name='category'),
        #     'title': forms.CharField(),
        #     'slug': forms.SlugField(),
        #     'intro': forms.CharField(),
        #     'body': RichTextField(),
        #     'status': forms.CharField(),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file mt-3'}),
            'clip': forms.ClearableFileInput(attrs={'class ': 'form-control-file mt-3'}),


        }
        labels = {
            'category': 'category', 'title': 'Title', 'slug': 'Slug', 'intro': 'Intro', 'body': 'Body', 'status': 'Status', 'image': 'Image', 'clip': 'Clip'
        }
