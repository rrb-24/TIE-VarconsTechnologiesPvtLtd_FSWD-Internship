from django.shortcuts import render, HttpResponse, redirect
from django.utils import timezone
from icalendar import Event, Calendar
from django.core.mail import send_mail
from django.template.loader import get_template
from urllib.parse import urlencode

from .models import bookingdetails


def index(request):
    return render(request, 'index.html')


def generate_ics_event(event_details):
    event = Event()
    event.add('summary', event_details['summary'])
    event.add('description', event_details['description'])
    event.add('dtstart', event_details['start_date'])
    event.add('dtend', event_details['end_date'])
    event.add('dtstamp', timezone.now())

    cal = Calendar()
    cal.add_component(event)

    ics_content = cal.to_ical()

    return ics_content


def store(request):
    if request.method == 'POST':
        name = request.POST['name']
        number = request.POST['number']
        email = request.POST['email']
        prizing = request.POST['prizing']
        classs = request.POST['classs']
        joining_date_str = request.POST['joining_date']
        end_date_str = request.POST['end_date']

        # Parse the date strings to datetime objects
        joining_date = timezone.datetime.strptime(joining_date_str, '%Y-%m-%d')
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')

        # Assuming you have retrieved the user's email address in the 'email' variable
        user_email = email

        # Generate the .ics event details
        event_details = {
            'summary': f'{classs} Booking Confirmation for {name}',
            'description': classs,
            'start_date': joining_date,
            'end_date': end_date,
        }

        # Create a Google Calendar link
        google_calendar_link = f'''https://www.google.com/calendar/render?{urlencode({
    'action': 'TEMPLATE',
    'text': event_details['summary'],
    'dates': f"{joining_date.strftime('%Y%m%d')}T{joining_date.strftime('%H%M%S')}/{end_date.strftime('%Y%m%d')}T{end_date.strftime('%H%M%S')}",
    'details': event_details['description'],
})}'''

        event_details['google_calendar_link'] = google_calendar_link

        # Send the confirmation email with the .ics attachment and Google Calendar link
        subject = event_details['summary']
        message = event_details['description']
        from_email = 'raghubavagi2002@gmail.com'  # Use your sender email address
        recipient_list = [user_email]

        text_template = get_template('email/email.txt')
        html_template = get_template('email/email.html')

        context = {'event_details': event_details}

        text_content = text_template.render(context)
        html_content = html_template.render(context)

        send_mail(subject, message, from_email, recipient_list,
                  fail_silently=False, html_message=html_content)

        # Create a booking entry in the database
        bookingdetails.objects.create(name=name, number=number, email=email, prizing=prizing,
                                      classs=classs, joining_date=joining_date, end_date=end_date)

        # Generate the .ics file and return it as a response
        ics_content = generate_ics_event(event_details)
        response = HttpResponse(ics_content, content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="event.ics"'

        return response

    return render(request, 'home.html')
