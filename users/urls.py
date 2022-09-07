from .views import CreateUser, SignInWithGithub, GetUserProfile, ActivateAccount
from .views.cli import GetCLIToken, LoginWithCli
from django.urls import path


urlpatterns = [
    path("create/", CreateUser.as_view(), name="Create User"),
    path("get/", GetUserProfile.as_view(), name="Get User"),
    path("signinwithgithub/", SignInWithGithub.as_view(),
         name="Sign In With Github"),
    path("activate/", ActivateAccount.as_view(), name="Activate Account"),
    path("token/cli/", GetCLIToken.as_view(), name="Get CLI Token"),
    path("login/cli/", LoginWithCli.as_view(), name="Login with cli"),
]
