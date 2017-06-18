from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

# ____________________________ DASHBOARD __________________________________

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='dashboard'),

    # ____________________________ ACCOUNT __________________________________
    url(r'^pre_register/$', views.PreRegisterView.as_view(), name='pre_register'),
    url(r'^register/$', views.RegisterFormView.as_view(), name='register'),
    url(r'^login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^profile/edit$', views.ProfileEditView.as_view(), name='edit_profile'),
    url(r'^change_password$', views.ChangePasswordView.as_view(), name='change_password'),
    url(r'^logout/$', views.Logout.as_view(), name='logout'),

    # ------------------------------PASSWORD RESET------------------------------
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),


    # _________________________________PROJECT____________________________________

    url(r'^projects/$', views.ProjectIndexView.as_view(), name='all_projects'),
    url(r'^projects/running$', views.ProjectRunningView.as_view(), name='running_projects'),
    url(r'^projects/expired$', views.ProjectExpiredView.as_view(), name='project_history'),
    url(r'^project/new$', views.ProjectCreateView.as_view(), name='new_project'),
    url(r'^projects/(?P<pk>[0-9]+)$', views.ProjectDetailView.as_view(), name='project_detail'),
    url(r'^project/(?P<pk>[0-9]+)/edit', views.ProjectEditView.as_view(), name='edit_project'),
    url(r'^project/(?P<pk>[0-9]+)/delete$', views.ProjectDeleteView.as_view(), name='delete_project'),

    # __________________________________________________________________________________________________________


    # __________________________AJAX CALLS___________________________________________
    url(r'^get_files_dates/$', views.getFilesDatesView.as_view(), name='get_files_dates'),
    url(r'^confirm_project/(?P<pk>[0-9]+)$', views.confirmProjectView.as_view(), name='confirm_project'),
]
