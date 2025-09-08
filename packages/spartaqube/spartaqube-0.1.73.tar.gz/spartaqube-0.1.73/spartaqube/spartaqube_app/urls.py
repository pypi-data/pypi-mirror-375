from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_2a61277a15.sparta_9ee4944bc9.qube_537842e9bb.sparta_b9069c23e8'
handler500='project.sparta_2a61277a15.sparta_9ee4944bc9.qube_537842e9bb.sparta_71778d0ffa'
handler403='project.sparta_2a61277a15.sparta_9ee4944bc9.qube_537842e9bb.sparta_7bd8dfc1ed'
handler400='project.sparta_2a61277a15.sparta_9ee4944bc9.qube_537842e9bb.sparta_0aceb1a6a7'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]