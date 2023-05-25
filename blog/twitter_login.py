import os
from io import BytesIO
from crashblog.settings import BASE_DIR, CLIENT_ID, CLIENT_SECRET, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_short
import tweepy
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
import datetime



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
    
    if "https://www.blogifyar.pro" in request.build_absolute_uri() or "https://blogifyar.onrender.com" in request.build_absolute_uri():
        redirect_uri = "https://www.blogifyar.pro/redirect_uri2/"
    else:
        redirect_uri = "http://127.0.0.1:9000/redirect_uri2/"

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
    post = Post.objects.get(slug=slug)
    category_slug = request.session.get('category_slug')
    request.session['slug'] = slug
    request.session['category_slug'] = category_slug
    
    # Llama a la función twitter_callback()
    return twitter_callback(request, slug, code)


def twitter_callback(request, slug, code):
    print('ENTRO EN LA FUNCION PARA OBTENER EL ACCESS TOKEN')
    # Retrieve the authorization code from the callback URL
    code = request.GET.get('code')
    print("RESPUESTA CODE", code)
    if code is None:
        return HttpResponse("No se recibió código de autorización.")

    category_slug = request.session.get('category_slug')
    post = Post.objects.get(slug=slug)
    request.session['slug'] = slug
    slug = request.session.get('slug')
    
    # Set up the OAuth 2.0 credentials
    client_id = str(CLIENT_ID)
    client_secret = str(CLIENT_SECRET)
    # str(REDIRECT_URI_3)
    # str() # 
    if "https://www.blogifyar.pro" in request.build_absolute_uri() or "https://blogifyar.onrender.com" in request.build_absolute_uri():
        redirect_uri = "https://www.blogifyar.pro/redirect_uri2/"
    else:
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
    response = requests.request('POST', token_url, data=params2, headers=headers)

    # Parse the response to get the access token
    if response.status_code == 200:
        # Try to extract access token from response
        access_token = response.json()['access_token']
        request.session['access_token'] = access_token
        print('RESPUESTA ACCESS TOKEN:', access_token)
        print('SE CREÓ EL ACCESS TOKEN EXITOSAMENTE')    
        
    else:
        # Mostrar un mensaje de error si la petición no fue exitosa
        return HttpResponse("Error al obtener el access token de twitter")
    access_token = request.session.get('access_token')
    return post_tweet_with_image(request, slug, access_token)


def post_tweet_with_image(request, slug, access_token):
    print('ENTRANDO EN LA FUNCION DE POST TWEET')
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
    slug = request.session.get('slug')
    category_slug = request.session.get('category_slug')
    # image_url = request.build_absolute_uri(post.image.url)
    print('A PUNTO DE DESCARGAR LA IMAGEN')
    # Descargar la imagen desde la URL
    # responseup = requests.get(image_url)
    if post.image:
        media_file = post.image
        with open(media_file.path, 'rb') as file:
            media_bytes = file.read()
    elif post.remote_image_url:
        media_file = post.remote_image_url
        response = requests.get(media_file)
        response.raise_for_status()
        media_bytes = response.content
    elif post.clip:
        media_file = post.clip
        with open(media_file.path, 'rb') as file:
            media_bytes = file.read()
    else:
        media_file = post.remote_clip_url
        response = requests.get(media_file)
        response.raise_for_status()
        media_bytes = response.content
    total_bytes = len(media_bytes)
    print('total_bytes:', total_bytes)
    # image_bytes = responseup.content
    # total_bytes = len(image_bytes)
    # print('total_bytes:', total_bytes)

    # Obtener el nombre y extensión del archivo
    if isinstance(media_file, str):  # Si es una URL
        file_name = os.path.basename(media_file)
    else:  # Si es un archivo local
        file_name = os.path.basename(media_file.path)


    file_name_without_ext, file_ext = os.path.splitext(file_name)

    # # Crear un archivo temporal con el mismo nombre y extensión del archivo original
    # print('CREANDO ARCHIVO TENPORAL Y LO ESCRIBE EN SERVER')
    # temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
    # temp_file.write(image_bytes)
    # temp_file.close()

    print('NOMBRE DE IMAGEN:', file_name) # media_file

    # Obtener el media_type según la extensión del archivo
    if file_ext.startswith("."):
        file_ext = file_ext[1:]  # Eliminar el punto inicial si existe
        print('EXTENSION:', file_ext)
    # Utilizar la extensión del archivo en el parámetro media_type
    # Verificar la extensión del archivo y asignar el tipo de media correspondiente
    if file_ext.lower() in ['jpg', 'jpeg', 'png', 'webp']:
        media_type = f"image/{file_ext}"
        media_category = "tweet_image"
    elif file_ext.lower() in ['mp4', 'avi', 'mov', 'webm']:        
        media_type = f"video/{file_ext}"
        media_category = "tweet_video"
    else:
        media_type = f"image/{file_ext}"
        media_category = "tweet_gif"
    print('media_category Y media_type:', media_category, media_type)
    # Configurar las credenciales de acceso a la API de Twitter
    consumer_key = str(CONSUMER_KEY)
    consumer_secret = str(CONSUMER_SECRET)
    access_token = str(ACCESS_TOKEN)
    access_token_secret = str(ACCESS_TOKEN_SECRET)

    # Autenticar con las credenciales
    # Ruta absoluta de la imagen o video que deseas subir
    if isinstance(media_file, str):
    # Si media_file es una URL o una cadena, usarla directamente como ruta absoluta
        absolute_path = media_file
    else:
        # Si media_file es una ruta de archivo local, obtener la ruta absoluta usando os.path.abspath()
        file_path = media_file.path
        absolute_path = os.path.abspath(file_path)
    print('Ruta absoluta:', absolute_path)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Crear una instancia de la API de Twitter
    api = tweepy.API(auth)
    

    # Ruta del archivo de imagen a subir
    # image_path = absolute_path
    # media_bytes_io = BytesIO(media_bytes)
    # # Subir la imagen a Twitter
    # media = api.media_upload(filename=file_name, file=media_bytes_io)
    # Ruta del archivo de media a subir
    
    media_file = absolute_path

    # Obtener el tamaño del archivo en bytes
    # def get_remote_file_size(url):
    #     response = requests.head(url)
    #     if 'Content-Length' in response.headers:
    #         file_size = int(response.headers['Content-Length'])
    #         return file_size
    #     else:
    #         return 0
    # if isinstance(media_file, str):   
    #     file_size = get_remote_file_size(media_file)
    # else:
    #     file_size = os.path.getsize(media_file) 
        
    image_threshold = 4*1024*1024  # 5 MB en bytes        
        
    # Verificar el tamaño del archivo
    if total_bytes <= image_threshold and media_category == 'tweet_image'  and not media_type == 'image/gif':
        media_bytes_io = BytesIO(media_bytes)
        # El archivo es lo suficientemente pequeño, realizar la carga directa
        media = api.media_upload(filename=file_name, file=media_bytes_io, media_category=media_category)
    elif total_bytes <= 15*1024*1024 and media_category == 'tweet_image' and media_type == 'image/gif':
        # El archivo es pequeño, pero es un gif, realizar la carga directa
        media_bytes_io = BytesIO(media_bytes)
        media = api.media_upload(filename=file_name, file=media_bytes_io, media_category=media_category)
    else:
        # El archivo es grande, realizar la carga fraccionada
            media_bytes_io = BytesIO(media_bytes)
            # Iniciar la carga fraccionada
            response = api.chunked_upload_init(total_bytes=media_bytes, media_type=media_type, media_category=media_category)
            media_id = response['media_id']

            # Enviar los fragmentos del archivo
            segment_id = 0
            while True:
                chunk = media_bytes_io.read(4*1024*1024)  # Leer fragmento de 5 MB
                if not chunk:
                    break
                response = api.chunked_upload_append(media_id, segment_id, chunk)
                segment_id += 1
                print('segment_id:', segment_id)
            # Finalizar la carga fraccionada
            media = api.chunked_upload_finalize(media_id)
            
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
    
    return redirect('post_detail', category_slug=category_slug, slug=slug)