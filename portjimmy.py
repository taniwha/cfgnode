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

def check_ports(vessel):
    parts = vessel.GetNodes('PART')
    part_map = make_part_map(parts)
    count = 0
    for p in parts:
        port = find_module(p, "ModuleDockingNode")
        if not port:
            continue
        if port.GetValue('dockUId') not in part_map:
            continue
        if 'Docked' in port.GetValue('state'):
            continue
        other_part = part_map[port.GetValue('dockUId')]
        other_port = find_module(other_part, "ModuleDockingNode")
        if other_port.GetValue('dockUId') != p.GetValue('uid'):
            continue
        if parts.index(other_part) != int(p.GetValue('parent')):
            continue
        events = port.GetNode('EVENTS')
        undock = events.GetNode('Undock')
        print(p.GetValue('uid'), port.GetValue('state'), port.GetValue('dockUId'))
        count+=1
    return count

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
    for v in vessels:
        if check_ports(v):
            print(v.GetValue("name"), v.GetValue("type"))
    sys.exit(0)
