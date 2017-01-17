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

tank_masses = {
    "Default":0.000625,
    "Fuselage":0.000625,
    "RCS":0.0006,
    "Xenon":0.000072,
    "unknown":0.000625,
}
basemass_override = {
    "liquidEngine303":"-1",
    "liquidEngine303_Boattail":"-1",
    "liquidEngine909":"-1",
    "liquidEngine909_Boattail":"-1",
}
utilizations = {
    "LiquidFuel":1.0,
    "Oxidizer":1.0,
    "SolidFuel":1.0,
    "MonoPropellant":1.0,
    "XenonGas":1.0,#56.0, Xenon tank type has a utilization of 1.0, other 56.0
    "ElectricCharge":60.0,
    "IntakeAir":0.0,
    "EVA Propellant":0.0,
}
resource_blacklist = {
    "Ablator",
    "IntakeAir",
    "Ore",
}
part_blacklist = {
    "Mark1-2Pod",
    "cupola",
    "Mark1Cockpit",
    "Mark2Cockpit",
    "landerCabinSmall",
    "mk1pod",
    "mk2Cockpit_Inline",
    "mk2Cockpit_Standard",
    "mk2DroneCore",
    "mk2LanderCabin",
    "mk3Cockpit_Shuttle",
    "probeCoreCube",
    "probeCoreHex",
    "probeCoreOcto",
    "probeCoreOcto2",
    "roverBody",
    "probeStackLarge",
    "probeStackSmall",
    "probeCoreSphere",
    "batteryPack",
    "batteryBank",
    "batteryBankMini",
    "ksp_r_largeBatteryPack",
    "batteryBankLarge",
    "MassiveBooster",
    "solidBooster1-1",
    "solidBooster",
    "solidBooster_sm",
    "sepMotor1",
    "FuelCell",
    "FuelCellArray",
    "LaunchEscapeSystem",
    "mk2DockingPort",

    "mk1podNew",
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
        pmass = float(node.GetValue("mass"))
        volume = 0.0
        resmass = 0.0
        pres = set()
        for rn in resnodes:
            rname = rn.GetValue("name")
            if rname in resource_blacklist:
                continue
            pres.add(rname)
            maxAmount = float(rn.GetValue("maxAmount"))
            resmass += maxAmount * float(resources[rname].GetValue("density"))
            ut = utilizations[rname]
            #print("//", rname, maxAmount, ut)
            if ut > 0:
                volume += maxAmount / ut
        if volume <= 0:
            #print("---")
            continue
        if pname in part_blacklist:
            continue
        if "LiquidFuel" in pres and "Oxidizer" in pres:
            tank_type = "Default"
        elif "LiquidFuel" in pres:
            tank_type = "Fuselage"
        elif "MonoPropellant" in pres:
            tank_type = "RCS"
        elif "XenonGas" in pres:
            tank_type = "Xenon"
        else:
            continue

        apart = ConfigNode()
        module = apart.AddNode("MODULE")
        module.AddValue("name", "ModuleFuelTanks")
        module.AddValue("volume", "%g" % volume)
        module.AddValue("type", tank_type)
        if pname in basemass_override:
            module.AddValue("basemass", basemass_override[pname])
        else:
            tm = tank_masses[tank_type]
            bm = pmass / volume
            if ("%g" % tm) != ("%g" % bm):
                module.AddValue("basemass", "volume * %g" % bm)
        print("@PART[%s] %s" % (pname, apart.ToString()))

recurse_tree("/home/bill/ksp/KSP_linux/GameData", find_resources)
gamedata = sys.argv[1]
recurse_tree(gamedata, find_parts)
