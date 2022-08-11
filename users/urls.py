from .views import CreateUser, SignInWithGithub, GetUserProfile, ActivateAccount
from django.urls import path


urlpatterns = [
    path("create/", CreateUser.as_view(), name="Create User"),
    path("get/", GetUserProfile.as_view(), name="Get User"),
    path("signinwithgithub/", SignInWithGithub.as_view(),
         name="Sign In With Github"),
    path("activate/", ActivateAccount.as_view(), name="Activate Account"),
]
