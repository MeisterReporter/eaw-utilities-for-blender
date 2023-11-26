import bpy

import sys

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       CollectionProperty)

from bpy.types import (PropertyGroup, 
                       Armature, 
                       Bone,
                       EditBone,
                       Object)

from mathutils import Vector

class EAWU_WightlistItem(PropertyGroup):

    value : StringProperty(
        name = "",
        description = "The weighted value",
        default = "Empty",
    )

    weight : FloatProperty(
        name = "Weight",
        description = "The weight for value",
        default = 1.0,
        min = 0.0,
        max = 1.0,
    )

class EAWU_Properties(PropertyGroup):

    utils = [
                ("PARENT_BONES", "Parent Bones", "Parent all matching child bones to the parent", "", 0),
                ("RANDOM_BONES", "Select Bones Randomly", "Select Bones of the active Armature randomly", "", 1),
                ("RENAME_BONES", "Rename Bones", "Rename all selected bones", "", 2),
                ("RENAME_BONES_BY_LIST", "Rename Bones by Weightlist", "Rename all selected bones using a Weightlist", "", 3),
                ("ROTATE_BONES", "Rotate Bones", "Rotate all selected bones is specific direction", "", 4),
                ("SCALE_CORRECT", "Scale by Reference", "Scale a target model by a reference model with lengths", "", 5)
            ]

    # General Properties

    utilityProperty : EnumProperty(
        name = "Choose Utility",
        description = "Choose the Utility you want to use",
        items = utils,
        default = "PARENT_BONES"
    )

    # Parent all Bones Properties

    def updateChildrenCoverage(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        armature = None
        for obj in scene.objects:
            if obj.type == "ARMATURE":
                armature = Armature(obj.data)

        childrenWithoutParent = 0
        childrenWithParent = 0
        childrenCount = 0
        children = 0

        if armature != None:
            for bone in armature.bones:
                # Count the total amount of children matching the childPrefix
                if bone.name.startswith(properties.childBonesPrefix):
                    childrenCount += 1
                    children += 1

                    if bone.parent != None:
                        childrenWithParent += 1

                # Count Children that will have a parent
                if bone.name.startswith(properties.parentBonesPrefix) and not bone.name.endswith(properties.containerBoneSufix):
                    for child in armature.bones:
                        
                        if child.name.startswith(properties.childBonesPrefix) and child.name != bone.name and child.parent == None:
                            loc1 = Vector(bone.head_local)
                            loc2 = Vector(child.head_local)
                            dist = (loc2 - loc1).length

                            if dist <= properties.distanceThreshold:
                                childrenWithoutParent += 1

        childrenCount -= childrenWithParent
        #print(childrenWithoutParent, childrenWithParent, childrenCount, children)

        if childrenWithParent == children:
            properties.childrenCoverage = "All children are parented"
        else:
            properties.childrenCoverage = str(int((childrenWithoutParent/childrenCount)*100)) + "% (" + str(childrenWithoutParent) + "/" + str(childrenCount) + ")"

    def distanceThresholdUpdated(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        properties.updateChildrenCoverage(context=context)

        if not properties.previewThreshold:
            return

        armature = None
        for obj in scene.objects:
            if obj.type == "ARMATURE":
                armature = Armature(obj.data)

        if armature != None:
            for bone in armature.bones:

                if bone.name.startswith(properties.parentBonesPrefix) and not bone.name.startswith(properties.childBonesPrefix) and bone.parent == None:
                    circle = scene.objects.get(bone.name)

                    if circle != None and circle.data.name.startswith("Circle"):
                        bpy.data.objects.remove(circle, do_unlink=True)

                    bpy.ops.mesh.primitive_circle_add(radius=properties.distanceThreshold, enter_editmode=False, align='WORLD', location=bone.head_local, scale=(1, 1, 1))
                    circle = context.object
                    circle.name = bone.name
                    circle.show_in_front = True

    distanceThreshold : FloatProperty(
        name = "",
        description = "The maximum distance between the child and the possible parent.",
        default = 0.0,
        min = 0,
        update=distanceThresholdUpdated
    )

    shouldAddContainerBone : BoolProperty(
        name = "Add Container Bone",
        description = "Should the script add a bone between parent and child",
        default = True,
    )

    containerBoneSufix : StringProperty(
        name = "Container Sufix",
        description = "The container bone will become the child of the chosen parent and the child will be parented to the Container",
        default = "_DMG",
    )

    parentBonesPrefix : StringProperty(
        name = "Parent Prefix",
        description = "All the bones with this prefix will be considered as possible parents",
        default = "HP_",
    )

    childBonesPrefix : StringProperty(
        name = "Child Prefix",
        description = "All the bones with this prefix will be considered as possible children",
        default = "P_",
    )

    def previewThresholdUpdated(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        if properties.previewThreshold:
            properties.distanceThresholdUpdated(context)
        else:
            armature = None
            for obj in scene.objects:
                if obj.type == "ARMATURE":
                    armature = Armature(obj.data)

            # Loop through bones
            for bone in armature.bones:

                # Test if is valid Parent
                if bone.name.startswith(properties.parentBonesPrefix):
                    circle = scene.objects.get(bone.name)

                    if circle != None and circle.data.name.startswith("Circle"):
                        bpy.data.objects.remove(circle, do_unlink=True)

    previewThreshold : BoolProperty(
        name = "Preview Threshold",
        description = "If ticked circles will be generated which visualizes the Distance Threshold",
        default = True,
        update=previewThresholdUpdated
    )

    childrenCoverage : StringProperty(
        name = "Children Coverage",
        default = "0% (0/0)"
    )

    # Select random Bones Properties

    randomBoneCount : IntProperty(
        name = "",
        description = "The count of bones that should be selected in the active armature",
        default = 1,
        min = 1,
    )

    spaceBonesByDistance : BoolProperty(
        name = "Space Bones by Distance",
        description = "Bones should be spaced a minimal distance away from the closest bone",
        default = True,
    )

    def updateMininalBoneDistance(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)
        # Get Armature
        obj = context.object
        armature = Armature(obj.data)
        bonesInRange = 0
        for bone1 in armature.bones:
            closestDistance = sys.float_info.max
            for bone2 in armature.bones:
                if bone1.name != bone2.name:
                    loc1 = Vector(bone1.head_local)
                    loc2 = Vector(bone2.head_local)
                    dist = (loc2 - loc1).length

                    if dist < closestDistance:
                        closestDistance = dist

            if closestDistance >= properties.minimalBoneDistance:
                bonesInRange += 1
        
        properties.bonesInRange = "Bones in Range: " + str(bonesInRange)+ "/" + str(len(armature.bones)) + " (inaccurate)"

        if bonesInRange < properties.randomBoneCount:
            self.randomBonesButtonEnabled = False
        else:
            self.randomBonesButtonEnabled = True

    minimalBoneDistance : FloatProperty(
        name = "",
        description = "The minimum distance the bone should be away from the closest bone",
        default = 0,
        min = 0,
        update = updateMininalBoneDistance,
    )

    randomBonesButtonEnabled : BoolProperty(
        name = "Random Bone Button Enabled",
        default = True,
    )

    bonesInRange : StringProperty(
        name = "Bones in Range",
        default = 'Bones in range: (inaccurate)'
    )

    def updatePreviewBonesInRange(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)
        # Get Armature
        obj = context.object
        armature = Armature(obj.data)
        for bone1 in armature.bones:
            editBone = EditBone(armature.edit_bones.get(bone1.name))
            editBone.select = False
            editBone.select_head = False
            editBone.select_tail = False

            if self.previewBonesInRange:
                closestDistance = sys.float_info.max
                for bone2 in armature.bones:
                    if bone1.name != bone2.name:
                        loc1 = Vector(bone1.head_local)
                        loc2 = Vector(bone2.head_local)
                        dist = (loc2 - loc1).length

                        if dist < closestDistance:
                            closestDistance = dist
                    
                if closestDistance >= properties.minimalBoneDistance:
                    editBone.select = True
                    editBone.select_head = True
                    editBone.select_tail = True

    previewBonesInRange : BoolProperty(
        name = "Preview Bones in Range (inaccurate)",
        default = True,
        update = updatePreviewBonesInRange,
    )

    renameStartNumber : IntProperty(
        name = "",
        description = "The number to start with and counting the stepsize upwards",
        default = 0,
        min = 0,
    )

    renameStepSizeNumber : IntProperty(
        name = "",
        description = "The number which will be added after each bone was renamed",
        default = 1,
        min = 1,
    )

    fillUpZeros : BoolProperty(
        name = "Fill Up Zeros",
        description = "Fill the numbers up with Zeros",
        default = True,
    )

    largestDigitSize : IntProperty(
        name = "",
        description = "How many characters has the largest digit. Use zero to auto detect.",
        default = 0,
        min = 0,
    )

    renameBonePreset : StringProperty(
        name = "Name Preset",
        description = "The name preset weill be taken to create the new name for the bones",
        default = "%s_%i",
    )

    enableRenamePreview : BoolProperty(
        name = "Enable Preview",
        description = "Show a preview of the first Item",
        default = True,
    )

    renamePreview : StringProperty(
        name = "Preview text",
        description = "Preview Text",
        default = "No Preview",
    )

    # Rename by Wieghtlist

    renameWeightList : CollectionProperty(
        type = EAWU_WightlistItem,
    )

    renameWeightListIndex : IntProperty(
        name = "Index for renameWeightList",
        default = 0,
    )

    shouldChangeAlamoProperties : BoolProperty(
        name = "Change Alamo Properties",
        description = "Changing Alamo Properties only works if the Alamo Importer by Gaukler is installed. It will change ProxyEnabled and ProxyName",
        default = True,
    )

    # Rotate Bones Properties
    
    boneDirections = [("NORMAL_DIRECTION", "Normal Direction", "Rotate the Bone in the closest normal direction", "", 0)]

    axis = [
            ("X_AXIS", "X Axis", "The red axis in the viewport", "", 0),
            ("Y_AXIS", "Y Axis", "The green axis in the viewport", "", 1),
            ("Z_AXIS", "Z Axis", "The blue axis or up and down in the viewport", "", 3),
           ]

    rotatingMethod : EnumProperty(
        name = "Rotate Bones In",
        description = "Rotate Bones using the selected rotation method",
        items = boneDirections,
        default = "NORMAL_DIRECTION",
    )

    facingAxis : EnumProperty(
        name = "Bone Face Axis",
        description = "The axis that should be facing in the selected direction",
        items = axis,
        default = "Z_AXIS",
    )

    useNormalObject : BoolProperty(
        name = "Use Source Mesh",
        description = "If true you can select a source mesh from which the normals should be taken from. If false all meshes will be treated as source meshes",
        default = False,
    )

    normalObject : StringProperty(
        name = "Source Mesh",
        description = "The Mesh from which the normal directions should be taken. The names listed here are mesh names, these names can be found by expanding" + 
                      " the mesh objects in the outliner. The name next to the green triangle is the mesh name",
        default = "",
    )

    # Scale by Reference Properties

    refModelLength : FloatProperty(
        name = "",
        description = "The length of the reference model",
        default = 1,
        min = 0,
    )

    refModel : StringProperty(
        name = "",
        description = "The reference model, will be used to calculate the length of it self and then the ratio.",
        default = "",
    )

    targetModelLength : FloatProperty(
        name = "",
        description = "The length of the target model",
        default = 1,
        min = 0,
    )

    targetModel : StringProperty(
        name = "",
        description = "The target model, will be used to calculate the length of it self and then the ratio to the desired length.",
        default = "",
    )

    lengthAxis : EnumProperty(
        name = "Length Axis",
        description = "The axis on which the length should be measured",
        items = axis,
        default = "Y_AXIS",
    )