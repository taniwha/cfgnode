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

def warning(file, line, message):
    print("%s:%d: warning: %s" % (file, line, message))

def checknode(file, node, level=0):
    for subnode in node.nodes:
        name = subnode[0]
        line = subnode[2]
        if name[0] in "@%-!+$":
            brace = 0
            for c in name:
                if c == '[':
                    brace += 1
                elif c == ']':
                    brace -= 1
            if brace:
                warning(file, line, "unbalanced [] brackets: " + name)
        elif "[" in name or "]" in name:
            warning(file, line, "name specifier in node with no MM command: " + name)
        else:
            pass
        checknode(file, subnode[1], level + 1)

for arg in sys.argv[1:]:
    text = open(arg, "rt").read()
    try:
        cfg = ConfigNode.load(text)
    except ConfigNodeError, e:
        print(arg+e.message)
        continue
    checknode(arg, cfg)
