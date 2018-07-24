"""virtmanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from node import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.indexviewer, name='index'),
    url(r'^host_list/$', views.hostviewer),
    url(r'^vm_list/$', views.vmviewer),
    url(r'^vm_list/(?P<pk>[\d]+)/$', views.vmviewer_detail),
    url(r'^start-vm/$', views.vm_start),
    url(r'^reboot-vm/$', views.vm_reboot),
    url(r'^shutdown-vm/$', views.vm_destroy),
    url(r'^suspend-vm/$', views.vm_suspend),
    url(r'^resume-vm/$', views.vm_suspend),

    # url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.logout, name='logout'),
]


