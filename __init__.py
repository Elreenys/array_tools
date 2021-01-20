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
import bpy

from . import at_array
from . import at_icons
from . import at_properties
from . import at_preset

bl_info = {
    "name": "Array_Tools",
    "author": "Elreenys",
    "description": "Tools to create array of objects",
    "blender": (2, 91, 0),
    "version": (2, 1, 0),
    "location": "View3D > sidebar > array tools tab",
    "category": "Object",
    "wiki_url": "https://github.com/Elreenys/array_tools/wiki"
}

classes = (
    at_operators.OBJECT_OT_at_start,
    at_operators.OBJECT_OT_at_cancel,
    at_operators.OBJECT_OT_at_done,
    at_operators.OBJECT_OT_fill_tr,
    at_operators.OBJECT_OT_fill_sc,
    at_operators.OBJECT_OT_fill_rot,
    at_operators.OBJECT_OT_x360,
    at_operators.OBJECT_OT_y360,
    at_operators.OBJECT_OT_z360,
    at_operators.OBJECT_OT_reset_tr,
    at_operators.OBJECT_OT_reset_sc,
    at_operators.OBJECT_OT_reset_rot,
    at_operators.OBJECT_OT_reset_second,
    at_operators.OBJECT_OT_error,
    at_operators.OBJECT_OT_mask,
    at_operators.OBJECT_OT_reset_mask,
    at_operators.OBJECT_OT_modifiers,
    at_operators.ANIM_OT_addkey,
    at_operators.ANIM_OT_delkey,
    at_operators.ANIM_OT_delallkeys,

    at_operators.OBJECT_OT_reset_properties,
    at_preset.AT_MT_preset_menu,
    at_preset.AT_OT_AddPreset,

    at_panels.UIPANEL_PT_anim,
    at_panels.UIPANEL_PT_trans,
    at_panels.UIPANEL_PT_rows,
    at_panels.UIPANEL_PT_options,
    at_panels.UIPANEL_PT_user_infos,
    at_properties.ArrayTools_props,
    at_panels.ArrayToolsPrefs
)


def register():
    scene = bpy.types.Scene
    pp = bpy.props.PointerProperty

    at_icons.register_icons()
    for cls in classes:
        bpy.utils.register_class(cls)
    scene.arraytools_prop = pp(type=at_properties.ArrayTools_props)
    at_panels.update_category(None, bpy.context)


def unregister():
    at_icons.unregister_icons()
    del bpy.types.Scene.arraytools_prop
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
