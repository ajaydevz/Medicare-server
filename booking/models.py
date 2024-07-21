from django.db import models
from accounts.models import User, Doctor
from datetime import date
from django.utils import timezone
from threading import Timer

# Create your models here.

class Available(models.Model):

    STATUS_CHOICES = [
        ("active", "active"),
        ("booked", "booked"),
        ("completed", "completed"),
        ("doctor_blocked and cancelled", "doctor_blocked and cancelled"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    is_morning = models.BooleanField(default=False)
    is_noon = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="active")

    def delete_on_date(self, delay):
        def delete_instance():
            try:
                obj = Available.objects.get(pk=self.pk)
                if obj.date == timezone.now().date() and obj.status != "booked":
                    obj.delete()
                    print(
                        f"Available object with ID {self.pk} has been deleted on {obj.date}."
                    )
                else:
                    if obj.status == "booked":
                        print(
                            f"Available object with ID {self.pk} is booked and cannot be deleted."
                        )
                    else:
                        print(
                            f"Available object with ID {self.pk} is not due for deletion today."
                        )
            except Available.DoesNotExist:
                print(f"Available object with ID {self.pk} does not exist.")

        Timer(delay, delete_instance).start()


class Booking(models.Model):

    STATUS_CHOICES = [
        ("confirmed", "confirmed"),
        ("completed", "completed"),
        ("cancelled", "cancelled"),
        ("cancelled_by_admin", "cancelled_by_admin"),
    ]

    booking_id = models.CharField(max_length=10, default="MC0001", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Available, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    date = models.DateField(default=date(2024, 12, 2))

    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
        default="confirmed",
    )
    shift = models.CharField(max_length=20, blank=True, null=True, default="morning")
    created_at = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True, null=True, default="kozhikode")

    def save(self, *args, **kwargs):
        if not self.pk:
            last_booking = Booking.objects.order_by("-id").first()
            if last_booking:  # If there are existing bookings
                last_id = int(last_booking.booking_id[2:])
                  
                new_id = f"MC{str(last_id + 1).zfill(4)}"
                self.booking_id = new_id 
        super().save(*args, **kwargs) 
    # Call the superclass's save method to actually save the instance


class Rating(models.Model):
    rating_value = models.CharField(max_length=5, blank=True, null=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)






