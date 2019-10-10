# -*- coding: utf-8 -*-
# ---------------------------- Operators ------------------------
import bpy
import math

from mathutils import Vector

from . import cfg
from . import at_interface
from . at_calc_func import at_random_fill, fill_rotation


class OBJECT_OT_at_start(bpy.types.Operator):
    """Start and init the addon"""
    bl_idname = 'scene.at_op'
    bl_label = "Start array"

    @classmethod
    def poll(cls, context):
        return not context.scene.arraytools_prop.already_start

    def execute(self, context):
        cfg.init_array_tool(context)
        return {'FINISHED'}


class OBJECT_OT_at_done(bpy.types.Operator):
    """Apply the settings"""
    bl_idname = 'scene.at_done'
    bl_label = "Done !"

    def execute(self, context):
        cfg.atools_objs.clear()
        #cfg.at_mtx_list.clear()
        array_col = bpy.data.collections.get(cfg.col_name)
        cfg.col_name = "Array_collection"
        context.scene.arraytools_prop.up_ui_reset()
        context.scene.arraytools_prop.already_start = False
        return {'FINISHED'}


class OBJECT_OT_at_cancel(bpy.types.Operator):
    """Cancel the settings"""
    bl_idname = 'scene.at_cancel'
    bl_label = "Cancel"

    def execute(self, context):
        scn = context.scene
        scn.arraytools_prop.at_del_all(True)
        scn.arraytools_prop.up_ui_reset()
        scn.arraytools_prop.already_start = False
        cfg.col_name = "Array_collection"
        return {'FINISHED'}


class OBJECT_OT_fill_tr(bpy.types.Operator):
    """Fill the random translation fields"""
    bl_idname = 'scene.fill_tr'
    bl_label = "Fill"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        offset = prop.tr_offset

        for i in range(3):
            if offset[i] == 0.0:
                prop.tr_min[i], prop.tr_max[i] = at_random_fill(-3.0, 3.0)
            else:
                prop.tr_min[i], prop.tr_max[i] = at_random_fill(-offset[i]/2, offset[i]/2)
        return{'FINISHED'}


class OBJECT_OT_fill_sc(bpy.types.Operator):
    """Fill the random scale fields"""
    bl_idname = 'scene.fill_sc'
    bl_label = "Fill"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        offset = prop.sc_offset

        if 100 in [offset[0], offset[1], offset[2]]:
            prop.sc_min_x, prop.sc_max_x = at_random_fill(40.0, 120.0)
            prop.sc_min_y, prop.sc_max_y = at_random_fill(40.0, 120.0)
            prop.sc_min_z, prop.sc_max_z = at_random_fill(40.0, 120.0)
        else:
            rand = [(100 - offset[i]) / 2 for i in range(3)]
            print(rand)
            prop.sc_min_x, prop.sc_max_x = at_random_fill(offset[0]-rand[0], offset[0]+rand[0])
            prop.sc_min_y, prop.sc_max_y = at_random_fill(offset[1]-rand[1], offset[1]+rand[1])
            prop.sc_min_z, prop.sc_max_z = at_random_fill(offset[2]-rand[2], offset[2]+rand[2])
        if prop.sc_all:
            prop.sc_min_x = prop.sc_min_y = prop.sc_min_z
            prop.sc_max_x = prop.sc_max_y = prop.sc_max_z
        return {'FINISHED'}


class OBJECT_OT_fill_rot(bpy.types.Operator):
    """Fill the random rotation fields"""
    bl_idname = 'scene.fill_rot'
    bl_label = "Fill"

    def execute(self, context):
        fill_rotation(context)
        return {'FINISHED'}


class OBJECT_OT_x360(bpy.types.Operator):
    """Quick 360 degrees on X axis"""
    bl_idname = 'scene.x360'
    bl_label = "360"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.tr_offset = Vector((0.0, 0.0, 0.0))
        prop.rot_global = Vector((math.pi/180*360, 0.0, 0.0))
        return{'FINISHED'}


class OBJECT_OT_y360(bpy.types.Operator):
    """Quick 360 degrees on Y axis"""
    bl_idname = 'scene.y360'
    bl_label = "360"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.tr_offset = Vector((0.0, 0.0, 0.0))
        prop.rot_global = Vector((0.0, math.pi/180*360, 0.0))
        return{'FINISHED'}


class OBJECT_OT_z360(bpy.types.Operator):
    """Quick 360 degrees on Z axis"""
    bl_idname = 'scene.z360'
    bl_label = "360"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.tr_offset = Vector((0.0, 0.0, 0.0))
        prop.rot_global = Vector((0.0, 0.0, math.pi/180*360))
        return{'FINISHED'}


class OBJECT_OT_reset_tr(bpy.types.Operator):
    """Reset the settings of random translation"""
    bl_idname = 'scene.at_reset_tr'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.tr_min[0], prop.tr_min[1], prop.tr_min[2] = 0.0, 0.0, 0.0
        prop.tr_max[0], prop.tr_max[1], prop.tr_max[2] = 0.0, 0.0, 0.0

        # if operator is used many times
        # get weird result != 0 with vector
        # prop.tr_max = Vector((0.0, 0.0, 0.0))
        return {'FINISHED'}


class OBJECT_OT_reset_sc(bpy.types.Operator):
    """Reset the settings of random scale"""
    bl_idname = 'scene.at_reset_sc'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.sc_min_x, prop.sc_min_y, prop.sc_min_z = 100, 100, 100
        prop.sc_max_x, prop.sc_max_y, prop.sc_max_z = 100, 100, 100
        return{'FINISHED'}


class OBJECT_OT_reset_rot(bpy.types.Operator):
    """Reset the settings of random rotation"""
    bl_idname = 'scene.at_reset_rot'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.rot_min[0], prop.rot_min[1], prop.rot_min[2] = 0.0, 0.0, 0.0
        prop.rot_max[0], prop.rot_max[1], prop.rot_max[2] = 0.0, 0.0, 0.0
        return{'FINISHED'}


class OBJECT_OT_reset_second(bpy.types.Operator):
    """Reset the settings of row options"""
    bl_idname = 'scene.at_reset_second'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.tr_second = (0,0,0)
        prop.sc_second = (100,100,100)
        prop.rot_second = (0,0,0)
        return {'FINISHED'}


class OBJECT_OT_error(bpy.types.Operator):
    """Draw a message box to display error"""
    bl_idname = "info.at_error"
    bl_label = "Message info"

    info: bpy.props.StringProperty(
        name = "Message",
        description = "Display a message",
        default = ''
    )

    def execute(self, context):
        self.report({'INFO'}, self.info)
        print(self.info)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.info)
        layout.label(text="")