from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from concession.models import SignForm,details,ApplicationStatus
from django.contrib import messages 
from datetime import datetime
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import SignForm
from django.contrib.auth import login
from django.utils.timezone import now
#Code for Sign up
def savedata(request):
    if request.method=="POST":
        username = request.POST.get('username')  # Fetching 'username' field
        email = request.POST.get('email1')  # Fetching 'email1' field
        password = request.POST.get('password1')
        data=SignForm(username=username,email=email,password=password)
        data.save()
    return render(request,'login.html')

# Code for saving Candidate details
def savedetail(request):
    if request.method == "POST":
        # Fetch form data
        studname = request.POST.get('studentname')
        clgname = request.POST.get('collegename')
        station1 = request.POST.get('station1')
        station2 = request.POST.get('station2')
        Class = request.POST.get('classes')
        validity = int(request.POST.get("month"))
        current = datetime.strptime(request.POST.get("current_date"), "%Y-%m-%d").date()
        valid_till = datetime.strptime(request.POST.get("valid_till_date"), "%Y-%m-%d").date()

        # Fetching the current user's SignForm instance using login_id
        signform_instance = SignForm.objects.filter(login_id=request.user.login_id).last()

        # Debug print statements to check form data and SignForm instance
        print("Student Name:", studname)
        print("College Name:", clgname)
        print("Station 1:", station1)
        print("Station 2:", station2)
        print("Class:", Class)
        print("Validity:", validity)
        print("Current Date:", current)
        print("Valid Till Date:", valid_till)
        print("SignForm Instance:", signform_instance)

        # Check if the user has a valid SignForm instance
        if signform_instance:
            try:
                # Create and save the Details instance
                detail = details(
                    studentname=studname,
                    collegename=clgname,
                    station1=station1,
                    station2=station2,
                    travel_class=Class,
                    validity=validity,
                    current_date=current,
                    valid_till_date=valid_till,
                    login_id=signform_instance
                )
                detail.save()  # Save the Details instance

                # Create the ApplicationStatus object and save it
                application_status = ApplicationStatus.objects.create(
                    concession_id=detail,
                    status="submitted",  # Set status to "submitted"
                    under_process_date=now().date(),  # Set the current date
                    login_id=request.user  # Automatically assigns the logged-in user as login_id
                )

                # Success message for the user
                messages.success(request, "Your concession request has been submitted.")
                return redirect('home')  # Redirect to 'home' after successful submission

            except Exception as e:
                # Error handling in case of failure during saving
                messages.error(request, f"An error occurred: {e}")
                return redirect('concession_form')  # Redirect back to the form if there's an error

        else:
            # If no SignForm instance is found for the user, show an error
            messages.error(request, "User not found or not logged in.")
            return redirect('concession_form')  # Redirect back to the form if user is not found

    # If the request method is not POST, render the concession form page
    # Check if the user already has a concession
    user_has_concession = details.objects.filter(login_id=request.user).exists()

    # Render the concession form page with the check for an existing concession
    return render(request, 'concession2.html', {"user_has_concession": user_has_concession})

#Code for Login

    
def login_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        print("📩 Received Email:", email)
        print("🔒 Received Password:", password)

        try:
            user = SignForm.objects.get(email=email)  # Check if email exists
            
            if user.password == password:  # ❌ Plain text comparison (NOT SECURE)
                login(request, user)  # Manually logging ins
                request.session["user_id"] = user.login_id  # Store user in session
                return JsonResponse({"success": True})  # Login success response
            else:
                return JsonResponse({"success": False, "error_type": "password", "message": "Incorrect password"})
        
        except SignForm.DoesNotExist:
            return JsonResponse({"success": False, "error_type": "email", "message": "Email not registered"})

    return JsonResponse({"error": "Invalid request"}, status=400)