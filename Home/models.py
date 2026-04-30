from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

# # 1. For Department category  
class Specialization(models.Model):
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.department


# 2. Doctor Details
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, 
        null=True, 
        blank=True)
    img=models.ImageField(upload_to='Doctor',null=True,blank=True)
    phone = models.CharField(max_length=15)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Dr. {self.user.username} ({'Approved' if self.status else 'Pending'})"

# 3. Patient Details
class Patient(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE','Female'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
    age =models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.user.username


# 4. The Appointment
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        unique_together = ('doctor', 'date', 'time')

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.date})"


# 5. For Prescripition to patient by doctor
class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    description = models.TextField()
    prescribed_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.first_name} by Dr. {self.doctor.user.last_name}"


# 6. To save feedback collected from feedback form in contact page
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    feedback_text = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __clstr__(self):
        return f"Feedback from {self.name}"


# 7. To generate a bill of consulting fee
class Bill(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.consultation_fee + self.other_charges
        super().save(*args, **kwargs)