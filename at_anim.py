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
from mathutils import Matrix

from . import at_array as aa
from . import at_calc_func as acf


def mode_rotation(rotation_mode):
    if rotation_mode == 'QUATERNION':
        rotation = 'rotation_quaternion'
    elif rotation_mode == 'AXIS_ANGLE':
        rotation = 'rotation_axis_angle'
    else:
        rotation = 'rotation_euler'
    return rotation


class Anim(object):
    rotation_mode = 'rotation_euler'
    transforms = {
        0: [],
        1: ['location'],
        2: ['scale'],
        3: ['location', 'scale'],
        4: [rotation_mode],
        5: ['location', rotation_mode],
        6: ['scale', rotation_mode],
        7: ['location', 'scale', rotation_mode],
        8: ['hide_viewport'],
        9: ['location', 'hide_viewport'],
        10: ['scale', 'hide_viewport'],
        11: ['location', 'scale', 'hide_viewport'],
        12: [rotation_mode, 'hide_viewport'],
        13: ['location', rotation_mode, 'hide_viewport'],
        13: ['scale', rotation_mode, 'hide_viewport'],
        15: ['location', 'scale', rotation_mode, 'hide_viewport'],
        16: ['hide_render'],
        17: ['location', 'hide_render'],
        18: ['scale', 'hide_render'],
        19: ['location', 'scale', 'hide_render'],
        20: [rotation_mode, 'hide_render'],
        21: ['location', rotation_mode, 'hide_render'],
        22: ['scale', rotation_mode, 'hide_render'],
        23: ['location', 'scale', rotation_mode, 'hide_render'],
        24: ['hide_viewport', 'hide_render'],
        25: ['location', 'hide_viewport', 'hide_render'],
        26: ['scale', 'hide_viewport', 'hide_render'],
        27: ['location', 'scale', 'hide_viewport', 'hide_render'],
        28: [rotation_mode, 'hide_viewport', 'hide_render'],
        29: ['location', rotation_mode, 'hide_viewport', 'hide_render'],
        30: ['scale', rotation_mode, 'hide_viewport', 'hide_render'],
        31: ['location', 'scale', rotation_mode, 'hide_viewport', 'hide_render']
    }


def sum_tsr():
    """With location (1 or 0), scale (2 or 0), rotation (4 or 0),
    viewport visibility (8 or 0) and render visibility (16 or 0).
    The sum gives what to add to data_path"""
    p = bpy.context.scene.arraytools_prop
    return p.tr_anim + p.sc_anim*2 + p.rt_anim*4 + p.viewport_anim*8 + \
        p.render_anim*16


def which_transform(number):
    """Return the data_path according to the given number"""
    Anim.rotation_mode = mode_rotation(bpy.context.object.rotation_mode)
    return Anim.transforms[number]


def add_keyframe(aframe, row1, row2, col1, col2, alt1, alt2):
    """Add a keyframe for all objects in bank"""
    lsr = which_transform(sum_tsr())

    for i in range(row1, row2):
        for j in range(col1 + i*alt1, col2 + i*alt2):
            for name in aa.Larray.bank[i][j]:
                obj = bpy.data.objects.get(name)
                if obj is None:
                    continue
                for data in lsr:
                    obj.keyframe_insert(data_path=data, frame=aframe)


def del_all_keyframes(aframe, row, col, alt):
    """Remove all keyframes"""
    lsr = which_transform(sum_tsr())

    for i in range(row):
        for j in range(col + i*alt):
            for name in aa.Larray.bank[i][j]:
                obj = bpy.data.objects.get(name)
                if obj is None:
                    continue
                obj.animation_data_clear()


def del_keyframe(aframe, row, col, alt):
    """Delete a keyframe for all objects in bank"""
    lsr = which_transform(sum_tsr())

    for i in range(row):
        for j in range(col + i*alt):
            for name in aa.Larray.bank[i][j]:
                obj = bpy.data.objects.get(name)
                if obj is None:
                    continue
                for data in lsr:
                    obj.keyframe_delete(data_path=data, frame=aframe)


def modify_keyframe(aframe):
    pass

"""
def have_keyframe(aframe, obj):
    if obj.animation_data is not None and obj.animation_data.action is not None:
        for fcurve in obj.animation_data.action.fcurves:
            if aframe in (p.co.x for p in fcurve.keyframe_points):
                return True
    return False
"""
