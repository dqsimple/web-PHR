from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username", 'autofocus': ''}))
    password = forms.CharField(label="Password", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password"}))

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Password", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirm Password", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class NameForm(forms.Form):
    your_heart_rate = forms.CharField(label="Your heart rate(bpm)", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    your_blood_pressure_up = forms.CharField(label="Your upper blood pressure(mmHg)", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    your_blood_pressure_down = forms.CharField(label="Your lower blood pressure(mmHg)", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    your_temperature = forms.CharField(label="Your temperature(℃)", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    your_weight = forms.CharField(label="Your weight(Kg)", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    your_disease = forms.CharField(label="Your disease", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

class BasicChangeForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    your_gender = forms.fields.ChoiceField(
        choices=(("Male", "Male"), ("Female", "Female")),
        label="Your gender",
        initial="Male",
        widget=forms.widgets.Select(attrs={'class': 'form-control'})
    )

class DiseaseChangeForm(forms.Form):
    your_disease = forms.CharField(label="Your disease", max_length=100,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
