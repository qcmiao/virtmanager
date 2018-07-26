#!/usr/bin/env python
#coding=utf-8
import os
import libvirt
import sys

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


