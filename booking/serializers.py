from rest_framework import serializers
from .models import *
from accounts.serializers import DoctorSerializer


class AvailableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Available
        fields = "__all__"

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating_value']


class BookingSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"

    def get_doctor(self, obj):
        if self.context.get("include_doctor", True):
            return DoctorSerializer(obj.slot.doctor).data

        return None
    
    def get_rating(self, obj):
        rating = Rating.objects.filter(booking=obj).first()
        if rating:
            return RatingSerializer(rating).data
        return None 


class DoctorBookings(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    doctor_name = serializers.CharField(source="slot.doctor.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "booking_id",
            "amount_paid",
            "date",
            "status",
            "shift",
            "created_at",
            "user_email",
            "doctor_name",
            "user",
        ]


# Serializer Method Fields in Django DRF provide a dynamic way to customize your API responses. Instead of static values, 
# these fields allow you to define methods that manipulate the data before it's serialized.