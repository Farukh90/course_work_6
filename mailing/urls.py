from django.urls import path
from django.views.decorators.cache import cache_page

from blog.views import BlogDetailView
from .views import (
    ClientListView,
    ClientDetailView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    MessageListView,
    MessageDetailView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    MailingAttemptListView,
    MailingAttemptDetailView,
    MailingAttemptCreateView,
    MailingAttemptUpdateView,
    MailingAttemptDeleteView,
    HomePageView,
    ContactView,
    RunMailingCommandView,
    RunMailingHardCommandView,
)


app_name = "mailing"


urlpatterns = [
    path("", cache_page(3)(HomePageView.as_view()), name="index"),
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path(
        "mailings/<int:mailing_id>/attempts/",
        MailingAttemptListView.as_view(),
        name="mailing_attempt_list",
    ),
    path(
        "mailings/<int:mailing_id>/attempts/<int:pk>/",
        MailingAttemptDetailView.as_view(),
        name="mailing_attempt_detail",
    ),
    path(
        "mailings/<int:mailing_id>/attempts/create/",
        MailingAttemptCreateView.as_view(),
        name="mailing_attempt_create",
    ),
    path(
        "mailings/<int:mailing_id>/attempts/<int:pk>/update/",
        MailingAttemptUpdateView.as_view(),
        name="mailing_attempt_update",
    ),
    path(
        "mailings/<int:mailing_id>/attempts/<int:pk>/delete/",
        MailingAttemptDeleteView.as_view(),
        name="mailing_attempt_delete",
    ),
    path("contacts/", ContactView.as_view(), name="contacts"),
    path(
        "mailings/<int:mailing_id>/run/",
        RunMailingCommandView.as_view(),
        name="run_mailing_command",
    ),
    path(
        "mailings/<int:mailing_id>/run/hard/",
        RunMailingHardCommandView.as_view(),
        name="run_mailing_hard_command",
    ),
]
