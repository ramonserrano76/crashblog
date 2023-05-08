import base64
import hashlib
import json
import random
import secrets
from django.shortcuts import redirect
from .models import Post
from django.shortcuts import redirect
from django.http import HttpResponse
import requests
import urllib.parse
from urllib.parse import urlencode
import urllib.request


# SECCION PARA POSTEAR EL TWITTER #
# Define a function to generate a random code_verifier and its corresponding code_challenge
def generate_code_verifier_and_challenge():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = urllib.parse.quote_plus(base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8'))
    return code_verifier, code_challenge


def twitter_login(request):
    # Set up the OAuth 2.0 credentials
    code_challenge, code_verifier = generate_code_verifier_and_challenge()
    client_id = "Njl1eG1MTkREM1J3UjVzWHBIRTc6MTpjaQ"
    client_secret = "LXd4FQxX0jVLarw8NStx4gtxGyHaXyk5uCpFxWv2xBHgRB1GhF"
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
    client_id = "Njl1eG1MTkREM1J3UjVzWHBIRTc6MTpjaQ"
    client_secret = "LXd4FQxX0jVLarw8NStx4gtxGyHaXyk5uCpFxWv2xBHgRB1GhF"
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
    # response = requests.post(token_url, data=params2, headers=headers)
    # Send request to Twitter API to get access token
    response = requests.post(token_url, data=params2, headers=headers)

    # Parse the response to get the access token
    if response.status_code == 200:
        # Try to extract access token from response
        access_token = response.json()['access_token']
        print('RESPUESTA ACCESS TOKEN:', response.text)
        # Parse the response to extract the access token
        # access_token = response.json()["access_token"]
        return post_tweet_with_image(request, slug, access_token)
    else:
        # Mostrar un mensaje de error si la petición no fue exitosa
        return HttpResponse("Error al obtener el access token de twitter")


def post_tweet_with_image(request, slug, access_token):

    # URL para publicar el tweet
    tweet_url = 'https://api.twitter.com/2/tweets'

    # URL para cargar la imagen
    upload_url = 'https://upload.twitter.com/1.1/media/upload.json'

    # Cabeceras para la autenticación con el token de acceso
    headers = {"Authorization": f'Bearer {access_token}',
               "User-Agent": "v2CreateTweetPY",
               "Content-Type": "application/json",
               "Content-Length": "128",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept": "*/*",
               "Connection": "keep-alive",
               }

    headers3 = {'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                }

    # Obtener la URL de la imagen
    post = Post.objects.get(slug=slug)
    image_url = request.build_absolute_uri(post.image.url)

    # Descargar la imagen desde la URL
    response = requests.get(image_url)

    # Obtener los bytes de la imagen
    image_bytes = response.content
    total_bytes = len(image_bytes)
    print('total_bytes:', total_bytes)

    # # Cargar la imagen en Twitter
    # files = {'command': 'INIT',
    #          'total_bytes': f'{total_bytes}',
    #          'media_type': 'image/jpeg',
    #          'media_category': 'tweet_image'
    #          }
    # media_response = requests.post(upload_url, headers=headers3, data=files)
    # print('STATUS_CODE:', media_response.status_code)
    # print('RESPONSE_JSON:', media_response.json())

    # media_id = media_response.json()['media_id']
    # print('MEDIA_ID:', media_id)

    # Tweet con imagen
    tweet_text = str(request.build_absolute_uri(post.get_absolute_url()))

    # Parámetros del tweet
    palabras = ['hola', 'adios', 'buenos dias',
                'buenas tardes', 'buenas noches']
    frases = ['El éxito es la suma de pequeños esfuerzos repetidos día tras día.',
              'No te rindas, cada día es una nueva oportunidad para triunfar', 'La paciencia es la madre de la ciencia']

    palabra_aleatoria = random.choice(palabras)
    frase_aleatoria = random.choice(frases)
    tweet_text = f'{palabra_aleatoria} {frase_aleatoria}'
    # with open('archivo.json', 'r') as f:
    #     data2 = json.load(f)
    data2 = {
        "text": f"{palabra_aleatoria} {frase_aleatoria}"
    }
    payload = json.dumps(data2)
    print(type(payload))

    # Publicar el tweet
    tweet_response = response = requests.request("POST", tweet_url, headers=headers, data=payload)

    # Comprobar la respuesta del tweet
    if tweet_response.status_code == 201:
        print('El tweet se ha publicado correctamente.')
    else:
        print(f'Error al publicar el tweet: {tweet_response.text}')

    # Redirigir al detalle del post
    category_slug = request.session.get('category_slug')
    return redirect('post_detail', category_slug=category_slug, slug=slug)