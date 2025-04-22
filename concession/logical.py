import fitz  # PyMuPDF
from django.http import HttpResponse, Http404
from django.conf import settings
import os
from io import BytesIO
from .models import ApplicationStatus
from datetime import datetime
def download_certificate(request, application_id):
    try:
        application = ApplicationStatus.objects.get(pk=application_id)
    except ApplicationStatus.DoesNotExist:
        raise Http404("Application not found.")

    # Only allow download if the current status is accepted
    if application.status != "accepted":
        raise Http404("Only accepted applications can be downloaded.")

    # Access the related details model through concession_id
    details = application.concession_id

    # Load the certificate PDF template
    template_path = os.path.join(settings.BASE_DIR, 'static', 'image', 'railway_certificate.pdf')
    doc = fitz.open(template_path)
    page = doc[0]
    text_to_remove = "Validity Period: 9th April to 9th June, 2025"
    matches = page.search_for(text_to_remove)
    for inst in matches:
        page.add_redact_annot(inst, fill=(1, 1, 1))  # White fill
    page.apply_redactions()

    current_date = datetime.now().strftime("%d-%m-%Y")
    page.insert_text((129.7919921875, 96.43501281738281), f"{details.studentname}", fontsize=12)     # Student Name
    page.insert_text((320.0759582519531, 96.43501281738281), f"{details.collegename}", fontsize=12)    # College Name
    page.insert_text((88.36000061035156, 207.5750274658203), f"{details.travel_class}", fontsize=12)       # Class/Period
    page.insert_text((179.41000366210938,  207.5750274658203), f"{details.station1}", fontsize=12)           # From Station
    page.insert_text((298.4700012207031,  207.5750274658203), f"{details.station2}", fontsize=12)           # To Station
    page.insert_text((439.869998931884766,  207.5750274658203), f"{details.validity}", fontsize=12)            # Validity in table
    page.insert_text((62.869998931884766, 546.9200439453125),current_date, fontsize=12) 

    # Save the updated PDF into memory
    buffer = BytesIO()
    doc.save(buffer)
    doc.close()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="certificate_{application_id}.pdf"'
    return response