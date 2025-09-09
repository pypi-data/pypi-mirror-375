from django.urls import include, path

from huscy.email_recruitment import views
from huscy.projects.urls import project_router


project_router.register('invitationemails', views.InvitationEMailViewSet,
                        basename='invitationemail')
project_router.register('reminderemails', views.ReminderEMailViewSet, basename='reminderemail')


urlpatterns = [
    path('api/', include(project_router.urls)),
]
