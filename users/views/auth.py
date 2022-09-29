import time
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes


@api_view()
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
@csrf_exempt
def session_info(request):
    """
    View to retrieve user info for current user. (Can be adapted to your needs). If user is not logged in, view will
    still return CSRF cookie which in neccessary for authentication.
    """
    if not request.user.is_authenticated:
        return Response({"message": "Not authenticated.", "authenticated": False})
    return Response(
        {"message": "Authenticated.", "authenticated": True,
            "user": str(request.user)}
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def session_auth(request):
    """
    Login-view.
    """
    user = request.user
    if user is not None:
        if user.is_active:
            login(request, user)
            request.session['authenticated_user'] = user.username
            return Response(
                data={
                    "message": "Authenticated.",
                    "authenticated": True,
                    "name": user.name,
                },
                status=status.HTTP_202_ACCEPTED
            )
    return Response(data={"message": "Not authenticated", "authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)
