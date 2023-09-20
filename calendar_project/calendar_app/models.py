from django.db import models

# Create your models here.


class bookingdetails(models.Model):
    name = models.CharField(max_length=255)
    number = models.BigIntegerField()
    email = models.EmailField()
    prizing = models.CharField(max_length=255)
    classs = models.CharField(max_length=255)
    joining_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
