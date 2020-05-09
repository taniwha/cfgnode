# vim:ts=4:et
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from cfgnode import *
import sys
import os
from uuid import uuid4

def recurse_tree(path, func):
    files = os.listdir(path)
    files.sort()
    for f in files:
        if f[0] in [".", "_"]:
            continue
        p = os.path.join(path, f)
        if os.path.isdir(p):
            recurse_tree(p, func)
        else:
            func(p)

static_by_uuid = {}

def find_statics(path):
    if path[-4:].lower() != ".cfg":
        return
    node = ConfigNode.loadfile(path)
    for n in node.nodes:
        if n[0].split(':', 1)[0] != 'STATIC':
            continue
        static = n[1]
        pname = static.GetValue("pointername")
        instances = static.GetNodes("Instances")
        for inst in instances:
            group = inst.GetValue("Group")
            uuid = inst.GetValue("UUID")
            if uuid not in static_by_uuid:
                static_by_uuid[uuid] = []
            static_by_uuid[uuid].append((group, pname, path))

def genUUID():
    while True:
        uuid = uuid4().urn[9:]
        if uuid not in static_by_uuid:
            static_by_uuid[uuid] = None
            return uuid

files_to_fix = set()

recurse_tree(".", find_statics)
for u in static_by_uuid:
    s = static_by_uuid[u]
    if len(s) > 1:
        print(f"duplicate uuid {u} on:")
        for d in s:
            print("   ", d[0], d[1])
            files_to_fix.add(d[2])

while files_to_fix:
    path = files_to_fix.pop()
    node = ConfigNode.loadfile(path)
    of = open(path, "wt")
    for n in node.nodes:
        if n[0].split(':', 1)[0] != 'STATIC':
            continue
        static = n[1]
        pname = static.GetValue("pointername")
        instances = static.GetNodes("Instances")
        for inst in instances:
            group = inst.GetValue("Group")
            uuid = genUUID()
            print(inst.GetValue("UUID"), uuid)
            inst.SetValue("UUID", uuid)
        of.write(n[0] + " " + static.ToString())
    of.close()
