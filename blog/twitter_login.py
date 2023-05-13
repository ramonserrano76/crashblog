import os
from crashblog.settings import BASE_DIR, CLIENT_ID, CLIENT_SECRET, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_short
import tweepy
import tempfile
import base64
import hashlib
import json
import random
import secrets
from django.shortcuts import redirect
from .models import Post
from django.http import HttpResponse
import requests
import urllib.parse
from urllib.parse import urlencode
import urllib.request
from configparser import SafeConfigParser
import datetime
from dotenv import load_dotenv
import time
import shutil
dotenv_path = BASE_DIR / 'crashblog' / '.env'
# SECCION PARA POSTEAR EL TWITTER #
# Define a function to generate a random code_verifier and its corresponding code_challenge


def generate_code_verifier_and_challenge():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = urllib.parse.quote_plus(base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8'))
    return code_verifier, code_challenge
code_challenge, code_verifier = generate_code_verifier_and_challenge()

def twitter_login(request):
    # Set up the OAuth 2.0 credentials
    
    client_id = str(CLIENT_ID)
    client_secret = str(CLIENT_SECRET)
    # str(REDIRECT_URI_3)
    redirect_uri = "https://www.blogifyar.pro/redirect_uri2/" #"http://127.0.0.1:9000/redirect_uri2/" # #  
    # Define the URL for the authorization endpoint
    authorize_url = "https://twitter.com/i/oauth2/authorize"
    # Define the parameters for the authorization request
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        # Replace with your desired scope
        "scope": "tweet.read tweet.write users.read tweet.moderate.write users.read follows.read follows.write",
        "state": "state",
        "code_challenge": "code_challenge",
        "code_challenge_method": "plain"
    }
    # Redirect the user to the authorization endpoint
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    return redirect(authorize_url + "?" + urlencode(params))

    # Redirigir al usuario a la URL de autorización
    # authorize_url2 = f"{authorize_url}?{urlencode(params)}"
    # return HttpResponse(status=302, headers={'Location': authorize_url2})


def handle_resp(request):
    code = request.GET.get('code')
    slug = request.session.get('slug')
    # Llama a la función twitter_callback()
    return twitter_callback(request, slug, code)


def twitter_callback(request, slug, code):

    # Retrieve the authorization code from the callback URL
    code = request.GET.get('code')
    print("RESPUESTA CODE", code)
    if code is None:
        return HttpResponse("No se recibió código de autorización.")

    category_slug = request.session.get('category_slug')
    post = Post.objects.get(slug=slug)
    # Set up the OAuth 2.0 credentials
    client_id = str(CLIENT_ID)
    client_secret = str(CLIENT_SECRET)
    # str(REDIRECT_URI_3)
    # str("https://www.blogifyar.pro/redirect_uri2/") #
    redirect_uri = "http://127.0.0.1:9000/redirect_uri2/"

    # Define the URL for the access token endpoint
    token_url = "https://api.twitter.com/2/oauth2/token"

    # Define the parameters for the access token request
    params2 = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        # "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code_verifier": "code_challenge"
    }

    # Codificar las credenciales en base64
    creds = f"{client_id}:{client_secret}"
    creds_b64 = base64.b64encode(creds.encode()).decode()

    headers = {
        'Authorization': f'Basic {creds_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # # Send the access token request
    
    # Send request to Twitter API to get access token
    response = requests.post(token_url, data=params2, headers=headers)

    # Parse the response to get the access token
    if response.status_code == 200:
        # Try to extract access token from response
        access_token = response.json()['access_token']
        print('RESPUESTA ACCESS TOKEN:', response.text)
        
        return post_tweet_with_image(request, slug, access_token)
    else:
        # Mostrar un mensaje de error si la petición no fue exitosa
        return HttpResponse("Error al obtener el access token de twitter")


def post_tweet_with_image(request, slug, access_token):

    # URL para publicar el tweet
    tweet_url = 'https://api.twitter.com/2/tweets'
    
    # Cabeceras para la autenticación con el token de acceso
    headers = {"Authorization": f'Bearer {access_token}',
               "User-Agent": "v2CreateTweetPY",
               "Content-Type": "application/json",
               "Content-Length": "128",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept": "*/*",
               "Connection": "keep-alive",
               }

    # Obtener la URL de la imagen y el objeto POST para acceder al contenido del post
    post = Post.objects.get(slug=slug)
    image_url = request.build_absolute_uri(post.image.url)

    # Descargar la imagen desde la URL
    responseup = requests.get(image_url)

    # Obtener los bytes de la imagen
    image_bytes = responseup.content
    total_bytes = len(image_bytes)
    print('total_bytes:', total_bytes)

    # Obtener el nombre y extensión del archivo original
    file_name = os.path.basename(post.image.name)
    file_name_without_ext, file_ext = os.path.splitext(file_name)

    # Crear un archivo temporal con el mismo nombre y extensión del archivo original
    temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
    temp_file.write(image_bytes)
    temp_file.close()

    print('NOMBRE DE IMAGEN:', temp_file.name)

    # Obtener el media_type según la extensión del archivo
    if file_ext.startswith("."):
        file_ext = file_ext[1:]  # Eliminar el punto inicial si existe

    # Utilizar la extensión del archivo en el parámetro media_type
    media_type = f"image/{file_ext}"

    # Configurar las credenciales de acceso a la API de Twitter
    consumer_key = str(CONSUMER_KEY)
    consumer_secret = str(CONSUMER_SECRET)
    access_token = str(ACCESS_TOKEN)
    access_token_secret = str(ACCESS_TOKEN_SECRET)

    # Autenticar con las credenciales
    # # Ruta de la imagen o video que deseas subir
    absolute_path = os.path.abspath(temp_file.name)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Crear una instancia de la API de Twitter
    api = tweepy.API(auth)
    
    # Ruta del archivo de imagen a subir
    image_path = absolute_path
    file = open(image_path, 'rb')
    # Subir la imagen a Twitter
    media = api.media_upload(filename=image_path, file=file)
    if media is not None:
        media_ids = [media.media_id_string]
    else:
    # Manejo del caso cuando media es None
        media_ids = []    
    # Obtener el media_id de la imagen subida
    media_id = str(media_ids[0])
    # Imprimir el media_id
    print('MEDIA_ID:', media_id)
    #api.update_status(status="Test Tweet", media_ids=media_ids)
    
    # Función para acortar el enlace utilizando Bitly
    def shorten_url(url):
        # Reemplaza con tu access token de Bitly
        ACCESS_TOKEN_SHORT = str(ACCESS_TOKEN_short)
        api_url = f'https://api-ssl.bitly.com/v4/shorten'

        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN_SHORT}',
            'Content-Type': 'application/json'
        }

        payload = {
            'long_url': url
        }

        response = requests.request('POST', api_url, headers=headers, json=payload)
        data = response.json()

        if 'id' in data:
            return data['id']
        else:
            return url


    # Longitud máxima permitida para el mensaje de Twitter
    MAX_TWEET_LENGTH = 280

    # Acortar el enlace original con Bitly
    # Obtener la URL completa del post
    url = request.build_absolute_uri(post.get_absolute_url())

    # Verificar si la URL comienza con 'http://127.0.0.1:9000'
    if url.startswith('http://127.0.0.1:9000'):
        # Reemplazar la parte inicial de la URL por 'https://www.blogifyar.pro'
        url = 'https://www.blogifyar.pro' + url[len('http://127.0.0.1:9000'):]

    shortened_url = str(shorten_url(url))
    print('SHORTEN URL:', shortened_url)
    # Acortar el título si excede la longitud máxima
    # Obtener el título acortado del post
    shortened_title = post.title[:MAX_TWEET_LENGTH - len(shortened_url) - 3] + '...' if len(
    post.title) > MAX_TWEET_LENGTH - len(shortened_url) - 3 else post.title

    # Crear el texto del tweet
    tweet_text = f'{shortened_title} | {shortened_url}'    
    
    # Parámetros del tweet
    palabras = ['hola', 'adios', 'buenos dias',
                'buenas tardes', 'buenas noches']
    frases = ['El éxito es la suma de pequeños esfuerzos repetidos día tras día.',
              'No te rindas, cada día es una nueva oportunidad para triunfar', 'La paciencia es la madre de la ciencia']

    palabra_aleatoria = random.choice(palabras)
    frase_aleatoria = random.choice(frases)
    tweet_text1 = f'{palabra_aleatoria} {frase_aleatoria}'
    # with open('archivo.json', 'r') as f:
    #     data2 = json.load(f)
    # "text": f"{palabra_aleatoria} {frase_aleatoria}"
    data2 = {
        "text": tweet_text, "media": {
            "media_ids": [media_id]}
        
    }
    payload = json.dumps(data2)
    print('FileType:', type(payload))

    # Publicar el tweet
    tweet_response = requests.request("POST", tweet_url, headers=headers, data=payload)
    print(tweet_response.text)
    # Comprobar la respuesta del tweet
    if tweet_response.status_code == 201:
        print('El tweet se ha publicado correctamente.')
        # Eliminar el archivo temporal cuando hayas terminado de usarlo
        
    else:
        print(f'Error al publicar el tweet: {tweet_response.text}')

    # Obtener el objeto datetime actual
    now = datetime.datetime.now()
    # Obtener el timestamp actual en segundos
    timestamp = round(now.timestamp())
    print(timestamp)
    
    
    # try:
    #     # Intentar eliminar el archivo
    #     os.remove(temp_file.name)
    # except PermissionError:
    #     time.sleep(5)
    #     # Si ocurre un error de permisos, intentar forzar el borrado con shutil
    #     shutil.rmtree(temp_file.name, ignore_errors=True)
        
    # Redirigir al detalle del post
    category_slug = request.session.get('category_slug')
    return redirect('post_detail', category_slug=category_slug, slug=slug)