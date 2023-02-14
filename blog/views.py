import random
import string
from crashblog.settings import DEFAULT_IMAGE_URL, LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, REDIRECT_URI
from .models import Post, Category
import os
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from .forms import CommentForm, PostForm, CategoryForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import json
import requests
from django.contrib import messages
from django.contrib.sessions.models import SessionManager, Session
from django.contrib.sessions.backends.base import SessionBase
import urllib.parse
from urllib.parse import urlencode, urlparse, unquote, quote
import urllib.request


def post_form(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse('uploads')
        print('Form not valid')
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {'form': form})

@method_decorator(staff_member_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('frontpage')

@method_decorator(staff_member_required, name='dispatch')
class PostUpdateView(UpdateView):
    template_name = 'blog/post_update_form.html'
    model = Post
    form_class = PostForm
    template_name_suffix = '_update_form'

    # def get_success_url(self):
    #     return reverse('update', args=[self.object.slug]) + '?ok'

    def get_object(self):
        return Post.objects.get(slug=self.kwargs['slug'])
    
    def get_success_url(self):
            return reverse('update', args=[self.get_object().slug]) + '?ok'
        
@method_decorator(staff_member_required, name='dispatch')
class PostDeleteView(DeleteView):
    template_name = 'blog/post_confirm_delete.html'
    model = Post
    success_url = reverse_lazy('frontpage')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        posts = get_object_or_404(Post, slug=kwargs['slug'])
        # Elimina los archivos de imagen y video asociados al post
        if posts.image:
            image_path = os.path.join(
                settings.MEDIA_ROOT, posts.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
            posts.image.storage.delete(posts.image.name)  # borrado fisico

        if posts.clip:
            clip_path = os.path.join(
                settings.MEDIA_ROOT, posts.clip.name)
            if os.path.exists(clip_path):
                os.remove(clip_path)
            posts.image.storage.delete(posts.clip.name)  # borrado fisico

        posts.delete()
        return HttpResponseRedirect(success_url)


def post_detail(request, category_slug, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.ACTIVE)
    # define la variable slug 
    slug = post.slug
    # guarda la variable slug en session para invocarla más adelante
    request.session['slug'] = slug
    # define la variable category_slug
    category_slug = post.category.slug
    # guarda la variable category_slug para invocarla más adelante 
    request.session['category_slug'] =  category_slug
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
    
            return redirect('post_detail', category_slug=category_slug, slug=slug)
    else:
        form = CommentForm(initial={
            "name": request.user.username if request.user.is_authenticated else "request.user",
            "email": request.user.email if request.user.is_authenticated else "user@user.com"
        })
    return render(request, 'blog/post_detail.html', {'form': form, 'post': post})

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category, status=Post.ACTIVE).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'blog/category.html', {'category': category, 'posts': posts, 'categories': categories})

def search(request):
    query = request.GET.get('query', '')

    posts = Post.objects.filter(status=Post.ACTIVE).filter(
        Q(title__icontains=query) | Q(intro__icontains=query) | Q(body__icontains=query))

    return render(request, 'blog/search.html', {'posts': posts, 'query': query})


def create_CSRF_token():
    '''
    This function generate a random string of letters.
    It is not required by the Linkedin API to use a CSRF token.
    However, it is recommended to protect against cross-site request forgery
    For more info on CSRF https://en.wikipedia.org/wiki/Cross-site_request_forgery
    '''
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token

def login_linkedin(request):
    # Construir la URL de redirección
    redirect_uri2 = "https://www.linkedin.com/developerstools/oauth/redirect" #request.build_absolute_uri(reverse('redirect_uri'))
    # Construir la URL para obtener el código de autorización
    url = "https://www.linkedin.com/oauth/v2/authorization"
    params = {
        'response_type': 'code',
        'client_id': {LINKEDIN_CLIENT_ID},
        'redirect_uri': {REDIRECT_URI},
        'state': 'DCEeFWf45A53sdfKef437',
        'scope': 'r_liteprofile%20r_emailaddress%20w_member_social%20openid%20profile%20email%20r_organization_social%20w_organization_social%20rw_organization_admin%20r_ads%20rw_ads%20r_basicprofile%20r_organization_admin%20r_1st_connections_size%20r_ads_reporting'
    }
    # enviar request a LinkedIn para obtener el código de autorización
    # response = requests.post(url, params=params, headers=headers)
    # code = request.GET.get('code')
    # Especificar la ruta de code response
    scope = 'r_liteprofile%20r_emailaddress%20w_member_social%20openid%20profile%20email'
    state = create_CSRF_token()
    url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={}&redirect_uri={}&state={}&scope={}".format(
        LINKEDIN_CLIENT_ID, REDIRECT_URI, state, scope)    
    # Redirigir al usuario a LinkedIn para obtener el código de autorización
    print('CODE URL:', url)
    return redirect(url)
    


def redirect_uri(request):
    # Obtener el código de autorización desde la respuesta de LinkedIn
    code = request.GET.get('code')
    print('CODE:', code)
    # redirect_url = f'http://127.0.0.1:9000/redirect_uri/handle_code?code={code}'    
    
    slug = request.session.get('slug')
    
    return handle_linkedin_response(request, slug, code)    

def handle_linkedin_response(request, slug, code):
    code = request.GET.get('code')
    if code is None:
        return HttpResponse("No se recibió código de autorización.")
    redirect_uri2 = request.build_absolute_uri(reverse('redirect_uri'))
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    # Definir los parámetros para intercambiar el código de autorización por un token de acceso
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    # Realizar la petición para intercambiar el código de autorización por un token de acceso
    responseC = requests.post(url, params=params, headers=headers)
    # Verificar que la petición fue exitosa
    if responseC.status_code == 200:
        # Obtener el access token desde la respuesta
        access_token = responseC.json()['access_token']
        # Guardar el access token en una variable de sesión
        request.session['access_token'] = access_token
        # Obtener el slug del post a compartir desde la vista post_detail
        slug = request.session.get('slug')
        # Redirigir al usuario a la página principal
        messages.success(request, 'access_token  successfully')
        
        return post_to_linkedin(request, slug, access_token)
    else:
        # Mostrar un mensaje de error si la petición no fue exitosa
        return HttpResponse("Error al obtener el access token")
    
def post_linkedin_network_update(request, access_token, title, body, intro, submitted_url, submitted_image_url):
    '''
    Get user information from Linkedin
    '''
    headers_ = {
        'Authorization': f'Bearer {access_token}',
        'cache-control': 'no-cache',
        'X-Restli-Protocol-Version': '2.0.0'
        }
    response_ = requests.get('https://api.linkedin.com/v2/me', headers=headers_)
    
    global userInfo
    userInfo = response_.json()
    if response_.status_code != 200:
        print('ERROR: no se obtuvo el json con el id') 
        
    else:
        print('RESPONSE CODE USERID', response_.status_code)
        print('USER INFO:', userInfo)      
    # # Get user id to make a UGC post # headers = {'content-type': 'application/json}
    urn = userInfo['id']
    print('URN', urn)
    global author
    author = f'urn:li:person:{urn}'
        
    
    PERSON_URN = "urn%3Ali%3Aperson%3ALIj21oTxSL"
    ORGANIZATION_URN = "urn%3Ali%3Aorganization%3A90238112"
    PERSON_URN2 = "urn:li:person:LIj21oTxSL"
    ORGANIZATION_URN2 = "urn:li:organization:90238112"
    
    # Upload Post Image
    # Aqui subo la imagen del post: PASO 1.- Register or initialize Upload IMAGE

    url4 = 'https://api.linkedin.com/rest/images?action=initializeUpload'
    url7 = "https://api.linkedin.com/v2/assets?action=registerUpload"

    headersImage = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202301',
        'Content-Type': 'application/json'
    }

    headersImage2 = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202301',
        'Content-Type': 'application/json'
    }
    
    dataImage = {
        "initializeUploadRequest": {
            "owner": author
        }
    }
    
    dataImage2 = {
        "registerUploadRequest": {
            "owner": author,
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "serviceRelationships": [
                {
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER"
                }
            ],
            "supportedUploadMechanism":[
                "SYNCHRONOUS_UPLOAD"
            ]
        }
    }

    responseImage = requests.post(url4, headers=headersImage, json=dataImage)
    response_dataImage = responseImage.json()
    responseImage2 = requests.post(url7, headers=headersImage2, json=dataImage2)
    response_dataImage2 = responseImage2.json()
    # Extraemos uploadUrl y asset del JASON par ausarlo en el upload a linkedin
    UploadUrl = response_dataImage.get('value').get('uploadUrl')
    image_urn = response_dataImage.get('value').get('image')
    UploadUrl2 = response_dataImage2.get('value').get('uploadMechanism').get('com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest').get('uploadUrl')
    asset = response_dataImage2.get('value').get('asset')
    # Imprimimos resultados para control
    print('CODIGO RESPUESTA uploadImage:', responseImage)
    print('RESP. JSON UploadImage:', response_dataImage)
    print('CODIGO RESPUESTA uploadImage UGC:', responseImage2)
    print('RESP. JSON UploadImage UGC:', response_dataImage2)

    # este se utiliza para subir la imagen y ser alojada en la web
    print("URL DE SUBIDA UPLOADURL POSTS:", UploadUrl)
    print("URN DE IMAGE POSTS :", image_urn)
    print("URL DE SUBIDA UPLOADURL UGC:", UploadUrl2)
    print("URN DE IMAGE UGC:", asset)
    
    # PASO 2.- Aqui se sube el archivo a la ruta UploadUrl creada en el paso  1
    url5 = UploadUrl
    url8 = UploadUrl2
    print("ES LA URL PARA EL UPLOAD PUT:", url5)
    headersUpl = {'Authorization': 'Bearer Redacted'}
    headersUpl2 = {'Authorization': 'Bearer Redacted'}
    # Aqui se abre la imagen que se va a subir y se guarda en 'file'
    file_path = str(request.build_absolute_uri(submitted_image_url))
    file_name = submitted_image_url.split("/")[-1]
    
    print('NOMBRE DE LA IMAGEN A UPLOAD:', file_name)
    urllib.request.urlretrieve(file_path, file_name)
    print("PATH DE LA IMAGEN:", file_path)
    
    # Comprueba si el archivo de imagen existe en la ruta especificada para Posts
    if os.path.isfile(file_name):
        # Abre el archivo en modo binario
        file = open(file_name, "rb")
        # Aquí puedes hacer lo que necesites con el archivo en este caso hacer put
        responseUpl = requests.put(url5, headers=headersUpl, data=file)
        
        responseUplData = responseUpl.text        
        file.close()
        print("STATUS CODE RESPONSE UPLOAD:", responseUpl.status_code)
        print("RESPONSE UPLOAD IMAGE:", responseUplData)
        
        if responseUpl.status_code == 201:
            print('URN DE IMAGEN 201 Posts:', image_urn)
        else:
            print('Ha ocurrido un error al subir la imagen')
        
    else:
        print("El archivo no existe en la ruta especificada")
    
    # Comprueba si el archivo de imagen existe en la ruta especificada para UGC Posts
    if os.path.isfile(file_name):
        # Abre el archivo en modo binario
        file = open(file_name, "rb")
        # Aquí puedes hacer lo que necesites con el archivo en este caso hacer put
        
        responseUpl2 = requests.put(url8, headers=headersUpl2, data=file)
        
        responseUplData2 = responseUpl2.text
        file.close()        
        print("STATUS CODE RESPONSE UPLOAD UGC:", responseUpl2.status_code)
        print("RESPONSE UPLOAD IMAGE UGC:", responseUplData2)
        if responseUpl2.status_code == 201:
            print('URN DE IMAGEN 201 UGC:', asset)
        else:
            print('Ha ocurrido un error al subir la imagen')
    else:
        print("El archivo no existe en la ruta especificada")
    # AQUI termina la rutina de upload de Imagen tanto de Posts como de UGC

    # comienza Obteniendo status web de la IMAGE  subida para  Posts
    url6 = 'https://api.linkedin.com/rest/images/'+image_urn
    headersUploadImage = {
        'Authorization': f'Bearer {access_token}',
        'LinkedIn-Version': '202301'
    }
    responseGETImage = requests.get(url6, headers=headersUploadImage)
    response_dataGETImage = responseGETImage.json()
    print("URL DEL GET:", url6)
    print("RESPUESTA JSON A GET DE IMAGEN YA SUBIDA:", response_dataGETImage)
    # termina Obteniendo status web de la IMAGE  subida para  Posts
    
    # Definicion de Variables para el post
    mention_name = 'BlogifyAR'
    mention2_name = 'Ramón Antonio Serrano Martin'
    message = f'Mira nuestras publicaciones en {mention_name} o a traves de {mention2_name} donde encontrarás temas de tecnología, servicios e internet, somos tu guía especializada del mundo digital, ¡¡Esta es la tercera publicación del sitio!!, Disfrútenla; #Tech, #Web, #SocialMedia.'
    mention_id = '90238112'
    mention_urn = f'urn:li:organization:{mention_id}'
    link = 'https://ramonserrano76.pythonanywhere.com'
    originalUrl = link + (urlparse(submitted_url)).path
    originalurl1 = str(request.build_absolute_uri(submitted_url))
    image_path= link + (urlparse(submitted_image_url)).path
    print('ORIGINAL URL:', originalUrl)
    print("image_path:", image_path)
    print("original url1:", originalurl1)
    # Aqui termina Definicion de Variables para post
    
    
    # aqui comienza Create a organic Post using Posts API
        
    url = "https://api.linkedin.com/rest/posts".format(access_token)
    
    headers =  {
        'LinkedIn-Version': '202301',
        'X-Restli-Protocol-Version': '2.0.0',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        }
    PERSON_URL_STR = str(PERSON_URN2)
    ORGANIZATION_URL_STR = str(ORGANIZATION_URN2)
    title_STR = str(title)
    originalUrl_STR = str(originalUrl)
    image_urn_STR = str(image_urn)
    image_path_STR = str(image_path)
    asett_STR = str(asset)
    message_STR = str(message)    
    body_STR = str(body)
    intro_STR = str(intro)
    params = {
        "author": ORGANIZATION_URL_STR,
        "commentary": message_STR,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },        
        "content": {
            "article": {
                "source": originalUrl_STR,
                "thumbnail": image_urn_STR,
                "thumbnailAltText": body_STR ,
                "title": title_STR,
                "description": body_STR,
            }            
        },
        
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
    
    response = requests.post(url, headers=headers, json=params)     
    
    # obtenemos los parámetros de la respuesta aqui termina Post
    response_data = response.status_code
    
    # Manejamos la respuesta del post para imprimir y monitorear
    if response_data == 201:
        # La respuesta es un 201, por lo que no se espera un JSON
        
        x_linkedin_id = response.headers.get("x-linkedin-id")
        
    else:        
        # manejar el error aquí
        print("Error:", response.status_code, response.text)
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            return HttpResponse("Lo sentimos, ha ocurrido un error al publicar en LinkedIn. Por favor, inténtalo de nuevo más tarde.")    # manejar la excepción aquí
    # aqui termina Create a organic Post using Posts API
    
    
    code = request.GET.get('code')
    print('URL RESPUESTA POST:', )   
    print('CODIGO RESPUESTA POST:', response_data)
    print('URL ENVIADA POST:', url + '?' + urlencode(params))   
    print('URL DE ORIGEN:', submitted_url)
    print('URL RELATIVA DE IMAGEN:', submitted_image_url)    
    print('CODE', code)
    print('ACCESS_TOKEN:', access_token)    
    print('TITULO:', title)
    print('BODY:', body)
    print('INTRO:', intro)  #OJO INTRO Y BODY ESTAN INTERCAMBIADAS
    
    
    # Aqui comienza el programa para requerir permisos a la API        
    person = "LIj21oTxSL"
    organization = "90238112"
    url2 = "https://api.linkedin.com/v2/organizations/{organization}".format(organization=organization)
    
    #'https://api.linkedin.com/rest/organizationAcls/(organization:{ORGANIZATION_URN},role:DIRECT_SPONSORED_CONTENT_POSTER,roleAssignee:{PERSON_URN})'.format(ORGANIZATION_URN=ORGANIZATION_URN, PERSON_URN=PERSON_URN)
    #'https://api.linkedin.com/rest/organizationAcls?q=organization&organization={}&role=ADMINISTRATOR&state=APPROVED'.format(ORGANIZATION_URN)
    #'https://api.linkedin.com/rest/organizationAcls?q=roleAssignee'
    #"https://api.linkedin.com/rest/organizationAcls/(organization:{},role:ADMINISTRATOR,roleAssignee:{})".format(ORGANIZATION_URN, PERSON_URN)
    
    headersO = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',        
        'LinkedIn-Version': '202301',
        'Content-Type': 'application/json'
    }
    responseO = requests.get(url2, headers=headersO)
    response_dataO = responseO.json()  # obtenemos los parámetros de la respuesta
    print('COD.RESP.ORG.ADMIN:', responseO)
    print('BUSCAR ORG.ADMIN:', response_dataO)
     # Aqui Termina el programa para requerir permisos a la API        
    
    # Definir los parametros para publicar con mención a una empresa. Esto era para UgcPosts   
    # funcion para buscar el lenght de la empresa mencionada
    def find_pos(mention_name, message):
        '''
        Find position of mention_name in the message
        '''
        index = 0
        if mention_name in message:
            c = mention_name[0]
            for ch in message:
                if ch == c:
                    if message[index:index+len(mention_name)] == mention_name:
                        return index
                index += 1
        return -1
    
    len_uname=len(mention_name)
    start = find_pos(mention_name, message)
    # Termina parametros para publicar con mención a una empresa. Esto era para UgcPosts

    
    
    # AQUI COMIENZA Realizar un Post personal UGC con mención a una empresa  
    
    url3 = "https://api.linkedin.com/v2/ugcPosts"
    headersP = {
        'X-Restli-Protocol-Version': '2.0.0',
        'Authorization': f'Bearer {access_token}',
        'LinkedIn-Version': '202301',
        'Content-Type': 'application/json'
    }
    paramsP = {
        "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "attributes": [
                            {
                                "length": len_uname,
                                "start": start,
                                "value": {
                                    "com.linkedin.common.CompanyAttributedEntity": {
                                        "company": mention_urn
                                    }
                                }
                            }
                        ],
                        "text": message
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {                            
                            "mediaType": "IMAGE",                            
                            "status": "READY",
                            "description": {
                                "text": body_STR
                            },                            
                            "originalUrl": originalurl1,
                            "title": {
                                "attributes": [],
                                "text": title
                            },
                            "thumbnails": [{
                                "url": file_path
                            }]
                            
                        }
                    ],
                                    
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    
    responseP = requests.post(url3, headers=headersP, json=paramsP)
    response_dataP = responseP.json()  # obtenemos los parámetros de la respuesta
    print('CODIGO RESPUESTA POST UGC:', responseP)
    print('POST PERSONAL UGC:', response_dataP)    
    # AQUI TERMINA POST UGCPOST
    
    
    # Codificamos los parámetros en una cadena string de consulta
    # query_string = urllib.parse.urlencode(response_data)
    # Agregamos la cadena de consulta a la URL de la respuesta
    # response_url = url + '?' + query_string
    # print('URL ORG ADMIN:', response_url)
    

def post_to_linkedin(request, slug, access_token):    
    # obtener el post mediante el slug
    slug = request.session.get('slug')
    category_slug = request.session.get('category_slug')
    post = Post.objects.get(slug=slug)
    title = post.title
    body = post.body
    intro = post.intro
    submitted_url = request.build_absolute_uri(post.get_absolute_url())
    parsed_url = urlparse(submitted_url)
    submitted_relative_url = parsed_url.path
    relative_url = str(submitted_relative_url)
    print('URL RELATIVA DEL POST:', relative_url)
    # verificar si el post tiene una imagen asociada
    if post.image:
        submitted_image_url = post.image.url  # post.get_absolute_url()
        
    else:
        submitted_image_url = DEFAULT_IMAGE_URL
    response_status_code = post_linkedin_network_update(request, access_token, title, intro, body, submitted_url, submitted_image_url)
    if response_status_code:
        messages.add_message(request, messages.SUCCESS, 'El post se ha compartido exitosamente en LinkedIn')
    else:
        messages.add_message(request, messages.ERROR, 'Ha ocurrido un error al compartir el post en LinkedIn')
        
    return redirect('post_detail', category_slug=category_slug, slug=slug)