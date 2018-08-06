# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from node.models import VirtMachine, HostMachine
from .vm_ctl import start_vm, reboot_vm, destroy_vm, suspend_vm
from django.http import HttpResponse
import threading

from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect,
                         JsonResponse,
                         HttpResponseForbidden)

from rest_framework.views import APIView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

# def index(request):
#     return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


@login_required
def indexviewer(request):
    return render(request, 'index.html')


class LoginView(View):
    def get(self, request):
        return self.response(request)

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if not form.is_valid():
            return self.response(request, form)
        user = form.get_user()
        auth_login(request, user)
        return HttpResponseRedirect(reverse("index"))

    def response(self, request, form=None):

        if form is None:
            form = AuthenticationForm(initial={'username': ''})
            error = False
        else:
            error = True

        return render(request, 'login.html', {
            "form": form,
            "error": error
        })


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def hostviewer(request):
    host_info_list = HostMachine.objects.all().order_by('-id')
    paginator = Paginator(host_info_list, 10)  # Show 10 host per page
    page = request.GET.get('page')
    try:
        host_info = paginator.page(page)
    except PageNotAnInteger:
        host_info = paginator.page(1)
    except EmptyPage:
        host_info = paginator.page(paginator.num_pages)
    return render(request, 'host_list.html', {'host_info': host_info})


@login_required
def hostviewer_detail(request,pk):
    host_id = pk
    host_ip = HostMachine.objects.get(id = host_id).host_ip
    vm_info = VirtMachine.objects.filter(host_machine_id=host_id)
    context = {'vm_info': vm_info, "host_ip": host_ip}
    return render(request, 'host_list_detail.html', context)


@login_required
def vmviewer(request):
    vm_info_list = VirtMachine.objects.all()
    paginator = Paginator(vm_info_list, 10)  # Show 10 vm per page
    page = request.GET.get('page')
    try:
        vm_info = paginator.page(page)
    except PageNotAnInteger:
        vm_info = paginator.page(1)
    except EmptyPage:
        vm_info = paginator.page(paginator.num_pages)
    return render(request, 'vm_list.html', {'vm_info': vm_info})


@login_required
def vmviewer_detail(request,pk):
    host_id = pk
    host_ip = HostMachine.objects.get(id = host_id).host_ip
    vm_info = VirtMachine.objects.filter(host_machine_id=host_id)
    context = {'vm_info': vm_info, "host_ip": host_ip}
    return render(request, 'vm_list_detail.html', context)


@login_required
def vm_start(request):
    vmid = request.POST.get('id')
    vm = VirtMachine.objects.get(id=vmid)
    virt_id = vm.vm_id
    host_id = vm.host_machine_id
    host = HostMachine.objects.get(id=host_id)
    host_ip = host.host_ip
    threading.Thread(target=start_vm, args=(host_ip, virt_id)).start()
    return HttpResponse('success')


@login_required
def vm_reboot(request):
    vmid = request.POST.get('id')
    vm = VirtMachine.objects.get(id=vmid)
    virt_id=vm.vm_id
    host_id=vm.host_machine_id
    host = HostMachine.objects.get(id=host_id)
    host_ip = host.host_ip
    threading.Thread(target=reboot_vm, args=(host_ip, virt_id)).start()
    return HttpResponse('success')


@login_required
def vm_destroy(request):
    vmid = request.POST.get('id')
    vm = VirtMachine.objects.get(id=vmid)
    virt_id = vm.vm_id
    host_id = vm.host_machine_id
    host = HostMachine.objects.get(id=host_id)
    host_ip = host.host_ip
    threading.Thread(target=destroy_vm, args=(host_ip, virt_id)).start()
    return HttpResponse('success')


@login_required
def vm_suspend(request):
    vmid = request.POST.get('id')
    vm = VirtMachine.objects.get(id=vmid)
    virt_id = vm.vm_id
    host_id = vm.host_machine_id
    host = HostMachine.objects.get(id=host_id)
    host_ip = host.host_ip
    threading.Thread(target=suspend_vm, args=(host_ip, virt_id)).start()
    return HttpResponse('success')

@login_required
def host_add(request):
    hostip = request.POST.get('ip').strip()
    description = request.POST.get('description')
    HostMachine.objects.create(host_ip=hostip, description=description)
    return HttpResponse('success')

@login_required
def host_del(request):
    hostid = request.POST.get('id')
    vm = VirtMachine.objects.filter(host_machine_id=hostid)
    vm.delete()
    host = HostMachine.objects.get(id=hostid)
    host.delete()
    return HttpResponse('success')


