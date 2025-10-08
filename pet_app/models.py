from django.db import models
from django.contrib.auth.models import User 
# Create your models here.
class Pet(models.Model):
    CATEGORY_CHOICES=[
        ('Dog','Dog'),
        ('Cat','Cat'),
        ('Bird','Bird'),
        ('Other','Other'),
    ]
    name=models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    age = models.IntegerField()
    breed = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='pets/')
    available = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    contact_email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        help_text="Email where adopters can contact the owner"
    )
    adopted = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    @property
    def status(self):
        return "Available" if self.available else "Adopted"

class AdoptionRequest(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.pet.name}"




