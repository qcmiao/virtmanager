#!/usr/bin/python
#coding=utf-8
import libvirt
import os
import sys
import django
import threading
import multiprocessing
import paramiko
import hashlib
from xml.etree import ElementTree as ET


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

	def get_vnc_port(self, vm_id):
		vm_info = self.conn.lookupByName(vm_id)
		vm_xml = vm_info.XMLDesc(0)
		xe = ET.fromstring(vm_xml)
		vnc_port = xe.findall('.//devices/graphics')[0].get('port')
		return vnc_port

	def create_token(self):
		pass

	def close(self):
		self.conn.close()


def create_vnc_token(host_ip, vm_id):
	lib_client = LibvirtClient(host_ip)
	vnc_port = lib_client.get_vnc_port(vm_id)
	token_str = hashlib.sha1(os.urandom(24)).hexdigest()
	token_line = '{}: {}:{}'.format(token_str, host_ip, vnc_port)
	tokenfile_name = '/watone/virtmanager/vmtokens/{}_{}.ini'.format(host_ip, vm_id)
	token_file = open(tokenfile_name, 'w')
	token_file.write(token_line)
	token_file.close()
	print token_line
	baseurl = 'http://172.16.42.77:8787/vnc.html?path=?token='
	fullurl = baseurl + token_str
	print fullurl
	novnc_cmd = '/root/noVNC/utils/websockify/websockify.py --web /root/noVNC --target-config={} 8787 &'.format(tokenfile_name)
	print novnc_cmd
	os.system(novnc_cmd)
	lib_client.close()


if __name__ == '__main__':
	create_vnc_token('30.207.39.18', 'mqc001')