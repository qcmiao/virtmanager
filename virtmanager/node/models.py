# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from common.models import BaseModel

# Create your models here.

class HostMachine(BaseModel):
    host_ip = models.CharField(max_length=40)
    host_ipmiip = models.CharField(max_length=40, null=True)
    host_name = models.CharField(max_length=40, null=True)
    host_sn = models.CharField(max_length=40, null=True)
    host_brand = models.CharField(max_length=40, null=True)
    host_pid = models.CharField(max_length=40, null=True)
    address = models.CharField(max_length=40, null=True)
    cpu_max = models.CharField(max_length=40, null=True)
    cpu_used = models.CharField(max_length=40, null=True)
    cpu_remain = models.CharField(max_length=40, null=True)
    mem_max = models.CharField(max_length=40, null=True)
    mem_used = models.CharField(max_length=40, null=True)
    mem_remain = models.CharField(max_length=40, null=True)
    pool_capacity = models.CharField(max_length=40, null=True)
    pool_allocation = models.CharField(max_length=40, null=True)
    pool_available = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=200, null=True)


class VirtMachine(BaseModel):
    int_ip = models.CharField(max_length=40, null=True)
    ext_ip = models.CharField(max_length=40, null=True)
    vm_id = models.CharField(max_length=40)
    vm_status = models.CharField(max_length=40, null=True)
    cpu_num = models.CharField(max_length=40, null=True)
    mem_num = models.CharField(max_length=40, null=True)
    vm_system = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=200, null=True)
    host_machine = models.ForeignKey('HostMachine')


class Switch(BaseModel):
    switch_name = models.CharField(max_length=40, null=True)
    switch_ip = models.CharField(max_length=40, null=True)
    swich_address = models.CharField(max_length=40, null=True)


class SwitchPort(BaseModel):
    switch = models.ForeignKey('Switch')
    switch_port = models.CharField(max_length=40, null=True)
    port_purpose = models.CharField(max_length=40, null=True)


class HostNet(BaseModel):
    host_machine = models.ForeignKey('HostMachine')
    iface_switch_port = models.ForeignKey('SwitchPort', null=True)
    iface_name = models.CharField(max_length=40, null=True)
    iface_mac = models.CharField(max_length=40, null=True)
    iface_ip = models.CharField(max_length=40, null=True)
    iface_prefix = models.CharField(max_length=40, null=True)
    iface_gw = models.CharField(max_length=40, null=True)
    iface_purpose = models.CharField(max_length=40, null=True)
    iface_switch_name = models.CharField(max_length=40, null=True)


class BridgeNet(BaseModel):
    host_net = models.ForeignKey('HostNet')
    bridge_name = models.CharField(max_length=40, null=True)


class VmNet(BaseModel):
    virt_machine = models.ForeignKey('VirtMachine')
    bridge_net = models.ForeignKey('BridgeNet', null=True)
    net_name= models.CharField(max_length=40, null=True)
    vnet_name = models.CharField(max_length=40, null=True)
    bridge_name = models.CharField(max_length=40, null=True)
    net_mac = models.CharField(max_length=40, null=True)
    net_ip = models.CharField(max_length=40, null=True)
    net_prefix = models.CharField(max_length=40, null=True)
    net_purpose = models.CharField(max_length=40, null=True)


