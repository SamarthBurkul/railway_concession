from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from concession.models import SignForm,details,ApplicationStatus
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.contrib import messages
from .form import PreferencesForm
from .models import UserProfile
from datetime import date
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta


def login(request):
    if request.session.get("user_id"):  # Check if user is already logged in
        return redirect("home") 
    return render(request, 'login.html')



@login_required(login_url="login")  
 # Only the user that has login can access the homepage
def homepage(request):
    print("📌 Function `homepage` called", flush=True)

    user = request.user  # ✅ Django automatically sets this if logged in

    if not user.is_authenticated:
        print("🚨 User is not authenticated. Redirecting to login.", flush=True)
        return redirect("login")

    try:
        user_concession = details.objects.filter(login_id=user.login_id).last()
    except AttributeError:
        print("⚠️ User object does not have `login_id`. Redirecting to login.")
        return redirect("login")

    if not user_concession:
        print(f"❌ No concession data found for user: {user}.", flush=True)
        return render(request, "home.html", {"status": "no_data"})
    
    # Extract and debug concession data
    status = user_concession.status
    start_date = user_concession.current_date
    end_date = user_concession.valid_till_date
    today = date.today()

    print(f"📅 Concession Status: {status}")
    print(f"📆 Start Date: {start_date}")
    print(f"📆 End Date: {end_date}")
    print(f"📌 Today's Date: {today}")

    # Handle None values safely
    if not start_date or not end_date:
        print("⚠️ Missing start_date or end_date. Defaulting to 0.", flush=True)
        total_days = 0
        used_days = 0
        remaining_days = 0
    else:
        total_days = max((end_date - start_date).days, 0)
        used_days = max((today - start_date).days, 0) if today >= start_date else 0
        remaining_days = max(total_days - used_days, 0)

    # Calculate percentage safely
    used_percentage = (used_days / total_days) * 100 if total_days else 0
    remaining_percentage = 100 - used_percentage

    print(f"📊 Used Days: {used_days}, Remaining Days: {remaining_days}")
    print(f"📈 Used Percentage: {used_percentage:.2f}%")
    print(f"📉 Remaining Percentage: {remaining_percentage:.2f}%")
    
    application = ApplicationStatus.objects.filter(login_id=user.login_id).order_by('-accepted_date', '-submitted_date').first()
    # Decide start/end dates based on status
    if status == "accepted" and application and application.accepted_date:
           concession_start = application.accepted_date
           validity_months = user_concession.validity or 1
           concession_end = concession_start + relativedelta(months=validity_months)
           print(f"✅ Accepted - Calculating from accepted_date: {concession_start} to {concession_end}")
    else:
           concession_start = None
           concession_end = None
           print(f"🕓 Concession Pending - Using default period: {concession_start} to {concession_end}")
           print(f"🕓 Not Accepted - Using default start and end: {concession_start} to {concession_end}")
    application_status = application.status if application else "No Progress"
    last_updated = application.accepted_date or application.submitted_date if application else None

    print(f"🧾 Application Status: {application_status}")
    print(f"📆 Last Updated: {last_updated}")
    return render(request, 'home.html', {
        "status": status,
        "used_percentage": used_percentage,
        "remaining_percentage": remaining_percentage,
         "last_updated": last_updated,
         "start_date": concession_start,
        "end_date": concession_end,

    })




  
def myform(request):
    
    # 1️⃣ Get user ID from session (since you're not using Django's auth system)
    user_id = request.session.get("user_id")  # Assuming you store user ID in session
    print(f" DEBUG: Logged-in user ID from session = {user_id}")

    # 2️⃣ Check if user ID exists in the session
    if not user_id:
        print(" ERROR: No user ID found in session!")
        return render(request, "concession2.html", {"user_has_concession": False})

    # 3️⃣ Check if the user has applied for a railway concession
    concession_exists = details.objects.filter(login_id=user_id).exists()
    print(f"DEBUG: user_has_concession = {concession_exists}")

    # 4️⃣ Render template with the correct context
    return render(request, "concession2.html", {"user_has_concession": concession_exists})





@login_required(login_url="login") 

def settings(request):
    user = SignForm.objects.get(login_id=request.user.login_id)
    
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        try:
            if 'change_password' in request.POST:
                current = request.POST.get('currentPassword')
                new = request.POST.get('newPassword')
                print("Current Input Password:", current)
                print("Stored Password:", user.password)

                if current == new:
                    messages.error(request, 'New password cannot be the same as the current password.')
                elif current == user.password: 
                   user.password = new  # 🔐 Directly storing raw password
                   user.save()
                   messages.success(request, 'Password updated successfully.')
                else:
                    messages.error(request, 'Current password is incorrect.')

            elif 'change_username' in request.POST:
                new_username = request.POST.get('username')
                current_password = request.POST.get('usernamePassword')
                user = request.user  # Get current logged-in user

                print("Current Inputs:", new_username, current_password)
                print("Stored Raw Password:", user.password)

                if current_password == user.password:  # ✅ Direct comparison (raw)
                    if SignForm.objects.exclude(login_id=user.login_id).filter(username=new_username).exists():

                        messages.error(request, 'Username already taken.')
                    else:
                        user.username = new_username
                        user.save()
                        messages.success(request, 'Username updated successfully.')
                else:
                    print("❌ Password is incorrect")
                    messages.error(request, 'Password is incorrect for username change.')

            elif request.POST.get('action') == 'save_preferences':
                profile.theme = request.POST.get('theme', profile.theme)
                profile.font_size = request.POST.get('font_size', profile.font_size)
                profile.contrast_mode = request.POST.get('contrast_mode', profile.contrast_mode)
                profile.save()
                messages.success(request, 'Preferences updated successfully.')

        except IntegrityError as e:
            print(f"Database integrity error: {e}")
            messages.error(request, 'A database error occurred.')
        except Exception as e:
            print(f"Unexpected error: {e}")
            messages.error(request, 'An unexpected error occurred.')

    form = PreferencesForm(instance=profile)

    return render(request, 'setting.html', {
        'form': form,
        'theme': profile.theme,
        'font_size': profile.font_size,
        'contrast_mode': profile.contrast_mode,
        'current_username': user.username
    })






def status(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if user is not logged in

    # Fetch the user's application statuses using the `login_id`
    login_id = request.user.login_id
    statuses = ApplicationStatus.objects.filter(login_id=login_id).order_by('-submitted_date')

    # Prepare the data for JSON format
    status_data = []
    for status in statuses:
        # Extract all date fields (submitted_date, under_process_date, accepted_date)
        submitted_date = status.submitted_date.strftime('%Y-%m-%d') if status.submitted_date else None
        under_process_date = status.under_process_date.strftime('%Y-%m-%d') if status.under_process_date else None
        accepted_date = status.accepted_date.strftime('%Y-%m-%d') if status.accepted_date else None

        # Append all dates to the status_data list
        status_data.append({
            'submitted_date': submitted_date,
            'under_process_date': under_process_date,
            'accepted_date': accepted_date,
        })

    # Debugging: Print all date fields to the console for checking
    print("DEBUG: All Dates:", status_data)

    # Pass the data to the template
    return render(request, 'status.html', {'status_data': status_data})















def logout(request):
    request.session.flush()  # Clear all session data (logs user out)
    return redirect("login")  # Redirect to login page after logout
 
#Logic for checking validity of pass
