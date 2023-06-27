from django.urls import path
from .views import AddEmail

urlpatterns = [
    path('news-letter/add-email/', AddEmail.as_view(), name='add-email'),
]
