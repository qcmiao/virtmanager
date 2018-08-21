# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404
from node.models import VirtMachine, HostMachine, VmNet, BridgeNet, HostNet, Switch, SwitchPort, HostnameRules, VmnameRules
from .vm_ctl import start_vm, reboot_vm, destroy_vm, suspend_vm, vnc_vm
from django.http import HttpResponse, HttpResponseRedirect
import threading
# from .hostinfo_get import *
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
import os

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
def hostname_conf(request):
    hostname_info = HostnameRules.objects.all().order_by('-id')
    return render(request, 'hostname_conf.html', {'hostname_info': hostname_info})

@login_required
def vmname_conf(request):
    vmname_info = VmnameRules.objects.all().order_by('-id')
    return render(request, 'vmname_conf.html', {'vmname_info': vmname_info})

@login_required
def hostviewer(request):
    host_info_list = HostMachine.objects.all().order_by('-id')
    hostname_info = HostnameRules.objects.all()
    paginator = Paginator(host_info_list, 10)  # Show 10 host per page
    page = request.GET.get('page')
    try:
        host_info = paginator.page(page)
    except PageNotAnInteger:
        host_info = paginator.page(1)
    except EmptyPage:
        host_info = paginator.page(paginator.num_pages)
    return render(request, 'host_list.html', {'host_info': host_info, 'hostname_info': hostname_info})


@login_required
def hostviewer_detail(request,pk):
    host_id = pk
    host_ip = HostMachine.objects.get(id = host_id).host_ip
    vm_info = VirtMachine.objects.filter(host_machine_id=host_id)
    context = {'vm_info': vm_info, "host_ip": host_ip}
    return render(request, 'host_list_detail.html', context)


@login_required
def vmviewer(request):
    vm_info_list = VirtMachine.objects.all().order_by('-host_machine_id')
    vmnet_info = VmNet.objects.all()
    paginator = Paginator(vm_info_list, 10)  # Show 10 vm per page
    page = request.GET.get('page')
    try:
        vm_info = paginator.page(page)

    except PageNotAnInteger:
        vm_info = paginator.page(1)
    except EmptyPage:
        vm_info = paginator.page(paginator.num_pages)
    return render(request, 'vm_list.html', {'vm_info': vm_info, 'vmnet_info': vmnet_info})


@login_required
def vmviewer_detail(request, pk):
    host_id = pk
    host_ip = HostMachine.objects.get(id = host_id).host_ip
    vm_info = VirtMachine.objects.filter(host_machine_id=host_id)
    vmnet_info = VmNet.objects.all()
    context = {'vm_info': vm_info, "host_ip": host_ip, 'vmnet_info':vmnet_info}
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
def vm_vnc(request):
    vmid = request.POST.get('id')
    vm = VirtMachine.objects.get(id=vmid)
    virt_id = vm.vm_id
    host_id = vm.host_machine_id
    host = HostMachine.objects.get(id=host_id)
    host_ip = host.host_ip
    vnc_url = vnc_vm(host_ip, virt_id)
    return HttpResponse(vnc_url)


@login_required
def host_add(request):
    hostip = request.POST.get('ip').strip()
    description = request.POST.get('description')
    HostMachine.objects.create(host_ip=hostip, description=description)
    return HttpResponse('success')


@login_required
def host_update(request):
    os.system('/watone/.venv/bin/python /watone/virtmanager/node/hostinfo_get.py ')
    return HttpResponse('success')


@login_required
def host_edit(request):
    host_id = request.POST.get('host_id')
    desc= request.POST.get('desc').strip()
    HostMachine.objects.filter(id=host_id).update(description=desc)
    return HttpResponse('success')


@login_required
def host_del(request):
    hostid = request.POST.get('id')
    vm = VirtMachine.objects.filter(host_machine_id=hostid)
    vm.delete()
    host = HostMachine.objects.get(id=hostid)
    host.delete()
    return HttpResponse('success')


@login_required
def host_refresh(request):
    hostid = request.POST.get('id')
    os.system('/watone/.venv/bin/python /watone/virtmanager/node/hostinfo_refresh.py {}'.format(hostid))
    return HttpResponse('success')


@login_required
def hostrules_add(request):
    hostname = request.POST.get('hostrules').strip()
    address = request.POST.get('address').strip()
    HostnameRules.objects.create(hostname_rules=hostname, address=address)
    return HttpResponse('success')


@login_required
def hostrules_edit(request):
    rules_id = request.POST.get('rules_id')
    hostname = request.POST.get('hostrules').strip()
    address = request.POST.get('addressrules').strip()
    HostnameRules.objects.filter(id=rules_id).update(hostname_rules=hostname, address=address)
    return HttpResponse('success')


@login_required
def hostrules_del(request):
    hostnameid = request.POST.get('hostname')
    hostnamerules = HostnameRules.objects.filter(id=hostnameid)
    hostnamerules.delete()
    return HttpResponse('success')


@login_required
def vmrules_add(request):
    vmname = request.POST.get('vmname').strip()
    business = request.POST.get('business').strip()
    VmnameRules.objects.create(vmname_rules=vmname, business=business)
    return HttpResponse('success')


@login_required
def vmrules_edit(request):
    rules_id = request.POST.get('rules_id')
    vmname = request.POST.get('vmrules').strip()
    business = request.POST.get('business').strip()
    VmnameRules.objects.filter(id=rules_id).update(vmname_rules=vmname, business=business)
    return HttpResponse('success')


@login_required
def vmrules_del(request):
    vmnameid = request.POST.get('vmname')
    vmnamerules = VmnameRules.objects.filter(id=vmnameid)
    vmnamerules.delete()
    return HttpResponse('success')



