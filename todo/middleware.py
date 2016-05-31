from django.utils import timezone


class TimezoneMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            tz = request.user.profile.timezone
            if tz:
                timezone.activate(tz)
            else:
                timezone.deactivate()