from django.shortcuts import redirect, render
from django.views import View
from .mixins import YouTube
from django.contrib.auth import  logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm,CommentForm
from .models import Comment
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from itertools import chain

class inicio(View):
    def get(self, request):
        return render(request, 'inicio.html')
    
class historia(View):
    def get(self, request):
        return render(request, 'historia/historia.html')
    
class cursos(View):
    def get(self, request):
        videos = YouTube().get_data()

        # Obtén todas las categorías de todos los videos y conviértelas en una lista plana
        all_categories = list(chain.from_iterable(v.get('categoria', []) for v in videos))

        # Elimina duplicados manteniendo el orden original
        unique_categories = sorted(set(all_categories), key=all_categories.index)

        # Implementa la paginación
        paginator = Paginator(videos, 10)  # Muestra 10 videos por página
        page = request.GET.get('page', 1)

        try:
            videos_pagina = paginator.page(page)
        except PageNotAnInteger:
            videos_pagina = paginator.page(1)
        except EmptyPage:
            videos_pagina = paginator.page(paginator.num_pages)

        context = {"videos": videos_pagina, "unique_categories": unique_categories}
        return render(request, 'cursos/cursos.html', context)
    
def videos(request):

	videos = YouTube().get_data()

	context = {"videos": videos}
	return render(request, 'videos.html', context)

 
'''
Basic view for showing a video in an iframe 
'''
# def play_video(request):
#     videos = YouTube().get_data()
#     vid_id = request.GET.get("vid_id")

#     vid_data = YouTube(vid_id=vid_id).get_video()

#     contextUno = {
#         "vid_data": vid_data,
#     	"videos": videos
#     }



#     return render(request, 'play_video.html', contextUno)


class play_video(View):
    def get(self, request, vid_id):

        videos = YouTube().get_data()  
        vid_data = YouTube(vid_id=vid_id).get_video()
       
        comments = Comment.objects.filter(video_id=vid_id).order_by('timestamp')
        comment_form = CommentForm()
        
        
        #  Problema en paginación
        main_comments = Comment.objects.filter(video_id=vid_id, parent_comment=None).order_by('timestamp')
        paginator = Paginator(main_comments, 3)
        page = request.GET.get('page')

        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        contextUno = {
            "vid_data": vid_data,
            "videos": videos,
            "comments": comments,
            "comment_form": comment_form,
        }
        

        return render(request, 'cursos/play_video.html', contextUno)

    def post(self, request, vid_id):
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid() and request.user.is_authenticated:
            text = comment_form.cleaned_data['text']
            new_comment = Comment(user=request.user, video_id=vid_id, text=text)
            new_comment.save()

            return redirect(reverse('play-video', kwargs={'vid_id': vid_id}))

        return redirect('play-video', vid_id=vid_id)






class ReplyComment(View):
    def post(self, request, vid_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        reply_form = CommentForm(request.POST)

        if reply_form.is_valid() and request.user.is_authenticated:
            text = reply_form.cleaned_data['text']

            new_reply = Comment(user=request.user, video_id=vid_id, text=text, parent_comment=comment)
            new_reply.save()
       
        return redirect(reverse('play-video', kwargs={'vid_id': vid_id}))





@login_required
def signout(request):
    logout(request)
    return redirect('/')



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            lastname = form.cleaned_data['lastname']
            
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con este nombre de usuario o correo electrónico.')
            else:
                user = form.save(commit=False)
                user.first_name = name
                user.last_name = lastname
                user.save()
               
                authenticated_user = authenticate(request, username=username, password=form.cleaned_data['password1'])
                login(request, authenticated_user)
                
                messages.success(request, 'Inicio de sesión exitoso')
                return redirect('/')
    else:
        form = CustomUserCreationForm()

    return render(request, 'account/signup.html', {'form': form})
