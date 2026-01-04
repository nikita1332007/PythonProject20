from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm


class ClientListView(ListView):
    model = Client
    paginate_by = 20


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('clients-list')


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('clients-list')


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('clients-list')


class MessageListView(ListView):
    model = Message
    paginate_by = 20


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('messages-list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('messages-list')


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('messages-list')


class MailingListView(ListView):
    model = Mailing
    paginate_by = 20


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailings-list')


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailings-list')


class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailings-list')


class HomePageView(TemplateView):
    template_name = 'mailing_app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_mailings_count = Mailing.objects.count()
        now = timezone.now()
        active_mailings_count = Mailing.objects.filter(start_time__lte=now, end_time__gte=now).count()
        unique_clients_count = Client.objects.count()

        context.update({
            'all_mailings_count': all_mailings_count,
            'active_mailings_count': active_mailings_count,
            'unique_clients_count': unique_clients_count,
            'now': now,
        })
        return context


class MailingSendView(View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        now = timezone.now()
        if not (mailing.start_time <= now <= mailing.end_time):
            messages.error(request, 'Отправка разрешена только между start_time и end_time.')
            return redirect('mailings-list')

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
                status=status,
                server_response=server_response,
            )

        messages.success(request, f'Рассылка #{mailing.pk} запущена для {recipients.count()} клиентов.')
        return redirect('mailings-list')

    class StatisticsView(LoginRequiredMixin, TemplateView):
        template_name = 'mailing_app/statistics.html'

        def get_context_data(self, **kwargs):
            user = self.request.user
            data = {}

            mailings = Mailing.objects.filter(owner=user)

            data['total_mailings'] = mailings.count()

            attempts = MailingAttempt.objects.filter(mailing__in=mailings)
            data['success_attempts'] = attempts.filter(status='Успешно').count()
            data['failed_attempts'] = attempts.filter(status='Не успешно').count()

            data['messages_sent'] = data['success_attempts']

            return data


@method_decorator(cache_control(public=True, max_age=300), name='dispatch')
class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/statistics.html'


def is_manager(user):
    return user.groups.filter(name='Менеджеры').exists()

@user_passes_test(is_manager)
def mailing_view(request):
    return render(request, 'mailing_app/mailing.html')
