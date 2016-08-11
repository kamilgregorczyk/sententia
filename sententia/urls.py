from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from poll.views import PollVoteView, IndexView, FAQView, PollResultsView, ExcelResultsView, PollStartView, PollEndView, PollErrorView

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^admin/faq/$', TemplateView.as_view(template_name='admin/faq.html')),
                  url(r'^$', IndexView.as_view(), name='index'),
                  url(r'^anonimowosc/$', FAQView.as_view(), name='faq'),

                  url(r'^wyniki/(?P<object_id>\d+)/$', PollResultsView.as_view(), name='results'),
                  url(r'^wyniki/(?P<object_id>\d+)/excel/$', ExcelResultsView.as_view(), name='results_excel'),

                  url(r'^ankieta/blad/$', PollErrorView.as_view(), name='poll_error'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/$', PollStartView.as_view(), name='poll'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/glosowanie/$', PollVoteView.as_view(), name='poll_vote'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/koniec/$', PollEndView.as_view(), name='poll_end'),

                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/(?P<token>[\w\-]+)/$', PollStartView.as_view(), name='poll'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/(?P<token>[\w\-]+)/glosowanie/$', PollVoteView.as_view(), name='poll_vote'),
                  url(r'^ankieta/(?P<poll_code>[\w\-]+)/(?P<token>[\w\-]+)/koniec/$', PollEndView.as_view(), name='poll_end'),

                  url(r'^nested_admin/', include('nested_admin.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = settings.ADMIN_SITE_HEADER
