import bpy

import mathutils

from bpy.types import (Operator, UIList, UILayout)

from bpy.props import (EnumProperty)

from ..eaw_utility_properties import (EAWU_Properties, EAWU_WightlistItem)

class EAWU_UL_WeightList(UIList):

    def draw_item(self, context, layout : UILayout, data, item : EAWU_WightlistItem, icon, active_data, active_propname, index):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        customIcon = 'OBJECT_DATAMODE'
        isSelected = index == properties.renameWeightListIndex

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Different Layouts if selected
            if isSelected:
                layout.prop(item, "value", icon=customIcon)
                layout.prop(item, "weight")
            else:
                layout.label(text=item.value, icon = customIcon)
                layout.label(text=str(round(item.weight, 2)))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = customIcon)

class EAWU_OT_WeightList_NewItem(Operator):

    bl_idname = "object.new_item"
    bl_label = "Add Item"

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        # Get Properties
        weightedList = properties.renameWeightList
        weightedList.add()

        return{'FINISHED'}

class EAWU_OT_WeightList_DeleteItem(Operator):

    bl_idname = "object.delete_item"
    bl_label = "Delete Item"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        return properties.renameWeightList

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        # Get Properties
        weightedList = properties.renameWeightList
        index = properties.renameWeightListIndex

        weightedList.remove(index)
        properties.renameWeightListIndex = min(max(0, index - 1), len(weightedList) - 1)

        return{'FINISHED'}

class EAWU_OT_WeightList_MoveItemUp(Operator):

    bl_idname = "object.move_item_up"
    bl_label = "Move Item"

    direction = EnumProperty(items=(('UP', 'Up', ""),
                                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        return properties.renameWeightList

    def move_index(self):
        scene = bpy.context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        index = properties.renameWeightListIndex
        weightedList = properties.renameWeightList

        listLength = len(weightedList) - 1
        newIndex = index - 1

        properties.renameWeightListIndex = max(0, min(newIndex, listLength))

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        index = properties.renameWeightListIndex
        weightedList = properties.renameWeightList

        neighbor = index - 1
        weightedList.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}

class EAWU_OT_WeightList_MoveItemDown(Operator):

    bl_idname = "object.move_item_down"
    bl_label = "Move Item"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        return properties.renameWeightList

    def move_index(self):
        scene = bpy.context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        index = properties.renameWeightListIndex
        weightedList = properties.renameWeightList

        listLength = len(weightedList) - 1
        newIndex = index + 1

        properties.renameWeightListIndex = max(0, min(newIndex, listLength))

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        index = properties.renameWeightListIndex
        weightedList = properties.renameWeightList

        neighbor = index + 1
        weightedList.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}