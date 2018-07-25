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
    for n in range(0,vmnum):
        vmname = conn.listAllDomains()[n].name()
        vmname_list.append(vmname)
    return vmname_list

# vmstate dom.info()[0]  (==1 runing)  (==3  paused)   (==5  shutdown)
def domain_state(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    dom = conn.lookupByName(vm_id)
    vm_status = dom.state()[0]
    if vm_status == 1:
        return "online"
    elif vm_status == 3:
        return "paused"
    elif vm_status == 5:
        return "offline"
    else:
        return "unknown"

if __name__ == '__main__':
    hostlist_ip = ['21.254.249.137','21.254.249.145','21.254.249.146','21.254.249.147','21.254.249.158','21.254.251.9','30.207.36.132','30.207.36.20','30.207.36.68','30.207.40.151','30.207.40.152','30.207.40.163','30.207.40.165','30.207.40.23','30.207.40.25','30.207.40.34','30.207.40.39','30.207.40.55','30.207.40.56','30.207.40.58','30.207.56.115','30.207.56.51','30.207.56.99']

    for hostip in hostlist_ip:
        h=HostMachine.objects.get_or_create(host_ip = hostip)
        for vmid in vmlist_get(hostip):
            vmstatus = domain_state(hostip, vmid)
            obj, created = VirtMachine.objects.update_or_create(vm_id = vmid, host_machine=h[0])
            obj.vm_status = vmstatus
            obj.save()
