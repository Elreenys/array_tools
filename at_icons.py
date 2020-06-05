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
import bpy.utils.previews
import os


class ImageIcon(object):
    icons_grp = {}


def register_icons():
    at_icons = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    dir_icons = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    for image in os.listdir(dir_icons):
        fname, ext = os.path.splitext(image)
        at_icons.load(fname, os.path.join(dir_icons, image), 'IMAGE')

    ImageIcon.icons_grp["main"] = at_icons


def unregister_icons():
    for at_icons in ImageIcon.icons_grp.values():
        bpy.utils.previews.remove(at_icons)
    ImageIcon.icons_grp.clear()

# N.B. : from Templates -> Python -> UI Previews Custom Icon
