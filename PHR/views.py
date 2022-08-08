from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponseRedirect
from .form import NameForm
from django.views import View
from . import models
from . import form
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
import hashlib
import datetime
import time
import json
import re
@csrf_exempt

def hash_code(s, salt='PHR'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def index(request):

    if not request.session.get('is_login', None):

        return redirect('/PHR/login/')
    patient = models.Patient.objects.get(username=request.session.get('user_id'))
    if request.method == "POST":
        return HttpResponseRedirect('/PHR/edit/')
    else:
        return render(request, 'index.html', {"patient": patient})

def phr(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    patient = models.Patient.objects.get(username=request.session.get('user_id'))
    if request.method == "POST":
        phr_form = form.NameForm(request.POST)
        message = 'Please write your information!'
        """your_name = request.POST.get('your_name')
        your_gender = request.POST.get('your_disease')
        your_disease = request.POST.get('your_disease')
        if your_name and not your_disease:
            patient = models.Patient.objects.get(name=your_name)
            return render(request, 'phr_change.html', {"patient": patient, "phr_form": phr_form})"""
        your_hr = request.POST.get('your_heart_rate')
        your_bp_up = request.POST.get('your_blood_pressure_up')
        your_bp_down = request.POST.get('your_blood_pressure_down')
        your_temperature = request.POST.get('your_temperature')
        your_weight = request.POST.get('your_weight')
        if your_weight or your_hr or your_bp_up or your_bp_down or your_temperature:
            """
            if request.session['user_name']:
                your_name = request.session['user_name']
            else:
                print("have")
                your_name = request.POST.get('your_name')
            print("edit")
            your_gender = phr_form.cleaned_data.get('your_gender')
            your_disease = phr_form.cleaned_data.get('your_disease')
            """
            if request.session['user_name']:
                your_name = request.session['user_name']
            """your_hr = phr_form.cleaned_data.get('your_heart_rate')
            your_bp_up = phr_form.cleaned_data.get('your_blood_pressure_up')
            your_bp_down = phr_form.cleaned_data.get('your_blood_pressure_down')
            your_temperature = phr_form.cleaned_data.get('your_temperature')
            your_weight = phr_form.cleaned_data.get('your_weight')"""
            regInt = '^0$|^[1-9]\d*$'
            regFloat = '^0\.\d+$|^[1-9]\d*\.\d+$'
            IntOrFloat = regInt + '|' + regFloat
            patternIntOrFloat = re.compile(IntOrFloat)
            if your_weight:
                print("your_weight")
                if patternIntOrFloat.search(your_weight):
                    if float(your_weight) > 600 or float(your_weight) < 0:
                        message = "Wrong weight data!(0<weight<600)"
                        return render(request, 'phr_change.html', locals())
                    else:
                        patient.weight = your_weight
                else:
                    message = "Data is not numeric or decimal!"
                    return render(request, 'phr_change.html', locals())
            else:
                your_weight = "n"
            if your_hr:
                print("your_hr")
                if patternIntOrFloat.search(your_hr):
                    if float(your_hr) > 250 or float(your_hr) < 0:
                        message = "Wrong heart rate data!(0<heart rate<250)"
                        return render(request, 'phr_change.html', locals())
                    else:
                        patient.heart_rate = your_hr
                else:
                    message = "Data is not numeric or decimal!"
                    return render(request, 'phr_change.html', locals())
            else:
                your_hr = "n"
            if your_temperature:
                print("your_temperature")
                if patternIntOrFloat.search(your_temperature):
                    if float(your_temperature) > 50 or float(your_temperature) < 0:
                        message = "Wrong temperature data!(0<temperature<50)"
                        return render(request, 'phr_change.html', locals())
                    else:
                        patient.temperature = your_temperature
                else:
                    message = "Data is not numeric or decimal!"
                    return render(request, 'phr_change.html', locals())
            else:
                your_temperature = "n"
            if your_bp_up:
                print("your_bp_up")
                if patternIntOrFloat.search(your_bp_up):
                    if float(your_bp_up) > 250 or float(your_bp_up) < 50:
                        message = "Wrong upper blood pressure data!(50<upper blood pressure<250)"
                        return render(request, 'phr_change.html', locals())
                    else:
                        patient.blood_pressure_up = your_bp_up
                else:
                    message = "Data is not numeric or decimal!"
                    return render(request, 'phr_change.html', locals())
            else:
                your_bp_up = "n"
            if your_bp_down:
                print("your_bp_down")
                if patternIntOrFloat.search(your_bp_down):
                    if float(your_bp_down) > 250 or float(your_bp_down) < 50:
                        message = "Wrong lower blood pressure data!(50<lower blood pressure<250)"
                        return render(request, 'phr_change.html', locals())
                    else:
                        patient.blood_pressure_down = your_bp_down
                else:
                    message = "Data is not numeric or decimal!"
                    return render(request, 'phr_change.html', locals())
            else:
                your_bp_down = "n"
            request.session['user_name'] = patient.name

            if not patient.r_time:
                print("1")
                patient.r_time = ""
            if not patient.r_weight:
                print("2")
                patient.r_weight = ""
            if not patient.r_temperature:
                patient.r_temperature = ""
            if not patient.r_heart_rate:
                patient.r_heart_rate = ""
            if not patient.r_blood_pressure_up:
                patient.r_blood_pressure_up = ""
            if not patient.r_blood_pressure_down:
                patient.r_blood_pressure_down = ""
            patient.set_list("blood_pressure_up", patient.blood_pressure_up)
            patient.set_list("blood_pressure_down", patient.blood_pressure_down)
            patient.set_list("heart_rate", patient.heart_rate)
            patient.set_list("temperature", patient.temperature)
            patient.set_list("weight", patient.weight)
            patient.set_list("r_time", patient.cc_time.strftime("%Y-%m-%d %H:%M:%S"))
            patient.save()
            """if patternIntOrFloat.search(your_hr) or patternIntOrFloat.search(your_bp_up) or \
                patternIntOrFloat.search(your_temperature) or patternIntOrFloat.search(your_weight) \
                or patternIntOrFloat.search(your_bp_down):
                if float(your_hr) > 250 or float(your_hr) < 0 or float(your_bp_up) > 250 or float(your_bp_up) < 50 or \
                    float(your_temperature) > 50 or float(your_temperature) < 0 or float(your_bp_down) > 250 or float(your_bp_down) < 50 \
                    or float(your_weight) > 600 or float(your_weight) < 0:
                    message = "Wrong data!"
                    return render(request, 'phr_change.html', locals())
                else:
                    
                    patient.name = your_name
                    patient.sex = your_gender
                    patient.disease = your_disease
                    patient.blood_pressure_up = your_bp_up
                    patient.blood_pressure_down = your_bp_down
                    patient.heart_rate = your_hr
                    patient.temperature = your_temperature
                    request.session['user_name'] = patient.name

                    if not patient.r_time:
                        print("1")
                        patient.r_time = ""
                    if not patient.r_weight:
                        print("2")
                        patient.r_weight = ""
                    if not patient.r_temperature:
                        patient.r_temperature = ""
                    if not patient.r_heart_rate:
                        patient.r_heart_rate = ""
                    if not patient.r_blood_pressure_up:
                        patient.r_blood_pressure_up = ""
                    if not patient.r_blood_pressure_down:
                        patient.r_blood_pressure_down = ""
                    patient.set_list("blood_pressure_up", patient.blood_pressure_up)
                    patient.set_list("blood_pressure_down", patient.blood_pressure_down)
                    patient.set_list("heart_rate", patient.heart_rate)
                    patient.set_list("temperature", patient.temperature)
                    patient.set_list("weight", patient.weight)
                    patient.set_list("r_time", patient.cc_time.strftime("%Y-%m-%d %H:%M:%S"))
                    patient.save()
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())"""
        else:
            return render(request, 'phr_change.html', locals())
        #return render(request, '/phr_change.html', {"patient": patient, "phr_form": phr_form})
        print("233")
        return HttpResponseRedirect('/PHR/index/')
    else:
        phr_form = form.NameForm()
        print("322")
        return render(request, 'phr_change.html', {"phr_form": phr_form, "patient": patient})



def register(request):

    if request.method == 'POST':

        register_form = form.RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            if password2 != password1:

                message = 'Password not same!'
                return render(request, 'register.html', locals())
            else:
                same_username = models.Patient.objects.filter(username=username)
                if same_username:
                    message = 'This user name already exists!'

                    return render(request, 'register.html', locals())
                new_user = models.Patient()
                new_user.username = username
                new_user.password = hash_code(password1)
                new_user.save()

                return redirect('/PHR/login/')
        else:

            return render(request, 'register.html', locals())
    register_form = form.RegisterForm()

    return render(request, 'register.html', locals())

def login(request):
    if request.session.get('is_login', None):
        print(request.session.get('is_login', None))
        return redirect('/PHR/index/')
    if request.method == "POST":
        login_form = form.UserForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                print(username)
                user = models.Patient.objects.get(username=username)
            except:
                message = 'User not exist!'
                """return render(request, 'PHR/login.html', locals())"""
                return render(request, 'login.html', {'message': message, 'login_form': login_form})
            if user.password == hash_code(password):
                print("666")
                request.session['is_login'] = True
                print(request.session.get('is_login', None))
                request.session['user_id'] = user.username
                request.session['user_name'] = user.name
                return redirect('/PHR/index/')
            else:
                message = 'Password not correct!'
                return render(request, 'login.html', {'message': message, 'login_form': login_form})
        else:
            return render(request, 'login.html', {'login_form': login_form})
    login_form = form.UserForm()
    return render(request, 'login.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/PHR/login/")
    request.session.flush()
    return redirect("/PHR/login/")
def graph(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    legend_data = ['Heart Rate(bpm)', 'Temperature(℃)', 'Upper Blood Pressure(mmHg)', 'Lower Blood Pressure(mmHg)',
                   'Weight(Kg)']
    patient = models.Patient.objects.get(username=request.session.get('user_id'))
    time_data = patient.get_list("r_time")

    heart_rate_data = patient.get_list("heart_rate")
    temperature_data = patient.get_list("temperature")
    blood_pressure_up_data = patient.get_list("blood_pressure_up")
    blood_pressure_down_data = patient.get_list("blood_pressure_down")
    weight_data = patient.get_list("weight")
    legend_data = json.dumps(legend_data)

    #heart_rate_data = [float(x) for x in heart_rate_data]
    #temperature_data = [float(x) for x in temperature_data]
    #blood_pressure_up_data = [float(x) for x in blood_pressure_up_data]
    #blood_pressure_down_data = [float(x) for x in blood_pressure_down_data]
    #weight_data = [float(x) for x in weight_data]
    weight_data_1 = []
    heart_rate_data_1 = []
    temperature_data_1 = []
    blood_pressure_up_data_1 = []
    blood_pressure_down_data_1 = []
    for i in range(len(weight_data)):
        if weight_data[i] != "n":
            weight_data_1.append([time_data[i], float(weight_data[i])])
        else:
            i = i + 1
    for i in range(len(heart_rate_data)):
        if heart_rate_data[i] != "n":
            heart_rate_data_1.append([time_data[i], float(heart_rate_data[i])])
        else:
            i = i + 1
    for i in range(len(temperature_data)):
        if temperature_data[i] != "n":
            temperature_data_1.append([time_data[i], float(temperature_data[i])])
        else:
            i = i + 1
    for i in range(len(blood_pressure_up_data)):
        if blood_pressure_up_data[i] != "n":
            blood_pressure_up_data_1.append([time_data[i], float(blood_pressure_up_data[i])])
        else:
            i = i + 1
    for i in range(len(blood_pressure_down_data)):
        if blood_pressure_down_data[i] != "n":
            blood_pressure_down_data_1.append([time_data[i], float(blood_pressure_down_data[i])])
        else:
            i = i + 1
    weight_data = weight_data_1
    blood_pressure_down_data = blood_pressure_down_data_1
    heart_rate_data = heart_rate_data_1
    temperature_data = temperature_data_1
    blood_pressure_up_data = blood_pressure_up_data_1
    time_data = json.dumps(time_data)
    heart_rate_data = json.dumps(heart_rate_data)
    temperature_data = json.dumps(temperature_data)
    blood_pressure_up_data = json.dumps(blood_pressure_up_data)
    blood_pressure_down_data = json.dumps(blood_pressure_down_data)
    weight_data = json.dumps(weight_data)
    return render(request, 'graph.html', locals())

def BasicChange(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    patient = models.Patient.objects.get(username=request.session.get('user_id'))
    if request.method == "POST":
        message = 'Please write your information!'
        if request.session['user_name']:
            your_name = request.session['user_name']
        BasicChange_form = form.BasicChangeForm(request.POST)
        your_name =  request.POST.get('your_name')
        your_gender =  request.POST.get('your_gender')
        if your_name or your_gender:
            patient.name = your_name
            patient.sex = your_gender
            patient.save()
        else:
            return render(request, 'phr_BasicChange.html', locals())
        return HttpResponseRedirect('/PHR/index/')
    BasicChange_form = form.BasicChangeForm()
    return render(request, 'phr_BasicChange.html', locals())

def DiseaseChange(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    patient = models.Patient.objects.get(username=request.session.get('user_id'))
    if request.method == "POST":
        message = 'Please write your information!'
        DiseaseChange_form = form.DiseaseChangeForm(request.POST)
        if DiseaseChange_form.is_valid():
            if request.session['user_name']:
                your_name = request.session['user_name']
            your_disease = request.POST.get('your_disease')
            patient.disease = your_disease
            patient.save()
        else:
            return render(request, 'phr_DiseaseChange.html', locals())
        return HttpResponseRedirect('/PHR/index/')
    DiseaseChange_form = form.DiseaseChangeForm(request.POST)
    return render(request, 'phr_DiseaseChange.html', locals())