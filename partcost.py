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

markup = {
    "tank": 1.2,
    "welded tank": 1.4,
    "structural": 1.1,
    "workshop": 25,
    "pad": 2.5,
    "smelter": 20,
    "science": 44,
    "auger": 1.5,
    "detector": 12.8,
}

part_type={
    "TAL.Large.HalfSpherical.Tank.Fuel":"tank",
    "TAL.Large.HalfSpherical.Tank.V2.Fuel":"tank",
    "TAL.Large.Spherical.Tank.Fuel":"tank",
    "TAL.Large.Spherical.Tank.V2.Fuel":"tank",
    "TAL.Medium.HalfSpherical.Tank.Fuel":"tank",
    "TAL.Medium.HalfSpherical.Tank.V2.Fuel":"tank",
    "TAL.Medium.Spherical.Tank.Fuel":"tank",
    "TAL.Medium.Spherical.Tank.V2.Fuel":"tank",
    "TAL.Small.HalfSpherical.Tank.Fuel":"tank",
    "TAL.Small.HalfSpherical.Tank.V2.Fuel":"tank",
    "TAL.Small.Spherical.Tank.Fuel":"tank",
    "TAL.Small.Spherical.Tank.V2.Fuel":"tank",
    "TAL.Toroidal.Tank.Large.Fuel":"tank",
    "TAL.Toroidal.Tank.Medium.Fuel":"tank",
    "TAL.Toroidal.Tank.Small.Fuel":"tank",
    "TAL.XLarge.Toroidal.Tank.Fuel":"tank",
    "TAL_Toroidal_Tank_Hub_Large":"tank",
    "TAL_Toroidal_Tank_Hub_Medium":"tank",
    "TAL_Toroidal_Tank_Hub_Small":"tank",
    "TAL_Toroidal_Tank_Hub_XLarge":"tank",
    "TAL.Radial.Experiment.Storage.Container":"science",
    "TAL.Cubic.Truss.Mini.0.5m":"structural",
    "TAL.Cubic.Truss.Mini.1.5m":"structural",
    "TAL.Cubic.Truss.Mini.5m":"structural",
    "TAL.Cubic.Truss.Mini.1m":"structural",
    "TAL.Cubic.Truss.Mini.2.5m":"structural",
    "TAL.Cubic.Truss.Mini.Adapter.Large":"structural",
    "TAL.Cubic.Truss.Mini.Adapter.Long":"structural",
    "TAL.Cubic.Truss.Mini.Adapter.Short":"structural",
    "TAL.Cubic.Truss.Mini.Half":"structural",
    "TAL.Cubic.Truss.Mini.Hub":"structural",
    "TAL.Cubic.Truss.10m":"structural",
    "TAL.Cubic.Truss.1m":"structural",
    "TAL.Cubic.Truss.2m":"structural",
    "TAL.Cubic.Truss.3m":"structural",
    "TAL.Cubic.Truss.5m":"structural",
    "TAL.Cubic.Truss.Adapter.Large":"structural",
    "TAL.Cubic.Truss.Adapter.Long":"structural",
    "TAL.Cubic.Truss.Adapter.Short":"structural",
    "TAL.Cubic.Truss.Half":"structural",
    "TAL.Cubic.Truss.Hub":"structural",
    "TAL.Extended.Radial.Mount.Large":"structural",
    "TAL.Extended.Radial.Mount.Medium":"structural",
    "TAL.Extended.Radial.Mount.Small":"structural",
    "TAL.Flush.Radial.Mount.Large":"structural",
    "TAL.Flush.Radial.Mount.Medium":"structural",
    "TAL.Flush.Radial.Mount.Small":"structural",
    "Auger":"auger",
    "SmallAuger":"auger",
    "TinyAuger":"auger",
    "HexCanMetalHuge":"tank",
    "HexCanMetalLarge":"tank",
    "HexCanMetal":"tank",
    "HexCanMetalSmall":"tank",
    "HexCanOreHuge":"tank",
    "HexCanOreLarge":"tank",
    "HexCanOre":"tank",
    "HexCanOreSmall":"tank",
    "HexCanRocketPartsHuge":"tank",
    "HexCanRocketPartsLarge":"tank",
    "HexCanRocketParts":"tank",
    "HexCanRocketPartsSmall":"tank",
    "RocketpartsHuge7x":"welded tank",
    "RocketpartsLarge7x":"welded tank",
    "Rocketparts7x":"welded tank",
    "RocketpartsSmall7x":"welded tank",
    "Magnetometer":"detector",
    "OMD":"detector",
    "ExOrbitalDock":"pad",
    "ExSurveyStake":"structural",
    "ExWorkshop":"workshop",
    "ELTankLargeMTL":"tank",
    "ELTankLargeORE":"tank",
    "ELTankLargeRP":"tank",
    "ELTankMedMTL":"tank",
    "ELTankMedORE":"tank",
    "ELTankMedRP":"tank",
    "ELTankSmlMTL":"tank",
    "ELTankSmlORE":"tank",
    "ELTankSmlRP":"tank",
    "exLaunchPad":"workshop",
    "exLaunchPad2":"workshop",
    "RocketBuilder":"workshop",
    "exRunway":"pad",
    "Smelter":"smelter",
    "SmallSmelter":"smelter",
    "TinySmelter":"smelter",
    "adapter3m1m7":"structural",
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
    lineoffs = 0
    for n in cfg.nodes:
        name, node, line = n
        if name != "PART":
            continue
        pname = node.GetValue("name").strip()
        mass = node.GetValue("mass").strip()
        cost = node.GetValue("cost").strip()
        costLine = node.GetValueLine("cost")
        ecost = node.GetValue("entryCost").strip()
        newcost = float(mass) * markup[part_type[pname]] * rp_cost
        rescost = get_resource_cost(node.GetNodes("RESOURCE"))
        #rescost = 0
        c = float(cost)
        m = float(mass)
        #print ("%s c %s m %s c/m %f e %s n %g r %g n + r %g (c-r)/m %g %g" % (pname, cost, mass, c / m, ecost, newcost, rescost, newcost + rescost, (c - rescost) / m, (c - rescost) / m / rp_cost))
        #print (r"sed -i -e '%ds/\<cost\>\s*=\s*%s\>/cost = %g\r\n\tTechRequired = specializedConstruction\r\n\tentryCost = 2000/' '%s'" % (costLine + lineoffs, cost, newcost + rescost, path))
        print (r"sed -i -e '%ds/\<cost\>\s*=\s*%s\>.*/cost = %g/' '%s'" % (costLine + lineoffs, cost, newcost + rescost, path))
        lineoffs += 2

recurse_tree("/home/bill/ksp/KSP_linux/GameData", find_resources)
#pprint(resources)
rp_cost = float(resources["RocketParts"].GetValue("unitCost")) / float(resources["RocketParts"].GetValue("density"))
#print(parts_cost)
recurse_tree("/home/bill/ksp/KSP_linux/GameData/ModsByTal", find_parts)
recurse_tree("/home/bill/ksp/src/Extraplanetary-Launchpads/GameData/ExtraplanetaryLaunchpads", find_parts)
recurse_tree("/home/bill/ksp/KSP_linux/GameData/mystuff", find_parts)
