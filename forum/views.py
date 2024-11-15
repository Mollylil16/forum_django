from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from .forms import UserRegisterForm, PostForm, CommentForm, ProfileForm, MessageForm
from .models import Post, Comment, Message, UserProfile, User, Like, Follow
from django.views import View  # Import de View pour la classe ProfileView
from django.http import Http404

class CustomLoginView(LoginView):
    template_name = 'forum/login.html'
    success_url = reverse_lazy('post_list')

    def get(self, request, *args, **kwargs):
        print("CustomLoginView called")
        return super().get(request, *args, **kwargs)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'forum/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('login')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'forum/register.html', {'form': form})

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'forum/post_list.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'forum/post_create.html', {'form': form})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    else:
        comment_form = CommentForm()
    
    return render(request, 'forum/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)  # Récupère le destinataire
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user  # Associe l'expéditeur (l'utilisateur connecté)
            message.recipient = recipient  # Associe le destinataire
            message.save()
            return redirect('inbox')  # Redirige vers une boîte de réception ou une page de confirmation
    else:
        form = MessageForm()
    return render(request, 'forum/send_message.html', {'form': form, 'recipient': recipient})


# ProfileView pour gérer l'affichage et la mise à jour du profil utilisateur
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        # Charger le formulaire avec les informations du profil
        form = ProfileForm(instance=user_profile)
        return render(request, 'forum/profile.html', {'form': form, 'user': user})

    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        # Mettre à jour le profil de l'utilisateur avec les nouvelles informations
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user_id)  # Redirige vers la page du profil mis à jour
        return render(request, 'forum/profile.html', {'form': form, 'user': user})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'forum/password_change.html', {'form': form})

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'forum/inbox.html', {'messages': messages})

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = message.sender  # Répondre à l'expéditeur du message original
            reply.save()
            return redirect('inbox')  # Ou rediriger vers le message spécifique ou la boîte de réception
    else:
        form = MessageForm()

    return render(request, 'forum/view_message.html', {'message': message, 'form': form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Vérifier si l'utilisateur est l'auteur du commentaire
    if comment.author == request.user:
        comment.delete()  # Supprimer le commentaire
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def toggle_follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    if not created:  # Already following, so unfollow
        follow.delete()
    return redirect('profile', user_id=user_to_follow.id)
 

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Vérifier si l'utilisateur a déjà un like ou dislike pour ce post
    existing_like = Like.objects.filter(user=request.user, post=post).first()
    
    if existing_like:
        if existing_like.value == 'like':  # L'utilisateur a déjà liké, il peut enlever son like
            existing_like.delete()
        elif existing_like.value == 'dislike':  # L'utilisateur a déjà disliké, changer en like
            existing_like.value = 'like'
            existing_like.save()
    else:
        # Créer un nouveau "like" si aucun "like" ou "dislike" existant
        Like.objects.create(user=request.user, post=post, value='like')

    return redirect('post_detail', pk=post.id)

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Vérifier si l'utilisateur a déjà un like ou dislike pour ce post
    existing_like = Like.objects.filter(user=request.user, post=post).first()
    
    if existing_like:
        if existing_like.value == 'dislike':  # L'utilisateur a déjà disliké, il peut enlever son dislike
            existing_like.delete()
        elif existing_like.value == 'like':  # L'utilisateur a déjà liké, changer en dislike
            existing_like.value = 'dislike'
            existing_like.save()
    else:
        # Créer un nouveau "dislike" si aucun "like" ou "dislike" existant
        Like.objects.create(user=request.user, post=post, value='dislike')

    return redirect('post_detail', pk=post.id)

@login_required
def chat_room(request, room_name):
    user_id = request.user.id  # Récupère l'ID de l'utilisateur connecté
    profile_url = reverse('profile', kwargs={'user_id': user_id})  # Crée l'URL du profil

    return render(request, 'forum/chat_room.html', {
        'room_name': room_name,
        'profile_url': profile_url,  # Passe l'URL du profil dans le contexte
    })