from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path('verify', VerifyView.as_view(), name='verify'),
    path("login", UserLoginView.as_view(), name="login"),
    path("register-doctor", RegisterDoctorView.as_view(), name="register_doctor"),
    path("users-list", UsersManageView.as_view(), name="users-list"),
    path("doctor-list", DoctorListView.as_view(), name="doctor-list"),
    path("get-user", get_user, name="get_user"),

   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)