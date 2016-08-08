from django.http import HttpResponseRedirect

allowed_urls = ['/admin/login/', '/ankieta/', '/', '/anonimowosc/']
class LoginRequiredMiddleware:
    def process_request(self, request):
        if not request.user.is_authenticated():
            path = request.path_info
            if not any([path.startswith(i) for i in allowed_urls]) and path != '/':
                return HttpResponseRedirect('/admin/login/?next=' + path)
