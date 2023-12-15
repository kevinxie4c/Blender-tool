import json
import bpy
import mathutils

filename = "r15_blocky_hier.json"
js = json.load(open(filename, "r"))

arm_data = bpy.data.armatures.new(filename)
arm_ob = bpy.data.objects.new(filename, arm_data)

bpy.context.collection.objects.link(arm_ob)

arm_ob.select_set(True)
bpy.context.view_layer.objects.active = arm_ob

def add_bone(bn, parent, v):
    head = v + mathutils.Vector(bn['pos'])
    if len(bn['children']) == 1:
        tail = head + mathutils.Vector(bn['children'][0]['pos'])
    elif len(bn['children']) > 1:
        for child in bn['children']:
            if (not 'Left' in child['name']) and (not 'Right' in child['name']):
                tail = head + mathutils.Vector(child['pos'])
    else:
        tail = head + mathutils.Vector(bn['COM'])
    bone = arm_data.edit_bones.new(bn['name'])
    bone.head = head
    bone.tail = tail
    bn['offset'] = head
    if parent != None:
        bone.parent = parent
    for child in bn['children']:
        add_bone(child, bone, head)

bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
bpy.ops.object.mode_set(mode='EDIT', toggle=False)

while arm_data.edit_bones:
    arm_data.edit_bones.remove(arm_data.edit_bones[-1])

add_bone(js, None, mathutils.Vector((0, 0, 0)))

def add_geometry(bn):
    for shape in bn['shape']:
        if shape['type'] == 'box':
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0), align='WORLD', scale=shape['size'])
            bpy.context.object.parent = arm_ob
            bpy.context.object.parent_type = 'BONE'
            bpy.context.object.parent_bone = bn['name']
            bpy.context.object.matrix_world = mathutils.Matrix.Translation(mathutils.Vector(shape['pos'])+bn['offset'])
        else:
            print(shape['type'] + ' is not supported')
    for child in bn['children']:
        add_geometry(child)

bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

add_geometry(js)
