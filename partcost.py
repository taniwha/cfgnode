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
from kspdata import *
from pprint import *
import sys
import os

def find_parts(path):
    if path[-4:].lower() != ".cfg":
        return
    text = open(path, "rt").read()
    try:
        cfg = ConfigNode.load(text)
    except ConfigNodeError as e:
        #print(path+e.message)
        return
    lineoffs = 0
    for n in cfg.nodes:
        name, node, line = n
        if name != "PART":
            continue
        mass = node.GetValue("mass");
        cost = node.GetValue("cost");
        costLine = node.GetValueLine("cost");
        ecost = node.GetValue("entryCost")
        newcost = float(mass) * parts_cost
        rescost = get_resource_cost(node.GetNodes("RESOURCE"))
        #rescost = 0
        #print ("%s c %s m %s c/m %f %s %g %g" % (node.GetValue("name"), cost, mass, float(cost)/float(mass), ecost, newcost, rescost))
        print (r"sed -i -e '%ds/\<cost\>\s*=\s*%s\>/cost = %g\r\n\tTechRequired = specializedConstruction\r\n\tentryCost = 2000/' '%s'" % (costLine + lineoffs, cost, newcost + rescost, path))
        lineoffs += 2

recurse_tree("/home/bill/ksp/KSP_linux/GameData", find_resources)
#pprint(resources)
parts_cost = 1.2 * float(resources["RocketParts"].GetValue("unitCost")) / float(resources["RocketParts"].GetValue("density"))
#print(parts_cost)
recurse_tree("/home/bill/ksp/KSP_linux/GameData/HexCans", find_parts)
