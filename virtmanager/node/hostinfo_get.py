#!/usr/bin/python
#coding=utf-8
import libvirt
import os
import sys
import django
import threading
import parmiko

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "."))
os.environ['DJANGO_SETTINGS_MODULE'] = 'virtmanager.settings'
django.setup()
from node.models import VirtMachine, HostMachine

class SSHConnection:
    def __init__(self, host_ip):
        self.host_ip = host_ip
        self._connect()

    def _connect(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.host_ip, timeout=10)
        self.ssh_client = ssh_client

    def exec_command(self, command):
        if self.ssh_client is None:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=self.host_ip, timeout=10)
            self.ssh_client = ssh_client
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        data = stdout.read()
        if len(data) > 0:
            return data.strip()

        err = stderr.read()
        if len(err) > 0:
            print err.strip()
            return data.strip()

        def get_ipmi_ip(self):
            yuminstall_cmd = 'yum install ipmitool -y'
            ipmi_ip_get = "ipmitool lan print |grep  -w 'IP Address'|tail -n1|awk {'print $NF'}"
            resp1 = self.exec_command(yuminstall_cmd)
            resp2 = self.exec_command(ipmi_ip_get)
            return resp2


class LibvirtClient:
    def __init__(self, host_ip):
        self.host_ip = host_ip
        self._connect()

    def _connect(self):
        try:
            host_ssh = 'qemu+ssh://root@{}/system'.format(self.host_ip)
            self.conn = libvirt.open(host_ssh)
        except Exception, e:
            print 'Connect failed' + e

    def get_vm_list(self):
        vm_obj_list = self.conn.listAllDomains()
        vm_list = []
        for vm in vm_obj_list:
            vm_name = vm.name()
            vm_list.append(vm_name)
        return vm_list

    def get_vm_info(self, vm_id):
        vm_info = self.conn.lookupByName(vm_id)
        vm_status = vm_info.state()[0]
        vm_cpu_info = vm_info.info()[3]
        vm_mem_info = vm_info.info()[2]/1024/1000
        return {'vm_status': vm_status, 'vm_cpu_info': vm_cpu_info, 'vm_mem_info': vm_mem_info}

    def get_host_info(self):
        host_info = self.conn.getInfo()
        host_cpu_info = host_info[2]
        host_mem_info = host_info[1]/1000
        return {'host_cpu_info': host_cpu_info, 'host_mem_info': host_mem_info}

    def close(self):
        self.conn.close()


lock = threading.Lock()


def update_vm_info(host_list):
    for host in host_list:
        try:
            lock.acquire()

            host_ip = host.host_ip
            lib_client = LibvirtClient(host_ip)
            ssh_client = SSHConnection(host_ip)
            vm_list = lib_client.get_vm_list()
            cpu_sum = 0
            mem_sum = 0
            for vm_id in vm_list:
                vm, created = VirtMachine.objects.get_or_create(vm_id=vm_id, host_machine=host)
                vm_info = lib_client.get_vm_info(vm_id)
                vm.vm_status = vm_info['vm_status']
                vm.cpu_num = vm_info['vm_cpu_info']
                vm.mem_num = vm_info['vm_mem_info']
                cpu_sum += vm_info['vm_cpu_info']
                mem_sum += vm_info['vm_mem_info']
                vm.save()

            host_info = lib_client.get_host_info()
            host.cpu_max = host_info['host_cpu_info']
            host.mem_max = host_info['host_mem_info']
            host.cpu_used = cpu_sum
            host.mem_used = mem_sum
            host.cpu_remain = host_info['host_cpu_info'] - cpu_sum
            host.mem_remain = host_info['host_mem_info'] - mem_sum
            host.host_ipmiip = ssh_client.get_ipmi_ip()
            host.save()

            lib_client.close()
            lock.release()
        except Exception, e:
            print e



if __name__ == '__main__':
    # hostlist_ip = ['21.254.249.137','21.254.249.145','21.254.249.146','21.254.249.147','21.254.249.158','21.254.251.9','30.207.36.132','30.207.36.20','30.207.36.68','30.207.40.151','30.207.40.152','30.207.40.163','30.207.40.165','30.207.40.23','30.207.40.25','30.207.40.34','30.207.40.39','30.207.40.55','30.207.40.56','30.207.40.58','30.207.56.115','30.207.56.51','30.207.56.99','30.207.39.18']
    # # hostlist_ip = ['30.207.39.18']
    # for hostip in hostlist_ip:
    #     host, created =HostMachine.objects.get_or_create(host_ip = hostip)
    #     host_infoget = host_cpumem_num(hostip)
    #     host.cpu_max = host_infoget[0]
    #     host.mem_max = host_infoget[1]
    #     vm_list = vmlist_get(hostip)
    #     cpu_sum = 0
    #     mem_sum = 0
    #     for vmid in vm_list:
    #         domain_list = domain_info(hostip, vmid)
    #         obj, created = VirtMachine.objects.update_or_create(vm_id = vmid, host_machine = host)
    #         obj.vm_status = domain_list[0]
    #         obj.cpu_num = domain_list[1]
    #         obj.mem_num = domain_list[2]
    #         cpu_sum += domain_list[1]
    #         mem_sum += domain_list[2]
    #         obj.save()
    #     host.cpu_used = cpu_sum
    #     host.mem_used = mem_sum
    #     host.cpu_remain = host.cpu_max - cpu_sum
    #     host.mem_remain = host.mem_max - mem_sum
    #     print host.cpu_remain
    #     host.save()
    # host_ip = '30.207.39.18'
    host_list = HostMachine.objects.all()
    thread_count = 10
    for i in xrange(thread_count):
        sum_hosts = host_list[i::thread_count]
        print sum_hosts
        if sum_hosts is not None:
            threading.Thread(target=update_vm_info, args=(sum_hosts, )).start()


