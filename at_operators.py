# -*- coding: utf-8 -*-
# <pep8-80 compliant>

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

# --------------------------- Operators -----------------------------
import bpy
import math

from mathutils import Vector

from . import at_array
from . import at_anim
from . import at_properties
from . at_calc_func import(
    at_random_fill,
    fill_rotation
)


class OBJECT_OT_at_start(bpy.types.Operator):
    """Start and init the addon"""
    bl_idname = 'scene.at_op'
    bl_label = "Start array"

    @classmethod
    def poll(cls, context):
        return not context.scene.arraytools_prop.already_start

    def execute(self, context):
        at_array.init_array_tools(context)
        return {'FINISHED'}


class OBJECT_OT_at_done(bpy.types.Operator):
    """Apply the settings"""
    bl_idname = 'scene.at_done'
    bl_label = "Done !"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        if prop.is_copy:
            at_array.make_single(prop.row, prop.count, prop.alter)
        at_array.del_obj_mask()
        at_array.Larray.bank.clear()
        grp = bpy.data.collections.get(at_array.Larray.grp_name)
        at_array.Larray.grp_name = "Array_collection"
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
        at_array.Larray.grp_name = "Array_collection"
        at_array.Larray.to_del.clear()
        at_array.Larray.bank.clear()
        at_array.Larray.mask.clear()
        print("Cancel array done !")
        return {'FINISHED'}


class OBJECT_OT_fill_tr(bpy.types.Operator):
    """Fill random translation fields"""
    bl_idname = 'scene.fill_tr'
    bl_label = "Fill"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        offset = prop.tr_offset

        for i in range(3):
            if offset[i] == 0.0:
                prop.tr_min[i], prop.tr_max[i] = at_random_fill(-3.0, 3.0)
            else:
                prop.tr_min[i], prop.tr_max[i] = at_random_fill(
                    -offset[i]/2, offset[i]/2)
        return{'FINISHED'}


class OBJECT_OT_fill_sc(bpy.types.Operator):
    """Fill random scale fields"""
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
            prop.sc_min_x, prop.sc_max_x = at_random_fill(
                offset[0]-rand[0], offset[0]+rand[0])
            prop.sc_min_y, prop.sc_max_y = at_random_fill(
                offset[1]-rand[1], offset[1]+rand[1])
            prop.sc_min_z, prop.sc_max_z = at_random_fill(
                offset[2]-rand[2], offset[2]+rand[2])
        if prop.sc_all:
            prop.sc_min_x = prop.sc_min_y = prop.sc_min_z
            prop.sc_max_x = prop.sc_max_y = prop.sc_max_z
        return {'FINISHED'}


class OBJECT_OT_fill_rot(bpy.types.Operator):
    """Fill random rotation fields"""
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
    """Reset settings of random translation"""
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
    """Reset settings of random scale"""
    bl_idname = 'scene.at_reset_sc'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.sc_min_x, prop.sc_min_y, prop.sc_min_z = 100, 100, 100
        prop.sc_max_x, prop.sc_max_y, prop.sc_max_z = 100, 100, 100
        return{'FINISHED'}


class OBJECT_OT_reset_rot(bpy.types.Operator):
    """Reset settings of random rotation"""
    bl_idname = 'scene.at_reset_rot'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.rot_min[0], prop.rot_min[1], prop.rot_min[2] = 0.0, 0.0, 0.0
        prop.rot_max[0], prop.rot_max[1], prop.rot_max[2] = 0.0, 0.0, 0.0
        return{'FINISHED'}


class OBJECT_OT_reset_second(bpy.types.Operator):
    """Reset settings of row options"""
    bl_idname = 'scene.at_reset_second'
    bl_label = 'Reset'

    def execute(self, context):
        prop = context.scene.arraytools_prop
        prop.tr_second = (0, 0, 0)
        prop.sc_second = (100, 100, 100)
        prop.rot_second = (0, 0, 0)
        return {'FINISHED'}


class OBJECT_OT_error(bpy.types.Operator):
    """Draw a message box to display error"""
    bl_idname = "info.at_error"
    bl_label = "Message info"

    info: bpy.props.StringProperty(
        name="Message",
        description="Display a message error",
        default=''
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


class OBJECT_OT_mask(bpy.types.Operator):
    """Allow to mask elements"""
    bl_idname = 'scene.at_mask'
    bl_label = "Mask"

    def execute(self, context):
        prop = context.scene.arraytools_prop
        grp = bpy.data.collections.get(at_array.Larray.grp_name)
        at_array.mask_obj(grp, prop.at_nb_mask)
        return{'FINISHED'}


class OBJECT_OT_reset_mask(bpy.types.Operator):
    """Reset masked objects"""
    bl_idname = 'scene.at_reset_mask'
    bl_label = "Reset mask"

    def execute(self, context):
        at_array.reset_mask()
        return{'FINISHED'}


class OBJECT_OT_modifiers(bpy.types.Operator):
    """Update modifiers for all copies"""
    bl_idname = 'scene.at_modifiers'
    bl_label = "Update Modifier(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        prop = scn.arraytools_prop
        at_array.add_del_modifiers(prop)
        return {'FINISHED'}


class ANIM_OT_anim_info(bpy.types.Operator):
    """Shows an info message for animation"""
    bl_idname = 'scene.at_anim_info'
    bl_label = "Informations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


class ANIM_OT_addkey(bpy.types.Operator):
    """Add or modify a keyframe for selected properties at the current frame"""
    bl_idname = 'scene.at_anim_addkey'
    bl_label = "Add a key"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prop = context.scene.arraytools_prop
        at_anim.add_keyframe(
            context.scene.frame_current, 0, prop.row, 0, prop.count,
            0, prop.alter
        )
        return {'FINISHED'}


class ANIM_OT_delkey(bpy.types.Operator):
    """Delete a keyframe for selected properties at the current frame"""
    bl_idname = 'scene.at_anim_delkey'
    bl_label = "Del a key"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prop = context.scene.arraytools_prop
        at_anim.del_keyframe(
            context.scene.frame_current, prop.row, prop.count, prop.alter
        )
        return {'FINISHED'}


class ANIM_OT_delallkeys(bpy.types.Operator):
    """Remove all keyframes"""
    bl_idname = 'scene.at_anim_delallkeys'
    bl_label = "Del all keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prop = context.scene.arraytools_prop
        at_anim.del_all_keyframes(
            context.scene.frame_current, prop.row, prop.count, prop.alter
        )
        at_anim.Anim.keys.clear()
        return {'FINISHED'}
