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

import sys
import os
import getopt

from cfgnode import *
from kspdata import recurse_tree, find_resources, resources

shortopts = ''
longopts = [
    'gamedata=',
    'resources='
]
errors = False

def error(path, line, message):
    global errors
    errors = True
    print(f"{path}:{line}: {message}")

def warning(path, line, message):
    print(f"{path}:{line}: warning: {message}")

part_required_fields = (
    ("name", error, "Missing field 'name'"),
    ("module", error, "Missing field 'module'"),
    ("TechRequired", error, "Missing field 'TechRequired'"),
    ("entryCost", error, "Missing field 'entryCost'"),
    ("cost", error, "Missing field 'cost'"),
    ("category", error, "Missing field 'category'"),
    ("title", error, "Missing field 'title'"),
    ("mass", error, "Missing field 'mass'"),

    ("tags", warning, "Missing field 'tags'"),
    ("manufacturer", warning, "Missing field 'manufacturer'"),
    ("description", warning, "Missing field 'description'"),
    ("rescaleFactor", warning, "rescaleFactor defaults to 1.25"),
    ("attachRules", warning, "attachRules defaults to not allowing attachment"),
    ("dragModelType", warning, "dragModelType defaults to 'default' (cube)"),
    ("maximum_drag", warning, "maximum_drag defaults to 0.1"),
    ("minimum_drag", warning, "minimum_drag defaults to 0.1"),
    ("angularDrag", warning, "angularDrag defaults to 2"),
    ("crashTolerance", warning, "crashTolerance defaults to 9"),
    ("maxTemp", warning, "maxTemp defaults to 2000 (Kelvin)"),
    ("heatConductivity", warning, "heatConductivity defaults to 0.12"),
    ("skinInternalConductionMult", warning, "skinInternalConductionMult defaults to 1"),
    ("emissiveConstant", warning, "emissiveConstant defaults to 0.4"),
)

def check_name(name, value, path, line):
    pass

def discourage_mesh(name, value, path, line):
    warning(path, line, "the value of 'mesh' is ignored and the first (ascii-sort) .mu file in the directory is used. use MODEL {} instead")

def positive_nonzero_float(name, value, path, line):
    try:
        val = float(value)
    except ValueError:
        error(path, line, f"{name} not a valid float")
    else:
        if val <= 0:
            warning(path, line, f"{name} should be > 0")

def positive_int(name, value, path, line):
    try:
        val = int(value)
    except ValueError:
        error(path, line, f"{name} not a valid int")
    else:
        if val < 0:
            warning(path, line, f"{name} should be >= 0")

def positive_float(name, value, path, line):
    try:
        val = float(value)
    except ValueError:
        error(path, line, f"{name} not a valid float")
    else:
        if val < 0:
            warning(path, line, f"{name} should be >= 0")

def boolean(name, value, path, line):
    if value.upper() not in ['TRUE', 'FALSE']:
        error(path, line, f"{name} not a valid bool")

def vector(name, value, path, line):
    vals = value.split(",")
    if len(vals) != 3:
        error(path, line, f"{name} must be a vector: 3 comma-separated floats")
    for i, v in enumerate(vals):
        try:
            val = float(v)
        except ValueError:
            error(path, line, f"{name}[i] not a valid float")

def quaternion(name, value, path, line):
    vals = value.split(",")
    if len(vals) != 4:
        error(path, line, f"{name} must be a quaternion: 4 comma-separated floats")
    for i, v in enumerate(vals):
        try:
            val = float(v)
        except ValueError:
            error(path, line, f"{name}[i] not a valid float")

def check_attachRules(name, value, path, line):
    vals = value.split(",")
    if len(vals) < 5:
        error(path, line, f"{name} must have at least 5 comma-separated 0 or 1 values")
        return
    if len(vals) > 8:
        warning(path, line, f"only 8 values are significant for {name}")
        vals = vals[:8]
    for i, v in enumerate(vals):
        if v  not in ["1", "0"]:
            warning(path, line, f"{name}[{i}]: {v} not a valid flag (anything but 1 is treated as 0")

def ignored(name, value, path, line):
    warning(path, line, f"{name} is ignored")

def physics_significance(name, value, path, line):
    if value not in ['FULL', 'NONE']:
        if value in ['-1', '0', '1']:
            warning(path, line, f"{name} should be FULL or NONE, not a number")
        else:
            error(path, line, f"{value} not valid for {name}")

def enum(enum_values, case_insensitive=False):
    class enum_check:
        def __init__(self, values, case_insensitive):
            self.values = values
            self.case_insensitive = case_insensitive
        def check(self, name, value, path, line):
            val = value
            if self.case_insensitive:
                val = value.upper()
            if val not in self.values:
                error(path, line, f"{value} not valid for {name}")
    e = enum_check(enum_values, case_insensitive)
    return e.check

def check_node(name, value, path, line):
    keyData = name.split("_")
    nodeData = value.split(",")
    if keyData[1] in ["stack", "dock"]:
        if len(keyData) < 3:
            warning(path, line, f"no id given for {name}")
        if len(keyData) > 3:
            warning(path, line, f"excess tags ignored in {name}. should be only 2 _")
    elif keyData[1] == "attach":
        if len(keyData) > 2:
            warning(path, line, f"excess tags ignored in {name}. should be only 1 _")
    else:
        warning(path, line, f"{name} not a known node type in {name}")
    if len(nodeData) < 6:
        error(path, line, f"need at least 6 comma-separated floats for a valid node")
        return
    for i in range(6):
        try:
            val = float(nodeData[i])
        except:
            error(path, line, f"{name}[i] not a valid float")
    if len(nodeData) > 11:
        warning(path, line, f"excess items in {name} ignored (up to 12 values)")
    for i in range(6, len(nodeData)):
        try:
            val = int(nodeData[i])
        except:
            error(path, line, f"{name}[i] not a valid int")

module_enum = {
    'Part',
    'CompoundPart',
}

TechRequired_enum = {
    'Unresearcheable',  #sic
    'Unresearchable',   #fake
    'actuators',
    'advAerodynamics',
    'advConstruction',
    'advElectrics',
    'advExploration',
    'advFlightControl',
    'advFuelSystems',
    'advLanding',
    'advMetalworks',
    'advRocketry',
    'advScienceTech',
    'advUnmanned',
    'advancedMotors',
    'aerodynamicSystems',
    'aerospaceTech',
    'automation',
    'aviation',
    'basicRocketry',
    'basicScience',
    'commandModules',
    'composites',
    'electrics',
    'electronics',
    'engineering101',
    'experimentalAerodynamics',
    'experimentalElectrics',
    'experimentalMotors',
    'experimentalScience',
    'fieldScience',
    'flightControl',
    'fuelSystems',
    'generalConstruction',
    'generalRocketry',
    'heavierRocketry',
    'heavyAerodynamics',
    'heavyLanding',
    'heavyRocketry',
    'highAltitudeFlight',
    'highPerformanceFuelSystems',
    'hypersonicFlight',
    'ionPropulsion',
    'landing',
    'largeElectrics',
    'largeUnmanned',
    'largeVolumeContainment',
    'metaMaterials',
    'miniaturization',
    'nanolathing',
    'nuclearPropulsion',
    'precisionEngineering',
    'precisionPropulsion',
    'propulsionSystems',
    'scienceTech',
    'spaceExploration',
    'specializedConstruction',
    'specializedControl',
    'specializedElectrics',
    'stability',
    'start',
    'supersonicFlight',
    'survivability',
    'unmannedTech',
    'veryHeavyRocketry',
}

category_enum = {
    'Command',
    'Propulsion',
    'FuelTank',
    'Engine',
    'Aero',
    'Electrical',
    'Structural',
    'Utility',
    'Wheel',
    'Ground',
    'Thermal',
    'Coupling',
    'Payload',
    'Communication',
    'Science',
    'none',
    'Robotics', # BG only?
    'Cargo', # BG only?
    'Control',
    'Pods',
}

dragModelType_enum = {
    'SPHERICAL',
    'CYLINDRICAL',
    'CONIC',
    'OVERRIDE',
    'NONE',
    'CUBE',
    'DEFAULT',
}

vesselType_enum = {
    'Debris',
    'SpaceObject',
    'Unknown',
    'Probe',
    'Relay',
    'Rover',
    'Lander',
    'Ship',
    'Plane',
    'Station',
    'Base',
    'EVA',
    'Flag',
    'DeployedScienceController',
    'DeployedSciencePart',
}

part_valid_fields = {
    'name': check_name,
    'module': enum(module_enum),
    'author': None,
    'mesh': discourage_mesh,
    'scale': positive_nonzero_float,
    'rescaleFactor': positive_nonzero_float,
    'attachRules': check_attachRules,
    'TechRequired': enum(TechRequired_enum),
    'entryCost': positive_int,
    'cost': positive_float,
    'category': enum(category_enum),
    'subcategory': ignored,
    'title': None,
    'manufacturer': None,
    'description': None,
    'tags': None,
    'mass': positive_nonzero_float,
    'dragModelType': enum(dragModelType_enum, True),
    'maximum_drag': positive_nonzero_float,
    'minimum_drag': positive_nonzero_float,
    'angularDrag': positive_nonzero_float,
    'crashTolerance': positive_nonzero_float,
    'maxTemp': positive_nonzero_float,
    'skinMaxTemp': positive_nonzero_float,
    'heatConductivity': positive_nonzero_float,
    'heatConvectiveConstant': positive_nonzero_float,
    'skinInternalConductionMult': positive_nonzero_float,
    'emissiveConstant': positive_nonzero_float,
    'thermalMassModifier': positive_nonzero_float,
    'CrewCapacity': positive_int,
    'bulkheadProfiles': None, #FIXME
    'stackSymmetry': positive_int,
    'breakingTorque': positive_nonzero_float,
    'breakingForce': positive_nonzero_float,
    'fuelCrossFeed': boolean,
    'inverseStageCarryover': boolean,
    'explosionPotential': positive_float,
    'vesselType': enum(vesselType_enum),
    'stageOffset': positive_int,
    'childStageOffset': positive_int,
    'CoMOffset': vector,
    'CoLOffset': vector,
    'CoPOffset': vector,
    'CenterOfDisplacement': vector,
    'CenterOfBuoyancy': vector,
    'skinMassPerArea': positive_float,
    'stagingIcon': None, #FIXME
    'bodyLiftOnlyAttachName': None, #FIXME
    'bodyLiftOnlyUnattachedLift': boolean,
    'bodyLiftOnlyUnattachedLiftActual': boolean,
    'TechHidden': boolean,
    'buoyancyUseSine': boolean,
    'buoyancy': positive_float,
    'PhysicsSignificance':physics_significance,
    'mirrorRefAxis': vector,
    'radiatorMax': positive_nonzero_float,
    'boundsCentroidOffset': vector,
    'partRendererBoundsIgnore': None, #FIXME
    'bodyLiftMultiplier': positive_nonzero_float,
    'buoyancyUseCubeNamed': None, #FIXME
    'initRotation': quaternion,
    'noAutoEVAMulti': boolean,
    'noAutoEVAAny': boolean,
    'iconCenter': ignored,
    'boundsMultiplier': positive_nonzero_float,
    'ActivatesEvenIfDisconnected': boolean,
    'radiatorHeadroom': positive_nonzero_float,
    'skipColliderIgnores': boolean,
    'mapActionsToSymmetryParts': boolean,
    'resourcePriorityUseParentInverseStage': boolean,
}

compoundpart_valid_fields = {
    'maxLength': positive_nonzero_float,
}

def check_resource(name, value, path, line):
    if value not in resources:
        error(path, line, f"'{value}' not a known resource")

resource_required_fields = (
    ('name', error, "Missing field 'name'"),
    ('amount', error, "Missing field 'amount'"),
    ('maxAmount', error, "Missing field 'maxAmount'"),
)

resource_valid_fields = {
    'name': check_resource,
    'amount': positive_float,
    'maxAmount': positive_float,
}

def parse_resource(path, line, resnode):
    seen_fields = {}
    for req in resource_required_fields:
        if not resnode.HasValue(req[0]):
            req[1](path, line, req[2])
    for name, value, line in resnode.values:
        if name in seen_fields:
            warning(path, line, f"{name} dups {name} on line {seen_fields[name]}")
        else:
            seen_fields[name] = line
        if name in resource_valid_fields:
            if resource_valid_fields[name]:
                resource_valid_fields[name](name, value, path, line)
        else:
            warning(path, line, f"{name} not a known RESOURCE field")
    rescost = 0
    if resnode.HasValue("name"):
        name = resnode.GetValue("name")
        if name in resources:
            rescost = resources[name].GetValue("unitCost")
            try:
                rescost = float(rescost)
            except ValueError:
                rescost = 0
    if resnode.HasValue("amount") and resnode.HasValue("maxAmount"):
        try:
            amount = float(resnode.GetValue("amount"))
            maxAmount = float(resnode.GetValue("maxAmount"))
        except ValueError:
            rescost = 0
        else:
            if amount > maxAmount:
                warning(path, line, f"amount {amount} > maxAmount {maxAmount}")
            rescost *= amount
    return rescost

def parse_part(path, line, partnode):
    seen_fields = {}
    for req in part_required_fields:
        if not partnode.HasValue(req[0]):
            req[1](path, line, req[2])
    for name, value, line in partnode.values:
        if name in seen_fields:
            warning(path, line, f"{name} dups {name} on line {seen_fields[name]}")
        else:
            seen_fields[name] = line
        if name in part_valid_fields:
            if part_valid_fields[name]:
                part_valid_fields[name](name, value, path, line)
        elif name[:5] == "node_":
            check_node(name, value, path, line)
        elif name[:6] == "sound_":
            pass
        elif name[:3] == "fx_":
            pass
        else:
            warning(path, line, f"{name} not a known Part field")
    resource_cost = 0.0
    for name, node, line in partnode.nodes:
        if name == 'RESOURCE':
            resource_cost += parse_resource(path, line, node)
    if partnode.HasValue("cost"):
        try:
            cost = float(partnode.GetValue("cost"))
        except ValueError:
            pass
        else:
            if cost < resource_cost:
                warning(path, line, f"part cost {cost} is not greater than resouce cost {resource_cost} (:skwod:)")

parsers = {
    'PART': parse_part,
}

options, cfgfiles = getopt.getopt(sys.argv[1:], shortopts, longopts)
for opt, arg in options:
    if opt == "--gamedata":
        recurse_tree(os.path.expanduser(arg), find_resources)
    elif opt == "--resources":
        find_resources(os.path.expanduser(arg))

for path in cfgfiles:
    try:
        cfg = ConfigNode.loadfile(os.path.expanduser(path))
    except ConfigNodeError as e:
        print(path + e.message)
    else:
        if not cfg:
            continue
        for n in cfg.nodes:
            name, node, line = n
            if name in parsers:
                parsers[name](path, line, node)
