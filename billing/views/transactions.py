from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from billing.models import MMPhoneNumber, Card, Transaction, UserProfile
from billing.serializers import CardSerializer, MMPhoneSerializer
from billing.utils.charge import charge_card, charge_mobile_money, verify_transaction
from billing.utils.sms import send_sms
import random

# An API View that adds a new card


def getUserProfile(user):
    profile = UserProfile.objects.get(user=user)
    return profile


class AddCardAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Print headers
        user = getUserProfile(request.user)
        data['user'] = user
        serializer = CardSerializer(data=data)
        if serializer.is_valid():
            card = serializer.save()
            tx = Transaction(
                user=user,
                amount=1,
                card=card,
                reason='Verify Card',
            )
            tx.save()
            exp_date = card.expiration_date.split('/')
            # Charge the user
            resp = charge_card(
                card_number=card.card_number,
                cvv=data['cvv'],
                expiry_month=exp_date[0],
                expiry_year=exp_date[1],
                transaction_id=str(tx.trans_id),
                amount=1,
                email=user.email,
            )
            print(resp)
            if resp['status'] == 'success':
                tx.transaction_status = 'success'
                tx.fw_id = resp['data']['id']
                tx.save()
                tx_data = verify_transaction(resp['data']['id'])
                print(tx_data)
                card_token = tx_data['data']['card']['token']
                print(card_token)
                card.card_token = card_token
                card.verified = True
                card.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                tx.transaction_status = 'failed'
                tx.save()
                return Response(data={
                    'message': 'Card could not be verified',
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# A generic view that lists all cards for a specific user


class ListCardsAPIView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CardSerializer

    def get_queryset(self):
        return Card.objects.filter(user=getUserProfile(self.request.user))

# A generic view that lists all mm phonenumber for a specific user


class ListMMPhoneNumbersAPIView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MMPhoneSerializer

    def get_queryset(self):
        return MMPhoneNumber.objects.filter(user=getUserProfile(self.request.user))

# A generic view that deletes a card


class DeleteCardAPIView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CardSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Card.objects.filter(user=getUserProfile(self.request.user))

# A generic view that deletes a mm phone number


class DeleteMMPhoneAPIView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MMPhoneSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return MMPhoneNumber.objects.filter(user=getUserProfile(self.request.user))


class AddMobileNumberAndSendOTPAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        phone_number = data.get('phone_number')
        country = data.get('country')
        user = getUserProfile(request.user)
        if phone_number:
            otp = random.randint(100000, 999999)
            mm_phone_number = MMPhoneNumber.objects.create(
                user=user,
                phone_number=phone_number,
                otp=otp,
                country=country
            )
            print('OTP: {}'.format(otp))

            send_sms(phone_number, f'Your OTP is {otp}')
            return Response({'message': 'OTP sent'}, status=status.HTTP_200_OK)
        return Response({'message': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyMobileNumberAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        otp = data.get('otp')
        phone_number = data.get('phone_number')
        if otp and phone_number:
            mm_phone_number = MMPhoneNumber.objects.filter(
                user=getUserProfile(request.user),
                phone_number=phone_number,
                otp=otp
            ).first()
            if mm_phone_number:
                mm_phone_number.is_verified = True
                mm_phone_number.save()
                return Response({'message': 'Phone number verified'}, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'OTP and phone number are required'}, status=status.HTTP_400_BAD_REQUEST)


class ChargeMobileMoneyAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        amount = data.get('amount')
        phone_number = data.get('phone_number')
        phone_id = data.get('phone_id')
        user = getUserProfile(request.user)
        if amount and phone_number:
            if MMPhoneNumber.objects.filter(
                id=phone_id,
                user=user,
                phone_number=phone_number,
                # is_verified=True
            ).exists():
                phone_obj = MMPhoneNumber.objects.get(
                    id=phone_id,
                    user=user,
                    phone_number=phone_number,
                    # is_verified=True
                )
                # Create a transaction
                tx = Transaction(
                    user=user,
                    amount=amount,
                    mm_phone_number=phone_obj,
                    reason='Mobile money charge',
                )
                tx.save()
                # Charge the user
                resp = charge_mobile_money(
                    phone_number=phone_number, transaction_id=str(tx.trans_id), order_id=str(tx.order_id), amount=amount, email=user.email, country="uganda")
                if resp["status"] == "success":
                    tx.status = 'success'
                    redirect_url = resp["meta"]["authorization"]["redirect"]
                    tx.redirect_url = redirect_url
                    tx.save()
                    return Response({'redirect_url': redirect_url}, status=status.HTTP_200_OK)
                else:
                    tx.status = 'failed'
                    tx.save()
                    print(resp)
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Phone number not verified'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Amount or phone number missing'}, status=status.HTTP_400_BAD_REQUEST)


class ChargeCardAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        amount = data.get('amount')
        card_id = data.get('card_id')
        cardcvv = data.get('card_id')
        user = getUserProfile(request.user)
        if amount and card_id:
            if Card.objects.filter(
                id=card_id,
                user=user,
            ).exists():
                card_obj = Card.objects.get(
                    id=card_id,
                    user=user,
                )
                # Create a transaction
                tx = Transaction(
                    user=user,
                    amount=amount,
                    card=card_obj,
                    reason='Card charge',
                )
                tx.save()
                # Charge the user
                resp = charge_card(
                    card_number=card_obj.card_number,
                    cvv=cardcvv,
                    expiry_month=card_obj.expiration_date,
                    expiry_year=card_obj.expiration_date,
                    transaction_id=tx.trans_id,
                    amount=amount,
                    email=user.email,
                )
                if resp["status"] == "success":
                    tx.status = 'success'
                    redirect_url = resp["meta"]["authorization"]["redirect"]
                    tx.redirect_url = redirect_url
                    tx.save()
                    return Response({'redirect_url': redirect_url}, status=status.HTTP_200_OK)
                else:
                    tx.status = 'failed'
                    tx.save()
                    print(resp)
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Card not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Amount or card id missing'}, status=status.HTTP_400_BAD_REQUEST)
