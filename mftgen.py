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

utilizations = {
    "LiquidFuel":1.0,
    "Oxidizer":1.0,
    "SolidFuel":1.0,
    "MonoPropellant":1.0,
    "XenonGas":56.0,
    "ElectricCharge":60.0,
    "IntakeAir":0.0,
    "EVA Propellant":0.0,
}
def find_parts(path):
    if path[-4:].lower() != ".cfg":
        return
    text = open(path, "rt").read()
    try:
        cfg = ConfigNode.load(text)
    except ConfigNodeError as e:
        #print(path+e.message)
        return
    for n in cfg.nodes:
        name, node, line = n
        if name != "PART":
            continue
        pname = node.GetValue("name")
        resnodes = node.GetNodes("RESOURCE")
        if not resnodes:
            continue
        volume = 0.0
        for rn in resnodes:
            rname = rn.GetValue("name")
            maxAmount = float(rn.GetValue("maxAmount"))
            ut = utilizations[rname]
            print("//", rname, maxAmount, ut)
            if ut > 0:
                volume += maxAmount / ut
        if volume > 0:
            apart = ConfigNode()
            module = apart.AddNode("MODULE")
            module.AddValue("name", "ModuleFuelTanks")
            module.AddValue("volume", "%g" % volume)
            module.AddValue("type", "default")
            print("@PART[%s] %s" % (pname, apart.ToString()))

gamedata = sys.argv[1]
recurse_tree(gamedata, find_parts)
