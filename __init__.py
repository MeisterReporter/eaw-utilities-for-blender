# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "EAW Utility",
    "author" : "Meister Reporter",
    "description" : "",
    "blender" : (3, 0, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Armature"
}

import bpy

from bpy.props import PointerProperty

from .eaw_utility_operators import (EAWU_OT_ParentAllBones, 
                                    EAWU_OT_SelectBonesRandomly, 
                                    EAWU_OT_RenameSelectedBones, 
                                    EAWU_OT_RenameByWeight, 
                                    EAWU_OT_RotateBones)
from .ui.eaw_utility_panel import EAWU_PT_Panel
from .ui.eaw_utility_weightlist import (EAWU_UL_WeightList, 
                                        EAWU_OT_WeightList_NewItem, 
                                        EAWU_OT_WeightList_DeleteItem, 
                                        EAWU_OT_WeightList_MoveItemUp, 
                                        EAWU_OT_WeightList_MoveItemDown)
from .eaw_utility_properties import (EAWU_Properties, EAWU_WightlistItem)

classes = (EAWU_OT_ParentAllBones, 
            EAWU_PT_Panel, 
            EAWU_WightlistItem, 
            EAWU_Properties, 
            EAWU_OT_SelectBonesRandomly, 
            EAWU_OT_RenameSelectedBones, 
            EAWU_UL_WeightList, 
            EAWU_OT_WeightList_NewItem, 
            EAWU_OT_WeightList_DeleteItem, 
            EAWU_OT_WeightList_MoveItemUp,
            EAWU_OT_WeightList_MoveItemDown,
            EAWU_OT_RenameByWeight,
            EAWU_OT_RotateBones)

def register():
    # Classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Properties
    bpy.types.Scene.eaw_utility = PointerProperty(type=EAWU_Properties)


def unregister():
    # Classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Properties
    del bpy.types.Scene.eaw_utility