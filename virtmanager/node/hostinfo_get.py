#coding=utf-8
import libvirt
import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "."))
os.environ['DJANGO_SETTINGS_MODULE'] = 'virtmanager.settings'
django.setup()
from node.models import VirtMachine, HostMachine


#vmid list
def vmlist_get(host_ip):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    vmlist = conn.listAllDomains()
    vmnum = len(vmlist)
    vmname_list = []
    for n in range(0, vmnum):
        # vmname = conn.listAllDomains()[n].name()
        vmname = vmlist[n].name()
        vmname_list.append(vmname)
    conn.close()
    return vmname_list


# vmstate dom.info()[0]  (==1 runing)  (==3  paused)   (==5  shutdown)
def domain_info(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    dom = conn.lookupByName(vm_id)
    vm_status = dom.state()[0]
    vm_cpunum = dom.info()[3]
    vm_memnum = dom.info()[2]/1024/1000  # Kib转化成GB
    conn.close()
    if vm_status == 1:
        return ("active", vm_cpunum, vm_memnum)
    elif vm_status == 3:
        return ("paused", vm_cpunum, vm_memnum)
    elif vm_status == 5:
        return ("offline", vm_cpunum, vm_memnum)
    else:
        return ("unknown", vm_cpunum, vm_memnum)


def host_cpumem_num(host_ip):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    host_info = conn.getInfo()
    cpu_num = host_info[2]
    mem_num = host_info[1]/1000  # MB转化成GB
    conn.close()
    return (cpu_num, mem_num)


if __name__ == '__main__':
    hostlist_ip = ['21.254.249.137','21.254.249.145','21.254.249.146','21.254.249.147','21.254.249.158','21.254.251.9','30.207.36.132','30.207.36.20','30.207.36.68','30.207.40.151','30.207.40.152','30.207.40.163','30.207.40.165','30.207.40.23','30.207.40.25','30.207.40.34','30.207.40.39','30.207.40.55','30.207.40.56','30.207.40.58','30.207.56.115','30.207.56.51','30.207.56.99','30.207.39.18']
    # hostlist_ip = ['30.207.39.18']
    for hostip in hostlist_ip:
        host, created =HostMachine.objects.get_or_create(host_ip = hostip)
        host_infoget = host_cpumem_num(hostip)
        host.cpu_max = host_infoget[0]
        host.mem_max = host_infoget[1]
        vm_list = vmlist_get(hostip)
        cpu_sum = 0
        mem_sum = 0
        for vmid in vm_list:
            domain_list = domain_info(hostip, vmid)
            obj, created = VirtMachine.objects.update_or_create(vm_id = vmid, host_machine = host)
            obj.vm_status = domain_list[0]
            obj.cpu_num = domain_list[1]
            obj.mem_num = domain_list[2]
            cpu_sum += domain_list[1]
            mem_sum += domain_list[2]
            obj.save()
        host.cpu_used = cpu_sum
        host.mem_used = mem_sum
        host.cpu_remain = host.cpu_max - cpu_sum
        host.mem_remain = host.mem_max - mem_sum
        print host.cpu_remain
        host.save()

