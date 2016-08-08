from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from poll.views import poll_view, poll_end, faq_view, index, poll_start, get_results, get_results_excel

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^admin/faq/$', TemplateView.as_view(template_name='admin/faq.html')),
                  url(r'^$', index, name='index'),
                  url(r'^anonimowosc/$', faq_view, name='faq'),

                  url(r'^wyniki/(?P<object_id>\d+)/$', get_results, name='results'),
                  url(r'^wyniki/(?P<object_id>\d+)/excel/$', get_results_excel, name='results_excel'),

                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/$', poll_start, name='poll'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/glosowanie/$', poll_view, name='poll_vote'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/koniec/$', poll_end, name='poll_end'),

                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/(?P<token>[\w\-]+)/$', poll_start, name='poll'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/(?P<token>[\w\-]+)/glosowanie/$', poll_view, name='poll_vote'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/(?P<token>[\w\-]+)/koniec/$', poll_end, name='poll_end'),

                  url(r'^nested_admin/', include('nested_admin.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = settings.ADMIN_SITE_HEADER
