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

from cfgnode import ConfigNode
import sys

def find_module(part, name):
    modules = part.GetNodes('MODULE')
    for m in modules:
        if m.GetValue('name') == name:
            return m
    return None

def make_part_map(parts):
    map = {}
    for p in parts:
        map[p.GetValue('uid')] = p
    return map

def check_resources(vessel, resource_set):
    parts = vessel.GetNodes('PART')
    part_map = make_part_map(parts)
    count = 0
    for p in parts:
        resources = p.GetNodes('RESOURCE')
        for res in resources:
            resname = res.GetValue('name')
            resource_set.add(resname.strip())

for arg in sys.argv[1:]:
    text = open(arg, "rt").read()
    node = ConfigNode.load(text)
    game = node.GetNode('GAME')
    if not game:
        print("could not find GAME")
        sys.exit(1)
    flightstate = game.GetNode("FLIGHTSTATE")
    if not flightstate:
        print("could not find FLIGHTSTATE")
        sys.exit(1)
    vessels = flightstate.GetNodes("VESSEL")
    resource_set = set()
    for v in vessels:
        check_resources(v, resource_set)
    print(resource_set)
    sys.exit(0)
