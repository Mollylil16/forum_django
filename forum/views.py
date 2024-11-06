from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .forms import UserRegisterForm, PostForm, CommentForm, ProfileForm, MessageForm
from .models import Post, Comment, Message, UserProfile, User
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


# Nouvelle classe ProfileView
@method_decorator(login_required, name='dispatch')  # Applique le décorateur à la méthode dispatch
class ProfileView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Vérifier si le profil existe pour l'utilisateur
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            # Créer un profil utilisateur vide si celui-ci n'existe pas
            user_profile = UserProfile.objects.create(user=request.user)

        form = ProfileForm(instance=user_profile)
        return render(request, 'forum/profile.html', {'form': form})

    def post(self, request, *args, **kwargs):
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)

        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'forum/profile.html', {'form': form})

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