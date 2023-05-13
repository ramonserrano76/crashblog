import os
import tweepy
import tempfile
from requests_oauthlib import OAuth1Session
from oauthlib.oauth1 import SIGNATURE_HMAC, SIGNATURE_TYPE_QUERY
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
from urllib.parse import parse_qs, urlencode
import urllib.request
from configparser import SafeConfigParser
import datetime
import json
import hashlib
import hmac
import base64
from urllib.parse import quote

############### AQUI COMIENZA  EL PROCESO DE SUBIDA DE IMAGEN PARA DESARROLLAR#################

# # URL de la API de Twitter para subir imágenes o videos
# upload_url = "https://upload.twitter.com/1.1/media/upload.json"

# # Ruta de la imagen o video que deseas subir
# absolute_path = os.path.abspath(temp_file.name)

# # Token de acceso generado en la autenticación con OAuth 2.0
# # no hace falta porque ya fue dfinido arriba

# # Leer el contenido del archivo en modo binario
# with open(absolute_path, "rb") as file:
#     file_data = file.read()

# # Parámetros de la solicitud
# paramsIMG = {
#     # Categoría de medios (puede ser "tweet_image" o "tweet_video")
#     "media_category": "tweet_image",
#     # "media_type": media_type,
# }

# # Encabezados de la solicitud
# headersIMG = {
#     "Authorization": f"Bearer {access_token}",
#     # Tipo de contenido para la solicitud multipart
#     "Content-Type": "multipart/form-data",
# }

# # Realizar la solicitud POST a la API de Twitter para subir la imagen o video
# responseIMG = requests.request('POST', upload_url, params=paramsIMG, files={
#                                "media": file_data}, headers=headersIMG)
# responseIMG_data = responseIMG.text
# print('RESPONSEIMG:', responseIMG_data)


################# AQUI TERMINA EL PROCESO DE SUBIDA DE IMAGEN PARA DESARROLLAR##################

# Obtener el media_id de la imagen o video subido
# media_id_upl = responseIMG.json()
# media_id = media_id_upl['media_id']
# Utilizar el media_id en la función de publicación de tweets para adjuntar la imagen o video al tweet

# # cuerpo del Tweet con link acortados
# tweet_text = f'{ post.title } ' + '| ' + str(request.build_absolute_uri(post.get_absolute_url()))






# # URL para obtener el oauth_signature y luego  el oauth_token
# token_url = 'https://api.twitter.com/oauth/request_token'

# oauth_consumer_key = "ogKdSKDeBi1oiUtB8LZCnYzkw"
# oauth_consumer_secret = "XG2SKvAjLDUlnw8R8Ghbg747m7OS0SC0vapUmhsBYPFl94nuAM"

# # Definir el URL base y los parámetros para el SIGNATURE
# base_url = "https://api.twitter.com/oauth/request_token"
# parameters = {
#     'include_entities': 'true',
#     'status': 'Hello Ladies + Gentlemen, a signed OAuth request!',
#     'oauth_consumer_key': oauth_consumer_key,
#     'oauth_nonce': "WQFRTfd",
#     'oauth_signature_method': 'HMAC-SHA1',
#     'oauth_timestamp': timestamp,
#     'oauth_version': '1.0'
# }

# # Ordenar los parámetros alfabéticamente
# sorted_params = sorted(parameters.items())

# # Generar la cadena de parámetros
# param_string = '&'.join([f"{quote(k)}={quote(v)}" for k, v in sorted_params])

# # Construir el signature base string
# method = "POST"
# base_url_encoded = quote(base_url, safe='')
# signature_base_string = f"{method}&{base_url_encoded}&{quote(param_string, safe='')}"

# # Construir el signing key
# signing_key = f"{quote(oauth_consumer_secret)}&"

# # Generar la firma HMAC-SHA1
# signature = base64.b64encode(hmac.new(signing_key.encode(
# ), signature_base_string.encode(), hashlib.sha1).digest()).decode()

# print("OAuth Signature:", signature)

# # Crear el header para oauth_token
# paramstoken = {
#     'oauth_callback': redirect_uri
# }
# headers2 = {
#     'Authorization': f'OAuth oauth_consumer_key= {oauth_consumer_key}, oauth_nonce="WQFRTfd", oauth_signature="rb4pNpvOeDPzRXrXqn6KIRFBh9g%3D", oauth_signature_method="HMAC-SHA1", oauth_timestamp= {timestamp}, oauth_version="1.0"',
# }
# responsetoken = requests.request('POST', token_url, headers=headers2, params=paramstoken)
# response_text = responsetoken.text
# response_data = parse_qs(response_text)
# #oauth_token = response_data['oauth_token'][0]
# #oauth_token_secret = response_data['oauth_token_secret'][0]
# print('STAT_CODE_TOKEN_200:', responsetoken.status_code)
# print('Response_Token:', response_text)

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
