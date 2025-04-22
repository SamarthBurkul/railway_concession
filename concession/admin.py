from django.contrib import admin
from concession.models import SignForm,ApplicationStatus
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import details
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.core.mail import send_mail

admin.site.site_header = "Railway Consession "
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Welcome to the Admin Dashboard"


class SignFormAdmin(admin.ModelAdmin):
    list_display = ('login_id', 'username', 'email', 'password')  # Columns in table format
    list_filter = ('username', 'email')  # Adds filter options in Django Admin
    search_fields = ('username', 'email')  # Adds a search bar
    ordering = ('login_id',)  # Orders records by `login_id`
    actions = ['delete_selected']
admin.site.register(SignForm, SignFormAdmin)  # Registering the model with custom Admin class


class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = (
        'application_id',
        'formatted_submitted_date',
        'formatted_under_process_date',
        'formatted_accepted_date',
        'formatted_rejected_date',
        'status',
        'concession_id',
        'login_id',
        'download_pdf_button'  # ✅ This must match the method name exactly
    )
    list_filter = ('status',)
    search_fields = ('application_id', 'login_id__id', 'concession_id__id')

    def formatted_submitted_date(self, obj):
        return obj.submitted_date.strftime("%Y-%m-%d") if obj.submitted_date else "NA"
    formatted_submitted_date.short_description = "Submitted Date"

    def formatted_under_process_date(self, obj):
        return obj.under_process_date.strftime("%Y-%m-%d") if obj.under_process_date else "NA"
    formatted_under_process_date.short_description = "Under Process Date"

    def formatted_accepted_date(self, obj):
        return obj.accepted_date.strftime("%Y-%m-%d") if obj.accepted_date else "NA"
    formatted_accepted_date.short_description = "Accepted Date"

    def formatted_rejected_date(self, obj):
        return obj.rejected_date.strftime("%Y-%m-%d") if obj.rejected_date else "NA"
    formatted_rejected_date.short_description = "Rejected Date"

    def login_id(self, obj):
        return obj.concession_id.login_id
    login_id.short_description = "Login ID"

    def download_pdf_button(self, obj):
        if obj.status.lower() == "accepted":
            url = reverse('download_certificate', args=[obj.application_id])
            return format_html('<a class="button" href="{}" target="_blank">Download PDF</a>', url)
        return "-"
    download_pdf_button.short_description = "Download Certificate"
    
   

admin.site.register(ApplicationStatus, ApplicationStatusAdmin)




#Details Table  Code

# DetailsAdmin class
class DetailsAdmin(admin.ModelAdmin):
    list_display = (
        'concession_id', 'studentname', 'collegename',
        'station1', 'station2', 'travel_class', 'validity',
        'current_date', 'valid_till_date', 'login_id', 'status', 'get_buttons'
    )
    search_fields = ('studentname', 'collegename', 'station1', 'station2')  # Enable search
    list_filter = ('validity', 'travel_class', 'current_date')  # Enable filtering

    def get_buttons(self, obj):
        """Show Accept and Reject buttons."""
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a class="button" style="background-color: green; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; text-align: center; display: inline-block;" href="accept/{}/">✔ Accept</a>'
            '<a class="button" style="background-color: red; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; text-align: center; display: inline-block;" href="reject/{}/">✘ Reject</a>'
            '</div>',
            obj.concession_id, obj.concession_id
        )
    
    get_buttons.short_description = 'Actions'

    def get_urls(self):
        """Add custom URLs for Accept and Reject actions."""
        urls = super().get_urls()
        custom_urls = [
            path('accept/<int:concession_id>/', self.admin_site.admin_view(self.accept_concession), name="accept_concession"),
            path('reject/<int:concession_id>/', self.admin_site.admin_view(self.reject_concession), name="reject_concession"),
        ]
        return custom_urls + urls

    def accept_concession(self, request, concession_id):
        """Mark the concession as accepted and update the ApplicationStatus table."""
        concession = details.objects.get(concession_id=concession_id)
        concession.status = "accepted"
        concession.save()
        concession = details.objects.get(concession_id=concession_id)
        concession.status = "accepted"
        concession.save()

        # Update the ApplicationStatus table
        application_status = ApplicationStatus.objects.get(concession_id=concession_id)
        application_status.accepted_date = timezone.now()
        application_status.status = "accepted"
        application_status.save()

        # ✅ Send email upon acceptance
        recipient_email =  str(concession.login_id.email)
        print("Users Email",recipient_email)
 # assuming foreign key to Login table
        send_mail(
            subject="Your Railway Concession Application is Accepted ✅",
            message="Hello,\n\nYour railway concession application has been accepted.\n\nYou ca.n now download your certificate from the portal.\n\nThank you!",
            from_email="jiveshwork16@gmail.com",  # or settings.DEFAULT_FROM_EMAIL
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        messages.success(request, "Concession Accepted and Email Sent")
      
        # Update the ApplicationStatus table with accepted date
        application_status = ApplicationStatus.objects.get(concession_id=concession_id)
        application_status.accepted_date = timezone.now()
        application_status.status = "accepted"
        application_status.save()

        messages.success(request, "Concession Accepted")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

    def reject_concession(self, request, concession_id):
        """Mark the concession as rejected and update the ApplicationStatus table."""
        concession = details.objects.get(concession_id=concession_id)
        concession.status = "rejected"
        concession.save()

        # Update the ApplicationStatus table with rejected date
        application_status = ApplicationStatus.objects.get(concession_id=concession_id)
        application_status.rejected_date = timezone.now()
        application_status.status = "rejected"
        application_status.save()

        messages.error(request, "Concession Rejected")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

admin.site.register(details, DetailsAdmin)