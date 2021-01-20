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

from bl_ui.utils import PresetPanel
from bpy.types import Panel, AddonPreferences

from . import at_icons
from . import at_preset


# ---------------------------- Panels -------------------------------
class UIPANEL_PT_def(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Array Tools"


class UIPANEL_PT_trans(UIPANEL_PT_def):
    """Contains the settings for translation, scale and rotation array"""
    bl_label = "Array Tools"

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None and
            len(context.selected_objects) > 0 and
            (context.object.mode == 'OBJECT')
        )

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        my_prop = scn.arraytools_prop

        row = layout.row()
        row.operator('scene.at_op')

        if not my_prop.already_start:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="~ Click to begin ~")
        else:
            row = layout.row(align=True)
            row.operator("scene.at_reset_props", text='', icon='CANCEL')
            row.menu("AT_MT_preset_menu", text=at_preset.AT_MT_preset_menu.bl_label)
            row.operator("scene.at_add_preset", text='', icon='ADD')
            row.operator("scene.at_add_preset", text='', 
                icon='REMOVE').remove_active = True
            row = layout.row()

            row.prop(my_prop, 'is_copy')
            row.prop(my_prop, 'count')

            row = layout.row(align=True)
            row.scale_y = 0.7
            row.prop(my_prop, 'reference', text='')
            row.operator('scene.at_modifiers')

            box = layout.box()
            split = box.split(factor=0.55)
            split.label(text="Translation")
            row = split.row()
            row.prop(my_prop, 'tr_axis', expand=True)
            split = box.split()
            split.prop(my_prop, 'tr_offset')
            split.prop(my_prop, 'tr_global')

            row = layout.row()
            row.prop(my_prop, 'at_pivot')

            box = layout.box()
            split = box.split(factor=0.55)
            split.label(text="Scaling (%)")
            row = split.row()
            row.prop(my_prop, 'sc_method', expand=True)
            split = box.split()
            split.prop(my_prop, 'sc_offset')
            split.prop(my_prop, 'sc_global')

            box = layout.box()
            split = box.split(factor=0.55)
            if scn.unit_settings.system_rotation == 'DEGREES':
                split.label(text="Rotation (Degrees)")
            else:
                split.label(text="Rotation (Radians)")
            row = split.row()
            row.prop(my_prop, 'rot_axis', expand=True)

            split = box.split(factor=0.08)

            col = split.column(align=True)
            col.label(text='')
            col.operator('scene.x360', text='X')
            col.operator('scene.y360', text='Y')
            col.operator('scene.z360', text='Z')

            col = split.column()
            col.prop(my_prop, 'rot_offset')
            col = split.column()
            col.prop(my_prop, 'rot_global')

            box = layout.box()
            row = box.row()
            row.scale_y = 1.5
            row.operator('scene.at_done')
            row.operator('scene.at_cancel')

            row = box.row()
            row.scale_y = 0.3
            row.alignment = 'CENTER'
            row.label(text="~ Transforms are NOT applied ~")


class UIPANEL_PT_rows(UIPANEL_PT_def):
    """Panel containing the row options"""
    bl_parent_id = 'UIPANEL_PT_trans'
    bl_label = 'Rows Options'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        my_prop = context.scene.arraytools_prop

        if my_prop.already_start:
            row = layout.row()
            row.prop(my_prop, 'count')
            row.prop(my_prop, 'row')
            row = layout.row()

            row.scale_y = 0.8
            row.prop(my_prop, 'align', icon_only=True, expand=True)
            row.prop(my_prop, 'alter')
            row = layout.row()

            row.alignment = 'CENTER'
            row.scale_x = 1.5
            row.scale_y = 0.6
            row.label(text=" - Offset Settings -")
            row.scale_x = 0.8
            row.operator('scene.at_reset_second')

            layout.use_property_split = True

            col = layout.column()
            row = col.row(align=True)
            row.prop(my_prop, 'tr_second')
            col = layout.column()
            row = col.row(align=True)
            row.prop(my_prop, 'sc_second')
            col = layout.column()
            row = col.row(align=True)
            row.prop(my_prop, 'rot_second')

            row = layout.row()
            row.scale_y = 0.5
            row.label(
                text="Total : " + my_prop.total +
                "    |    current Row : " + my_prop.erow
            )


class UIPANEL_PT_options(UIPANEL_PT_def):
    """Panel containing the random options"""
    bl_parent_id = 'UIPANEL_PT_trans'
    bl_label = 'Random Options'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        my_prop = context.scene.arraytools_prop

        layout.enabled = my_prop.already_start
        row = layout.row()
        row.alignment = 'CENTER'
        row.prop(my_prop, 'at_seed')
        row = layout.row()
        row.prop(my_prop, 'at_mode', expand=True)
        row = layout.row()
        if my_prop.at_mode == 'SIM':
            row.prop(my_prop, 'at_is_tr')
            row.prop(my_prop, 'tr_rand', text='')
            row = layout.row()
            row.prop(my_prop, 'at_is_sc')
            row.prop(my_prop, 'sc_rand', text='')
            row = layout.row()
            row.prop(my_prop, 'at_is_rot')
            row.prop(my_prop, 'rot_rand', text='')
        else:
            row.label(text='')
            row.label(text='X')
            row.label(text='Y')
            row.label(text='Z')
            row = layout.row()
            row.prop(my_prop, 'at_is_tr')
            row.scale_x = 0.5
            row.scale_y = 0.7
            row.operator('scene.at_reset_tr')
            row.operator('scene.fill_tr')
            row = layout.row()
            row.prop(my_prop, 'tr_min')
            row = layout.row()
            row.prop(my_prop, 'tr_max')
            row = layout.row()

            row.prop(my_prop, 'at_is_sc')
            row.scale_x = 0.5
            row.scale_y = 0.7
            row.operator('scene.at_reset_sc')
            row.operator('scene.fill_sc')
            row = layout.row()
            row.alignment = "CENTER"
            row.scale_y = 0.7
            row.prop(my_prop, 'sc_all')
            row = layout.row(align=True)
            row.label(text='min:')
            row.prop(my_prop, 'sc_min_x', text='')
            row.prop(my_prop, 'sc_min_y', text='')
            row.prop(my_prop, 'sc_min_z', text='')
            row = layout.row(align=True)
            row.label(text='max:')
            row.prop(my_prop, 'sc_max_x', text='')
            row.prop(my_prop, 'sc_max_y', text='')
            row.prop(my_prop, 'sc_max_z', text='')

            row = layout.row()
            row.prop(my_prop, "at_is_rot")
            row.scale_x = 0.5
            row.scale_y = 0.7
            row.operator('scene.at_reset_rot')
            row.operator('scene.fill_rot')
            row = layout.row()
            row.prop(my_prop, 'rot_min')
            row = layout.row()
            row.prop(my_prop, 'rot_max')

        row = layout.row()
        row.alignment = "CENTER"
        row.label(text="___________________________")
        box = layout.box()
        row = box.row()
        row.prop(my_prop, 'at_nb_mask')
        row = box.row()
        row.operator('scene.at_mask')
        row.operator('scene.at_reset_mask')


class UIPANEL_PT_anim(UIPANEL_PT_def):
    """Panel containing the animation options"""
    bl_label = 'Animation Options'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.arraytools_prop.already_start

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        my_prop = context.scene.arraytools_prop
        icons = at_icons.ImageIcon.icons_grp["main"]

        row = layout.row()
        row.prop(scn, 'frame_start', text='Start')
        row.prop(scn, 'frame_end', text='End')
        row = layout.row()
        row.prop(scn, 'frame_current')
        row = layout.row()

        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.scale_x = 1.5
        row.scale_y = 1.5
        row.prop(
            my_prop, "tr_anim", toggle=True, icon_only=True,
            icon_value=icons["location"].icon_id
        )
        row.prop(
            my_prop, "sc_anim", toggle=True, icon_only=True,
            icon_value=icons["scale"].icon_id
        )
        row.prop(
            my_prop, "rt_anim", toggle=True, icon_only=True,
            icon_value=icons["rotation"].icon_id
        )
        row.prop(
            my_prop, "viewport_anim", toggle=True, icon_only=True,
            icon='RESTRICT_VIEW_OFF'
        )
        row.prop(
            my_prop, "render_anim", toggle=True, icon_only=True,
            icon='RESTRICT_RENDER_OFF'
        )

        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.scale_x = 2
        row.operator(
            'scene.at_anim_addkey', text='',
            icon_value=icons["key_add"].icon_id
        )
        row.operator(
            'scene.at_anim_delkey', text='',
            icon_value=icons["key_del"].icon_id
        )
        row.operator(
            'scene.at_anim_delallkeys', text='',
            icon_value=icons["key_all"].icon_id
        )

        row = layout.row()
        row.prop(my_prop, 'anim_mode', expand=True)

        row = layout.row()
        row.scale_y = 0.3
        row.label(text="Max Count : " + str(my_prop.count))
        row.label(text="Max Row : " + str(my_prop.row))

        if my_prop.anim_mode == '1':
            row = layout.row()
            row.prop(my_prop, 'anim_count')
            row.prop(my_prop, 'anim_row')

            row = layout.row()
            row.scale_y = 0.8
            row.prop(my_prop, 'align', icon_only=True, expand=True)
            row.prop(my_prop, 'anim_alter')
        else:
            row = layout.row()
            row.prop(my_prop, 'count')
            row.prop(my_prop, 'row')

            row = layout.row()
            row.scale_y = 0.8
            row.prop(my_prop, 'align', icon_only=True, expand=True)
            row.prop(my_prop, 'alter')

        row = layout.row()
        row.scale_y = 0.7
        split = row.split(factor=0.55)
        split.label(text="Translation")
        row = split.row()
        row.prop(my_prop, 'tr_axis', expand=True)

        row = layout.row()
        box = row.box()
        split = box.split(align=True)
        split.prop(my_prop, 'tr_offset')
        split.prop(my_prop, 'tr_global')
        split = row.split()
        split.prop(my_prop, 'tr_second', text='Row')

        row = layout.row()
        row.scale_y = 0.7
        split = row.split(factor=0.55)
        split.label(text="Scaling (%)")
        row = split.row()
        row.prop(my_prop, 'sc_method', expand=True)

        row = layout.row()
        box = row.box()
        split = box.split(align=True)
        split.prop(my_prop, 'sc_offset')
        split.prop(my_prop, 'sc_global')
        split = row.split()
        split.prop(my_prop, 'sc_second', text='Row')

        row = layout.row()
        row.scale_y = 0.7
        row.prop(my_prop, 'at_pivot')

        row = layout.row()
        row.scale_y = 0.7
        split = row.split(factor=0.55)
        if scn.unit_settings.system_rotation == 'DEGREES':
            split.label(text="Rotation (Degrees)")
        else:
            split.label(text="Rotation (Radians)")
        row = split.row()
        row.prop(my_prop, 'rot_axis', expand=True)

        row = layout.row()
        box = row.box()
        split = box.split(factor=0.08, align=True)
        col = split.column(align=True)
        col.label(text='')
        col.operator('scene.x360', text='X')
        col.operator('scene.y360', text='Y')
        col.operator('scene.z360', text='Z')

        split.prop(my_prop, 'rot_offset')
        split.prop(my_prop, 'rot_global')
        split = row.split()
        split.prop(my_prop, 'rot_second', text='Row')

        row = layout.row()
        row.scale_y = 0.7
        row.prop(my_prop, 'at_mode', expand=True)
        row = layout.row()
        row.scale_y = 0.8
        row.alignment = 'CENTER'
        row.prop(my_prop, 'at_seed')

        row = layout.row()
        if my_prop.at_mode == 'SIM':
            row.prop(my_prop, 'at_is_tr')
            row.prop(my_prop, 'tr_rand', text='')
            row = layout.row()
            row.prop(my_prop, 'at_is_sc')
            row.prop(my_prop, 'sc_rand', text='')
            row = layout.row()
            row.prop(my_prop, 'at_is_rot')
            row.prop(my_prop, 'rot_rand', text='')
        else:
            row.scale_y = 0.4
            row.label(text='')
            row.label(text='X')
            row.label(text='Y')
            row.label(text='Z')
            row = layout.row()
            row.prop(my_prop, 'at_is_tr')
            row.scale_x = 0.5
            row.scale_y = 0.7
            row.operator('scene.at_reset_tr')
            row.operator('scene.fill_tr')
            row = layout.row()
            row.scale_y = 0.8
            row.prop(my_prop, 'tr_min')
            row = layout.row()
            row.scale_y = 0.8
            row.prop(my_prop, 'tr_max')
            row = layout.row()

            row.prop(my_prop, 'at_is_sc')
            row.scale_x = 0.5
            row.scale_y = 0.7
            row.operator('scene.at_reset_sc')
            row.operator('scene.fill_sc')
            row = layout.row()
            row.alignment = "CENTER"
            row.scale_y = 0.7
            row.prop(my_prop, 'sc_all')
            row = layout.row(align=True)
            row.scale_y = 0.8
            row.label(text='min:')
            row.prop(my_prop, 'sc_min_x', text='')
            row.prop(my_prop, 'sc_min_y', text='')
            row.prop(my_prop, 'sc_min_z', text='')
            row = layout.row(align=True)
            row.scale_y = 0.8
            row.label(text='max:')
            row.prop(my_prop, 'sc_max_x', text='')
            row.prop(my_prop, 'sc_max_y', text='')
            row.prop(my_prop, 'sc_max_z', text='')

            row = layout.row()
            row.prop(my_prop, "at_is_rot")
            row.scale_x = 0.5
            row.scale_y = 0.7
            row.operator('scene.at_reset_rot')
            row.operator('scene.fill_rot')
            row = layout.row()
            row.scale_y = 0.8
            row.prop(my_prop, 'rot_min')
            row = layout.row()
            row.scale_y = 0.8
            row.prop(my_prop, 'rot_max')

class UIPANEL_PT_user_infos(UIPANEL_PT_def):
    """Panel containing tips"""
    bl_parent_id = 'UIPANEL_PT_trans'
    bl_label = 'Tips'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Do you know the Blender Backspace shortcut ?", icon='INFO')
        row = layout.row()
        row.label(text="Reset values with it!")

panels = (
    UIPANEL_PT_user_infos, UIPANEL_PT_options, UIPANEL_PT_rows, 
    UIPANEL_PT_trans, UIPANEL_PT_anim
)


# ---------------------------- Preferences --------------------------
def update_category(self, context):
    """Update the tab category of the addon"""
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)
        prefs = context.preferences.addons[__package__].preferences

        UIPANEL_PT_def.bl_category = prefs.category
        for panel in reversed(panels):
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\nError in updating category tab")
        pass


class ArrayToolsPrefs(AddonPreferences):
    bl_idname = __package__

    category: bpy.props.StringProperty(
        name="Category",
        default="Array Tools",
        update=update_category
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 0.2
        row.alignment = 'CENTER'
        row.label(text=" ~ Choose the tab name for the addon. ~")
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Tab Name: ")
        row.alignment = 'LEFT'
        row.prop(self, 'category', text='')
