# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from common.models import BaseModel

# Create your models here.

class HostMachine(BaseModel):
    host_ip = models.CharField(max_length=40)
    address = models.CharField(max_length=40, null=True)
    cpu_max = models.CharField(max_length=40, null=True)
    cpu_used = models.CharField(max_length=40, null=True)
    cpu_remain = models.CharField(max_length=40, null=True)
    mem_max = models.CharField(max_length=40, null=True)
    mem_used = models.CharField(max_length=40, null=True)
    mem_remain = models.CharField(max_length=40, null=True)
    disk_max = models.CharField(max_length=40, null=True)
    disk_used = models.CharField(max_length=40, null=True)
    disk_remain = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=200, null=True)

class VirtMachine(BaseModel):
    int_ip = models.CharField(max_length=40, null=True)
    ext_ip = models.CharField(max_length=40, null=True)
    vm_id = models.CharField(max_length=40)
    vm_status = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=200, null=True)
    host_machine = models.ForeignKey('HostMachine')
