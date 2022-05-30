from .views import CreateUser, SignInWithGithub
from django.urls import path


urlpatterns = [
    path("create/", CreateUser.as_view(), name="Create User"),
    path("signinwithgithub/", SignInWithGithub.as_view(),
         name="Sign In With Github"),
]
