import oauthlib.oauth1
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
from urllib.parse import parse_qs, urlencode
import urllib.request
import os

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
    redirect_uri = "http%3A%2F%2F127.0.0.1%3A9000%2Fredirect_uri2%2F"
    # Cabeceras para la autenticación con el token de acceso
    headers = {"Authorization": f'Bearer {access_token}',
               "User-Agent": "v2CreateTweetPY",
               "Content-Type": "application/json",
               "Content-Length": "128",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept": "*/*",
               "Connection": "keep-alive",
               }
    
    # Obtener la URL de la imagen
    post = Post.objects.get(slug=slug)
    image_url = request.build_absolute_uri(post.image.url)

    # Descargar la imagen desde la URL
    responseup = requests.get(image_url)

    # Obtener los bytes de la imagen
    image_bytes = responseup.content
    total_bytes = len(image_bytes)
    print('total_bytes:', total_bytes)
    file_name = os.path.basename(post.image.name)
    print('IMAGEN:', file_name)
    import datetime
    # Obtener el objeto datetime actual
    now = datetime.datetime.now()
    # Obtener el timestamp actual en segundos
    timestamp = now.timestamp()
    print(timestamp)
    oauth_consumer_key = "ogKdSKDeBi1oiUtB8LZCnYzkw"
    oauth_consumer_secret = "XG2SKvAjLDUlnw8R8Ghbg747m7OS0SC0vapUmhsBYPFl94nuAM"    
    
    # URL para obtener  oauth_signature y luego oauth_token
    token_url = 'https://api.twitter.com/oauth/request_token'

    # Crear el objeto de firma OAuth1
    oauth_client = oauthlib.oauth1.Client(oauth_consumer_key, oauth_consumer_secret)


    paramssign = {
        'oauth_consumer_key': oauth_consumer_key,
        'oauth_nonce': "WQFRTfd",
        'oauth_timestamp': timestamp,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version': '1.0'
}
    # Generar la firma
    uri, headers, body = oauth_client.sign(token_url, 'POST', paramssign)
    
    # Obtener la firma de los headers
    oauth_signature = headers['Authorization'].split('oauth_signature="')[1].split('"')[0]
    print('OAuth Signature:', oauth_signature)
    
    # URL para obtener luego oauth_token
    token_url = 'https://api.twitter.com/oauth/request_token'
    paramstoken = {
            'oauth_callback': redirect_uri
        }
    headers2 = {
            'Authorization': f'OAuth oauth_consumer_key= {oauth_consumer_key}, oauth_nonce="WQFRTfd", oauth_signature= {oauth_signature}, oauth_signature_method="HMAC-SHA1", oauth_timestamp= {timestamp}, oauth_version="1.0"',
        }

    
    responsetoken = requests.request('POST', token_url, headers=headers2, params=paramstoken)
    response_text = responsetoken.text
    response_data = parse_qs(response_text)
    #oauth_token = response_data['oauth_token'][0]
    #oauth_token_secret = response_data['oauth_token_secret'][0]
    print('STAT_CODE_TOKEN_200:', responsetoken.status_code)
    print('Response_Token:', response_text)
    
    # URL para cargar la imagen   
    # upload_url = 'https://upload.twitter.com/1.1/media/upload.json'
    # headers3 = {
    #     'Authorization': f'OAuth oauth_consumer_key= {oauth_consumer_key}, oauth_token={oauth_token}, oauth_signature_method="HMAC-SHA1", oauth_timestamp= {timestamp}, oauth_nonce="WQFRTfd",oauth_version="1.0", oauth_callback={redirect_uri}, oauth_signature="rb4pNpvOeDPzRXrXqn6KIRFBh9g%3D"',
    #     'Content-Type': 'multipart/form-data',
    #     'Content-Length': f'{total_bytes}',
    #     'media_type': 'image/jpeg',
    #     'media_category': 'tweet_image'
    # }
    
    # # Obtener la URL de la imagen
    # post = Post.objects.get(slug=slug)
    # image_url = request.build_absolute_uri(post.image.url)

    # # Descargar la imagen desde la URL
    # responseup = requests.get(image_url)

    # # Obtener los bytes de la imagen
    # image_bytes = responseup.content
    # total_bytes = len(image_bytes)
    # print('total_bytes:', total_bytes)
    # file_name = os.path.basename(post.image.name)
    # print('IMAGEN:', file_name)
    # # Cargar la imagen en Twitter
    # files = {
    #     'media': (file_name, image_bytes, 'image/png')
    # }
    
    # payload2 = files
    # media_response = requests.request('POST', upload_url, headers=headers3, data=payload2)
    # response_json = media_response.text
    # status_code = media_response.status_code
    # print('STATUS_CODE:', status_code)
    # print('Response UPLOAD:', response_json)
    # file = {'command': 'INIT',
    #         'total_bytes': f'{total_bytes}',
    #         'media_type': 'image/jpeg',
    #         'media_category': 'tweet_image'
    #         }

    # media_id = media_response.json()['media_id']
    # print('MEDIA_ID:', media_id)

    # # Tweet con imagen
    # tweet_text = f'{ post.title } ' + '| ' + str(request.build_absolute_uri(post.get_absolute_url()))

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
    print('FileType:', type(payload))

    # Publicar el tweet
    tweet_response = requests.request(
        "POST", tweet_url, headers=headers, data=payload)
    print(tweet_response.text)
    # Comprobar la respuesta del tweet
    if tweet_response.status_code == 201:
        print('El tweet se ha publicado correctamente.')
    else:
        print(f'Error al publicar el tweet: {tweet_response.text}')

    # Redirigir al detalle del post
    category_slug = request.session.get('category_slug')
    return redirect('post_detail', category_slug=category_slug, slug=slug)




