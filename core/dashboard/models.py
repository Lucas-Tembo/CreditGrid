from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class borrower(models.Model):
    STATUS_CHOICES = (
        ('active','Active'),
        ('paid','Paid'),
        ('defaulted','Defaulted'),
    )
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    interest = models.IntegerField()
    date = models.DateField()
    author = models.ForeignKey(User,default=None, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def mark_as_paid(self):
        self.status = 'paid'
        self.save()

    @property
    def interest_amount(self):
        return self.amount * (self.interest/100)
    
    @property
    def amount_due(self):
        return self.amount + self.interest_amount
    
    def __str__(self):
        print(f"__str__ called for:{self.name}")
        return self.name
    

class user_details(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    email = models.EmailField( default= None)
    phone_number = models.IntegerField( default=None)
    author = models.ForeignKey(User,default=None, on_delete=models.CASCADE)



