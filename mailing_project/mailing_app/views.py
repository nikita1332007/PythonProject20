from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Min, Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect,render
from django.utils import timezone
from django.contrib import messages
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm, SignUpForm


class ProfileView(TemplateView):
    template_name = 'profile.html'

class ClientListView(ListView):
    model = Client
    paginate_by = 20

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing_app:clients-list')

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing_app:clients-list')

class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('mailing_app:clients-list')

class MessageListView(ListView):
    model = Message
    paginate_by = 20

class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing_app:messages-list')

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing_app:messages-list')

class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('mailing_app:messages-list')

class MailingListView(ListView):
    model = Mailing
    paginate_by = 20

class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing_app:mailings-list')

class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing_app:mailings-list')

class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailing_app:mailings-list')

class HomePageView(TemplateView):
    template_name = 'mailing_app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        all_mailings = Mailing.objects.all()
        active_mailings = Mailing.objects.filter(start_time__lte=now, end_time__gte=now)
        total_recipients = Client.objects.count()

        context.update({
            'all_mailings_count': all_mailings.count(),
            'active_mailings_count': active_mailings.count(),
            'start_time': active_mailings.aggregate(min_start=Min('start_time'))['min_start'],
            'end_time': active_mailings.aggregate(max_end=Max('end_time'))['max_end'],
            'total_recipients': total_recipients,
            'active_mailings_list': active_mailings,
            'last_updated': now,
        })
        return context


class MailingSendView(View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        now = timezone.now()
        if not (mailing.start_time <= now <= mailing.end_time):
            messages.error(request, 'Отправка разрешена только между start_time и end_time.')
            return redirect('mailing_app:mailings-list')

        recipients = mailing.recipients.all()
        message_obj = mailing.message

        for client in recipients:
            try:
                send_mail(
                    subject=message_obj.subject,
                    message=message_obj.body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = 'Успешно'
                server_response = 'Письмо отправлено успешно.'
            except Exception as e:
                status = 'Не успешно'
                server_response = str(e)

            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status=status,
                server_response=server_response,
            )

        messages.success(request, f'Рассылка #{mailing.pk} запущена для {recipients.count()} клиентов.')
        return redirect('mailing_app:mailings-list')

@method_decorator(cache_control(public=True, max_age=300), name='dispatch')
class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/statistics.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        mailings = Mailing.objects.filter(owner=user)

        context['total_mailings'] = mailings.count()

        attempts = MailingAttempt.objects.filter(mailing__in=mailings)
        context['success_attempts'] = attempts.filter(status='Успешно').count()
        context['failed_attempts'] = attempts.filter(status='Не успешно').count()

        context['messages_sent'] = context['success_attempts']

        return context

def is_manager(user):
    return user.groups.filter(name='Менеджеры').exists()

@user_passes_test(is_manager)
def mailing_view(request):
    return render(request, 'mailing_app/mailing.html')

def mailing_form(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно создана!')
            return redirect('mailing_app:mailings-list')
    else:
        form = MailingForm()
    return render(request, 'mailing_app/mailing_form.html', {'form': form})


class ProfileView(TemplateView):
    template_name = 'mailing_app/profile.html'


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
