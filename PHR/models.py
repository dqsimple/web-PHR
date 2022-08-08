from django.db import models
import datetime
from django.utils import timezone

class User(models.Model):
    ID = (('Doctor', "Doctor"), ('Patient', "Patient"))
    username = models.CharField(max_length=200, unique=True)
    identity = models.CharField(max_length=32, choices=ID, default="Patient")
    password = models.CharField(max_length=256)
    c_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-c_time"]
        verbose_name = "Users"

class Patient(User):
    gender = (('Male', "Male"), ('Female', "Female"))
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=32, choices=gender, default="Male")
    disease = models.CharField(max_length=200)
    heart_rate = models.TextField(max_length=30, null=True)
    blood_pressure_up = models.TextField(max_length=30, null=True)
    blood_pressure_down = models.TextField(max_length=30, null=True)
    temperature = models.TextField(max_length=30, null=True)
    weight = models.TextField(max_length=30, null=True)


    cc_time = models.DateTimeField(auto_now=True)
    r_time = models.TextField(null=True, default="")
    r_heart_rate = models.TextField(null=True, default="")
    r_blood_pressure_up = models.TextField(null=True, default="")
    r_blood_pressure_down = models.TextField(null=True, default="")
    r_temperature = models.TextField(null=True, default="")
    r_weight = models.TextField(null=True, default="")

    def __str__(self):
        return self.username

    def set_list(self, info, element):
        if info == "r_time":
            if self.r_time != "":
                self.r_time = self.r_time+ "," + element
            else:
                self.r_time = element
        if info == "heart_rate":
            if self.r_heart_rate != "":
                self.r_heart_rate = self.r_heart_rate + "," + element
            else:
                self.r_heart_rate = element
        if info == "blood_pressure_up":
            if self.r_blood_pressure_up != "":
                self.r_blood_pressure_up = self.r_blood_pressure_up + "," + element
            else:
                self.r_blood_pressure_up = element
        if info == "blood_pressure_down":
            if self.r_blood_pressure_down != "":
                self.r_blood_pressure_down = self.r_blood_pressure_down + "," + element
            else:
                self.r_blood_pressure_down = element
        if info == "temperature":
            if self.r_temperature != "":
                self.r_temperature = self.r_temperature + "," + element
            else:
                self.r_temperature = element
        if info == "weight":
            if self.r_weight != "":
                self.r_weight = self.r_weight + "," + element
            else:
                self.r_weight = element

    def get_list(self, info):
        if info == "r_time":
            if self.r_time != "":
                return self.r_time.split(",")
            else:
                None
        if info == "heart_rate":
            if info == "heart_rate":
                return self.r_heart_rate.split(",")
            else:
                None
        if info == "blood_pressure_up":
            if self.r_blood_pressure_up != "":
                return self.r_blood_pressure_up.split(",")
            else:
                None
        if info == "blood_pressure_down":
            if self.r_blood_pressure_down != "":
                return self.r_blood_pressure_down.split(",")
            else:
                None
        if info == "temperature":
            if self.r_temperature != "":
                return self.r_temperature.split(",")
            else:
                None
        if info == "weight":
            if self.r_weight != "":
                return self.r_weight.split(",")
            else:
                None
    class Meta:
        ordering = ["-c_time"]
        verbose_name = "Patients"




"""class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text"""

#class HealthRecord(models.Model):

# Create your models here.
