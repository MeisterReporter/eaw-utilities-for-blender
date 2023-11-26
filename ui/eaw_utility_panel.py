import bpy

from bpy.types import (Panel, Armature)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty)

from ..eaw_utility_properties import EAWU_Properties
from ..eaw_utility_util import (adjustBoneNameByProperties, autoDetectLargestDigit)

from mathutils import Vector

class EAWU_PT_Panel(Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Utility Operations"
    bl_category = "EAW Utility"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        # Properties
        utilityProperty = properties.utilityProperty

        # Adding a row at the end of each area will seperate them in the ui a bit 

        # General Panel Part
        # Utility Chooser
        row = layout.row()
        row.prop(properties, "utilityProperty")
        row = layout.row()

        if utilityProperty == "PARENT_BONES":
            ##############################################
            # Match bones and make them parent and child #
            ##############################################

            # Distance Threshold
            row = layout.row()
            row.label(text="Distance Threshold:")
            row.prop(properties, "distanceThreshold")
            row = layout.row()
            # Container Bone
            row = layout.row()
            row.prop(properties, "shouldAddContainerBone")
            row = layout.row()
            row.prop(properties, "containerBoneSufix")
            row.enabled = properties.shouldAddContainerBone
            row = layout.row()
            # Parent-Child Prefixes
            row = layout.row()
            row.prop(properties, "parentBonesPrefix")
            row = layout.row()
            row.prop(properties, "childBonesPrefix")
            row = layout.row()
            # Preview
            row = layout.row()
            row.label(text="Children Coverage: " + str(properties.childrenCoverage))
            row.prop(properties, "previewThreshold")
            row = layout.row()
            # Button
            row = layout.row()
            name = 'Parent Bones starting with "' + properties.parentBonesPrefix + '"'
            # Get Armature
            obj = context.object
            if obj is not None:
                if obj.type != "ARMATURE":
                    name = "Select an Armature"
            else:
                name = "Select an Armature"
            row.operator("object.parent_all_bones", text=name)

        elif utilityProperty == "RANDOM_BONES":
            ###############################################
            # Select Bones randomly based on some options #
            ###############################################
            
            # Get Armature
            obj = context.object

            # Bone Count
            row = layout.row()
            row.label(text="Bone Count:")
            row.prop(properties, "randomBoneCount")
            row.enabled = False
            if obj is not None:
                if obj.type == "ARMATURE":
                    row.enabled = True
            row = layout.row()
            # Spacing Properties
            row = layout.row()
            row.prop(properties, "spaceBonesByDistance")
            row = layout.row()
            row.label(text="Min Bone Distance:")
            row.prop(properties, "minimalBoneDistance")
            row.enabled = True
            if not properties.spaceBonesByDistance:
                row.enabled = False
            row = layout.row()
            row.label(text=properties.bonesInRange)
            row = layout.row()
            row.prop(properties, "previewBonesInRange")
            row = layout.row()
            # Operator Button
            row = layout.row()
            # Check if active object is armature
            name = "Select Bones Randomly"
            if obj is not None:
                if obj.type != "ARMATURE":
                    name = "Select an Armature"
                # Disable if to large
                if obj.type == "ARMATURE":
                    armature = Armature(obj.data)
                    if properties.randomBoneCount > len(armature.bones):
                        row.enabled = False
                # Disable if minimumDistance causes infinit loop
                if not properties.randomBonesButtonEnabled:
                    row.enabled = False
            else:
                name = "Select an Armature"
            row.operator("object.select_bones_randomly", text=name)
        elif utilityProperty == "RENAME_BONES":
            #########################
            # Rename selected Bones #
            #########################

            # Get Armature Object
            obj = context.object
            # Advise
            row = layout.row()
            row.label(text="Description: ")
            row = layout.row()
            row.label(text="When renaming bones you can use specific formatting options.")
            row = layout.row()
            row.label(text="Use %i to place the current number in the String.")
            row = layout.row()
            row.label(text="Use %s to preserve the original bone name.")
            row = layout.row()
            # Numbering
            row = layout.row()
            row.label(text="Start Number")
            row.prop(properties, "renameStartNumber")
            row.label(text="Stepsize")
            row.prop(properties, "renameStepSizeNumber")
            row = layout.row()
            col1 = row.column()
            col1.prop(properties, "fillUpZeros")
            # Create second column and add a row to it
            col2 = row.column()
            encasedRow = col2.row()
            encasedRow.label(text="Largest Digit Size")
            encasedRow.prop(properties, "largestDigitSize")
            # Enable or disable the encased row
            if not properties.fillUpZeros:
                encasedRow.enabled = False
            row = layout.row()
            # Name
            row = layout.row()
            row.prop(properties, "renameBonePreset")
            row = layout.row()
            # Preview
            row = layout.row()
            row.prop(properties, "enableRenamePreview")
            if obj == None or context.selected_bones == None or len(context.selected_bones) == 0 or obj.type != "ARMATURE" or bpy.context.active_object.mode != "EDIT":
                row.enabled = False
            else:
                if properties.enableRenamePreview:
                    row = layout.row()
                    row.label(text=self.calculateRenamePreview(context, properties))
                    if not properties.enableRenamePreview:
                        row.enabled = False
            row = layout.row()
            # Operator Button
            row = layout.row()
            # Check if active object is armature
            name = "Rename Selected Bones"
            if obj is not None:
                if context.selected_bones != None and len(context.selected_bones) == 0:
                    name = "Select a Bone in the Outliner"
                if bpy.context.active_object.mode != "EDIT":
                    name = "Go into EDIT Mode (e.g. by pressing tab)"
                if obj.type != "ARMATURE":
                    name = "Select an Armature"
            else:
                name = "Select an Armature"
            row.operator("object.rename_selected_bones", text=name)
        elif utilityProperty == "RENAME_BONES_BY_LIST":
            ##############################
            # Rename Bones by Wight List #
            ##############################

            # Get Armature Object
            obj = context.object
            # Description
            row = layout.row()
            row.label(text="Add Names with a coresponding weights to the List")
            row = layout.row()
            # Weight List
            row = layout.row()
            row.template_list("EAWU_UL_WeightList", "WeightedList", properties, "renameWeightList", properties, "renameWeightListIndex")
            row = layout.row()
            row.operator("object.new_item", text="Add", icon="PLUS")
            row.operator("object.delete_item", text="Remove", icon="TRASH")
            row.operator("object.move_item_up", text="Up", icon="TRIA_UP")
            row.operator("object.move_item_down", text="Down", icon="TRIA_DOWN")
            row = layout.row()
            # Edit Value and Weight
            if properties.renameWeightListIndex >= 0 and properties.renameWeightList:
                item = properties.renameWeightList[properties.renameWeightListIndex]

                row = layout.row()
                row.prop(item, "value")
                row.prop(item, "weight")
                row = layout.row()
            # Change Alamo Object Settings
            row = layout.row()
            row.prop(properties, "shouldChangeAlamoProperties")
            row = layout.row()
            # Button Operator
            row = layout.row()
            # Button name based on the neccessary conditions
            name = "Rename by Weight"
            if obj is not None:
                if context.selected_bones != None and len(context.selected_bones) == 0:
                    name = "Select a Bone in the Outliner"
                if bpy.context.active_object.mode != "EDIT":
                    name = "Go into EDIT Mode (e.g. by pressing tab)"
                if obj.type != "ARMATURE":
                    name = "Select an Armature"
            else:
                name = "Select an Armature"
            row.operator("object.rename_by_weight", text=name)
        elif utilityProperty == "ROTATE_BONES":
            ###########################
            # Rotate Bones by options #
            ###########################

            # Get Armature Object
            obj = context.object
            # Get Properties
            rotatingMethod = properties.rotatingMethod

            # Method Selector
            row = layout.row()
            row.label(text="Choose a Rotation Method")
            row = layout.row()
            row.prop(properties, "rotatingMethod")
            row = layout.row()
            # Change Panel Content based on rotation method
            if rotatingMethod == "NORMAL_DIRECTION":
                # Description
                row = layout.row()
                row.label(text="Method Properties:")
                row = layout.row()
                row.label(text="Rotate all selected bones in the normal direction of the closest vertex.")
                if properties.useNormalObject:
                    row = layout.row()
                    row.label(text="Select a specific mesh to find the closest normal")
                    row = layout.row()
                    row.label(text="The names listed in the Source Mesh Text Box are mesh names.")
                    row = layout.row()
                    row.label(text="You can find them by exapdning the")
                    row = layout.row()
                    row.label(text="Mesh Objects then search for a green triangle ", icon="OUTLINER_OB_MESH")
                    row = layout.row()
                    row.label(text="the label next to it is the mesh name", icon="MESH_DATA")
                    row = layout.row()
                else:
                    row = layout.row()
                    row.label(text="All meshes will be used for finding the closest normal")
                # Custom Source Object
                row = layout.row()
                row.prop(properties, "useNormalObject")
                if properties.useNormalObject:
                    row = layout.row()
                    row.prop_search(properties, "normalObject", bpy.data, "meshes")
                row = layout.row()
                # Facing Axis
                row = layout.row()
                row.prop(properties, "facingAxis")
                row = layout.row()
            # Button Operator
            row = layout.row()
            # Button name based on the neccessary conditions
            name = "Rotate Bones"
            if obj is not None:
                if context.selected_bones != None and len(context.selected_bones) == 0:
                    name = "Select a Bone in the Outliner"
                if bpy.context.active_object.mode != "EDIT":
                    name = "Go into EDIT Mode (e.g. by pressing tab)"
                if obj.type != "ARMATURE":
                    name = "Select an Armature"
                if properties.useNormalObject and properties.normalObject == "":
                    name = "Choose a valid Mesh as Source Object"
            else:
                name = "Select an Armature"
            row.operator("object.rotate_bones", text=name)
        elif utilityProperty == "SCALE_CORRECT":
            ###########################
            # Scale the model correct #
            ###########################

            # Reference Model Scale
            row = layout.row()
            row.label(text="Reference Model Length:")
            row.prop(properties, "refModelLength")
            row = layout.row()

            row = layout.row()
            row.label(text="Reference Model:")
            row.prop_search(properties, "refModel", bpy.data, "meshes")
            row = layout.row()

            # Target Model Scale
            row = layout.row()
            row.label(text="Traget Model Length:")
            row.prop(properties, "targetModelLength")
            row = layout.row()

            row = layout.row()
            row.label(text="Target Model:")
            row.prop_search(properties, "targetModel", bpy.data, "meshes")
            row = layout.row()

            # Length Axis
            row = layout.row()
            row.prop(properties, "lengthAxis")
            row = layout.row()

            row = layout.row()
            row.label(text="It is important to APPLY THE SCALE of the target model before you use this method.")
            row = layout.row()

            # Button Operator
            row = layout.row()
            # Button name based on the neccessary conditions
            name = "Scale by Reference"
            if properties.refModel == "":
                name = "Select a target mesh"
            elif properties.targetModel == "":
                name = "Select a reference mesh"
            elif properties.refModelLength == 0:
                name = "The reference length can not be 0"
            elif properties.targetModelLength == 0:
                name = "The target length can not be 0"
            row.operator("object.scale_by_reference", text=name)

    def calculateRenamePreview(self, context, properties : EAWU_Properties, bone = None):
        selectedBones = context.selected_bones

        if selectedBones == None or len(selectedBones) == 0 or not properties.enableRenamePreview:
            if selectedBones != None and len(selectedBones) == 0: return "Select a Bone"

            return "No Preview"
        else:
            
            if bone == None:
                bone = selectedBones[0]

            return adjustBoneNameByProperties(context, properties, bone)