#!/usr/bin/env python
#coding=utf-8
import os
import libvirt
import sys
import hashlib
from xml.etree import ElementTree as ET
import numpy
from node.models import VirtMachine

#dom.info()[0]==1 runing  ==3  paused   ==5  shutdown
def destroy_vm(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    dom = conn.lookupByName(vm_id)
    if dom.info()[0] == 1 or dom.info()[0] == 3:
        dom.destroy()
        conn.close()
    else:
        pass


def start_vm(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    dom = conn.lookupByName(vm_id)
    if dom.info()[0] == 5:
        dom.create()
        conn.close()
    else:
        pass


def reboot_vm(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    dom = conn.lookupByName(vm_id)
    if dom.info()[0] == 1:
        dom.reboot()
        conn.close()
    elif dom.info()[0] == 3:
        dom.destroy()
        dom.create()
        conn.close()
    elif dom.info()[0] == 5:
        dom.create()
        conn.close()
    else:
        pass


def suspend_vm(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    dom = conn.lookupByName(vm_id)
    if dom.info()[0] == 1:
       dom.suspend()
       conn.close()
    elif dom.info()[0] == 3:
       dom.resume()
       conn.close()
    else:
       pass

def vnc_vm(host_ip, vm_id):
    host_ssh = 'qemu+ssh://root@{}/system'.format(host_ip)
    conn = libvirt.open(host_ssh)
    vm_info = conn.lookupByName(vm_id)
    vm_xml = vm_info.XMLDesc(0)
    xe = ET.fromstring(vm_xml)
    vnc_port = xe.findall('.//devices/graphics')[0].get('port')
    token_str = hashlib.sha1(os.urandom(24)).hexdigest()
    token_line = '{}: {}:{}'.format(token_str, host_ip, vnc_port)
    tokenfile_name = '/watone/virtmanager/vmtokens/token.ini'.format(host_ip, vm_id)
    token_file = open(tokenfile_name, 'w')
    token_file.write(token_line)
    token_file.close()
    baseurl = 'http://172.16.42.77:8787/vnc.html?path=?token='
    fullurl = baseurl + token_str
    conn.close()
    return fullurl


if __name__ == '__main__':
    vnc_vm('30.207.39.18', 'mqc001')
