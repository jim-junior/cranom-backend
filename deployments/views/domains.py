from deployments.models import DomainName
from deployments.serializers import DomainNameSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from users.models import UserProfile
import dns.resolver


# A list of all domains for authenticated user
class DomainList(generics.ListAPIView):
    serializer_class = DomainNameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        return DomainName.objects.filter(user=profile)


# create a new domain for authenticated user
class DomainCreate(APIView):
    serializer_class = DomainNameSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        domain_name = request.data.get('domain_name')
        try:
            profile = UserProfile.objects.get(user=user)
            domain = DomainName.objects.create(
                domain_name=domain_name,
                user=profile
            )

        except Exception as e:
            return Response(
                {"error": "Error creating domain name"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"domain_name": domain.domain_name},
            status=status.HTTP_201_CREATED
        )

# delete a domain for authenticated user


class DomainDelete(generics.DestroyAPIView):
    serializer_class = DomainNameSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        domain_name = kwargs.get('domain_name')
        try:
            domain = DomainName.objects.get(
                domain_name=domain_name,
                user=user
            )
        except:
            return Response(
                {"error": "Domain name does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        domain.delete()
        return Response(
            {"domain_name": domain.domain_name},
            status=status.HTTP_200_OK
        )

# update a domain for authenticated user


class DomainUpdate(generics.UpdateAPIView):
    serializer_class = DomainNameSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = self.request.user
        domain_name = kwargs.get('domain_name')
        new_domain_name = request.data.get('domain_name')
        try:
            domain = DomainName.objects.get(
                domain_name=domain_name,
                user=user
            )
        except:
            return Response(
                {"error": "Domain name does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        domain.domain_name = new_domain_name
        domain.save()
        return Response(
            {"domain_name": domain.domain_name},
            status=status.HTTP_200_OK
        )


class GetDomainRecords(APIView):
    serializer_class = DomainNameSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, domain_name, *args, **kwargs):
        if domain_name == None:
            return Response(
                {"error": "Domain name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            a_records = dns.resolver.query(domain_name, 'A')
            name_servers = dns.resolver.query(domain_name, 'NS')
            payload = {

                "a_records": [
                    str(record.to_text()) for record in a_records  # type: ignore
                ],

                "name_servers": [
                    str(record) for record in name_servers  # type: ignore
                ]
            }
            return Response(
                data=payload,
                status=status.HTTP_200_OK
            )
        except (dns.resolver.LifetimeTimeout, dns.resolver.NXDOMAIN,
                dns.resolver.YXDOMAIN, dns.resolver.NoAnswer,
                dns.resolver.NoNameservers, dns.resolver.NotAbsolute,) as e:
            print(e)
            return Response(
                {"error": "Error getting domain records"},
                status=status.HTTP_400_BAD_REQUEST
            )
