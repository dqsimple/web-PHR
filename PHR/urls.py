from django.urls import path
from django.contrib import admin
from PHR import views
from django.conf.urls.static import static
from django.conf import settings
#from . import views

app_name = 'PHR'
"""urlpatterns = [
    path('', views.IndexView.as_view(), name= 'index'),
]"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('edit/', views.phr),
    path('register/', views.register),
    #path('login/', views.login, name='login'),
    path('logout/', views.logout),
    path('Height_Record/', views.HeightRecord),
    path('Weight_Record/', views.WeightRecord),
    path('Temperature_Record/', views.TemperatureRecord),
    path('Steps_Record/', views.StepsRecord),
    path('BMI_Record/', views.BMIRecord),
    path('BloodPressure_Record/', views.BloodPressureRecord),
    path('HeartRate_Record/', views.HeartRateRecord),
    path('Respiration_Record/', views.RespirationRecord),
    path('Smoking_Record/', views.SmokingRecord),
    path('Imaging_History/', views.ImagingHistory),
    path('Laboratory_History/', views.LaboratoryHistory),
    path('Medications_History/', views.MedicationsHistory),
    path('Allergies_History/', views.AllergiesHistory),
    path('Diagnosis_History/', views.DiagnosisHistory),
    path('Visit/<str:En_id>/', views.Visit, name='Visit'),
    path('Visit/ImagingFile/<str:FileCode>/', views.ImagingFile, name='ImagingFile'),
    path('Visit/LaboratoryFile/<str:FileCode>/', views.LaboratoryFile, name='LaboratoryFile')
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)