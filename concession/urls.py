from django.urls import path
from . import logical, views, views_auth
urlpatterns = [
  path("", views.login, name="login"),
  path("home/", views.homepage, name="home"),
  path("concession/", views.myform, name="concession"),
  path("status/", views.status, name="status"),
  path("settings/", views.settings, name="mysettings"),
  path("logout/",views.logout,name="logout"),
  path("savedata/",views_auth.savedata,name="savedata"),#SignUp Url
  path("savedetails/",views_auth.savedetail,name="savedetail"),# Candidate details URL
  path("login_ajax/", views_auth.login_ajax, name="login_ajax"),
 path('download/<int:application_id>/', logical.download_certificate, name='download_certificate'),

  # path("con_page/",views_auth.railway_concession_form,name="concessionform")

]