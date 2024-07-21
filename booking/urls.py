from django.urls import path
from .views import *

urlpatterns = [
    path("available-doctors", available_doctors, name="available_associates"),
]