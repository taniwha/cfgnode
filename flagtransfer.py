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

src = sys.argv[1]
dst = sys.argv[2]
out = sys.argv[3]

src_text = open(src, "rt").read()
dst_text = open(dst, "rt").read()
src_node = ConfigNode.load(src_text)
src_game = src_node.GetNode('GAME')
dst_node = ConfigNode.load(dst_text)
dst_game = dst_node.GetNode('GAME')
if not src_game:
    print("could not find source GAME")
    sys.exit(1)
if not dst_game:
    print("could not find destination GAME")
    sys.exit(1)

src_flightstate = src_game.GetNode("FLIGHTSTATE")
if not src_flightstate:
    print("could not find source FLIGHTSTATE")
    sys.exit(1)
dst_flightstate = dst_game.GetNode("FLIGHTSTATE")
if not dst_flightstate:
    print("could not find destination FLIGHTSTATE")
    sys.exit(1)

vessels = src_flightstate.GetNodes("VESSEL")
for v in vessels:
    if v.GetValue("type") != "Flag":
        continue
    parts = v.GetNodes("PART")
    if len(parts) != 1:
        continue
    p = parts[0]
    if p.GetValue("name") != "flag":
        continue
    print (v.GetValue("name"))
    dst_flightstate.nodes.append(("VESSEL", v))

open(out, "wt").write("GAME " + dst_game.ToString ())
sys.exit(0)
