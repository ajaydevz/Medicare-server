from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Remove password from validated_data before creating the user
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
            user.is_google = True
        user.save()
        return user

    def update(self, user, validated_data):
        fields_to_update = ["date_of_birth", "location", "profile_picture"]
        for field_name in fields_to_update:
            field_value = validated_data.get(field_name)
            if (field_value is not None):  # Check if the field is provided in validated_data
                setattr(user, field_name, field_value)

        user.save()
        return user




class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        print(email)
        print(password)

        if email and password:
            # user = User.objects.filter(email=email).first()
            user = User.objects.get(email=email)
            if user:
                return data
            raise serializers.ValidationError("invalid user credentials")
        raise serializers.ValidationError("Both fields are required")




class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"

    def create(self, validated_data):
        user_id = validated_data.pop("user", None)

        print(user_id.id)
        if user_id:
            user = User.objects.get(id=user_id.id)

            associate = Doctor.objects.create(user=user, **validated_data)
            

            return associate


class DoctorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        validated_data["is_doctor"] = True
        password = validated_data.pop("password", None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            return user
