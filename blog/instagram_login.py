
from django.http import HttpResponse
import requests
from urllib.parse import urlencode
from django.shortcuts import redirect
from crashblog.settings import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET
from .models import Post
import urllib.request


def instagram_login(request):
    client_id = "1341312053390377"
    
    authorize_url = "https://api.instagram.com/oauth/authorize"
    if "https://www.blogifyar.pro" in request.build_absolute_uri() or "https://blogifyar.onrender.com" in request.build_absolute_uri():
        redirect_uri = "https://www.blogifyar.pro/redirect_uri3/"
    else:
        redirect_uri = "http://127.0.0.1:9000/redirect_uri3/"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        # Especifica los alcances que necesitas
        "scope": "public_profile user_profile pages_manage_posts publish_video instagram_basic"
    }

    return redirect(authorize_url + "?" + urlencode(params))


def handle_respuesta(request):
    code = request.GET.get('code')
    slug = request.session.get('slug')
    post = Post.objects.get(slug=slug)
    category_slug = request.session.get('category_slug')
    request.session['slug'] = slug
    request.session['category_slug'] = category_slug

    # Llama a la función twitter_callback()
    return instagram_callback(request, slug, code)

def instagram_callback(request, slug, code):
    client_id = INSTAGRAM_CLIENT_ID
    client_secret = INSTAGRAM_CLIENT_SECRET
    category_slug = request.session.get('category_slug')
    post = Post.objects.get(slug=slug)
    request.session['slug'] = slug
    slug = request.session.get('slug')
    # URL de redireccionamiento después de obtener el access_token
    if "https://www.blogifyar.pro" in request.build_absolute_uri() or "https://blogifyar.onrender.com" in request.build_absolute_uri():
        redirect_uri = "https://www.blogifyar.pro/redirect_uri3/"
    else:
        redirect_uri = "http://127.0.0.1:9000/redirect_uri3/"

    # Datos requeridos para obtener el access_token de Instagram
    client_id = client_id
    client_secret = client_secret
    grant_type = 'authorization_code'

    # Intercambiar el código de autorización por el access_token
    access_token_url = 'https://api.instagram.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': grant_type,
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.request('POST', access_token_url, data=data)

    if response.status_code == 200:
        # Extracción del access_token de la respuesta JSON
        access_token = response.json()['access_token']
        # Realizar la publicación en Instagram usando el access_token
       
        # Redirigir a una página de éxito
        request.session['access_token'] = access_token        
        print('SE CREÓ EL ACCESS TOKEN EXITOSAMENTE') 
        print('RESPUESTA ACCESS TOKEN:', access_token)
        post_to_instagram(request, slug, access_token)
    else:
        # Manejar el error de obtener el access_token
        return HttpResponse('No se obtuvo el ACCESS_TOKEN')
    access_token = request.session.get('access_token')
    return post_to_instagram(request, slug, access_token)

def post_to_instagram(request, slug, access_token):
    # Obtener la URL de la imagen del post
    post = Post.objects.get(slug=slug)
    image_url = request.build_absolute_uri(post.image.url)
    category_slug = request.get('category_slug')
    # Preparar los datos de la solicitud de publicación en Instagram
    url = 'https://graph.instagram.com/me/media'
    data = {
        'image_url': image_url,
        'caption': post.title,
        'access_token': access_token,
        'hashtags': ['Tech', 'BlogifyAR', '']
    }

    # Realizar la solicitud POST para publicar en Instagram
    response = requests.request('POST', url, data=data)

    if response.status_code == 200:
        # Manejar la respuesta exitosa
        print('Publicación exitosa en Instagram')
    else:
        # Manejar el error de publicación en Instagram
        print('Error al publicar en Instagram:', response.json())
        
    return redirect('post_detail', category_slug=category_slug, slug=slug)
