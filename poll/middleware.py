from django.http import HttpResponseRedirect


class LoginRequiredMiddleware:
    def process_request(self, request):
        if not request.user.is_authenticated():
            path = request.path_info
            if not (path.startswith('/admin/login/') or path.startswith('/ankieta/')):
                return HttpResponseRedirect('/admin/login/?next=' + path)
