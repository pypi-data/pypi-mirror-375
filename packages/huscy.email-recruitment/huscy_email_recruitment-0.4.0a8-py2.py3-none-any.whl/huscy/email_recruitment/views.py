from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from huscy.email_recruitment.serializer import (
    InvitationEMailSerializer,
    ReminderEMailSerializer,
    UpdateInvitationEMailSerializer,
    UpdateReminderEMailSerializer,
)
from huscy.email_recruitment.services import get_invitation_emails, get_reminder_emails
from huscy.projects.models import Project
from huscy.projects.permissions import IsProjectMember


class EMailViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions | IsProjectMember)

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, id=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(project=self.project)


class InvitationEMailViewSet(EMailViewSet):

    def get_queryset(self):
        return get_invitation_emails(self.project)

    def get_serializer_class(self):
        if self.action == 'update':
            return UpdateInvitationEMailSerializer
        return InvitationEMailSerializer


class ReminderEMailViewSet(EMailViewSet):
    def get_queryset(self):
        return get_reminder_emails(self.project)

    def get_serializer_class(self):
        if self.action == 'update':
            return UpdateReminderEMailSerializer
        return ReminderEMailSerializer
