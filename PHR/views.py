from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.server import FHIRNotFoundException
import fhirclient.models.humanname as hn
from fhirclient.models import fhirdate, bundle as b, meta, resource, fhirabstractresource, observation, address
from fhirclient.models import patient, contactpoint, period, codeableconcept, coding, quantity, fhirreference, organization
from fhirclient.models import medicationrequest, dosage, extension, duration, timing, ratio, medication, bodystructure, condition
from fhirclient.models import device, allergyintolerance, diagnosticreport, imagingstudy, attachment, binary, media, encounter
from collections import defaultdict
import time
import base64
from dateutil.relativedelta import relativedelta
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
import fhirclient.models.observation as ob
from fhirclient import client
import fhirclient.models.patient as p
from fhirclient.models.medication import Medication
import fhirclient.models.humanname as hn
from fhirclient.models import fhirdate, bundle as b, meta, resource, fhirabstractresource


@csrf_exempt

def hash_code(s, salt='PHR'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def takeFirst(elem):
    return elem[0]

def phrOrganization():
    settings = {
        'app_id': 'phr',
        'api_base': 'https://server.fire.ly'
    }
    smart = client.FHIRClient(settings=settings)
    phr = organization.Organization()
    phr.name = "PHR Prototype"
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.system = "http://terminology.hl7.org/CodeSystem/organization-type"
    coding1.code = "prov"
    coding1.display = "Healthcare Provider"
    code1 = [coding1]
    phr.type = [code1]
    tele1 = contactpoint.ContactPoint()
    tele1.system = "phone"
    tele1.value = "022-655-2300"
    tele1.use = "work"
    phr.telecom = [tele1]
    tele2 = contactpoint.ContactPoint()
    tele2.system = "phone"
    tele2.value = "080-3338-2334"
    telecom = [tele2]
    phr.contact = [telecom]
    response = phr.create(smart.server)
    if response:
        print(f"Created Organzation with id: {response['id']}")
    else:
        print("Failed to create Organzation")

def create_BloodPressure(value1, value2, patient_id, date, organization_id):
    BP = observation.Observation()
    BP.status = "final"
    BP.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '85354-9'
    coding1.system = "http://loinc.org"
    coding1.display = "Blood pressure panel with all children optional"
    code1.coding = [coding1]
    code1.text = "Blood pressure systolic & diastolic"
    BP.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding2]
    BP.category = [code2]
    code3 = codeableconcept.CodeableConcept()
    coding3 = coding.Coding()
    coding3.code = '8480-6'
    coding3.display = 'Systolic blood pressure'
    coding3.system = "http://loinc.org"
    code3.coding = [coding3]
    quantity1 = quantity.Quantity()
    quantity1.value = value1
    quantity1.unit = 'mmHg'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = 'mm[Hg]'
    code4 = codeableconcept.CodeableConcept()
    coding4 = coding.Coding()
    coding4.code = '8462-4'
    coding4.display = 'Diastolic blood pressure'
    coding4.system = "http://loinc.org"
    code4.coding = [coding4]
    quantity2 = quantity.Quantity()
    quantity2.value = value2
    quantity2.unit = 'mmHg'
    quantity2.system = "http://unitsofmeasure.org"
    quantity2.code = 'mm[Hg]'
    component1 = observation.ObservationComponent()
    component1.code = code3
    component1.valueQuantity = quantity1
    component2 = observation.ObservationComponent()
    component2.code = code4
    component2.valueQuantity = quantity2
    BP.component = [component1, component2]
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    BP.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    BP.performer = [performer1]

    return BP

def create_Smoking(value, patient_id, date, organization_id):
    height = observation.Observation()
    height.status = "final"
    height.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '63773-6'
    coding1.system = "http://loinc.org"
    coding1.display = "Body Height"
    code1.text = "Body Height"
    code1.coding = [coding1]
    height.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'social-history'
    coding2.display = 'Social History'
    coding2.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding2]
    height.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = '/d'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = '/d'
    height.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    height.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    height.performer = [performer1]
    return height

def create_BodyHeight(value, patient_id, date, organization_id):
    height = observation.Observation()
    height.status = "final"
    height.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '8302-2'
    coding1.system = "http://loinc.org"
    coding1.display = "Body Height"
    code1.text = "Body Height"
    code1.coding = [coding1]
    height.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding2]
    height.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = 'cm'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = 'cm'
    height.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    height.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    height.performer = [performer1]
    return height

def create_HeartRate(value, patient_id, date, organization_id):
    HR = observation.Observation()
    HR.status = "final"
    HR.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '8867-4'
    coding1.system = "http://loinc.org"
    coding1.display = "Heart rate"
    code1.text = "Heart rate"
    code1.coding = [coding1]
    HR.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding2]
    HR.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = 'beats/minute'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = '/min'
    HR.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    HR.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    HR.performer = [performer1]
    return HR

def create_RespiratoryRate(value, patient_id, date, organization_id):
    RR = observation.Observation()
    RR.status = "final"
    RR.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '9279-1'
    coding1.system = "http://loinc.org"
    coding1.display = "Respiratory rate"
    code1.text = "Respiratory rate"
    code1.coding = [coding1]
    RR.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding2]
    RR.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = 'breaths/minute'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = '/min'
    RR.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    RR.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    RR.performer = [performer1]
    return RR

def create_BodyWeight(value, patient_id ,date, organization_id):
    weight = observation.Observation()
    weight.status = "final"
    weight.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '29463-7'
    coding1.system = "http://loinc.org"
    coding1.display = "Body Weight"
    code1.text = "Body Weight"
    code1.coding = [coding1]
    weight.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding2]
    weight.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = 'kg'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = 'kg'
    weight.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    weight.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    weight.performer = [performer1]
    return weight

def create_BodyTemp(value, patient_id, date, organization_id):
    temp = observation.Observation()
    temp.status = "final"
    temp.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '8310-5'
    coding1.system = "http://loinc.org"
    coding1.display = "Body temperature"
    code1.text = "Body temperature"
    code1.coding = [coding1]
    temp.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding3 = coding.Coding()
    coding3.code = 'vital-signs'
    coding3.display = 'vital-signs'
    coding3.system = "http://hl7.org/fhir/ValueSet/observation-category"
    code2.coding = [coding3]
    temp.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = 'Cel'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = 'Cel'
    temp.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    temp.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    temp.performer = [performer1]
    return temp

def create_BMI(value, patient_id, date, organization_id):
    BMI = observation.Observation()
    BMI.status = "registered"
    BMI.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '39156-5'
    coding1.system = "http://loinc.org"
    coding1.display = "Body mass index (BMI) [Ratio]"
    code1.text = "BMI"
    code1.coding = [coding1]
    BMI.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://terminology.hl7.org/CodeSystem/observation-category"
    code2.coding = [coding2]
    BMI.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = 'kg/m2'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = 'kg/m2'
    BMI.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    BMI.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    BMI.performer = [performer1]
    return BMI

def create_Steps(value, patient_id, date, organization_id):
    steps = observation.Observation()
    steps.status = "final"
    steps.effectiveDateTime = fhirdate.FHIRDate(date)
    code1 = codeableconcept.CodeableConcept()
    coding1 = coding.Coding()
    coding1.code = '41950-7'
    coding1.system = "http://loinc.org"
    coding1.display = "Number of steps"
    code1.text = "Steps"
    code1.coding = [coding1]
    steps.code = code1
    code2 = codeableconcept.CodeableConcept()
    coding2 = coding.Coding()
    coding2.code = 'vital-signs'
    coding2.display = 'vital-signs'
    coding2.system = "http://terminology.hl7.org/CodeSystem/observation-category"
    code2.coding = [coding2]
    steps.category = [code2]
    quantity1 = quantity.Quantity()
    quantity1.value = value
    quantity1.unit = '/24h'
    quantity1.system = "http://unitsofmeasure.org"
    quantity1.code = '/24h'
    steps.valueQuantity = quantity1
    subject1 = fhirreference.FHIRReference()
    subject1.reference = "Patient/" + patient_id
    steps.subject = subject1
    performer1 = fhirreference.FHIRReference()
    performer1.reference = "Organization/" + organization_id
    steps.performer = [performer1]
    return steps

def index(request):
    request.session['is_new'] = True
    request.session['RecordType'] = "Allergies"
    request.session['Encounter'] = "None"
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    p_id = request.session['patient_id']
    patient = models.Patient.objects.filter(cid=p_id)
    if len(patient) > 1:
        patient = patient.get(name=request.session['patient_name'])
    else:
        patient = patient[0]
    #NHINumber = 'baede442-d962-45f1-8958-0cb838540ecf'
    NHINumber = patient.NHINumber
    request.session['NHINumber'] = NHINumber
    request.session['DataType'] = "Record"
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    smart = client.FHIRClient(settings=settings)
    p1 = Patient.read(NHINumber, smart.server)
    print("##########Patient##########")
    print(smart.human_name(p1.name[0]))
    p1_Name = smart.human_name(p1.name[0])
    c_time = time.ctime()
    age = str(int(c_time[-4:]) - int(p1.birthDate.isostring[0:4]))
    print(p1.gender, p1.birthDate.isostring, age, p1.address)
    """organization_id = "dea39875-4931-43b5-9d3b-6d52142b1cc5"
    patient.organization_id = organization_id
    patient.NHINumber = NHINumber
    patient.save()"""
    if p1.address:
        Address = p1.address[0].line[0] + "," + p1.address[0].city + "," + p1.address[0].country
    if p1.telecom:
        for i in p1.telecom:
            if i.system=="phone":
                Phone = i.value
            else:
                Phone = "None"
            if i.system=="email":
                Email = i.value
            else:
                Email = "None"
    else:
        Phone = "None"
        Email = "None"
    BirthDate = p1.birthDate.isostring
    Photo = p1.photo[0].data
    Observation = observation.Observation.where({'patient': NHINumber, '_sort': '-date'}).perform(smart.server)
    Weight = []
    Height = []
    HR = []
    BodyTem = []
    BP = []
    RR = []
    Steps = []
    BMI = []
    Smoking = []
    if Observation.entry != None:
        Observation = [ob.resource for ob in Observation.entry]
        # 可以尝试用include进行优化
        if len(Observation) > 0:
            for Ob in Observation:
                print(Ob.code)
                if Ob.code.coding[0].code == '29463-7':
                    Weight.append(Ob)
                elif Ob.code.coding[0].code == '8302-2':
                    Height.append(Ob)
                elif Ob.code.coding[0].code == '8867-4':
                    HR.append(Ob)
                elif Ob.code.coding[0].code == '8310-5':
                    BodyTem.append(Ob)
                elif Ob.code.coding[0].code == '85354-9':
                    BP.append(Ob)
                elif Ob.code.coding[0].code == '9279-1':
                    RR.append(Ob)
                elif Ob.code.coding[0].code == '41950-7':
                    Steps.append(Ob)
                elif Ob.code.coding[0].code == '39156-5':
                    BMI.append(Ob)
                elif Ob.code.coding[0].code == '63773-6':
                    Smoking.append(Ob)

    """Weight = observation.Observation.where({'patient': NHINumber, 'code': '29463-7', '_count': '2', '_sort': '-date'}).perform(smart.server)
    HR = observation.Observation.where({'patient': NHINumber, 'code': '8867-4', '_count': '2', '_sort': '-date'}).perform(smart.server)
    BodyTem = observation.Observation.where({'patient': NHINumber, 'code': '8310-5', '_count': '2', '_sort': '-date'}).perform(smart.server)
    BP = observation.Observation.where({'patient': NHINumber, 'code': '85354-9', '_count': '2', '_sort': '-date'}).perform(smart.server)
    Height = observation.Observation.where({'patient': NHINumber, 'code': '8302-2', '_count': '2', '_sort': '-date'}).perform(smart.server)
    #RR = observation.Observation.where({'patient': NHINumber, 'code': '9279-1'}).perform(smart.server)
    RR = observation.Observation.where({'patient': NHINumber, 'code': '9279-1', '_count': '2', '_sort': '-date'}).perform(smart.server)
    Steps = observation.Observation.where({'patient': NHINumber, 'code': '41950-7', '_count': '2', '_sort': '-date'}).perform(
        smart.server)
    BMI = observation.Observation.where(
        {'patient': NHINumber, 'code': '39156-5', '_count': '2', '_sort': '-date'}).perform(
        smart.server)
    Smoking = observation.Observation.where(
        {'patient': NHINumber, 'code': '63773-6', '_count': '2', '_sort': '-date'}).perform(
        smart.server)"""
    print(RR)
    if RR != []:
        RR_Name = RR[0].code.text
        if len(RR) > 0:
            RR_Last = str(RR[0].valueQuantity.value)
            if len(RR) > 1:
                RR_Trend = str(RR[0].valueQuantity.value-RR[1].valueQuantity.value)
            else:
                RR_Trend = "None"
        else:
            RR_Last = "None"
    else:
        RR_last = "None"
        RR_Trend = "None"

    if Height != []:
        if len(Height) > 0:
            Height_Last = str(Height[0].valueQuantity.value) + "cm"
            if len(Height) > 1:
                Height_Trend = str(Height[0].valueQuantity.value - Height[1].valueQuantity.value)
            else:
                Height_Trend = "None"
        else:
            Height_Last = "None"
    else:
        Height_Last = "None"
        Height_Trend = "None"

    if Weight != []:
        if len(Weight) > 0:
            Weight_Last = str(Weight[0].valueQuantity.value) + str(Weight[0].valueQuantity.unit)
            if len(Weight) > 1:
                Weight_Trend = str(Weight[0].valueQuantity.value - Weight[1].valueQuantity.value)
            else:
                Weight_Trend = "None"
        else:
            Weight_Last = "None"
    else:
        Weight_Last = "None"
        Weight_Trend = "None"

    if BodyTem != []:

        if len(BodyTem) > 0:
            BodyTem_Last = str(BodyTem[0].valueQuantity.value)
            if len(BodyTem) > 1:
                BodyTem_Trend = str(BodyTem[0].valueQuantity.value - BodyTem[1].valueQuantity.value)
            else:
                BodyTem_Trend = "None"
        else:
            BodyTem_Last = "None"
    else:
        BodyTem_Last = "None"
        BodyTem_Trend = "None"

    if Steps != []:
        if len(Steps) > 0:
            Steps_Last = str(int(Steps[0].valueQuantity.value))
            if len(Steps) > 1:
                Steps_Trend = str(int(Steps[0].valueQuantity.value - Steps[1].valueQuantity.value))
            else:
                Steps_Trend = "None"
        else:
            Steps_Last = "None"
    else:
        Steps_Last = "None"
        Steps_Trend = "None"

    if BMI != []:

        if len(BMI) > 0:
            BMI_Last = str(BMI[0].valueQuantity.value)
            if len(BMI) > 1:
                BMI_Trend = str(BMI[0].valueQuantity.value - BMI[1].valueQuantity.value)
            else:
                BMI_Trend = "None"
        else:
            BMI_Last = "None"
    else:
        BMI_Last = "None"
        BMI_Trend = "None"

    if BP != []:
        if len(BP) > 0:
            BP_Last = str(str(BP[0].component[0].valueQuantity.value) + "/" + str(BP[0].component[1].valueQuantity.value))
            if len(BP) > 1:
                BP_Trend = str(BP[0].component[0].valueQuantity.value - BP[1].component[0].valueQuantity.value) + "/" + str(BP[0].component[1].valueQuantity.value - BP[1].component[1].valueQuantity.value)
            else:
                BP_Trend = "None"
        else:
            BP_Last = "None"
    else:
        BP_Last = "None"
        BP_Trend = "None"

    if HR != []:
        if len(HR) > 0:
            HR_Last = str(HR[0].valueQuantity.value)
            if len(HR) > 1:
                HR_Trend = str(HR[0].valueQuantity.value - HR[1].valueQuantity.value)
            else:
                HR_Trend = "None"
        else:
            HR_Last = "None"
    else:
        HR_Last = "None"
        HR_Trend = "None"

    if Smoking != []:

        if len(Smoking) > 0:
            Smoking_Last = str(int(Smoking[0].valueQuantity.value))
            if len(HR) > 1:
                Smoking_Trend = str(int(Smoking[0].valueQuantity.value - Smoking[1].valueQuantity.value))
            else:
                Smoking_Trend = "None"
        else:
            Smoking_Last = "None"
    else:
        Smoking_Last = "None"
        Smoking_Trend = "None"
    ##################################

    Encounter_List = encounter.Encounter.where({'patient': NHINumber, '_include': ['Encounter:diagnosis', 'Encounter:serviceProvider'], '_sort': '-date'}).perform(smart.server)

    En_All_DataList = []
    En_In_DataList = []
    En_Out_DataList = []
    En_All_List = []
    Condition_TemList = []
    Organization_TemList = []
    if Encounter_List.entry != None:
        Encounter_List = [e.resource for e in Encounter_List.entry]
        #可以尝试用include进行优化
        if len(Encounter_List)>0:
            for i in Encounter_List:
                if i.resource_type == "Encounter":
                    En_All_List.append(i)
                if i.resource_type == "Condition":
                    Condition_TemList.append(i)
                if i.resource_type == "Organization":
                    Organization_TemList.append(i)
            for i in En_All_List:
                Diagnosis_FirstID = []
                Condition_List = []
                Organization_ID = i.serviceProvider.reference.split("/")
                Organization_ID = Organization_ID[-1]
                Organization_Tem = "None"
                for o in Organization_TemList:
                    if o.id == Organization_ID:
                        Organization_Tem = o.name
                En_id = i.id
                for o in i.diagnosis:
                    print(o.rank)
                    if o.rank == 1:
                        Condition_ID = o.condition.reference.split("/")
                        Diagnosis_FirstID = Condition_ID[-1]
                for c in Condition_TemList:
                    Encounter_Tem = c.encounter.reference.split("/")
                    Encounter_Tem = Encounter_Tem[-1]
                    if Encounter_Tem == En_id:
                        Condition_List.append(c)

                if Condition_List != None:
                    if len(Condition_List)>0:
                        tem = []
                        for c in Condition_List:
                            print("##############")
                            print(Diagnosis_FirstID)
                            print(c.id)
                            if c.id == Diagnosis_FirstID:
                                tem_str = ""
                                for disease in c.code.coding:
                                    if tem_str == "":
                                        tem_str += disease.display
                                    else:
                                        tem_str += "; " + disease.display
                                T_Start = i.period.start.isostring

                                try:
                                    T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    try:
                                        T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                    except ValueError:
                                        T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%d").strftime("%Y-%m-%d")

                                T_End = i.period.end.isostring
                                try:
                                    T_End = datetime.datetime.strptime(T_End, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    try:
                                        T_End = datetime.datetime.strptime(T_End, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                    except ValueError:
                                        T_End = datetime.datetime.strptime(T_End, "%Y-%m-%d").strftime("%Y-%m-%d")

                                if i.class_fhir.code == "AMB":
                                    tem = [i.id, "Outpatient", T_Start, T_End,
                                                    Organization_Tem, tem_str]
                                if i.class_fhir.code == "IMP" or i.class_fhir.code == "ACUTE" or i.class_fhir.code == "NONAC":
                                    tem = [i.id, "Inpatient", T_Start, T_End,
                                           Organization_Tem, tem_str]
                                break
                        tem_str = ""
                        for c in Condition_List:

                            if c.id != Diagnosis_FirstID:

                                for disease in c.code.coding:
                                    if tem_str == "":
                                        tem_str += disease.display
                                    else:
                                        tem_str += "; " + disease.display

                        tem.append(tem_str)

                        En_All_DataList.append(tem)


    print("########END############")


    if request.method == "POST":
        pass
    else:
        return render(request, 'index.html', locals())

def phr(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    NHINumber = request.session['NHINumber']
    smart = client.FHIRClient(settings=settings)
    p1 = Patient.read(NHINumber, smart.server)
    p1_Name = smart.human_name(p1.name[0])
    c_time = time.ctime()
    age = str(int(c_time[-4:]) - int(p1.birthDate.isostring[0:4]))

    Photo = p1.photo[0].data
    print(p1.gender, p1.birthDate.isostring, age, p1.address)
    if p1.address:
        Address = p1.address[0].line[0] + "," + p1.address[0].city + "," + p1.address[0].country
    if p1.telecom:
        if p1.telecom[0]:
            Phone = p1.telecom[0].value
        else:
            Phone = "None"
        if len(p1.telecom)==2:
            Email = p1.telecom[1].value
        else:
            Email = "None"
    else:
        Phone = "None"
        Email = "None"

    BirthDate = p1.birthDate.isostring
    Observation = observation.Observation.where({'patient': NHINumber, '_sort': '-date'}).perform(smart.server)

    Weight_List = []
    Height_List = []
    if Observation.entry != None:
        Observation = [ob.resource for ob in Observation.entry]
        #可以尝试用include进行优化
        if len(Observation)>0:
            for Ob in Observation:
                if Ob.code == '29463-7':
                    Weight_List.append(Ob)
                elif Ob.code == '8302-2':
                    Height_List.append(Ob)
        if len(Weight_List)>0:
            Weight = Weight_List[0]
            Weight_Name = Weight[0].code.text
            Weight_Last = str(Weight[0].valueQuantity.value) + " " + Weight[0].valueQuantity.unit
        else:
            Weight = "None"
        if len(Height_List)>0:
            Height = Height_List[0]
            Height_Name = Height[0].code.text
            Height_Last = str(Height[0].valueQuantity.value) + " " + Height[0].valueQuantity.unit
        else:
            Height = "None"

    p_id = request.session['patient_id']
    patient = models.Patient.objects.filter(cid=p_id)
    if len(patient) > 1:
        patient = patient.get(name=request.session['patient_name'])
    else:
        patient = patient[0]
    organization_id = patient.organization_id
    """time_data = patient.get_list("r_time")
    if request.session['is_new'] == False:
        your_number = int(request.session['number'])
        tem_date = time_data[your_number]"""
    if request.method == "POST":
        phr_form = form.NameForm(request.POST)
        message = 'Please write your information!'

        if request.session['user_name']:
            your_name = request.session['user_name']
        your_date = request.POST.get('your_date')
        your_height = request.POST.get('your_height')
        your_weight = request.POST.get('your_weight')
        your_temperature = request.POST.get('your_temperature')
        your_steps = request.POST.get('your_steps')
        your_BMI = request.POST.get('your_BMI')
        your_bp_up = request.POST.get('your_blood_pressure_up')
        your_bp_down = request.POST.get('your_blood_pressure_down')
        your_pr = request.POST.get('your_pulse_rate')
        your_respiration = request.POST.get('your_respiration')
        your_smoking = request.POST.get('your_smoking')

        regInt = '^0$|^[1-9]\d*$'
        regFloat = '^0\.\d+$|^[1-9]\d*\.\d+$'
        IntOrFloat = regInt + '|' + regFloat
        patternIntOrFloat = re.compile(IntOrFloat)
        patternInt = re.compile(regInt)
        date = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        date = date[:-2] + ":" + date[-2:]
        if your_smoking:
            print("your_smoking")
            if patternInt.search(your_smoking):
                your_smoking = float(your_smoking)
                if float(your_smoking) < 0:
                    message = "Wrong Smoking data!(0<Smoking)"
                    return render(request, 'phr_change.html', locals())
                else:
                    Smoking = create_Smoking(your_smoking, p1.id, date, organization_id)
                    response = Smoking.create(smart.server)
                    if response:
                        print(f"Created Steps with id: {response['id']}")
                    else:
                        print("Failed to create Steps")
            else:
                message = "Data is not numeric!"
                return render(request, 'phr_change.html', locals())
        if your_steps:
            print("your_steps")
            if patternInt.search(your_steps):
                your_steps = float(your_steps)
                if float(your_steps) < 0:
                    message = "Wrong Steps data!(0<Steps)"
                    return render(request, 'phr_change.html', locals())
                else:
                    Steps = create_Steps(your_steps, p1.id, date, organization_id)
                    print(Steps.as_json())
                    response = Steps.create(smart.server)
                    if response:
                        print(f"Created Steps with id: {response['id']}")
                    else:
                        print("Failed to create Steps")
            else:
                message = "Data is not numeric!"
                return render(request, 'phr_change.html', locals())
        if your_BMI:
            print("your_BMI")
            if patternIntOrFloat.search(your_BMI):
                your_BMI = float(your_BMI)
                if float(your_BMI) > 50 or float(your_BMI) < 0:
                    message = "Wrong BMI data!(0<BMI<50)"
                    return render(request, 'phr_change.html', locals())
                else:
                    BMI = create_BMI(your_BMI, p1.id, date, organization_id)
                    response = BMI.create(smart.server)
                    if response:
                        print(f"Created BMI with id: {response['id']}")
                    else:
                        print("Failed to create BMI")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())
        if your_respiration:
            print("your_respiration")
            if patternIntOrFloat.search(your_respiration):
                your_respiration = float(your_respiration)
                if float(your_respiration) > 80 or float(your_respiration) < 0:
                    message = "Wrong respiration data!(0<respiration<80)"
                    return render(request, 'phr_change.html', locals())
                else:
                    Respiration = create_RespiratoryRate(your_respiration, p1.id, date, organization_id)
                    response = Respiration.create(smart.server)
                    if response:
                        print(f"Created Respiration with id: {response['id']}")
                    else:
                        print("Failed to create Respiration")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())
        if your_height:
            print("your_height")
            if patternIntOrFloat.search(your_height):
                your_height = float(your_height)
                if float(your_height) > 300 or float(your_height) < 0:
                    message = "Wrong height data!(0<height<300)"
                    return render(request, 'phr_change.html', locals())
                else:
                    Height = create_BodyHeight(your_height, p1.id, date, organization_id)
                    response = Height.create(smart.server)
                    if response:
                        print(f"Created Height with id: {response['id']}")
                    else:
                        print("Failed to create Height")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())
        if your_weight:
            print("your_weight")
            if patternIntOrFloat.search(your_weight):
                your_weight = float(your_weight)
                if float(your_weight) > 300 or float(your_weight) < 0:
                    message = "Wrong weight data!(0<weight<300)"
                    return render(request, 'phr_change.html', locals())
                else:
                    Weight = create_BodyWeight(your_weight, p1.id, date, organization_id)
                    response = Weight.create(smart.server)
                    if response:
                        print(f"Created Weight with id: {response['id']}")
                    else:
                        print("Failed to create Weight")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())

        if your_pr:
            print("your_hr")
            if patternIntOrFloat.search(your_pr):
                your_pr = float(your_pr)
                if float(your_pr) > 250 or float(your_pr) < 0:
                    message = "Wrong heart rate data!(0<heart rate<250)"
                    return render(request, 'phr_change.html', locals())
                else:
                    Pulse = create_HeartRate(your_pr, p1.id, date, organization_id)
                    response = Pulse.create(smart.server)
                    if response:
                        print(f"Created Pulse with id: {response['id']}")
                    else:
                        print("Failed to create Pulse")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())

        if your_temperature:
            print("your_temperature")
            if patternIntOrFloat.search(your_temperature):
                your_temperature = float(your_temperature)
                if float(your_temperature) > 50 or float(your_temperature) < 0:
                    message = "Wrong temperature data!(0<temperature<50)"
                    return render(request, 'phr_change.html', locals())
                else:

                    Temperature = create_BodyTemp(your_temperature, p1.id, date, organization_id)
                    response = Temperature.create(smart.server)
                    if response:
                        print(f"Created Temperature with id: {response['id']}")
                    else:
                        print("Failed to create Temperature")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())

        if your_bp_up and your_bp_down:
            print("your_bp_up")
            if patternIntOrFloat.search(your_bp_up) and patternIntOrFloat.search(your_bp_down):
                your_bp_up = float(your_bp_up)
                your_bp_down = float(your_bp_down)
                if float(your_bp_up) > 250 or float(your_bp_up) < 50:
                    message = "Wrong Systolic blood pressure data!(50<upper blood pressure<250)"
                    return render(request, 'phr_change.html', locals())
                elif float(your_bp_down) > 250 or float(your_bp_down) < 50:
                    message = "Wrong Diastolic blood pressure data!(50<lower blood pressure<250)"
                    return render(request, 'phr_change.html', locals())
                else:
                    patient.blood_pressure_up = your_bp_up
                    Weight = create_BloodPressure(your_bp_up, your_bp_down, p1.id, date, organization_id)
                    response = Weight.create(smart.server)
                    if response:
                        print(f"Created Weight with id: {response['id']}")
                    else:
                        print("Failed to create Weight")
            else:
                message = "Data is not numeric or decimal!"
                return render(request, 'phr_change.html', locals())

        return HttpResponseRedirect('/PHR/index/')

    else:
        phr_form = form.NameForm()
        print("322")
    return render(request, 'phr_change.html', locals())





def register(request):

    if request.method == 'POST':

        register_form = form.RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            patient_name = register_form.cleaned_data.get('patient_name')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            NHINumber = register_form.cleaned_data.get('NHINumber')
            phoneNumber = register_form.cleaned_data.get('phoneNumber')
            organization_id = "dea39875-4931-43b5-9d3b-6d52142b1cc5"
            if password2 != password1:

                message = 'Password not same!'
                return render(request, 'register.html', locals())
            else:
                same_username = models.User.objects.filter(username=username)
                if same_username:
                    message = 'This user name already exists!'
                    return render(request, 'register.html', locals())
                new_user = models.User()
                new_user.username = username
                new_user.password = hash_code(password1)

                new_patient = models.Patient()
                new_user.save()
                new_patient.cid = new_user
                new_patient.name = patient_name
                new_patient.NHINumber = NHINumber
                new_patient.phoneNumber = phoneNumber
                new_patient.organization_id = organization_id
                new_patient.add_time = new_patient.cc_time.strftime("%Y-%m-%d %H:%M:%S")
                new_patient.save()

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
                user = models.User.objects.get(username=username)
            except:
                message = 'User not exist!'
                """return render(request, 'PHR/login.html', locals())"""
                return render(request, 'login.html', {'message': message, 'login_form': login_form})
            if user.password == hash_code(password):
                pid = user.u_id
                print(pid)
                patient = models.Patient.objects.filter(cid=pid)
                patient = patient[0]
                print("666")
                request.session['is_login'] = True
                print(request.session.get('is_login', None))
                request.session['user_id'] = user.username
                request.session['user_name'] = patient.name
                #request.session['patient_id'] = user.get_list("pid")[0]
                p_tem = models.Patient.objects.filter(cid_id=user.u_id)
                request.session['patient_id'] = p_tem[0].cid_id
                request.session["patient_name"] = p_tem[0].name
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

def WeightRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["Weight"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Weight = observation.Observation.where({'patient': NHINumber, 'code': '29463-7', '_sort': '-date'}).perform(smart.server)
    Weight_TimeList = []
    Weight_DataList = []
    Weight_YearDic = {}
    Weight_MonthDic = {}
    Weight_DayDic = {}
    Weight_DataList1 = []
    Weight_DataList2 = []
    # one month
    Weight_DataList3 = []
    # one years
    Weight_DataList4 = []
    # all
    Weight_DataList5 = []
    if Weight.entry != None:
        Weight = [ob.resource for ob in Weight.entry]
        if len(Weight) > 0:


            for i in Weight:
                print("Weight Test-----------------")
                if i.effectiveDateTime != None:
                    Weight_TimeList.append(i.effectiveDateTime.isostring)
                    # Height_DataList.append(str(i.valueQuantity.value) + " " + i.valueQuantity.unit)
                    Weight_DataList.append(float(i.valueQuantity.value))

            if Weight_TimeList != []:
                for i in range(len(Weight_TimeList)):
                    #Height_TimeList[i] = Height_TimeList[i][:-1]
                    #Height_TimeList[i] = Height_TimeList[i][:10] + " " + Height_TimeList[i][11:]
                    Weight_DataList1.append([Weight_TimeList[i], Weight_DataList[i]])
                    Weight_DataList1.reverse()
                    Weight_DataList2.append([Weight_TimeList[i], str(Weight_DataList[i])])

                try:
                    date_tem = datetime.datetime.strptime(Weight_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(Weight_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(Weight_TimeList[0], "%Y-%m-%d")
                try:
                    Weight_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Weight_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    Weight_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Weight_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(Weight_MonthTem)

                for t, data in Weight_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in Weight_DayDic:
                        Weight_DayDic[str(date_tem.date())].append(data)
                    else:
                        Weight_DayDic[str(date_tem.date())] = [data]
                for time, value in Weight_DayDic.items():
                    average = sum(value) / len(value)
                    Weight_DataList5.append([time, average])
                for t, data in Weight_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > Weight_MonthTem:
                        Weight_DataList3.append([t, data])
                    if date_tem > Weight_YearTem:
                        Weight_DataList4.append([t,data])
                print(Weight_YearDic, Weight_MonthDic, Weight_DayDic)
                print(Weight_DataList3,Weight_DataList4,Weight_DataList5)
            Weight_DataList1 = json.dumps(Weight_DataList1)
            Weight_DataList3 = json.dumps(Weight_DataList3)
            Weight_DataList4 = json.dumps(Weight_DataList4)
            Weight_DataList5 = json.dumps(Weight_DataList5)
    return render(request, 'Weight_Record.html', locals())

def HeightRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["Height"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Height = observation.Observation.where({'patient': NHINumber, 'code': '8302-2', '_sort': '-date'}).perform(smart.server)
    Height_TimeList = []
    Height_DataList = []
    Height_YearDic = {}
    Height_MonthDic = {}
    Height_DayDic = {}
    Height_DataList1 = []
    Height_DataList2 = []
    # one month
    Height_DataList3 = []
    # one years
    Height_DataList4 = []
    # all
    Height_DataList5 = []
    if Height.entry != None:
        Height = [ob.resource for ob in Height.entry]
        if len(Height)>0:


            for i in Height:
                print("Height Test-----------------")
                if i.effectiveDateTime != None:
                    Height_TimeList.append(i.effectiveDateTime.isostring)
                    # Height_DataList.append(str(i.valueQuantity.value) + " " + i.valueQuantity.unit)
                    Height_DataList.append(float(i.valueQuantity.value))

            if Height_TimeList != []:
                for i in range(len(Height_TimeList)):
                    #Height_TimeList[i] = Height_TimeList[i][:-1]
                    #Height_TimeList[i] = Height_TimeList[i][:10] + " " + Height_TimeList[i][11:]
                    Height_DataList1.append([Height_TimeList[i], Height_DataList[i]])
                    Height_DataList1.reverse()
                    Height_DataList2.append([Height_TimeList[i], str(Height_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(Height_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(Height_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(Height_TimeList[0], "%Y-%m-%d")
                try:
                    Height_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Height_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    Height_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Height_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(Height_MonthTem)

                for t, data in Height_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in Height_DayDic:
                        Height_DayDic[str(date_tem.date())].append(data)
                    else:
                        Height_DayDic[str(date_tem.date())] = [data]
                for time, value in Height_DayDic.items():
                    average = sum(value) / len(value)
                    Height_DataList5.append([time, average])
                for t, data in Height_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > Height_MonthTem:
                        Height_DataList3.append([t, data])
                    if date_tem > Height_YearTem:
                        Height_DataList4.append([t,data])
                print(Height_YearDic, Height_MonthDic, Height_DayDic)
                print(Height_DataList3,Height_DataList4,Height_DataList5)
            Height_DataList1 = json.dumps(Height_DataList1)
            Height_DataList3 = json.dumps(Height_DataList3)
            Height_DataList4 = json.dumps(Height_DataList4)
            Height_DataList5 = json.dumps(Height_DataList5)
    return render(request, 'Height_Record.html', locals())

def TemperatureRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["Temperature"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Temperature = observation.Observation.where({'patient': NHINumber, 'code': '8310-5', '_sort': '-date'}).perform(smart.server)
    Temperature_TimeList = []
    Temperature_DataList = []
    Temperature_YearDic = {}
    Temperature_MonthDic = {}
    Temperature_DayDic = {}
    Temperature_DataList1 = []
    Temperature_DataList2 = []
    # one month
    Temperature_DataList3 = []
    # one years
    Temperature_DataList4 = []
    # all
    Temperature_DataList5 = []
    if Temperature.entry != None:
        Temperature = [ob.resource for ob in Temperature.entry]
        if len(Temperature)>0:

            for i in Temperature:
                print("Temperature Test-----------------")
                if i.effectiveDateTime != None:
                    Temperature_TimeList.append(i.effectiveDateTime.isostring)

                    Temperature_DataList.append(float(i.valueQuantity.value))

            if Temperature_TimeList != []:
                for i in range(len(Temperature_TimeList)):

                    Temperature_DataList1.append([Temperature_TimeList[i], Temperature_DataList[i]])
                    Temperature_DataList1.reverse()
                    Temperature_DataList2.append([Temperature_TimeList[i], str(Temperature_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(Temperature_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(Temperature_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(Temperature_TimeList[0], "%Y-%m-%d")
                try:
                    Temperature_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Temperature_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    Temperature_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Temperature_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(Temperature_MonthTem)

                for t, data in Temperature_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in Temperature_DayDic:
                        Temperature_DayDic[str(date_tem.date())].append(data)
                    else:
                        Temperature_DayDic[str(date_tem.date())] = [data]
                for time, value in Temperature_DayDic.items():
                    average = sum(value) / len(value)
                    Temperature_DataList5.append([time, average])
                for t, data in Temperature_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > Temperature_MonthTem:
                        Temperature_DataList3.append([t, data])
                    if date_tem > Temperature_YearTem:
                        Temperature_DataList4.append([t,data])
                print(Temperature_YearDic, Temperature_MonthDic, Temperature_DayDic)
                print(Temperature_DataList3,Temperature_DataList4,Temperature_DataList5)
            Temperature_DataList1 = json.dumps(Temperature_DataList1)
            Temperature_DataList3 = json.dumps(Temperature_DataList3)
            Temperature_DataList4 = json.dumps(Temperature_DataList4)
            Temperature_DataList5 = json.dumps(Temperature_DataList5)
    return render(request, 'Temperature_Record.html', locals())

def StepsRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["Steps"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Steps = observation.Observation.where({'patient': NHINumber, 'code': '41950-7', '_sort': '-date'}).perform(smart.server)
    Steps_TimeList = []
    Steps_DataList = []
    Steps_YearDic = {}
    Steps_MonthDic = {}
    Steps_DayDic = {}
    Steps_DataList1 = []
    Steps_DataList2 = []
    # one month
    Steps_DataList3 = []
    # one years
    Steps_DataList4 = []
    # all
    Steps_DataList5 = []
    if Steps.entry != None:
        Steps = [ob.resource for ob in Steps.entry]
        if len(Steps)>0:

            for i in Steps:
                print("Steps Test-----------------")
                if i.effectiveDateTime != None:
                    Steps_TimeList.append(i.effectiveDateTime.isostring)

                    Steps_DataList.append(float(i.valueQuantity.value))

            if Steps_TimeList != []:
                for i in range(len(Steps_TimeList)):

                    Steps_DataList1.append([Steps_TimeList[i], Steps_DataList[i]])
                    Steps_DataList1.reverse()
                    Steps_DataList2.append([Steps_TimeList[i], str(Steps_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(Steps_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(Steps_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(Steps_TimeList[0], "%Y-%m-%d")
                try:
                    Steps_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Steps_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    Steps_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Steps_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(Steps_MonthTem)

                for t, data in Steps_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")


                    if str(date_tem.date()) in Steps_DayDic:
                        Steps_DayDic[str(date_tem.date())].append(data)
                    else:
                        Steps_DayDic[str(date_tem.date())] = [data]
                for time, value in Steps_DayDic.items():
                    average = sum(value) / len(value)
                    Steps_DataList5.append([time, average])
                for t, data in Steps_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > Steps_MonthTem:
                        Steps_DataList3.append([t, data])
                    if date_tem > Steps_YearTem:
                        Steps_DataList4.append([t,data])
                print(Steps_YearDic, Steps_MonthDic, Steps_DayDic)
                print(Steps_DataList3,Steps_DataList4,Steps_DataList5)
            Steps_DataList1 = json.dumps(Steps_DataList1)
            Steps_DataList3 = json.dumps(Steps_DataList3)
            Steps_DataList4 = json.dumps(Steps_DataList4)
            Steps_DataList5 = json.dumps(Steps_DataList5)
    return render(request, 'Steps_Record.html', locals())

def BMIRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["BMI"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    BMI = observation.Observation.where({'patient': NHINumber, 'code': '39156-5', '_sort': '-date'}).perform(smart.server)
    BMI_TimeList = []
    BMI_DataList = []
    BMI_YearDic = {}
    BMI_MonthDic = {}
    BMI_DayDic = {}
    BMI_DataList1 = []
    BMI_DataList2 = []
    # one month
    BMI_DataList3 = []
    # one years
    BMI_DataList4 = []
    # all
    BMI_DataList5 = []
    if BMI.entry != None:
        BMI = [ob.resource for ob in BMI.entry]
        if len(BMI)>0:

            for i in BMI:
                print("BMI Test-----------------")
                if i.effectiveDateTime != None:
                    BMI_TimeList.append(i.effectiveDateTime.isostring)

                    BMI_DataList.append(float(i.valueQuantity.value))

            if BMI_TimeList != []:
                for i in range(len(BMI_TimeList)):

                    BMI_DataList1.append([BMI_TimeList[i], BMI_DataList[i]])
                    BMI_DataList1.reverse()
                    BMI_DataList2.append([BMI_TimeList[i], str(BMI_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(BMI_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(BMI_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(BMI_TimeList[0], "%Y-%m-%d")
                try:
                    BMI_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    BMI_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    BMI_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    BMI_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(BMI_MonthTem)

                for t, data in BMI_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in BMI_DayDic:
                        BMI_DayDic[str(date_tem.date())].append(data)
                    else:
                        BMI_DayDic[str(date_tem.date())] = [data]
                for time, value in BMI_DayDic.items():
                    average = sum(value) / len(value)
                    BMI_DataList5.append([time, average])
                for t, data in BMI_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > BMI_MonthTem:
                        BMI_DataList3.append([t, data])
                    if date_tem > BMI_YearTem:
                        BMI_DataList4.append([t,data])
                print(BMI_YearDic, BMI_MonthDic, BMI_DayDic)
                print(BMI_DataList3,BMI_DataList4,BMI_DataList5)
            BMI_DataList1 = json.dumps(BMI_DataList1)
            BMI_DataList3 = json.dumps(BMI_DataList3)
            BMI_DataList4 = json.dumps(BMI_DataList4)
            BMI_DataList5 = json.dumps(BMI_DataList5)
    return render(request, 'BMI_Record.html', locals())

def BloodPressureRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    # higher lower
    Legend_Data = ["Systolic Blood Pressure", "Diastolic Blood Pressure"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    """if BP.entry != None:
        BP = [ob.resource for ob in BP.entry]
        if len(BP) > 0:
            BP_Last = str(str(BP[0].component[0].valueQuantity.value) + "/" + str(BP[0].component[1].valueQuantity.value))
            if len(BP) > 1:
                BP_Trend = str(BP[0].component[0].valueQuantity.value - BP[1].component[0].valueQuantity.value) + "/" + str(BP[0].component[1].valueQuantity.value - BP[1].component[1].valueQuantity.value)
            else:
                BP_Trend = "None"
        else:
            BP_Last = "None"
    else:
        BP_Last = "None"
        BP_Trend = "None"
        """
    NHINumber = request.session['NHINumber']
    BloodPressure = observation.Observation.where({'patient': NHINumber, 'code': '85354-9', '_sort': '-date'}).perform(smart.server)
    BloodPressure_TimeList = []
    # lower
    DiastolicBloodPressure_DataList = []
    DiastolicBloodPressure_YearDic = {}
    DiastolicBloodPressure_MonthDic = {}
    DiastolicBloodPressure_DayDic = {}
    # higher
    SystolicBloodPressure_DataList = []
    SystolicBloodPressure_YearDic = {}
    SystolicBloodPressure_MonthDic = {}
    SystolicBloodPressure_DayDic = {}
    SystolicBloodPressure_DataList1 = []
    # SystolicBloodPressure_DataList2 = []
    DiastolicBloodPressure_DataList1 = []
    # DiastolicBloodPressure_DataList2 = []
    BloodPressure_DataList2 = []

    # one month
    SystolicBloodPressure_DataList3 = []
    # one years
    SystolicBloodPressure_DataList4 = []
    # all
    SystolicBloodPressure_DataList5 = []
    # one month
    DiastolicBloodPressure_DataList3 = []
    # one years
    DiastolicBloodPressure_DataList4 = []
    # all
    DiastolicBloodPressure_DataList5 = []
    if BloodPressure.entry != None:
        BloodPressure = [ob.resource for ob in BloodPressure.entry]
        if len(BloodPressure)>0:

            for i in BloodPressure:
                print("BloodPressure Test-----------------")
                if i.effectiveDateTime != None:
                    BloodPressure_TimeList.append(i.effectiveDateTime.isostring)
                    for o in i.component:
                        code_List = o.code.coding
                        for code in code_List:
                            if code.code == "8480-6" or code.code == "271649006" or code.code == "bp-s":
                                SystolicBloodPressure_DataList.append(float(o.valueQuantity.value))
                                print("8480-6")
                            if code.code == "8462-4":
                                DiastolicBloodPressure_DataList.append(float(o.valueQuantity.value))
                                print("8462-4")
                        print(o.valueQuantity.value)

            if BloodPressure_TimeList != []:
                for i in range(len(BloodPressure_TimeList)):
                    print(BloodPressure_TimeList)
                    print(SystolicBloodPressure_DataList)
                    SystolicBloodPressure_DataList1.append([BloodPressure_TimeList[i], SystolicBloodPressure_DataList[i]])
                    SystolicBloodPressure_DataList1.reverse()


                    DiastolicBloodPressure_DataList1.append([BloodPressure_TimeList[i], DiastolicBloodPressure_DataList[i]])
                    DiastolicBloodPressure_DataList1.reverse()

                    BloodPressure_DataList2.append([BloodPressure_TimeList[i], str(SystolicBloodPressure_DataList[i]), str(DiastolicBloodPressure_DataList[i])])

                try:
                    date_tem = datetime.datetime.strptime(BloodPressure_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(BloodPressure_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(BloodPressure_TimeList[0], "%Y-%m-%d")
                try:
                    BloodPressure_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    BloodPressure_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    BloodPressure_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    BloodPressure_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(BloodPressure_MonthTem)

                for t, data in SystolicBloodPressure_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if str(date_tem.date()) in SystolicBloodPressure_DayDic:
                        SystolicBloodPressure_DayDic[str(date_tem.date())].append(data)
                    else:
                        SystolicBloodPressure_DayDic[str(date_tem.date())] = [data]
                for time, value in SystolicBloodPressure_DayDic.items():
                    average = sum(value) / len(value)
                    SystolicBloodPressure_DataList5.append([time, average])
                for t, data in SystolicBloodPressure_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > BloodPressure_MonthTem:
                        SystolicBloodPressure_DataList3.append([t, data])
                    if date_tem > BloodPressure_YearTem:
                        SystolicBloodPressure_DataList4.append([t,data])

                for t, data in DiastolicBloodPressure_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if str(date_tem.date()) in DiastolicBloodPressure_DayDic:
                        DiastolicBloodPressure_DayDic[str(date_tem.date())].append(data)
                    else:
                        DiastolicBloodPressure_DayDic[str(date_tem.date())] = [data]
                for time, value in DiastolicBloodPressure_DayDic.items():
                    average = sum(value) / len(value)
                    DiastolicBloodPressure_DataList5.append([time, average])
                for t, data in DiastolicBloodPressure_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > BloodPressure_MonthTem:
                        DiastolicBloodPressure_DataList3.append([t, data])
                    if date_tem > BloodPressure_YearTem:
                        DiastolicBloodPressure_DataList4.append([t,data])
                #print(BloodPressure_YearDic, BloodPressure_MonthDic, BloodPressure_DayDic)
                #print(BloodPressure_DataList3,BloodPressure_DataList4,BloodPressure_DataList5)

                #BloodPressure_DataList1 = json.dumps(BloodPressure_DataList1)
            SystolicBloodPressure_DataList3 = json.dumps(SystolicBloodPressure_DataList3)
            SystolicBloodPressure_DataList4 = json.dumps(SystolicBloodPressure_DataList4)
            SystolicBloodPressure_DataList5 = json.dumps(SystolicBloodPressure_DataList5)

            DiastolicBloodPressure_DataList3 = json.dumps(DiastolicBloodPressure_DataList3)
            DiastolicBloodPressure_DataList4 = json.dumps(DiastolicBloodPressure_DataList4)
            DiastolicBloodPressure_DataList5 = json.dumps(DiastolicBloodPressure_DataList5)
    return render(request, 'BloodPressure_Record.html', locals())

def HeartRateRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["HeartRate"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    HeartRate = observation.Observation.where({'patient': NHINumber, 'code': '8867-4', '_sort': '-date'}).perform(smart.server)
    HeartRate_TimeList = []
    HeartRate_DataList = []
    HeartRate_YearDic = {}
    HeartRate_MonthDic = {}
    HeartRate_DayDic = {}
    HeartRate_DataList1 = []
    HeartRate_DataList2 = []
    # one month
    HeartRate_DataList3 = []
    # one years
    HeartRate_DataList4 = []
    # all
    HeartRate_DataList5 = []
    if HeartRate.entry != None:
        HeartRate = [ob.resource for ob in HeartRate.entry]
        if len(HeartRate)>0:

            for i in HeartRate:
                print("HeartRate Test-----------------")
                if i.effectiveDateTime != None:
                    HeartRate_TimeList.append(i.effectiveDateTime.isostring)

                    HeartRate_DataList.append(float(i.valueQuantity.value))

            if HeartRate_TimeList != []:
                for i in range(len(HeartRate_TimeList)):

                    HeartRate_DataList1.append([HeartRate_TimeList[i], HeartRate_DataList[i]])
                    HeartRate_DataList1.reverse()
                    HeartRate_DataList2.append([HeartRate_TimeList[i], str(HeartRate_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(HeartRate_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(HeartRate_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(HeartRate_TimeList[0], "%Y-%m-%d")
                try:
                    HeartRate_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    HeartRate_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    HeartRate_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    HeartRate_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(HeartRate_MonthTem)

                for t, data in HeartRate_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in HeartRate_DayDic:
                        HeartRate_DayDic[str(date_tem.date())].append(data)
                    else:
                        HeartRate_DayDic[str(date_tem.date())] = [data]
                for time, value in HeartRate_DayDic.items():
                    average = sum(value) / len(value)
                    HeartRate_DataList5.append([time, average])
                for t, data in HeartRate_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > HeartRate_MonthTem:
                        HeartRate_DataList3.append([t, data])
                    if date_tem > HeartRate_YearTem:
                        HeartRate_DataList4.append([t,data])
                print(HeartRate_YearDic, HeartRate_MonthDic, HeartRate_DayDic)
                print(HeartRate_DataList3,HeartRate_DataList4,HeartRate_DataList5)
            HeartRate_DataList1 = json.dumps(HeartRate_DataList1)
            HeartRate_DataList3 = json.dumps(HeartRate_DataList3)
            HeartRate_DataList4 = json.dumps(HeartRate_DataList4)
            HeartRate_DataList5 = json.dumps(HeartRate_DataList5)
    return render(request, 'HeartRate_Record.html', locals())

def RespirationRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["Respiration"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Respiration = observation.Observation.where({'patient': NHINumber, 'code': '9279-1', '_sort': '-date'}).perform(smart.server)
    Respiration_TimeList = []
    Respiration_DataList = []
    Respiration_YearDic = {}
    Respiration_MonthDic = {}
    Respiration_DayDic = {}
    Respiration_DataList1 = []
    Respiration_DataList2 = []
    # one month
    Respiration_DataList3 = []
    # one years
    Respiration_DataList4 = []
    # all
    Respiration_DataList5 = []
    if Respiration.entry != None:
        Respiration = [ob.resource for ob in Respiration.entry]
        if len(Respiration)>0:

            for i in Respiration:
                print("Respiration Test-----------------")
                if i.effectiveDateTime != None:
                    Respiration_TimeList.append(i.effectiveDateTime.isostring)

                    Respiration_DataList.append(float(i.valueQuantity.value))

            if Respiration_TimeList != []:
                for i in range(len(Respiration_TimeList)):

                    Respiration_DataList1.append([Respiration_TimeList[i], Respiration_DataList[i]])
                    Respiration_DataList1.reverse()
                    Respiration_DataList2.append([Respiration_TimeList[i], str(Respiration_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(Respiration_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(Respiration_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(Respiration_TimeList[0], "%Y-%m-%d")
                try:
                    Respiration_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Respiration_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    Respiration_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Respiration_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(Respiration_MonthTem)

                for t, data in Respiration_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in Respiration_DayDic:
                        Respiration_DayDic[str(date_tem.date())].append(data)
                    else:
                        Respiration_DayDic[str(date_tem.date())] = [data]
                for time, value in Respiration_DayDic.items():
                    average = sum(value) / len(value)
                    Respiration_DataList5.append([time, average])
                for t, data in Respiration_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > Respiration_MonthTem:
                        Respiration_DataList3.append([t, data])
                    if date_tem > Respiration_YearTem:
                        Respiration_DataList4.append([t,data])
                print(Respiration_YearDic, Respiration_MonthDic, Respiration_DayDic)
                print(Respiration_DataList3,Respiration_DataList4,Respiration_DataList5)
            Respiration_DataList1 = json.dumps(Respiration_DataList1)
            Respiration_DataList3 = json.dumps(Respiration_DataList3)
            Respiration_DataList4 = json.dumps(Respiration_DataList4)
            Respiration_DataList5 = json.dumps(Respiration_DataList5)
    return render(request, 'Respiration_Record.html', locals())

def SmokingRecord(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    Legend_Data = ["Smoking"]
    Legend_Data = json.dumps(Legend_Data)
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Smoking = observation.Observation.where({'patient': NHINumber, 'code': '63773-6', '_sort': '-date'}).perform(smart.server)
    Smoking_TimeList = []
    Smoking_DataList = []
    Smoking_YearDic = {}
    Smoking_MonthDic = {}
    Smoking_DayDic = {}
    Smoking_DataList1 = []
    Smoking_DataList2 = []
    # one month
    Smoking_DataList3 = []
    # one years
    Smoking_DataList4 = []
    # all
    Smoking_DataList5 = []
    if Smoking.entry != None:
        Smoking = [ob.resource for ob in Smoking.entry]
        if len(Smoking)>0:

            for i in Smoking:
                print("Smoking Test-----------------")
                if i.effectiveDateTime != None:
                    Smoking_TimeList.append(i.effectiveDateTime.isostring)

                    Smoking_DataList.append(float(i.valueQuantity.value))

            if Smoking_TimeList != []:
                for i in range(len(Smoking_TimeList)):

                    Smoking_DataList1.append([Smoking_TimeList[i], Smoking_DataList[i]])
                    Smoking_DataList1.reverse()
                    Smoking_DataList2.append([Smoking_TimeList[i], str(Smoking_DataList[i])])
                try:
                    date_tem = datetime.datetime.strptime(Smoking_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(Smoking_TimeList[0], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(Smoking_TimeList[0], "%Y-%m-%d")
                try:
                    Smoking_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Smoking_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                 "%Y-%m-%d")
                try:
                    Smoking_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    Smoking_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                "%Y-%m-%d")
                print(Smoking_MonthTem)

                for t, data in Smoking_DataList1:
                    print(t,data)
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                    if str(date_tem.date()) in Smoking_DayDic:
                        Smoking_DayDic[str(date_tem.date())].append(data)
                    else:
                        Smoking_DayDic[str(date_tem.date())] = [data]
                for time, value in Smoking_DayDic.items():
                    average = sum(value) / len(value)
                    Smoking_DataList5.append([time, average])
                for t, data in Smoking_DataList5:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                    if date_tem > Smoking_MonthTem:
                        Smoking_DataList3.append([t, data])
                    if date_tem > Smoking_YearTem:
                        Smoking_DataList4.append([t,data])
                print(Smoking_YearDic, Smoking_MonthDic, Smoking_DayDic)
                print(Smoking_DataList3,Smoking_DataList4,Smoking_DataList5)
            Smoking_DataList1 = json.dumps(Smoking_DataList1)
            Smoking_DataList3 = json.dumps(Smoking_DataList3)
            Smoking_DataList4 = json.dumps(Smoking_DataList4)
            Smoking_DataList5 = json.dumps(Smoking_DataList5)
    return render(request, 'Smoking_Record.html', locals())

def ImagingHistory(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    request.session['RecordType'] = "Imaging"
    request.session['DataType'] = "Record"
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Imaging_List = []

    Imaging_DataList1 = []

    DiagnosticReport_List = diagnosticreport.DiagnosticReport.where(
        {'patient': NHINumber, '_sort': '-date'}).perform(smart.server)
    if DiagnosticReport_List.entry != None:
        DiagnosticReport_List = [c.resource for c in DiagnosticReport_List.entry]
        # MedicationRequest_List.pop(0)
        if len(DiagnosticReport_List) > 0:
            for DR in DiagnosticReport_List:
                if DR.resource_type == "DiagnosticReport":
                    if DR.category[0].coding[0].code == "LP29684-5":
                        Imaging_List.append(DR)
            for image in Imaging_List:
                Imaging_DataList_1 = []

                Name = image.code.coding[0].display
                Time = image.effectiveDateTime.isostring
                try:
                    date_tem = datetime.datetime.strptime(Time, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    date_tem = datetime.datetime.strptime(Time, "%Y-%m-%d %H:%M:%S")
                Time = date_tem.strftime("%Y-%m-%d %H:%M:%S")
                En_id = image.encounter.reference.split("/")
                En_id = En_id[-1]
                Record_ID = image.id
                # Conclusion = image.
                Imaging_DataList_1.append(Name)
                Imaging_DataList_1.append(Time)
                Imaging_DataList_1.append(En_id)
                Imaging_DataList_1.append(Record_ID)
                Imaging_DataList1.append(Imaging_DataList_1)

    if request.method == "post":
        if 'Report' in request.POST:
            request.session['DataType'] = "Report"
            render(request, 'Imaging_History.html', locals())

    return render(request, 'Imaging_History.html', locals())

def LaboratoryHistory(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    request.session['RecordType'] = "Laboratory"
    request.session['DataType'] = "Record"
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Lab_List = []

    Imaging_List = []

    Laboratory_DataList1 = []
    Value_List = []
    DiagnosticReport_List = diagnosticreport.DiagnosticReport.where(
        {'patient': NHINumber, '_include': 'DiagnosticReport:result', '_sort': '-date'}).perform(smart.server)

    if DiagnosticReport_List.entry != None:
        DiagnosticReport_List = [c.resource for c in DiagnosticReport_List.entry]
        # MedicationRequest_List.pop(0)
        if len(DiagnosticReport_List) > 0:
            for DR in DiagnosticReport_List:
                if DR.resource_type == "DiagnosticReport":
                    if DR.category[0].coding[0].code != "LP29684-5":
                        Lab_List.append(DR)
                if DR.resource_type == "Observation":
                    Value_List.append(DR)
            for lab in Lab_List:
                Lab_DataList = []
                Name = lab.code.text
                Time = lab.effectiveDateTime.isostring
                try:
                    date_tem = datetime.datetime.strptime(Time, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    date_tem = datetime.datetime.strptime(Time, "%Y-%m-%d %H:%M:%S")
                Time = date_tem.strftime("%Y-%m-%d %H:%M:%S")
                En_id = lab.encounter.reference.split("/")
                En_id = En_id[-1]
                Record_ID = lab.id
                Value_idList_1 = []
                Value_List1 = []
                for i in lab.result:
                    Ob_tem = i.reference.split("/")
                    Value_idList_1.append(Ob_tem[-1])
                for Ob in Value_List:
                    if Ob.id in Value_idList_1:
                        Value_List1.append(Ob)

                """DR_Tem_List = diagnosticreport.DiagnosticReport.where(
        {'_id': Record_ID, '_include': 'DiagnosticReport:result', '_sort': '-date'}).perform(smart.server)
                DR_Tem_List = [c.resource for c in DR_Tem_List.entry]
                for DR_Tem in DR_Tem_List:
                    if DR_Tem.resource_type == "Observation":
                        Value_List.append(DR_Tem)"""
                Critical_Sign = "-"
                for Ob in Value_List1:
                    if Ob.interpretation:
                        if Ob.interpretation[0].coding[0].code == "LL":
                            Critical_Sign = "!"
                        if Ob.interpretation[0].coding[0].code == "HH":
                            Critical_Sign = "!"
                Lab_DataList.append(Name)
                Lab_DataList.append(Time)
                Lab_DataList.append(Critical_Sign)
                Lab_DataList.append(En_id)
                Lab_DataList.append(Record_ID)
                Laboratory_DataList1.append(Lab_DataList)

    if request.method == "post":
        if 'Report' in request.POST:
            request.session['DataType'] = "Report"
            render(request, 'Imaging_History.html', locals())
    return render(request, 'Laboratory_History.html', locals())

def MedicationsHistory(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    request.session['RecordType'] = "Medications"
    request.session['DataType'] = "Record"
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    MedicationRequestTem_List = []
    Medication_List = []
    Medications_DataList = []
    MedicationTem_List = []
    Medications_DataList1 = []
    MedicationRequest_List = medicationrequest.MedicationRequest.where(
        {'patient': NHINumber, '_include': 'MedicationRequest:medication', '_sort': '-date'}).perform(smart.server)
    if MedicationRequest_List.entry != None:
        MedicationRequest_List = [c.resource for c in MedicationRequest_List.entry]
        # MedicationRequest_List.pop(0)
        if len(MedicationRequest_List) > 0:
            for MR in MedicationRequest_List:

                if MR.resource_type == "MedicationRequest":
                    MedicationRequestTem_List.append(MR)
                if MR.resource_type == "Medication":
                    Medication_List.append(MR)
            for i in range(len(MedicationRequestTem_List)):
                MedicationTem_List.append(Medication_List[i].code.coding[0].display)
                Me = MedicationRequestTem_List[i].dosageInstruction[0]
                Dose_Str = str(Me.doseAndRate[0].doseQuantity.value) + " " + str(Me.doseAndRate[0].doseQuantity.unit)
                Fre_Str = str(Me.timing.repeat.frequency) + "/" + str(Me.timing.repeat.period) + \
                          str(Me.timing.repeat.periodUnit)
                Route = Me.route.coding[0].display
                try:
                    Start = datetime.datetime.strptime(
                        MedicationRequestTem_List[i].dispenseRequest.validityPeriod.start.isostring,
                        "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        Start = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.start.isostring,
                            "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        Start = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.start.isostring, "%Y-%m-%d")
                Start = str(Start.date())
                try:
                    End = datetime.datetime.strptime(
                        MedicationRequestTem_List[i].dispenseRequest.validityPeriod.end.isostring,
                        "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        End = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.end.isostring,
                            "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        End = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.end.isostring, "%Y-%m-%d")
                End = str(End.date())
                En_id = MedicationRequestTem_List[i].encounter.reference.split("/")
                En_id = En_id[-1]
                MedicationTem_List.append(Dose_Str)
                MedicationTem_List.append(Route)
                MedicationTem_List.append(Fre_Str)
                MedicationTem_List.append(Start)
                MedicationTem_List.append(En_id)
                Medications_DataList1.append(MedicationTem_List)
                MedicationTem_List = []
    return render(request, 'Medications_History.html', locals())

def AllergiesHistory(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    request.session['RecordType'] = "Allergies"
    request.session['DataType'] = "Record"
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Allergy_List = allergyintolerance.AllergyIntolerance.where(
        {'patient': NHINumber, '_sort': '-date'}).perform(smart.server)
    if Allergy_List.entry != None:
        Allergy_List = [a.resource for a in Allergy_List.entry]
    Allergies_DataList1 = []
    if len(Allergy_List) > 0:
        for allergy in Allergy_List:
            En_id = allergy.encounter.reference.split("/")
            En_id = En_id[-1]
            tem = []
            tem.append(allergy.code.coding[0].display)
            try:
                date_tem = datetime.datetime.strptime(allergy.recordedDate.isostring, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    date_tem = datetime.datetime.strptime(allergy.recordedDate.isostring, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_tem = datetime.datetime.strptime(allergy.recordedDate.isostring, "%Y-%m-%d")

            tem.append(allergy.criticality)
            tem.append(str(date_tem.date()))
            if allergy.reaction:
                Reaction = allergy.reaction
                Str_Tem = ""

                for reaction in Reaction:
                    if reaction.manifestation:
                        for c in reaction.manifestation:
                            for d in c.coding:
                                if Str_Tem == "":
                                    Str_Tem = d.display
                                else:
                                    Str_Tem += ", " + d.disply
            tem.append(Str_Tem)
            tem.append(En_id)
            Allergies_DataList1.append(tem)
    return render(request, 'Allergies_History.html', locals())

def DiagnosisHistory(request):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    request.session['RecordType'] = "Diagnosis"
    request.session['DataType'] = "Record"
    smart = client.FHIRClient(settings=settings)
    NHINumber = request.session['NHINumber']
    Encounter_List = encounter.Encounter.where({'patient': NHINumber, '_include': ['Encounter:diagnosis', 'Encounter:participant'],
                                                '_sort': '-date'}).perform(smart.server)
    En_All_DataList = []
    En_In_DataList = []
    En_Out_DataList = []
    En_All_List = []
    Condition_TemList = []
    Practitioner_TemList = []
    print("#############DiagnosisHistory###############")
    if Encounter_List.entry != None:
        Encounter_List = [e.resource for e in Encounter_List.entry]
        if len(Encounter_List) > 0:
            for i in Encounter_List:
                if i.resource_type == "Encounter":
                    En_All_List.append(i)
                if i.resource_type == "Condition":
                    Condition_TemList.append(i)
                if i.resource_type == "Practitioner":
                    Practitioner_TemList.append(i)
            for i in En_All_List:
                Diagnosis_FirstID = []
                Condition_List = []
                print(i.id)
                En_id = i.id
                Practitioner_id = i.participant[0].individual.reference.split("/")
                Practitioner_id = Practitioner_id[-1]
                for p in Practitioner_TemList:
                    if p.id == Practitioner_id:
                        Practitioner = smart.human_name(p.name[0])
                for o in i.diagnosis:
                    print(o.rank)
                    if o.rank == 1:
                        Condition_ID = o.condition.reference.split("/")
                        Diagnosis_FirstID = Condition_ID[-1]
                for c in Condition_TemList:
                    Encounter_Tem = c.encounter.reference.split("/")
                    Encounter_Tem = Encounter_Tem[-1]
                    if Encounter_Tem == En_id:
                        Condition_List.append(c)

                if Condition_List != None:
                    if len(Condition_List) > 0:
                        tem = []
                        for c in Condition_List:
                            if c.id == Diagnosis_FirstID:
                                tem_str = ""
                                for disease in c.code.coding:
                                    if tem_str == "":
                                        tem_str += disease.display
                                    else:
                                        tem_str += "; " + disease.display
                                T_Start = i.period.start.isostring

                                try:
                                    T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%dT%H:%M:%S%z").strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    try:
                                        T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%d %H:%M:%S").strftime(
                                            "%Y-%m-%d %H:%M:%S")
                                    except ValueError:
                                        T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%d").strftime("%Y-%m-%d")
                                tem.append(tem_str)
                                break
                        tem_str = ""
                        Comorbidities = []
                        for c in Condition_List:
                            if c.id != Diagnosis_FirstID:
                                for disease in c.code.coding:
                                    Comorbidities.append(disease.display)
                        tem.append(Comorbidities)
                        tem.append(T_Start)
                        tem.append(Practitioner)
                        tem.append(En_id)
                        En_All_DataList.append(tem)
    return render(request, 'Diagnosis_History.html', locals())

def Visit(request, En_id):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    RecordType = request.session['RecordType']
    DataType = request.session['DataType']
    NHINumber = request.session['NHINumber']
    request.session['Encounter'] = En_id
    smart = client.FHIRClient(settings=settings)
    Legend_Data = ["Temperature", "Pulse", "Respiration", "Systolic Blood Pressure", "Diastolic Blood Pressure"]
    Encounter_Tem = encounter.Encounter.read(En_id, smart.server)
        ##encounter.Encounter.where({'patient': NHINumber, '_sort': '-date'}).perform(smart.server)
    En_All_DataList = []
    if Encounter_Tem:
        Diagnosis_FirstID = []
        Organization_ID = Encounter_Tem.serviceProvider.reference.split("/")
        Organization_ID = Organization_ID[-1]
        Organization_List = organization.Organization.where({'_id': Organization_ID}).perform(smart.server)
        if Organization_List.entry != None:
            Organization_List = [c.resource for c in Organization_List.entry]
            if len(Organization_List) > 0:
                Organization_Tem = Organization_List[0]
                Organization_BelongTo_ID = Organization_Tem.partOf.reference.split("/")
                if Organization_Tem:
                    Organization_Tem = Organization_Tem.name
        else:
            Organization_Tem = None
        """    
        try:
            Organization_Tem = organization.Organization.read(Organization_ID, smart.server)
        except FHIRNotFoundException:
            Organization_Tem = None"""


        Organization_BelongTo_ID = Organization_BelongTo_ID[-1]
        """try:
            Organization_BelongTo_Tem = organization.Organization.read(Organization_BelongTo_ID, smart.server)
        except FHIRNotFoundException:
            Organization_BelongTo_Tem = None"""
        Organization_List = organization.Organization.where({'_id': Organization_BelongTo_ID}).perform(
            smart.server)
        if Organization_List.entry != None:
            Organization_List = [c.resource for c in Organization_List.entry]
            if len(Organization_List) > 0:
                Organization_BelongTo_Tem = Organization_List[0]
                if Organization_BelongTo_Tem:
                    Organization_BelongTo_Tem = Organization_BelongTo_Tem.name
        else:
            Organization_BelongTo_Tem = None
        for o in Encounter_Tem.diagnosis:
            if o.rank == 1:
                Condition_ID = o.condition.reference.split("/")
                Diagnosis_FirstID = Condition_ID[-1]
        Condition_List = condition.Condition.where({'encounter': Encounter_Tem.id}).perform(smart.server)
        if Condition_List.entry != None:
            Condition_List = [c.resource for c in Condition_List.entry]
            if len(Condition_List) > 0:
                for c in Condition_List:
                    if c.id == Diagnosis_FirstID:
                        tem_str = ""
                        for disease in c.code.coding:
                            if tem_str == "":
                                tem_str += disease.display
                            else:
                                tem_str += "; " + disease.display

                        T_Start = Encounter_Tem.period.start.isostring
                        try:
                            T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                T_Start = datetime.datetime.strptime(T_Start, "%Y-%m-%d").strftime("%Y-%m-%d")
                        T_End = Encounter_Tem.period.end.isostring
                        try:
                            T_End = datetime.datetime.strptime(T_End, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                T_End = datetime.datetime.strptime(T_End, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                T_End = datetime.datetime.strptime(T_End, "%Y-%m-%d").strftime("%Y-%m-%d")
                        if Encounter_Tem.class_fhir.code == "AMB":
                            tem = [T_Start, T_End]
                            if Organization_BelongTo_Tem:
                                tem.append(Organization_BelongTo_Tem)
                            else:
                                tem.append("None")
                            if Organization_Tem:
                                tem.append(Organization_Tem)
                            else:
                                tem.append("None")
                            reason_Str = ""
                            for reason in Encounter_Tem.reasonCode:
                                if reason_Str == "":
                                    reason_Str = reason.text
                                else:
                                    reason_Str += reason.text
                            tem.append(reason_Str)
                            tem.append(tem_str)
                        if Encounter_Tem.class_fhir.code == "IMP" or Encounter_Tem.class_fhir.code == "ACUTE" or Encounter_Tem.class_fhir.code == "NONAC":
                            tem = [T_Start, T_End]
                            if Organization_BelongTo_Tem:
                                tem.append(Organization_BelongTo_Tem)
                            else:
                                tem.append("None")
                            if Organization_Tem:
                                tem.append(Organization_Tem)
                            else:
                                tem.append("None")
                            reason_Str = ""
                            for reason in Encounter_Tem.reasonCode:
                                if reason_Str == "":
                                    reason_Str = reason.text
                                else:
                                    reason_Str += reason.text
                            tem.append(reason_Str)
                            tem.append(tem_str)
                        break
                tem_str = ""
                for c in Condition_List:
                    if c.id != Diagnosis_FirstID:
                        for disease in c.code.coding:
                            if tem_str == "":
                                tem_str += disease.display
                            else:
                                tem_str += "; " + disease.display
                tem.append(tem_str)
                En_All_DataList.append(tem)
    # ###############################Vital Signs
    HeartRate = []
    Temperature = []
    BloodPressure = []
    Respiration = []

    Sign_Tem = []
    FileCode = "1"
    VitalSigns_DataList1 = []
    VitalSign_List = encounter.Encounter.where(
        {'_id': En_id, '_revinclude': 'Observation:encounter', '_sort': '-date'}).perform(smart.server)
    if VitalSign_List.entry != None:
        VitalSign_List = [c.resource for c in VitalSign_List.entry]
        VitalSign_List.pop(0)

        if len(VitalSign_List) > 0:
            for VitalSign in VitalSign_List:
                for c in VitalSign.code.coding:
                    #Heart Rate
                    if c.code == '8867-4':
                        HeartRate.append(VitalSign)
                    #Temperature
                    if c.code == '8310-5':
                        Temperature.append(VitalSign)
                    #Blood Pressure
                    if c.code == '85354-9':
                        BloodPressure.append(VitalSign)
                    #Respiration
                    if c.code == '9279-1':
                        Respiration.append(VitalSign)
    else:
        VitalSign_List = None

    HeartRate_TimeList = []
    HeartRate_DataList = []
    HeartRate_YearDic = {}
    HeartRate_MonthDic = {}
    HeartRate_DayDic = {}
    HeartRate_DataList1 = []
    HeartRate_DataList2 = []
    # one month
    HeartRate_DataList3 = []
    # one years
    HeartRate_DataList4 = []
    # all
    HeartRate_DataList5 = []

    if len(HeartRate) > 0:

        for i in HeartRate:
            print("HeartRate Test-----------------")
            if i.effectiveDateTime != None:
                HeartRate_TimeList.append(i.effectiveDateTime.isostring)

                HeartRate_DataList.append(float(i.valueQuantity.value))

        if HeartRate_TimeList != []:
            for i in range(len(HeartRate_TimeList)):
                HeartRate_DataList1.append([HeartRate_TimeList[i], HeartRate_DataList[i]])
                HeartRate_DataList1.reverse()
                HeartRate_DataList2.append([HeartRate_TimeList[i], str(HeartRate_DataList[i])])
            try:
                date_tem = datetime.datetime.strptime(HeartRate_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    date_tem = datetime.datetime.strptime(HeartRate_TimeList[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_tem = datetime.datetime.strptime(HeartRate_TimeList[0], "%Y-%m-%d")
            try:
                HeartRate_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                "%Y-%m-%d %H:%M:%S")
            except ValueError:
                HeartRate_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                "%Y-%m-%d")
            try:
                HeartRate_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                               "%Y-%m-%d %H:%M:%S")
            except ValueError:
                HeartRate_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                               "%Y-%m-%d")
            print(HeartRate_MonthTem)

            for t, data in HeartRate_DataList1:
                print(t, data)
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                if str(date_tem.date()) in HeartRate_DayDic:
                    HeartRate_DayDic[str(date_tem.date())].append(data)
                else:
                    HeartRate_DayDic[str(date_tem.date())] = [data]
            for time, value in HeartRate_DayDic.items():
                average = sum(value) / len(value)
                HeartRate_DataList5.append([time, average])
            for t, data in HeartRate_DataList5:
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if date_tem > HeartRate_MonthTem:
                    HeartRate_DataList3.append([t, data])
                if date_tem > HeartRate_YearTem:
                    HeartRate_DataList4.append([t, data])
            print(HeartRate_YearDic, HeartRate_MonthDic, HeartRate_DayDic)
            print(HeartRate_DataList3, HeartRate_DataList4, HeartRate_DataList5)
        HeartRate_DataList1 = json.dumps(HeartRate_DataList1)
        HeartRate_DataList3 = json.dumps(HeartRate_DataList3)
        HeartRate_DataList4 = json.dumps(HeartRate_DataList4)
        #HeartRate_DataList5 = json.dumps(HeartRate_DataList5)

    Temperature_TimeList = []
    Temperature_DataList = []
    Temperature_YearDic = {}
    Temperature_MonthDic = {}
    Temperature_DayDic = {}
    Temperature_DataList1 = []
    Temperature_DataList2 = []
    # one month
    Temperature_DataList3 = []
    # one years
    Temperature_DataList4 = []
    # all
    Temperature_DataList5 = []

    if len(Temperature) > 0:

        for i in Temperature:
            print("Temperature Test-----------------")
            if i.effectiveDateTime != None:
                Temperature_TimeList.append(i.effectiveDateTime.isostring)

                Temperature_DataList.append(float(i.valueQuantity.value))

        if Temperature_TimeList != []:
            for i in range(len(Temperature_TimeList)):
                Temperature_DataList1.append([Temperature_TimeList[i], Temperature_DataList[i]])
                Temperature_DataList1.reverse()
                Temperature_DataList2.append([Temperature_TimeList[i], str(Temperature_DataList[i])])
            try:
                date_tem = datetime.datetime.strptime(Temperature_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    date_tem = datetime.datetime.strptime(Temperature_TimeList[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_tem = datetime.datetime.strptime(Temperature_TimeList[0], "%Y-%m-%d")
            try:
                Temperature_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                  "%Y-%m-%d %H:%M:%S")
            except ValueError:
                Temperature_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                  "%Y-%m-%d")
            try:
                Temperature_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                 "%Y-%m-%d %H:%M:%S")
            except ValueError:
                Temperature_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                 "%Y-%m-%d")
            print(Temperature_MonthTem)

            for t, data in Temperature_DataList1:
                print(t, data)
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                if str(date_tem.date()) in Temperature_DayDic:
                    Temperature_DayDic[str(date_tem.date())].append(data)
                else:
                    Temperature_DayDic[str(date_tem.date())] = [data]
            for time, value in Temperature_DayDic.items():
                average = sum(value) / len(value)
                Temperature_DataList5.append([time, average])
            for t, data in Temperature_DataList5:
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if date_tem > Temperature_MonthTem:
                    Temperature_DataList3.append([t, data])
                if date_tem > Temperature_YearTem:
                    Temperature_DataList4.append([t, data])
            print(Temperature_YearDic, Temperature_MonthDic, Temperature_DayDic)
            print(Temperature_DataList3, Temperature_DataList4, Temperature_DataList5)
        Temperature_DataList1 = json.dumps(Temperature_DataList1)
        Temperature_DataList3 = json.dumps(Temperature_DataList3)
        Temperature_DataList4 = json.dumps(Temperature_DataList4)
        #Temperature_DataList5 = json.dumps(Temperature_DataList5)
    BloodPressure_TimeList = []
    # lower
    DiastolicBloodPressure_DataList = []
    DiastolicBloodPressure_YearDic = {}
    DiastolicBloodPressure_MonthDic = {}
    DiastolicBloodPressure_DayDic = {}
    # higher
    SystolicBloodPressure_DataList = []
    SystolicBloodPressure_YearDic = {}
    SystolicBloodPressure_MonthDic = {}
    SystolicBloodPressure_DayDic = {}
    SystolicBloodPressure_DataList1 = []
    # SystolicBloodPressure_DataList2 = []
    DiastolicBloodPressure_DataList1 = []
    # DiastolicBloodPressure_DataList2 = []
    BloodPressure_DataList2 = []
    BloodPressure_DataList3 = []


    # one month
    SystolicBloodPressure_DataList3 = []
    # one years
    SystolicBloodPressure_DataList4 = []
    # all
    SystolicBloodPressure_DataList5 = []
    # one month
    DiastolicBloodPressure_DataList3 = []
    # one years
    DiastolicBloodPressure_DataList4 = []
    # all
    DiastolicBloodPressure_DataList5 = []

    if len(BloodPressure) > 0:

        for i in BloodPressure:
            print("BloodPressure Test-----------------")
            if i.effectiveDateTime != None:
                BloodPressure_TimeList.append(i.effectiveDateTime.isostring)
                for o in i.component:
                    code_List = o.code.coding
                    for code in code_List:
                        if code.code == "8480-6" or code.code == "271649006" or code.code == "bp-s":
                            SystolicBloodPressure_DataList.append(float(o.valueQuantity.value))
                            print("8480-6")
                        if code.code == "8462-4":
                            DiastolicBloodPressure_DataList.append(float(o.valueQuantity.value))
                            print("8462-4")
                    print(o.valueQuantity.value)

        if BloodPressure_TimeList != []:
            for i in range(len(BloodPressure_TimeList)):
                print(BloodPressure_TimeList)
                print(SystolicBloodPressure_DataList)
                SystolicBloodPressure_DataList1.append(
                    [BloodPressure_TimeList[i], SystolicBloodPressure_DataList[i]])
                SystolicBloodPressure_DataList1.reverse()

                DiastolicBloodPressure_DataList1.append(
                    [BloodPressure_TimeList[i], DiastolicBloodPressure_DataList[i]])
                DiastolicBloodPressure_DataList1.reverse()

                BloodPressure_DataList2.append([BloodPressure_TimeList[i], str(SystolicBloodPressure_DataList[i]),
                                                str(DiastolicBloodPressure_DataList[i])])

            try:
                date_tem = datetime.datetime.strptime(BloodPressure_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    date_tem = datetime.datetime.strptime(BloodPressure_TimeList[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_tem = datetime.datetime.strptime(BloodPressure_TimeList[0], "%Y-%m-%d")
            try:
                BloodPressure_MonthTem = datetime.datetime.strptime(
                    str((date_tem.date() - relativedelta(months=1))), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                BloodPressure_MonthTem = datetime.datetime.strptime(
                    str((date_tem.date() - relativedelta(months=1))),
                    "%Y-%m-%d")
            try:
                BloodPressure_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                   "%Y-%m-%d %H:%M:%S")
            except ValueError:
                BloodPressure_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                   "%Y-%m-%d")
            print(BloodPressure_MonthTem)

            for t, data in SystolicBloodPressure_DataList1:
                print(t, data)
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if str(date_tem.date()) in SystolicBloodPressure_DayDic:
                    SystolicBloodPressure_DayDic[str(date_tem.date())].append(data)
                else:
                    SystolicBloodPressure_DayDic[str(date_tem.date())] = [data]
            for time, value in SystolicBloodPressure_DayDic.items():
                average = sum(value) / len(value)
                SystolicBloodPressure_DataList5.append([time, average])
            for t, data in SystolicBloodPressure_DataList5:
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if date_tem > BloodPressure_MonthTem:
                    SystolicBloodPressure_DataList3.append([t, data])
                if date_tem > BloodPressure_YearTem:
                    SystolicBloodPressure_DataList4.append([t, data])

            for t, data in DiastolicBloodPressure_DataList1:
                print(t, data)
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if str(date_tem.date()) in DiastolicBloodPressure_DayDic:
                    DiastolicBloodPressure_DayDic[str(date_tem.date())].append(data)
                else:
                    DiastolicBloodPressure_DayDic[str(date_tem.date())] = [data]
            for time, value in DiastolicBloodPressure_DayDic.items():
                average = sum(value) / len(value)
                DiastolicBloodPressure_DataList5.append([time, average])
            for t, data in DiastolicBloodPressure_DataList5:
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if date_tem > BloodPressure_MonthTem:
                    DiastolicBloodPressure_DataList3.append([t, data])
                if date_tem > BloodPressure_YearTem:
                    DiastolicBloodPressure_DataList4.append([t, data])
            # print(BloodPressure_YearDic, BloodPressure_MonthDic, BloodPressure_DayDic)
            # print(BloodPressure_DataList3,BloodPressure_DataList4,BloodPressure_DataList5)

            # BloodPressure_DataList1 = json.dumps(BloodPressure_DataList1)

        for i in range(len(SystolicBloodPressure_DataList5)):

            tem = []
            tem.append(SystolicBloodPressure_DataList5[i][0])
            tem.append(SystolicBloodPressure_DataList5[i][1])
            tem.append(DiastolicBloodPressure_DataList5[i][1])
            BloodPressure_DataList3.append(tem)
        SystolicBloodPressure_DataList3 = json.dumps(SystolicBloodPressure_DataList3)
        SystolicBloodPressure_DataList4 = json.dumps(SystolicBloodPressure_DataList4)
        SystolicBloodPressure_DataList5 = json.dumps(SystolicBloodPressure_DataList5)

        DiastolicBloodPressure_DataList3 = json.dumps(DiastolicBloodPressure_DataList3)
        DiastolicBloodPressure_DataList4 = json.dumps(DiastolicBloodPressure_DataList4)
        DiastolicBloodPressure_DataList5 = json.dumps(DiastolicBloodPressure_DataList5)
    Respiration_TimeList = []
    Respiration_DataList = []
    Respiration_YearDic = {}
    Respiration_MonthDic = {}
    Respiration_DayDic = {}
    Respiration_DataList1 = []
    Respiration_DataList2 = []
    # one month
    Respiration_DataList3 = []
    # one years
    Respiration_DataList4 = []
    # all
    Respiration_DataList5 = []

    if len(Respiration) > 0:

        for i in Respiration:
            print("Respiration Test-----------------")
            if i.effectiveDateTime != None:
                Respiration_TimeList.append(i.effectiveDateTime.isostring)

                Respiration_DataList.append(float(i.valueQuantity.value))

        if Respiration_TimeList != []:
            for i in range(len(Respiration_TimeList)):
                Respiration_DataList1.append([Respiration_TimeList[i], Respiration_DataList[i]])
                Respiration_DataList1.reverse()
                Respiration_DataList2.append([Respiration_TimeList[i], str(Respiration_DataList[i])])
            try:
                date_tem = datetime.datetime.strptime(Respiration_TimeList[0], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    date_tem = datetime.datetime.strptime(Respiration_TimeList[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_tem = datetime.datetime.strptime(Respiration_TimeList[0], "%Y-%m-%d")
            try:
                Respiration_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                  "%Y-%m-%d %H:%M:%S")
            except ValueError:
                Respiration_MonthTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(months=1))),
                                                                  "%Y-%m-%d")
            try:
                Respiration_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                 "%Y-%m-%d %H:%M:%S")
            except ValueError:
                Respiration_YearTem = datetime.datetime.strptime(str((date_tem.date() - relativedelta(years=1))),
                                                                 "%Y-%m-%d")
            print(Respiration_MonthTem)

            for t, data in Respiration_DataList1:
                print(t, data)
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")

                if str(date_tem.date()) in Respiration_DayDic:
                    Respiration_DayDic[str(date_tem.date())].append(data)
                else:
                    Respiration_DayDic[str(date_tem.date())] = [data]
            for time, value in Respiration_DayDic.items():
                average = sum(value) / len(value)
                Respiration_DataList5.append([time, average])
            for t, data in Respiration_DataList5:
                try:
                    date_tem = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        date_tem = datetime.datetime.strptime(t, "%Y-%m-%d")
                if date_tem > Respiration_MonthTem:
                    Respiration_DataList3.append([t, data])
                if date_tem > Respiration_YearTem:
                    Respiration_DataList4.append([t, data])
            print(Respiration_YearDic, Respiration_MonthDic, Respiration_DayDic)
            print(Respiration_DataList3, Respiration_DataList4, Respiration_DataList5)
        Respiration_DataList1 = json.dumps(Respiration_DataList1)
        Respiration_DataList3 = json.dumps(Respiration_DataList3)
        Respiration_DataList4 = json.dumps(Respiration_DataList4)
        #Respiration_DataList5 = json.dumps(Respiration_DataList5)

    print(Temperature_DataList5)
    print(HeartRate_DataList5)
    print(Respiration_DataList5)
    print(BloodPressure_DataList3)
    t_Tem = []
    t_TemperatureTem = []
    t_HeartRateTem = []
    t_RespirationTem = []
    t_BloodPressureTem = []
    if len(Temperature_DataList5) > 0:
        for t, data in Temperature_DataList5:
            t_Tem.append(t)
            t_TemperatureTem.append(t)
        for t, data in HeartRate_DataList5:
            if t not in t_Tem:
                t_Tem.append(t)
            t_HeartRateTem.append(t)
        for t, data in Respiration_DataList5:
            if t not in t_Tem:
                t_Tem.append(t)
            t_RespirationTem.append(t)
        for t, data1, data2 in BloodPressure_DataList3:
            if t not in t_Tem:
                t_Tem.append(t)
            t_BloodPressureTem.append(t)


    t_Tem = sorted(t_Tem, key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), reverse=True)
    for t in t_Tem:
        for t_1, data_1 in Temperature_DataList5:
            if t in t_TemperatureTem:
                if t_1 == t:
                    Sign_Tem.append(t)
                    Sign_Tem.append(data_1)
            else:
                break
        for t_2, data_2 in HeartRate_DataList5:
            if t in t_HeartRateTem:
                if t_2 == t:
                    Sign_Tem.append(data_2)
            else:
                break
        for t_3, data_3 in Respiration_DataList5:
            if t in t_RespirationTem:
                if t_3 == t:
                    Sign_Tem.append(data_3)
            else:
                break
        for t_4, data_4, data_5 in BloodPressure_DataList3:
            if t in t_BloodPressureTem:
                if t_4 == t:
                    tem = str(data_4) + "/" + str(data_5)
                    Sign_Tem.append(tem)
            else:
                break

        print(Sign_Tem)
        VitalSigns_DataList1.append(Sign_Tem)
        Sign_Tem = []
    Temperature_DataList5 = json.dumps(Temperature_DataList5)
    HeartRate_DataList5 = json.dumps(HeartRate_DataList5)
    Respiration_DataList5 = json.dumps(Respiration_DataList5)
    print("###############vital signs##############")
    print(VitalSigns_DataList1)
    PulseRate_Data1 = HeartRate_DataList3
    PulseRate_Data2 = HeartRate_DataList4
    PulseRate_Data3 = HeartRate_DataList5
    BloodPressureUp_Data1 = SystolicBloodPressure_DataList3
    BloodPressureUp_Data2 = SystolicBloodPressure_DataList4
    BloodPressureUp_Data3 = SystolicBloodPressure_DataList5
    BloodPressureDown_Data1 = DiastolicBloodPressure_DataList3
    BloodPressureDown_Data2 = DiastolicBloodPressure_DataList4
    BloodPressureDown_Data3 = DiastolicBloodPressure_DataList5
    Respiration_Data1 = Respiration_DataList3
    Respiration_Data2 = Respiration_DataList4
    Respiration_Data3 = Respiration_DataList5
    Temperature_Data1 = Temperature_DataList3
    Temperature_Data2 = Temperature_DataList4
    Temperature_Data3 = Temperature_DataList5
    #################################Allergy######################################
    #不能使用encounter的id进行搜索allergyintorlerance资源
    Allergy_List = allergyintolerance.AllergyIntolerance.where(
        {'patient': NHINumber, '_sort': '-date'}).perform(smart.server)
    if Allergy_List.entry != None:
        Allergy_List = [a.resource for a in Allergy_List.entry]
    Allergy_List_1 = []
    Allergies_DataList1 = []
    print("#####################Allergy##################")
    if len(Allergy_List) > 0:
        for allergy in Allergy_List:
            tem = allergy.encounter.reference.split("/")
            tem = tem[-1]
            if tem == En_id:
                Allergy_List_1.append(allergy)
        for allergy in Allergy_List_1:
            tem = []

            print(allergy.id)
            print(allergy.code.coding)
            tem.append(allergy.code.coding[0].display)
            try:
                date_tem = datetime.datetime.strptime(allergy.recordedDate.isostring, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    date_tem = datetime.datetime.strptime(allergy.recordedDate.isostring, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_tem = datetime.datetime.strptime(allergy.recordedDate.isostring, "%Y-%m-%d")
            tem.append(str(date_tem.date()))
            tem.append(allergy.criticality)
            if allergy.reaction:
                Reaction = allergy.reaction
                Str_Tem = ""

                for reaction in Reaction:
                    if reaction.manifestation:
                        for c in reaction.manifestation:
                            for d in c.coding:
                                if Str_Tem == "":
                                    Str_Tem = d.display
                                else:
                                    Str_Tem += ", " + d.disply
            tem.append(Str_Tem)
            Str_Tem = ""
            if allergy.note:
                for n in allergy.note:
                    if Str_Tem == "":
                        Str_Tem = n.text
                    else:
                        Str_Tem += " " + n.text
                tem.append(Str_Tem)
            else:
                tem.append("None")
            Allergies_DataList1.append(tem)
    #################################Medication###################################
    MedicationRequestTem_List = []
    Medication_List = []
    Medications_DataList = []
    MedicationTem_List = []
    Medications_DataList1 = []
    MedicationRequest_List = medicationrequest.MedicationRequest.where(
        {'encounter': En_id, '_include': 'MedicationRequest:medication', '_sort': '-date'}).perform(smart.server)
    if MedicationRequest_List.entry != None:
        MedicationRequest_List = [c.resource for c in MedicationRequest_List.entry]
        #MedicationRequest_List.pop(0)
        if len(MedicationRequest_List) > 0:
            for MR in MedicationRequest_List:

                if MR.resource_type == "MedicationRequest":
                    MedicationRequestTem_List.append(MR)
                if MR.resource_type == "Medication":
                    Medication_List.append(MR)
            for i in range(len(MedicationRequestTem_List)):
                MedicationTem_List.append(Medication_List[i].code.coding[0].display)
                Me = MedicationRequestTem_List[i].dosageInstruction[0]
                Dose_Str = str(Me.doseAndRate[0].doseQuantity.value) + " " + str(Me.doseAndRate[0].doseQuantity.unit)
                Fre_Str = str(Me.timing.repeat.frequency) + "/" + str(Me.timing.repeat.period)  + \
                          str(Me.timing.repeat.periodUnit)
                Route = Me.route.coding[0].display
                try:
                    Start = datetime.datetime.strptime(
                        MedicationRequestTem_List[i].dispenseRequest.validityPeriod.start.isostring,
                        "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        Start = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.start.isostring,
                            "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        Start = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.start.isostring, "%Y-%m-%d")
                Start = str(Start.date())
                try:
                    End = datetime.datetime.strptime(
                        MedicationRequestTem_List[i].dispenseRequest.validityPeriod.end.isostring,
                        "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        End = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.end.isostring,
                            "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        End = datetime.datetime.strptime(
                            MedicationRequestTem_List[i].dispenseRequest.validityPeriod.end.isostring, "%Y-%m-%d")
                End = str(End.date())
                MedicationTem_List.append(Dose_Str)
                MedicationTem_List.append(Route)
                MedicationTem_List.append(Fre_Str)
                MedicationTem_List.append(Start)
                MedicationTem_List.append(End)
                Medications_DataList1.append(MedicationTem_List)
                MedicationTem_List = []
    #################################Lab###################################
    Lab_List = []
    Value_List = []
    Imaging_List = []
    Critical_List = []
    Laboratory_DataList2 = []
    Imaging_DataList1 = []
    Imaging_DataList2 = []
    DiagnosticReport_List = diagnosticreport.DiagnosticReport.where(
        {'encounter:Encounter': En_id, '_include': 'DiagnosticReport:result', '_sort': '-date'}).perform(smart.server)
    if DiagnosticReport_List.entry != None:
        DiagnosticReport_List = [c.resource for c in DiagnosticReport_List.entry]
        #MedicationRequest_List.pop(0)
        if len(DiagnosticReport_List) > 0:
            for DR in DiagnosticReport_List:
                if DR.resource_type == "DiagnosticReport":
                    if DR.category[0].coding[0].code == "LP29684-5":
                        Imaging_List.append(DR)
                    else:
                        Lab_List.append(DR)
                if DR.resource_type == "Observation":
                    Value_List.append(DR)
            print("######################CriticalValue################")
            print(len(Value_List))
            for Ob in Value_List:
                if Ob.interpretation:
                    tem = []
                    Critical_ID = ""
                    print(Ob.id)
                    if Ob.interpretation[0].coding[0].code == "LL":
                        print("LL")
                        #可能需要修改
                        Item = Ob.code.text
                        Result = str(Ob.valueQuantity.value) + " " + Ob.valueQuantity.unit
                        Abnormal = "↓"
                        Range = str(Ob.referenceRange[0].low.value) + "-" + str(Ob.referenceRange[0].high.value) + \
                                " " + str(Ob.referenceRange[0].high.unit)
                        Critical_ID = Ob.id
                        tem.append(Item)
                        tem.append(Result)
                        tem.append(Abnormal)
                        tem.append(Range)
                    if Ob.interpretation[0].coding[0].code == "HH":
                        print("HH")
                        Item = Ob.code.text
                        Result = str(Ob.valueQuantity.value) + " " + Ob.valueQuantity.unit
                        Abnormal = "↑"
                        Range = str(Ob.referenceRange[0].low.value) + "-" + str(Ob.referenceRange[0].high.value) + \
                                " " + str(Ob.referenceRange[0].high.unit)
                        Critical_ID = Ob.id
                        tem.append(Item)
                        tem.append(Result)
                        tem.append(Abnormal)
                        tem.append(Range)
                    for lab in Lab_List:
                        Report_List = [r.reference.split('/')[-1] for r in lab.result]
                        print(Report_List)
                        if Critical_ID in Report_List:
                            Link = lab.id
                            tem.append(Link)
                            Critical_List.append(tem)
            Laboratory_DataList1 = Critical_List
            for lab in Lab_List:
                Lab_DataList = []
                Name = lab.code.text
                Lab_DataList.append(Name)
                Lab_DataList.append(lab.id)
                Laboratory_DataList2.append(Lab_DataList)
            for image in Imaging_List:
                Imaging_DataList_1 = []
                Imaging_DataList_2 = []
                Conclusion = "None"
                Name = image.code.coding[0].display
                #Conclusion = image.
                Imaging_DataList_1.append(Conclusion)
                Imaging_DataList_1.append(Name)
                Imaging_DataList_1.append(image.id)
                Imaging_DataList1.append(Imaging_DataList_1)
                Imaging_DataList_2.append(Name)
                Imaging_DataList_2.append(image.id)
                Imaging_DataList2.append(Imaging_DataList_2)


    return render(request, 'Visit.html', locals())

def ImagingFile(request, FileCode):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    RecordType = "Imaging"
    DataType = request.session['DataType']
    NHINumber = request.session['NHINumber']
    Encounter = request.session['Encounter']
    smart = client.FHIRClient(settings=settings)
    Lab = diagnosticreport.DiagnosticReport.where({'_id': FileCode, '_include': 'DiagnosticReport:media',
                                                   '_sort': '-date'}).perform(smart.server)
    request.session['RecordType'] = "Imaging"

    PDF_List = []
    Imaging_List = []
    PDF_DataList = ""
    Imaging_DataList = []
    Lab = [lab.resource for lab in Lab.entry]
    for i in Lab:
        if i.resource_type == "DiagnosticReport":
            PDF_List.append(i)
        elif i.resource_type == "Media":
            Imaging_List.append(i)
    PDF_DataList = PDF_List[0].presentedForm[0].data

    for i in Imaging_List:
        Imaging_DataList.append(i.content.data)
    return render(request, 'ImagingFile.html', locals())

def LaboratoryFile(request, FileCode):
    if not request.session.get('is_login', None):
        return redirect('/PHR/login/')
    settings = {
        'app_id': 'my_web_app',
        'api_base': 'https://server.fire.ly',
    }
    RecordType = "Laboratory"
    DataType = request.session['DataType']
    NHINumber = request.session['NHINumber']
    Encounter = request.session['Encounter']
    smart = client.FHIRClient(settings=settings)
    Lab = diagnosticreport.DiagnosticReport.where({'_id': FileCode,
                                                   '_sort': '-date'}).perform(smart.server)
    request.session['RecordType'] = "Laboratory"

    PDF_DataList = ""
    Lab = [lab.resource for lab in Lab.entry]
    Code = Lab[0].code.coding[0].code
    PDF_DataList = Lab[0].presentedForm[0].data
    Lab = diagnosticreport.DiagnosticReport.where({'_id': FileCode, '_include': 'DiagnosticReport:result',
                                                   '_sort': '-date'}).perform(smart.server)
    Lab = [lab.resource for lab in Lab.entry]
    Laboratory_List = []
    for i in Lab:
        if i.resource_type == "Observation":
            Laboratory_List.append(i)
    Observation_Data = defaultdict(list)
    for i in Laboratory_List:
        Item_Name = i.code.text
        Time = i.effectiveDateTime.isostring
        try:
            date_tem = datetime.datetime.strptime(Time, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            date_tem = datetime.datetime.strptime(Time, "%Y-%m-%d %H:%M:%S")
        Time = date_tem.strftime("%Y-%m-%d %H:%M:%S")
        #Time = datetime.datetime.strptime(Time, "%Y-%m-%d %H:%M:%S")
        Value = i.valueQuantity.value
        Unit = i.valueQuantity.unit
        Keys = Item_Name + "(" + Unit + ")"
        Observation_Data[Keys].append([Time, Value])
    Legend_Data = list(Observation_Data.keys())
    Observation_Data = json.dumps(Observation_Data)
    """Lab = diagnosticreport.DiagnosticReport.where({'patient': '12892'}).perform(smart.server)
    Imaging_DataList1 = []
    Imaging_DataList2 = []
    Lab_TimeList = []
    Binary_List1 = []
    Lab_Item = []
    Lab = [lab.resource for lab in Lab.entry]
    for i in Lab:
        if i.presentedForm and i.issued:
            Lab_TimeList.append(i.issued)
            Lab_Item.append(i.code.text)
            for o in i.presentedForm:
                Binary_List1.append(o.url)
    Binary_List = []
    for i in range(len(Binary_List1)):
        Binary_ID = Binary_List1[i].split('/')[-1]
        Binary = binary.Binary.read(Binary_ID, smart.server)
        data = Binary.data
        Binary_List.append(data)
    Lab_DataList = []
    for i in range(len(Lab_TimeList)):
        Lab_DataList.append([Lab_Item[i], Lab_TimeList[i], Binary_List[i]])"""

    return render(request, 'LaboratoryFile.html', locals())