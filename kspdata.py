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
from pprint import *
import sys
import os

resources = {}


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

def find_resources(path):
    if path[-4:].lower() != ".cfg":
        return
    bytes = open(path, "rb").read()
    text = "".join(map(lambda b: chr(b), bytes))
    try:
        cfg = ConfigNode.load(text)
    except ConfigNodeError as e:
        #print(path+e.message)
        return
    for node in cfg.nodes:
        if node[0] == "RESOURCE_DEFINITION":
            res = node[1]
            resname = res.GetValue("name")
            resources[resname] = res
                
def get_resource_cost(nodes):
    cost = 0.0
    for resnode in nodes:
        name = resnode.GetValue("name")
        amount = resnode.GetValue("amount")
        maxAmount = resnode.GetValue("maxAmount")
        rescost = resources[name].GetValue("unitCost")
        if rescost == None:
            rescost = 0
        cost += float(maxAmount) * float(rescost)
    return cost
