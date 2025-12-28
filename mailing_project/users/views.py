from django.views.generic import UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import CustomUserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .models import CustomUser
from django.contrib.auth import login
from mailing_app.models import Client


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Подтверждение регистрации'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
            message = f'Перейдите по ссылке для активации: {activation_link}'
            send_mail(subject, message, None, [user.email])
            return render(request, 'users/activation_sent.html')
        return render(request, 'users/register.html', {'form': form})

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except:
            user = None
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'users/activation_invalid.html')


class ClientListView(LoginRequiredMixin, ListView):
    model = Client

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Client.objects.all()
        return Client.objects.filter(owner=user)

class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    ...

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Client.objects.filter(owner=user)
        return Client.objects.filter(owner=user)

    def test_func(self):
        return not self.request.user.is_blocked


class UsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role == 'manager'


class UserBlockToggleView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.role == 'manager'

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if user.role != 'manager':
            user.is_blocked = not user.is_blocked
            user.save()
        return redirect('users-list')