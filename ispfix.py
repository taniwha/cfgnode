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

def uses_intakeair(engine):
    propellants = engine.GetNodes("PROPELLANT")
    for p in propellants:
        if p.GetValue("name") == "IntakeAir":
            return True
    return False

def engine_modules(node):
    modules = node.GetNodes("MODULE")
    em = []
    for m in modules:
        if m.GetValue("name") not in "ModuleEnginesFX":
            continue
        if uses_intakeair(m):
            continue
        em.append (m)
    return em

engine_blacklist = {
    "ionEngine",        #no change
    "radialEngineMini",
    "nuclearEngine",
    "sepMotor1",        #improved in 1.0
    "microEngine",
    "solidBooster_sm",  #new engine
}
engine_isp = {}

def collect_isps(path):
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
        engines = engine_modules (node)
        if not engines:
            continue
        for e in engines:
            atmCrv = e.GetNode ("atmosphereCurve")
            keys = atmCrv.GetValues("key")
            isp = keys[0].split(" ")[1]
            engine_isp[node.GetValue("name")] = isp

def find_engines(path):
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
        engines = engine_modules (node)
        if not engines:
            continue
        pname = node.GetValue("name")
        if pname in engine_blacklist:
            continue
        print("@PART[%s] {" % pname)
        for e in engines:
            print("\t@MODULE[%s]:HAS[!PROPELLANT[IntakeAir]] {" % e.GetValue("name"))
            atmCrv = e.GetNode ("atmosphereCurve")
            keys = atmCrv.GetValues("key")
            visp = keys[0].split(" ")[1]
            aisp = keys[1].split(" ")[1]
            aisp = float(aisp)*float(engine_isp[pname])/float(visp)
            print("\t\t@atmosphereCurve:HAS[#key[0?%s]] {" % visp)
            print("\t\t\t@key,0 = 0 %s" % engine_isp[pname])
            print("\t\t\t@key,1 = 1 %g" % aisp)
            print("\t\t}")
            print("\t}")
        print("}")

recurse_tree("/home/bill/ksp/KSP_linux-0.90/GameData/Squad", collect_isps)
recurse_tree("/home/bill/ksp/KSP_linux-0.90/GameData/NASAmission", collect_isps)
recurse_tree("/home/bill/ksp/KSP_linux/GameData/Squad", find_engines)
