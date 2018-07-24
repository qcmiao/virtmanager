from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^start-vm$', views.vm_start),
    url(r'^reboot-vm$', views.vm_reboot),
    url(r'^shutdown-vm$', views.vm_destroy),
    url(r'^suspend-vm$', views.vm_suspend),
    url(r'^resume-vm$', views.vm_suspend),
]