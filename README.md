# Utilites for making Empire at War models
## !!! Requires [Blender-ALAMAO-Plugin](https://github.com/Gaukler/Blender-ALAMO-Plugin) by Gaukler !!!

### Functions
#### Armature Operations
- Parent Bones:
  - Helps you doing Parenting bones to other bones at the same or near the child location
  - Can be used for assigning Damage Particles to the coresponding Bones
  - ![Parent Bones](/img/parent_bones.png)

- Select Bones Randomly:
  - Select Bones of the active Armature randomly
  - ![Random Bones](/img/select_random_bones.png)

- Rename Bones:
  - Rename all selected bones
  - This can be helpful if you have a large amount of bones that should be ranamed after a specific pattern
  - ![Rename Bones](/img/rename_bones.png)
  
- Rename Bones by Weightlist:
  - Rename all selected bones using a Weightlist
  - Renaming the selected bones by Weightlist can be helpful if you want to rename multiple bones with multiple names but the names should be distributed by a certain ratio
  - ![Rename Bones by Weightlist](/img/rename_bones_by_weight.png)
  - In this example "Name1" should be represented by 80% and "Name2" by 20%
- Rotate Bones:
  - Rotate all selected bones is specific direction
  - Method - Rotate in Normal Direction:
    - Good for rotating all selected bones away from the surface, e.g. for automatically set the rotation for Fire Particles
    - ![Rotate Normal](/img/rotate_bones_normal.png)
