#!/usr/bin/python
#coding=utf-8
import libvirt
import os
import sys
import django
import threading
import multiprocessing
import paramiko
from xml.etree import ElementTree as ET
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "."))
os.environ['DJANGO_SETTINGS_MODULE'] = 'virtmanager.settings'
django.setup()
from node.models import VirtMachine, HostMachine, HostNet, BridgeNet, VmNet, Switch, SwitchPort


class SSHConnection:
    def __init__(self, host_ip):
        self.host_ip = host_ip
        self._connect()

    def _connect(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.host_ip, timeout=5)
        self.ssh_client = ssh_client

    def exec_command(self, command):
        if self.ssh_client is None:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=self.host_ip, timeout=5)
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
        ipmi_ip_get = "ipmitool lan print |grep  -w 'IP Address'|tail -n1|awk {'print $NF'}"
        ipmi_ip = self.exec_command(ipmi_ip_get)
        return ipmi_ip

    def get_sn(self):
        sn_get = "dmidecode -t system|grep 'Serial Number:'|awk {'print $3'}"
        sn = self.exec_command(sn_get)
        return sn

    def get_brand(self):
        brand_get = "dmidecode -t system|grep 'Manufacturer:'|awk {'print $2'}"
        brand = self.exec_command(brand_get)
        return brand

    def get_host_pid(self):
        host_pid_get = "dmidecode -t system|grep 'Product Name:'|awk {'print $3'}"
        host_pid = self.exec_command(host_pid_get)
        return host_pid


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

    def get_hostname(self):
        hostname = self.conn.getHostname()
        return hostname

    def get_address(self):
        address_temp = self.get_hostname()[:-3]
        address_dic = {
            "bj-gt": "北京-工体",
            "sh-gq": "上海-桂桥",
            "gz-hxy": "广州-华新园",
            "sz-sjhl": "深圳-世纪互联",
            "cd-zl": "成都-中立",
            "hz-zt": "杭州-转塘",
            "wh-yl": "武汉-银联",
            "tj-tf": "天津-天纺"
        }
        try:
            host_address = address_dic[address_temp]
        except Exception, e:
            print e, "has no match address"
            host_address = ""
        return host_address

    def get_vm_list(self):
        vm_obj_list = self.conn.listAllDomains()
        vm_list = []
        vm_list = [i.name() for i in vm_obj_list]
        return vm_list

    def get_vm_info(self, vm_id):
        vm_info = self.conn.lookupByName(vm_id)
        vm_status = vm_info.state()[0]
        vm_cpu_info = vm_info.info()[3]
        vm_mem_info = vm_info.info()[2]/1024/1000
        vm_xml = vm_info.XMLDesc(0)
        xe = ET.fromstring(vm_xml)
        try:
            vm_net_info = vm_info.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        except:
            print vm_id, 'no agent'
            vm_net_info = {}
            pass
        return {'vm_status': vm_status,
                'vm_cpu_info': vm_cpu_info,
                'vm_mem_info': vm_mem_info,
                'vm_xe': xe,
                'vm_net_info': vm_net_info
        }

    def get_host_info(self):
        host_info = self.conn.getInfo()
        host_cpu_info = host_info[2]
        host_mem_info = host_info[1]/1000
        return {
                'host_cpu_info': host_cpu_info,
                'host_mem_info': host_mem_info
        }



    def get_pool_info(self, poolname='vmdata'):
        try:
            pool_list =self.conn.listStoragePools()
            if poolname in pool_list:
                pool = self.conn.storagePoolLookupByName(poolname)
                pool_info = pool.info()
                pool_capacity = pool_info[1]/1024**3
                pool_allocation = pool_info[2]/1024**3
                pool_available = pool_info[3]/1024**3
            else:
                print "storage info get error: 'no poolname is {}'".format(poolname)
                pool_capacity = ""
                pool_allocation = ""
                pool_available = ""
        except Exception, e:
            print e
        return {
            'pool_capacity': pool_capacity,
            'pool_allocation': pool_allocation,
            'pool_available': pool_available
        }

    def get_host_iface(self):
        host_iface_obj_list = self.conn.listAllInterfaces()
        host_iface_list = []
        host_iface_list = [i.name() for i in host_iface_obj_list if i.name() != 'lo']
        return host_iface_list

    def get_hostiface_info(self, iface_name):
        hostiface_info = self.conn.interfaceLookupByName(iface_name)
        hostiface_mac = hostiface_info.MACString()
        hostiface_xml = hostiface_info.XMLDesc(0)
        return {
                "hostiface_mac": hostiface_mac,
                "hostiface_xml": hostiface_xml
        }

    def close(self):
        self.conn.close()


lock = multiprocessing.Lock()


def update_vm_info(host):
    lock.acquire()
    try:
        host_ip = host.host_ip
        ssh_client = SSHConnection(host_ip)
        host.host_ipmiip = ssh_client.get_ipmi_ip()
        host.host_sn = ssh_client.get_sn()
        host.host_brand = ssh_client.get_brand()
        host.host_pid = ssh_client.get_host_pid()
        lib_client = LibvirtClient(host_ip)
        hostnet_list = lib_client.get_host_iface()
        bri_mac_list = []
        for iface_name in hostnet_list:
            iface_obj, created = HostNet.objects.get_or_create(iface_name=iface_name, host_machine=host)
            hostiface_info = lib_client.get_hostiface_info(iface_name)
            iface_obj.iface_mac = hostiface_info['hostiface_mac']
            bridge_obj, created = BridgeNet.objects.get_or_create(bridge_name=iface_name, host_net=iface_obj)
            bri_mac_list.append((iface_name, iface_obj.iface_mac))
        bri_mac_dic = {bridge: mac for (bridge, mac) in bri_mac_list}
        iface_obj.save()
        bridge_obj.save()

        vm_list = lib_client.get_vm_list()
        cpu_sum = 0
        mem_sum = 0
        for vm_id in vm_list:
            vm_obj, created = VirtMachine.objects.get_or_create(vm_id=vm_id, host_machine=host)
            vm_info = lib_client.get_vm_info(vm_id)
            vm_obj.vm_status = vm_info['vm_status']
            vm_obj.cpu_num = vm_info['vm_cpu_info']
            vm_obj.mem_num = vm_info['vm_mem_info']
            cpu_sum += vm_info['vm_cpu_info']
            mem_sum += vm_info['vm_mem_info']

            vm_net_obj = vm_info['vm_net_info']
            vm_iface_name_list = []
            vm_iface_mac_list = []
            vm_iface_ip_list = []
            vm_iface_prefix_list = []
            for vm_iface_name, vm_iface_info in vm_net_obj.items():
                if vm_iface_name != "lo":
                    vm_iface_name_list.append(vm_iface_name)
                    vm_iface_mac_list.append(vm_iface_info['hwaddr'])
                    vm_iface_ip_list.append(vm_iface_info['addrs'][0]['addr'])
                    vm_iface_prefix_list.append(vm_iface_info['addrs'][0]['prefix'])
                else:
                    pass
            vm_xe =vm_info['vm_xe']
            for vnet_xml in vm_xe.findall('.//devices/interface'):
                try:
                    vnet_name = vnet_xml.find('target').get('dev')
                except:
                    vnet_name = 'unknown'
                finally:
                    vnet_mac = vnet_xml.find('mac').get('address')
                    bridge_name = vnet_xml.find('source').get('bridge')
                    vnet_obj, created = VmNet.objects.get_or_create(net_mac=vnet_mac, virt_machine=vm_obj)
                    vnet_obj.vnet_name = vnet_name
                    vnet_obj.host_net = iface_obj
                    vnet_obj.bridge_name = bridge_name
                    if bridge_name in bri_mac_dic.keys():
                        vnet_obj.bridge_mac = bri_mac_dic[bridge_name]
                    else:
                        pass
                    if vnet_mac in vm_iface_mac_list:
                        ip_index = vm_iface_mac_list.index(vnet_mac)
                        vnet_obj.net_ip = vm_iface_ip_list[ip_index]
                        vnet_obj.net_name = vm_iface_name_list[ip_index]
                        vnet_obj.net_prefix = vm_iface_prefix_list[ip_index]
                    vnet_obj.save()
            vm_obj.save()
        host_info = lib_client.get_host_info()
        host.cpu_max = host_info['host_cpu_info']
        host.mem_max = host_info['host_mem_info']
        host.cpu_used = cpu_sum
        host.mem_used = mem_sum
        host.cpu_remain = host_info['host_cpu_info'] - cpu_sum
        host.mem_remain = host_info['host_mem_info'] - mem_sum
        host.host_name = lib_client.get_hostname()
        host.address = lib_client.get_address()
        pool_info = lib_client.get_pool_info()
        host.pool_capacity = pool_info['pool_capacity']
        host.pool_allocation = pool_info['pool_allocation']
        host.pool_available = pool_info['pool_available']
        host.save()
        lib_client.close()
        print host_ip
        print 'ok'
        print '####result######'
    except:
        host.save()
        print host_ip
        print 'error'
        print '####result######'

    lock.release()


if __name__ == '__main__':
    host_list = HostMachine.objects.all()
    # host_list = HostMachine.objects.filter(host_ip='30.207.40.25')
    pools = multiprocessing.Pool(4)
    for h in host_list:
        pools.apply_async(update_vm_info, (h,))
    pools.close()
    pools.join()



