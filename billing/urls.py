#from .views import CreateDeploymentView
from django.urls import path
from .views import (
    AddCardAPIView,
    ListCardsAPIView,
    DeleteCardAPIView,
    AddMobileNumberAndSendOTPAPIView,
    VerifyMobileNumberAPIView,
    ChargeMobileMoneyAPIView,
    ListMMPhoneNumbersAPIView,
    DeleteMMPhoneAPIView,
    ChargeMobileMoneyAPIView,

)
from .views.webhooks import FlutterwaveTransactionWebhooks

urlpatterns = [
    path('add-card/', AddCardAPIView.as_view(), name='add-card'),
    path('list-cards/', ListCardsAPIView.as_view(), name='list-cards'),
    path('list-mm-phone-numbers/', ListMMPhoneNumbersAPIView.as_view(),
         name='list-mm-phone-numbers'),
    path('delete-card/<pk>/', DeleteCardAPIView.as_view(), name='delete-card'),
    path('delete-mm-phone/<pk>/',
         DeleteMMPhoneAPIView.as_view(), name='delete-mm-phone'),
    path('add-mobile-number/', AddMobileNumberAndSendOTPAPIView.as_view(),
         name='add-mobile-number'),
    path('verify-mobile-number/', VerifyMobileNumberAPIView.as_view(),
         name='verify-mobile-number'),
    path('charge-mobile-money/', ChargeMobileMoneyAPIView.as_view(),
         name='charge-mobile-money'),
    path('flutterwave-webhooks/', FlutterwaveTransactionWebhooks.as_view(),
         name='flutterwave-webhooks'),
    path('charge-mobile-money/', ChargeMobileMoneyAPIView.as_view(),
         name='charge-mobile-money'),
]
