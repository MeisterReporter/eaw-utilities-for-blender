import bpy

from . eaw_utility_properties import EAWU_Properties

from bpy.types import (EditBone)

from typing import List

from mathutils import (Vector, Matrix, Euler)
from math import *

def autoDetectLargestDigit(selectedBones : List[EditBone], startNumber : int, stapSize : int):
    largestDigit = (len(selectedBones) - 1) * stapSize + startNumber
    largestDigitSize = len(str(largestDigit))
    return largestDigitSize


def adjustBoneNameByProperties(context, properties : EAWU_Properties, bone = None, i = 0):
    # Get Properties
    renameStartNumber = properties.renameStartNumber
    renameStepSizeNumber = properties.renameStepSizeNumber
    fillUpZeros = properties.fillUpZeros
    largestDigitSize = properties.largestDigitSize
    renameBonePreset = properties.renameBonePreset

    selectedBones = context.selected_bones

    if bone != None:
        # Value for %s
        currentBoneName = bone.name
        currentNumber = renameStartNumber + (i * renameStepSizeNumber)
        # Value for %i
        currentNumberString = str(currentNumber)

        # Auto detect largestDigitSize
        if largestDigitSize == 0:
            largestDigitSize = autoDetectLargestDigit(selectedBones, renameStartNumber, renameStepSizeNumber)

        # Fill up Zeros (if neccessary)
        if fillUpZeros and len(currentNumberString) < largestDigitSize:
            currentNumberString = "0" + str(currentNumber)

        return renameBonePreset.replace("%s", currentBoneName).replace("%i", currentNumberString)
    else:
        return "The supplied Bone is None"

def lookAt(pos : Vector, target : Vector, up : Vector):
    '''Only tested with 0,0,1 as the up vector. Other up vectors might give inaccurate results'''

    d = target.normalized()
    u = up.normalized()
    # Modify Direction Vector
    if up.z == 1: d.z *= -1
    h = Vector((d.x, d.y, 0))

    # Calculate Yaw
    zAngle = atan2(d.y, d.x)
    # Calculate Pitch
    yAngle = asin(d.z)
    # Calculate Roll
    w0 = Vector((-d.y, d.x, 0))
    u0 = Vector.cross(w0, d)
    xAngle = atan2(Vector.dot(w0, u) / w0.length, Vector.dot(u0, u) / u0.length)

    euler = Euler()
    euler.x = xAngle
    euler.y = yAngle
    euler.z = zAngle

    print("Rotation:", "X", degrees(euler.x), "Y", degrees(euler.y), "Z", degrees(euler.z))

    return euler.to_matrix()
