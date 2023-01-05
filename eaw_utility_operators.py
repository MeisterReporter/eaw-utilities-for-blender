import bpy

import random

import sys

from bpy.types import (Operator, Armature, Bone, EditBone, MeshVertex, Mesh)

from mathutils import (Vector, Matrix, Quaternion, Euler)
from math import radians

from . eaw_utility_properties import EAWU_Properties
from .eaw_utility_util import *

###############################################################
# Parent All Bones:                                           #
# Parent all bones from the active armature based on distance #
###############################################################
class EAWU_OT_ParentAllBones(Operator):

    bl_idname = "object.parent_all_bones"
    bl_label = "Parent all Bones"
    bl_description = "Parent all bones from the active armature based on the distance to eachother"

    @classmethod
    def poll(cls, context):
        obj = context.object
        
        if obj is not None:
            if obj.type == "ARMATURE":
                return True

        return False

    def execute(self, context):
        scene = context.scene
        armature = Armature(context.object.data)
        properties = scene.eaw_utility

        # Get Properties
        distanceThreshold = properties.distanceThreshold

        shouldAddContainerBone = properties.shouldAddContainerBone
        containerBoneSufix = properties.containerBoneSufix

        parentBonesPrefix = properties.parentBonesPrefix
        childBonesPrefix = properties.childBonesPrefix

        # Goto Edit Mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Loop through bones
        for bone in armature.bones:

            # Test if is valid Parent
            if bone.name.startswith(parentBonesPrefix):
                for child in armature.bones:

                    # Test if child.name starts with the childPrefix, child.name and bone.name are unequal and the child has no parent
                    if child.name.startswith(childBonesPrefix) and child.name != bone.name and child.parent == None:
                        loc1 = Vector(bone.head_local)
                        loc2 = Vector(child.head_local)
                        dist = (loc2 - loc1).length

                        if dist <= distanceThreshold:
                            editBones = armature.edit_bones
                            parent = editBones[bone.name]

                            if shouldAddContainerBone:
                                # Add Container Bone
                                editBone = editBones.new(bone.name + containerBoneSufix)
                                editBone.tail = bone.tail_local
                                editBone.head = bone.head_local
                                editBone.parent = parent
                                # Adjust the Parent for the child
                                parent = editBone
                            
                            # Set the correct parent for the child
                            editChild = editBones[child.name]
                            editChild.parent = parent

                            break

        # Goto Object Mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {"FINISHED"}

############################################################
# Select Bones Randomly:                                   #
# Bones in the selected armature will be selected randomly #
############################################################
class EAWU_OT_SelectBonesRandomly(Operator):

    bl_idname = "object.select_bones_randomly"
    bl_label = "Select Bones Randomly"
    bl_description = "Select bones in the active armature randomly. You can customize the selection by adjusting the available options."

    @classmethod
    def poll(cls, context):
        obj = context.object
        
        if obj is not None:
            if obj.type == "ARMATURE":
                return True

        return False

    def execute(self, context):
        scene = context.scene
        armature = Armature(context.object.data)
        properties = EAWU_Properties(scene.eaw_utility)

        # Get Properties
        randomBoneCount = properties.randomBoneCount
        spaceBonesByDistance = properties.spaceBonesByDistance
        minimalBoneDistance = properties.minimalBoneDistance

        # Goto Edit Mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        length = len(armature.bones)

        if randomBoneCount > length:
            return {"CANCELLED"}

        properties.previewBonesInRange = False

        selectedIndecies = {}

        editBones = armature.edit_bones

        for bone in armature.bones:
            tmp = editBones.get(bone.name)
            if tmp:
                editBone = EditBone(tmp)
                editBone.select = False
                editBone.select_head = False
                editBone.select_tail = False

        i = 0
        while i < randomBoneCount:
            index = random.randint(0, length - 1)

            # Get closest distance to bones already selected
            closestDistance = sys.float_info.max
            for x in selectedIndecies:
                bone1 = armature.bones[x]
                bone2 = armature.bones[index]
                loc1 = Vector(bone1.head_local)
                loc2 = Vector(bone2.head_local)
                dist = (loc2 - loc1).length

                if dist < closestDistance:
                    closestDistance = dist

            if not index in selectedIndecies:
                if spaceBonesByDistance and closestDistance < minimalBoneDistance:
                    continue

                selectedIndecies[i] = index
                bone = armature.bones[index]
                editBone = EditBone(editBones.get(bone.name))
                editBone.select = True
                editBone.select_head = True
                editBone.select_tail = True
                i += 1

        return {"FINISHED"}

#####################################
# Rename Selected Bones:            #
# Rename Selected Bones with format #
#####################################
class EAWU_OT_RenameSelectedBones(Operator):

    bl_idname = "object.rename_selected_bones"
    bl_label = "Rename Selected Bones"
    bl_description = "Rename selected bones with a cartain format"

    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            if obj.type == "ARMATURE" and bpy.context.active_object.mode == "EDIT" and len(context.selected_bones) > 0:
                return True

        return False

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)

        selectedBones = context.selected_bones

        for i in range(0, len(selectedBones)):
            bone = selectedBones[i]
            bone.name = adjustBoneNameByProperties(context, properties, bone, i)

        return {"FINISHED"}

#####################################
# Rename Selected Bones:            #
# Rename Selected Bones with format #
#####################################
class EAWU_OT_RenameByWeight(Operator):

    bl_idname = "object.rename_by_weight"
    bl_label = "Rename by Weight"
    bl_description = "Rename selected bones by weight"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)
        obj = context.object

        if obj is not None:
            if obj.type == "ARMATURE" and bpy.context.active_object.mode == "EDIT" and len(context.selected_bones) > 0 and properties.renameWeightList:
                return True

        return False

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)
        armature = Armature(context.object.data)

        selectedBones = context.selected_bones
        selectedCount = len(selectedBones)

        # Copy important Values
        weightList = properties.renameWeightList
        weights = []
        names = []
        totalWeights = 0
        for item in weightList:
            totalWeights += item.weight
            weights.append(item.weight)
            names.append(item.value)
        weightStepSize = totalWeights / selectedCount

        for bone in selectedBones:
            randomIndex = random.randint(0, len(names) - 1)
            newName = names[randomIndex]
            # Update weight
            weights[randomIndex] -= weightStepSize
            # Remove weight and name if neccessary
            if weights[randomIndex] <= 0:
                weights.remove(weights[randomIndex])
                names.remove(newName)
            
            # Update name
            bone.name = newName
            if properties.shouldChangeAlamoProperties:
                # Update Alamo Bone Properties (Changing mode not required, because we are already in it)
                editBone = EditBone(armature.edit_bones.get(bone.name))
                try:
                    editBone.EnableProxy = True
                    editBone.ProxyName = newName
                except:
                    print("The Alamo Object Import plugin is not installed")

        return {"FINISHED"}

#####################################
# Rotate Selected Bones:            #
# Rotate selected Bones by method   #
#####################################
class EAWU_OT_RotateBones(Operator):

    bl_idname = "object.rotate_bones"
    bl_label = "Rotate Bones"
    bl_description = "Rotate bones using a specified method"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)
        obj = context.object

        if obj is not None:
            if obj.type == "ARMATURE" and bpy.context.active_object.mode == "EDIT" and len(context.selected_bones) > 0 :
                if properties.useNormalObject:
                    if properties.normalObject != "":
                        return True
                else:
                    return True

        return False

    def execute(self, context):
        scene = context.scene
        properties = EAWU_Properties(scene.eaw_utility)
        armature = Armature(context.object.data)

        selectedBones = context.selected_bones

        # Get Properties
        rotatingMehtod = properties.rotatingMethod
        useNormalMesh = properties.useNormalObject
        normalMeshName = properties.normalObject
        facingAxis = properties.facingAxis

        if rotatingMehtod == "NORMAL_DIRECTION":
            for bone in selectedBones: 
                boneLoc = Vector(bone.head)

                # Get Closest Vertex
                closestVertex = None
                closestDistance = sys.float_info.max
                # Use custom Normal Mesh
                if useNormalMesh:
                    # Find correct Mesh
                    outer = None
                    for obj in scene.objects:
                        if obj.data.name == normalMeshName:
                            outer = obj
                    # Stop if outer is None
                    if outer == None: return {"CANCELLED"}
                    mesh = Mesh(outer.data)
                    for vertex in mesh.vertices:
                        vertexLoc = Vector(outer.matrix_world @ vertex.co)
                        dist = (vertexLoc - boneLoc).length
                        if dist < closestDistance:
                            closestDistance = dist
                            closestVertex = vertex
                # Use all meshes as Normal Mesh
                else:
                    objects = scene.objects
                    for outer in objects:
                        if outer.type == "MESH":
                            mesh = Mesh(outer.data)
                            for vertex in mesh.vertices:
                                vertexLoc = Vector(outer.matrix_world @ vertex.co)
                                dist = (vertexLoc - boneLoc).length
                                if dist < closestDistance:
                                    closestDistance = dist
                                    closestVertex = vertex
                
                # Get Vertex Normal
                if closestVertex != None:
                    normal = closestVertex.normal.copy()

                    print("Use normal", normal, "for Bone", bone.name)
                    
                    # Define Up axis
                    tail = Vector((0,0,1))
                    if facingAxis == "X_AXIS":
                        tail = Vector((0,1,0))
                    elif facingAxis == "Y_AXIS":
                        tail = Vector((1,0,0))
                    elif facingAxis == "Z_AXIS":
                        tail = Vector((0,1,0))
                    
                    # Save offset to Origin
                    originOffset = -bone.head
                    # Apply Facepreset
                    bone.head = Vector((0,0,0))
                    bone.tail = tail
                    bone.roll = 0

                    # Create Rotation Matrix
                    rotMatrix = lookAt(boneLoc, normal, Vector((0,0,1)))
                    eulerRot = Euler(rotMatrix.to_euler())

                    # Rotate Bone
                    bone.transform(eulerRot.to_matrix(), scale=False)
                    # Special Case Z Axis
                    if facingAxis == "Z_AXIS": bone.roll += radians(90)
                    bone.translate(-originOffset)

                    if facingAxis == "X_AXIS":
                        print("Bone Normal", bone.x_axis)
                    elif facingAxis == "Y_AXIS":
                        print("Bone Normal", bone.y_axis)
                    elif facingAxis == "Z_AXIS":
                        print("Bone Normal", bone.z_axis)

        return {"FINISHED"}