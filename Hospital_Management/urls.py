"""
URL configuration for Hospital_Management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from Home.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',homefn, name='home'),
    path('about/',aboutfn, name='about'),
    path('contact/',contactfn, name='contact'),
    path('doctorlist/',doctorlistfn, name='doctorlist'),
    path('viewspl/<int:s_id>/',viewsplfn),
    path('index/',indexfn, name='index'),

    path('doctor_signup/',doctor_signupfn, name='doctor_signup'),
    path('patient_signup/',patient_signupfn, name='patient_signup'),
    path('login/',loginfn, name='login'),
    path('logout/',logoutfn, name='logout'),
    path('dashboard-redirect/', dashboard_redirectfn, name='dashboard-redirect'),

    
    path('admindashboard/',admin_dashboardfn, name='admin_dashboard'),
    path('doctordashboard/',doctor_dashboardfn, name='doctor_dashboard'),
    path('patientdashboard/',patient_dashboardfn, name='patient_dashboard'),
    

    path('adminadddoctor/',admin_add_doctorfn, name='admin_add_doctor'),
    path('adminviewdoctor/',admin_view_doctorfn, name='admin_view_doctor'),
    path('approve_doctor/<int:pk>/',approve_doctorfn, name='approve_doctor'),
    path('admineditdoctor/<int:u_id>/',admin_edit_doctorfn, name='admin_edit_doctor'),
    path('admindeletedoctor/<int:u_id>/',admin_delete_doctorfn, name='admin_delete_doctor'),


    path('adminaddpatient/',admin_add_patientfn, name='admin_add_patient'),
    path('adminviewpatient/',admin_view_patientfn, name='admin_view_patient'),   
    path('admineditpatient/<int:u_id>/',admin_edit_patientfn, name='admin_edit_patient'),
    path('admindeletepatient/<int:u_id>/',admin_delete_patientfn, name='admin_delete_patient'),


    path('adminaddappointment/',admin_add_appointmentfn, name='admin_add_appointment'),
    path('adminviewappointment/',admin_view_appointmentfn, name='admin_view_appointment'),
    path('approve-appointment/<int:pk>/', approve_appointmentfn, name='approve_appointment'),
    path('admineditappointment/<int:pk>/', admin_edit_appointmentfn, name='admin_edit_appointment'),
    path('admindeleteappointment/<int:pk>/', admin_delete_appointmentfn, name='admin_delete_appointment'),
    path('adminviewbills/', admin_view_billsfn, name='admin_view_bills'),
    path('mark_paid/<int:pk>/', mark_bill_paidfn, name='mark_bill_paid'),


    path('patientbookappointment/',patient_book_appointmentfn, name='patient_book_appointment'),
    path('patientviewappointment/',patient_view_appointmentfn, name='patient_view_appointment'),
    path('patientviewdoctor/',patient_view_doctorfn, name='patient_view_doctor'),
    path('doctor_dep/<int:s_id>/',doctor_depfn),
    path('patientviewprescription/',patient_view_prescriptionfn, name='patient_view_prescription'),


    path('doctorviewappointment/',doctor_view_appointmentfn, name='doctor_view_appointment'),
    path('doctoraddprescription/<int:appt_id>/', doctor_add_prescriptionfn, name='doctor_add_prescription'),
    path('complete-appointment/<int:pk>/', complete_appointmentfn, name='complete_appointment'),


]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
