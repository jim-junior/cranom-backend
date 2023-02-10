from .views import CreateUser, SignInWithGithub, GetUserProfile, ActivateAccount, ResendActivationEmail, IsVerified, LinkGithubAccount
from .views.cli import GetCLIToken, LoginWithCli
from django.urls import path
from .views import auth
from .views.base import GetUnreadNotifications, MarkNotificationAsRead, MarkAllNotificationsAsRead


urlpatterns = [
    path("create/", CreateUser.as_view(), name="Create User"),
    path("get/", GetUserProfile.as_view(), name="Get User"),
    path("signinwithgithub/", SignInWithGithub.as_view(),
         name="Sign In With Github"),
    path("activate/", ActivateAccount.as_view(), name="Activate Account"),
    path("token/cli/", GetCLIToken.as_view(), name="Get CLI Token"),
    path("login/cli/", LoginWithCli.as_view(), name="Login with cli"),
    path("session/", auth.session_info, name="sesion info"),
    path("sessionauth/", auth.session_auth, name="session auth"),
    path("notifications/unread/", GetUnreadNotifications.as_view(),
         name="Get Unread Notifications"),
    path("notifications/read/", MarkNotificationAsRead.as_view(),
         name="Mark Notification As Read"),
    path("notifications/readall/", MarkAllNotificationsAsRead.as_view(),
         name="Mark All Notifications As Read"),
    path("resendactivationemail/", ResendActivationEmail.as_view(),
         name="Resend Activation Email"),
    path("isverified/", IsVerified.as_view(), name="Is Verified"),
    path("linkgithubaccount/", LinkGithubAccount.as_view(),
         name="Link Github Account"),

]
