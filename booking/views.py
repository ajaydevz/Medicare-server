import stripe
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, viewsets, pagination
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal, ROUND_DOWN
from django.utils import timezone
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_doctors(request):

    print(request.headers, "CHECK HEADERS")

    try:
        # Query Available instances where either morning or noon slot is available
        available_slots = Available.objects.filter(Q(status="active")).select_related(
            "doctor"
        )
        doctors_dict = {}

        for slot in available_slots:
            doctor = slot.doctor
            if doctor.id not in doctors_dict:

                user = doctor.user

                doctors_dict[doctor.id] = {
                    "id": doctor.id,
                    "name": doctor.name,
                    "age": doctor.age,
                    "experience": doctor.experience,
                    "certificate_no": doctor.certificate_no,
                    "fee_per_hour": doctor.fee_per_hour,
                    "phone": doctor.phone,
                    "description": doctor.description,
                    "user": {
                        "location": user.location,
                        "email": user.email,
                    },
                    "slots": [],
                }

            doctors_dict[doctor.id]["slots"].append(
                {
                    "id": slot.id,
                    "date": slot.date,
                    "is_morning": slot.is_morning,
                    "is_noon": slot.is_noon,
                    "status": slot.status,
                }
            )

        data = list(doctors_dict.values())
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": "Doctors with slots don't exist"},
            status=status.HTTP_404_NOT_FOUND,
        )
    


    

