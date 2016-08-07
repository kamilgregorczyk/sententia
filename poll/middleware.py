from django.http import HttpResponseRedirect

allowed_urls = ['/admin/login/', '/ankieta/', '/', '/anonimowosc/']
class LoginRequiredMiddleware:
    def process_request(self, request):
        if not request.user.is_authenticated():
            path = request.path_info
            if path not in allowed_urls:
                return HttpResponseRedirect('/admin/login/?next=' + path)
