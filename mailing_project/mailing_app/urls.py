
from django.urls import path
from .views import (
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    MailingListView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    MailingSendView,
    HomePageView, StatisticsView, signup_view,
)

app_name = 'mailing_app'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('clients/', ClientListView.as_view(), name='clients-list'),
    path('clients/add/', ClientCreateView.as_view(), name='clients-add'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='clients-edit'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='clients-delete'),
    path('messages/', MessageListView.as_view(), name='messages-list'),
    path('messages/add/', MessageCreateView.as_view(), name='messages-add'),path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='messages-edit'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='messages-delete'),
    path('mailings/', MailingListView.as_view(), name='mailings-list'),
    path('mailings/add/', MailingCreateView.as_view(), name='create_mailing'),
    path('mailings/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailings-edit'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailings-delete'),
    path('mailings/<int:pk>/send/', MailingSendView.as_view(), name='mailings-send'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('signup/', signup_view, name='signup'),
]