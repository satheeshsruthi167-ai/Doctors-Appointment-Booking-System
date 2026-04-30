from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.db.models import Sum
from .models import *
from.forms import *

User = get_user_model()
# Create your views here.

##---------------------Home,About,Contact,Doctors-list,Specialization------------------##

def homefn(request):
    return render(request,'home.html')

def aboutfn(request):
    return render(request,'about.html')

def doctorlistfn(request):
    d=Doctor.objects.all()
    s=Specialization.objects.all()
    return render(request,'doctorlist.html',{'doc':d,'spl':s})

def contactfn(request):
    if request.method == 'POST':
        name = request.POST.get('user_name')
        email = request.POST.get('user_email')
        feedback = request.POST.get('user_feedback')

        Feedback.objects.create(
            name=name,
            email=email,
            feedback_text=feedback
        )
        
        messages.success(request, "Thank you! Your feedback has been submitted.")
        return redirect('/contact/')     
    return render(request, 'contact.html')

##----- to view specialization list in doctors list -----##

def viewsplfn(request,s_id):  
    d=Doctor.objects.filter(specialization=s_id)
    s=Specialization.objects.all()
    return render(request,'doctorlist.html',{'doc':d,'spl':s})

def indexfn(request):                         ##-----Signup dashboard-----##
    return render(request,'index.html')

##---------------------Register,Login,Logout------------------##

def doctor_signupfn(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = DoctorProfileForm(request.POST, request.FILES)
        user_is_valid = user_form.is_valid()
        profile_is_valid = profile_form.is_valid()
        if user_is_valid and profile_is_valid:
           
            new_user = user_form.save()            
            profile = profile_form.save(commit=False)

            profile.user = new_user
            profile.status = False
            profile.save()
            messages.success(request, 'Registration successful! Please wait for Admin approval before logging in.')
            return redirect('/login/')
    else:
        user_form = UserRegisterForm()
        profile_form = DoctorProfileForm()
    return render(request, 'doctor_signup.html', {'user_form': user_form,'profile_form': profile_form})


def patient_signupfn(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = PatientProfileForm(request.POST)
        user_is_valid = user_form.is_valid()
        profile_is_valid = profile_form.is_valid()
        if user_is_valid and profile_is_valid:
           
            new_user = user_form.save()            
            profile = profile_form.save(commit=False)

            profile.user = new_user
            profile.save()
            return redirect('/login/')
    else:
        user_form = UserRegisterForm()
        profile_form = PatientProfileForm()
    return render(request, 'patient_signup.html', {'user_form': user_form,'profile_form': profile_form})


##-------- Admin, Doctor, Patient can login --------##

def loginfn(request):
    error = ""
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('psw1')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                doctor = Doctor.objects.get(user=user)
                if not doctor.status:
                    error = "Your account is pending admin approval."
                    return render(request, 'login.html', {'er': error})
            except Doctor.DoesNotExist:
                pass
            login(request, user)
            return redirect('/dashboard-redirect/') 
        else:
            error = "Invalid username or password"
            
    return render(request, 'login.html', {'er': error})

##----- after login users will be redirected to their dashboard -----##

@login_required
def dashboard_redirectfn(request):
    if request.user.is_superuser or request.user.is_staff:
        print(f"User {request.user.username} is Admin")
        return redirect('/admindashboard/')

    elif hasattr(request.user, 'doctor'):
        print(f"User {request.user.username} is a Doctor")
        return redirect('/doctordashboard/')
    
    elif hasattr(request.user, 'patient'):
        print(f"User {request.user.username} is a Patient")
        return redirect('/patientdashboard/')
    
    else:
        print("No profile found for this user.")
        return redirect('/login/')

##----- logout -----##

def logoutfn(request):
    logout(request)
    return redirect('/')

 
##---------------------dashboard------------------##

@login_required
def admin_dashboardfn(request):
    doctor_count = Doctor.objects.all().count()
    patient_count = Patient.objects.all().count()
    pending_doctors = Doctor.objects.filter(status=False).count()
    pending_count = Appointment.objects.filter(status='PENDING').count()
    earnings_query = Bill.objects.filter(is_paid=True).aggregate(total=Sum('total_amount'))
    total_earnings = earnings_query['total'] or 0
    recent_bills = Bill.objects.all().order_by('-generated_at')[:5]
    feedbacks = Feedback.objects.all().order_by('-date_submitted')[:5]

    context = {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'pending_doctors': pending_doctors,
        'pending_count': pending_count,
        'total_earnings': total_earnings,
        'recent_bills': recent_bills,
        'feedbacks': feedbacks,
    }
    
    return render(request, 'admin_dashboard.html', context)


@login_required
def doctor_dashboardfn(request):
    doctor = Doctor.objects.get(user=request.user)
        
    total_patients = Appointment.objects.filter(doctor=doctor, status='CONFIRMED').count()
    pending_requests = Appointment.objects.filter(doctor=doctor, status='PENDING').count()

    from datetime import date
    todays_appts = Appointment.objects.filter(doctor=doctor, date=date.today()).count()

    context = {
        'doctor': doctor,
        'total_p': total_patients,
        'pending': pending_requests,
        'today': todays_appts,
        }
    return render(request, 'doctor_dashboard.html', context)



@login_required
def patient_dashboardfn(request):
    patient = Patient.objects.get(user=request.user)
    
    upcoming = Appointment.objects.filter(patient=patient, status='CONFIRMED').count()
    pending = Appointment.objects.filter(patient=patient, status='PENDING').count()
    total = Appointment.objects.filter(patient=patient).count()
    total_prescriptions = Prescription.objects.filter(patient=patient).count()

    context = {
        'upcoming': upcoming,
        'pending': pending,
        'total': total,
        'prescriptions_count': total_prescriptions
    }
    return render(request, 'patient_dashboard.html', context)



##---------------------Admin------------------##     ##---CRUD OPERATIONS VIEWS---##

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_view_doctorfn(request):
    doc = Doctor.objects.all()
    return render(request,'admin_view_doctor.html',{'d':doc})

@login_required
def approve_doctorfn(request, pk):
    doctor = Doctor.objects.get(user_id=pk)
    doctor.status = True  
    doctor.save()
    return redirect('/adminviewdoctor/')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_add_doctorfn(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = DoctorProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
           
            new_user = user_form.save()            
            profile = profile_form.save(commit=False)

            profile.user = new_user
            profile.status = True
            profile.save()
            return redirect('/adminviewdoctor/')
    else:
        user_form = UserRegisterForm()
        profile_form = DoctorProfileForm()
    return render(request, 'admin_add_doctor.html', {'user_form': user_form,'profile_form': profile_form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_edit_doctorfn(request, u_id):
    user =User.objects.get(id=u_id)
    doctor = user.doctor

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/adminviewdoctor/')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = DoctorProfileForm(instance=doctor)
        
    return render(request, 'admin_edit_doctor.html', {'user_form': user_form,'profile_form': profile_form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_doctorfn(request, u_id):
    user =User.objects.get( id=u_id)
    user.delete() 
    return redirect('/adminviewdoctor/')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_view_patientfn(request):
    patient = Patient.objects.all()
    return render(request,'admin_view_patient.html',{'p':patient})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_add_patientfn(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = PatientProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
           
            new_user = user_form.save()            
            profile = profile_form.save(commit=False)

            profile.user = new_user
            profile.save()
            return redirect('/adminviewpatient/')
    else:
        user_form = UserRegisterForm()
        profile_form = PatientProfileForm()
    return render(request, 'admin_add_patient.html', {'user_form': user_form,'profile_form': profile_form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_edit_patientfn(request, u_id):
    user =User.objects.get(id=u_id)
    patient = user.patient

    if request.method == 'POST':
        user_form = UserEditForm(request.POST,instance=user)
        profile_form = PatientProfileForm(request.POST,instance=patient)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/adminviewpatient/')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = PatientProfileForm(instance=patient)
        
    return render(request, 'admin_edit_patient.html',{'user_form': user_form,'profile_form': profile_form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_patientfn(request, u_id):
    user =User.objects.get( id=u_id)
    user.delete() 
    return redirect('/adminviewpatient/')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_add_appointmentfn(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect('/adminviewappointment/')
    else:
        form = AppointmentForm() 
    return render(request, 'admin_add_appointment.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_view_appointmentfn(request):
    appointments = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'admin_view_appointments.html', {'a': appointments})


@login_required
def approve_appointmentfn(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.status = 'CONFIRMED'
    appointment.save()
    
    messages.success(request, f"Appointment for {appointment.patient.user.get_full_name()} confirmed.")
    if request.user.is_superuser:
        return redirect('/adminviewappointment/')
    else:
        return redirect('/doctorviewappointment/')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_edit_appointmentfn(request,pk):
    appointment=Appointment.objects.get(id=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST,instance=appointment)      
        if form.is_valid():
            form.save()
            return redirect('/adminviewappointment/')
    else:
        form = AppointmentForm(instance=appointment) 
    return render(request, 'admin_edit_appointment.html',{'form':form,'appointment':appointment})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_appointmentfn(request, pk):
    appointment=Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('/adminviewappointment/')


@login_required
def admin_view_billsfn(request):
    bills = Bill.objects.all().order_by('-generated_at')
    return render(request, 'admin_view_bills.html', {'bills': bills})

@login_required
def mark_bill_paidfn(request, pk):
    bill = Bill.objects.get(id=pk)
    bill.is_paid = True
    bill.save()
    messages.success(request, f"Payment received for {bill.appointment.patient.user.first_name}")
    return redirect('/adminviewbills/')



##---------------------Patient------------------##

@login_required
def patient_book_appointmentfn(request):
    patient = Patient.objects.get(user=request.user)
    if request.method == 'POST':
        form = PatientAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.status = 'PENDING'           
            appointment.save()
            messages.success(request, "Your appointment has been requested and is pending approval.")
            return redirect('/patientdashboard/')
    else:
        selected_doctor_id = request.GET.get('doctor_id')
        initial_data = {}
        if selected_doctor_id:
            initial_data['doctor'] = selected_doctor_id
        form = PatientAppointmentForm(initial=initial_data)      
    return render(request, 'patient_book_appointment.html', {'form': form})


@login_required
def patient_view_appointmentfn(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')   
    return render(request, 'patient_view_appointment.html', {'appointments': appointments})


@login_required
def patient_view_doctorfn(request):
    d=Doctor.objects.all()
    s=Specialization.objects.all()
    return render(request,'patient_view_doctor.html',{'doc':d,'spl':s})


@login_required
def doctor_depfn(request,s_id):  
    d=Doctor.objects.filter(specialization=s_id)
    s=Specialization.objects.all()
    return render(request,'patient_view_doctor.html',{'doc':d,'spl':s})



@login_required
def patient_view_prescriptionfn(request):
    patient = Patient.objects.get(user=request.user)
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescribed_date')
    return render(request, 'patient_view_prescription.html', {'prescriptions': prescriptions})




##---------------------Doctor------------------##

@login_required
def doctor_view_appointmentfn(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-date')
        return render(request, 'doctor_view_appointment.html', {'appointments': appointments})
    except Doctor.DoesNotExist:
            if request.user.is_superuser:
                return redirect('/adminviewappointment/')       
            logout(request) 
            messages.error(request, "Please log in with a valid Doctor account.")
            return redirect('/login/')

@login_required
def complete_appointmentfn(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.status = 'COMPLETED'
    appointment.save()
    Bill.objects.get_or_create(
        appointment=appointment,
        defaults={
            'consultation_fee': 500.00,
            'other_charges': 0.00,
            'is_paid': False
        }
    )

    messages.success(request, f"Appointment for {appointment.patient.user.first_name} completed. Bill generated.")
    if request.user.is_superuser:
        return redirect('/adminviewappointment/')
    else:
        return redirect('/doctorviewappointment/')

        
@login_required
def doctor_add_prescriptionfn(request, appt_id):
    appointment = Appointment.objects.get(id=appt_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.patient = appointment.patient
            prescription.doctor = appointment.doctor
            prescription.save()   
            messages.success(request, "Prescription saved successfully!")
            return redirect('/doctorviewappointment/')
    else:
        form = PrescriptionForm()
    return render(request, 'doctor_add_prescription.html', {'form': form, 'appointment': appointment})
