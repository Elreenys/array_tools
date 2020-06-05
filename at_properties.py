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
import math
from bpy.types import PropertyGroup
from mathutils import Vector

from . import at_array as aa
from . import at_anim
from . import at_calc_func as acf
from . import at_panels
from . import at_operators
from . import at_icons


def crea_anim(self, context):
    custom = at_icons.ImageIcon.icons_grp['main']

    return [
        ('0', 'Creation', "Add or remove elements",
            custom["creation"].icon_id, 0),
        ('1', 'Animation', "Animate the array",
            custom["animation"].icon_id, 1)
    ]


def get_count(self):
    return self.get("count", 2)


def set_count(self, value):
    self.old_count = self.get("count", 2)
    self["count"] = value


def get_row(self):
    return self.get("row", 1)


def set_row(self, value):
    self.old_row = self.get("row", 1)
    self["row"] = value


def get_alter(self):
    return self.get("alter", 0)


def set_alter(self, value):
    self.old_alter = self.get("alter", 0)
    self["alter"] = value


# -------------------------------------------------------------------
def get_anim_count(self):
    return self.get("anim_count", 2)


def set_anim_count(self, value):
    self.anim_old_count = self.get("anim_count", 2)
    self["anim_count"] = value if value < self.count else self.count


def get_anim_row(self):
    return self.get("anim_row", 1)


def set_anim_row(self, value):
    self.anim_old_row = self.get("anim_row", 1)
    self["anim_row"] = value if value < self.row else self.row


def get_anim_alter(self):
    return self.get("anim_alter", 0)


def set_anim_alter(self, value):
    self.anim_old_alter = self.get("anim_alter", 0)
    self["anim_alter"] = value if value < self.alter else self.alter


# -------------------------------------------------------------------
def elem_in_row(column, row, indice):
    """Return the number of elements in a row"""
    elements = column + (row - 1) * indice
    # print("row elements =", elements)
    return elements


def cancel_array():
    """Call the operator if a problem occurs"""
    bpy.ops.scene.at_cancel()


def items_refs(self, context):
    return aa.Larray.items


def select_ref(self, context):
    aa.select_all(self.row, self.count, self.alter, int(self.reference))


# ---------------------------- Properties ---------------------------
class ArrayTools_props(PropertyGroup):
    """Properties for array tools"""

    def at_del_all(self, del_rall):
        """Delete all copies and remove objects from lists
        del_rall : boolean, True to del reference object from list
        """
        grp = bpy.data.collections.get(aa.Larray.grp_name)
        refs = aa.Larray.bank[0][0]
        for i in range(self.row):
            elem = aa.pop_row(i)
            for elem in reversed(elem):
                if elem in refs:
                    continue
                # test if object exist
                obj = bpy.data.objects.get(elem)
                if obj is not None:
                    col = obj.users_collection[0]
                    col.objects.unlink(obj)
                    bpy.data.objects.remove(obj, do_unlink=True)

        if del_rall:
            aa.Larray.bank.clear()
            # removing the collection if empty
            if grp is not None and not grp.objects:
                bpy.data.collections.remove(grp)
        else:
            aa.Larray.bank.append([[[refs]]])
        # print("Del_all done!")

    # ----------------------- UI update -----------------------------
    # ---------------------------------------------------------------
    # ----------------------- count update --------------------------
    def update_count(self, context):
        """update the number of element(s) in column"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            difference = self.count - self.old_count
            self.update_infos()

            if difference > 0:
                aa.add_column(
                    aa.Larray.bank[0][0], aa.Larray.grp_name,
                    self.row, self.old_count, self.count, self.alter
                )
                aa.to_hide(
                    0, self.anim_row, self.anim_count,
                    self.old_count, 0, self.anim_alter, False
                )
            elif difference < 0:
                aa.del_col(self.row, self.count, -difference)
                aa.to_hide(
                    0, self.anim_row, self.anim_count,
                    self.count, 0, self.anim_alter, False
                )

            if self.is_tr_off_last:
                self.update_offset(context)
            else:
                self.update_global(context)

            self.anim_count = self.update_ui(self.count)
            self.anim_old_count = self.count

    # ----------------------- Row update ----------------------------
    def update_row(self, context):
        """Update row property"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            if self.alter < 0 and self.maxrow < self.row:
                aa.display_error(
                    "Maximun rows for these settings is : " + str(self.maxrow)
                )
                self.row = self.update_ui(self.maxrow)
                return

            difference = self.row - self.old_row
            if difference > 0:
                aa.add_row(
                    aa.Larray.bank[0][0], aa.Larray.grp_name,
                    self.old_row, self.row, self.count, self.alter
                )
                aa.to_hide(
                    self.anim_row, self.old_row, 0,
                    self.count, 0, self.anim_alter, False
                )
                if self.is_tr_off_last:
                    self.update_offset(context)
                else:
                    self.update_global(context)
            elif difference < 0:
                aa.del_row(self.old_row, self.row)
                aa.to_hide(
                    self.anim_row, self.row, 0,
                    self.count, 0, self.anim_alter, False
                )

            line = elem_in_row(self.count, self.row, self.alter)

            self.anim_row = self.update_ui(self.row)
            self.anim_old_row = self.row
            self.update_infos()

    # ----------------------- Alter update --------------------------
    def update_alter(self, context):
        """Update alter property"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            # alter must have at least 2 rows
            if self.row == 1 and self.alter != 0:
                aa.display_error("Add more rows first.")
                self.alter = self.update_ui(0)
                return
            if self.alter < 0:
                """ (column + (row - 1)* alter) is the number of elements
                 of the last row and must be at least >= 1
                 """
                alter = int((1 - self.count) / (self.row - 1))
                if self.alter < alter:
                    aa.display_error(
                        "Min variation is '" + str(alter) +
                        "' for these settings."
                    )
                    self.alter = self.update_ui(alter)
                    return

            self.anim_alter = self.update_ui(self.alter)
            self.update_ralign()

            difference = self.alter - self.old_alter
            if difference > 0:
                aa.add_alt(
                    aa.Larray.bank[0][0], aa.Larray.grp_name, self.row,
                    self.count, self.old_alter, self.alter
                )
            elif difference < 0:
                aa.del_alt(
                    self.row, self.count,
                    self.old_alter, self.alter
                )

            if self.is_tr_off_last:
                self.update_offset(context)
            else:
                self.update_global(context)

            # print(f"count={self.count}, row={self.row}, alter={self.alter}")
            line = elem_in_row(self.count, self.row, self.alter)
            # print("elems in row =", line)

            self.update_infos()

    # ----------------------- Align update --------------------------
    def update_ralign(self):
        """Update the value of the align vector"""
        decal = -self.alter * self.tr_offset
        if self.align == 'LEFT':
            self.ralign = Vector((0.0, 0.0, 0.0))
        elif self.align == 'CENTER':
            self.ralign = decal / 2
        elif self.align == 'RIGHT':
            self.ralign = decal

    def update_align(self, context):
        """According to the value of align, calculate ralign"""
        self.update_ralign()

        if self.is_tr_off_last:
            self.update_offset(context)
        else:
            self.update_global(context)

    # ---------------------------------------------------------------
    def update_infos(self):
        """Update properties total and erow"""
        sum = acf.sum_serie(self.row, self.alter)
        square = self.count * self.row
        if self.alter >= 0:
            self.maxrow = self.row
        else:
            ca = self.count // -self.alter
            self.maxrow = ca if self.count % self.alter == 0 else ca + 1
        self.total = str(int(square + sum))
        self.erow = str(elem_in_row(self.count, self.row, self.alter))

    # ---------------------------------------------------------------
    def update_ui(self, val):
        """Return the value to modify a property"""
        self.is_prog_change = True
        return val

    # ---------------------------------------------------------------
    def update_offset(self, context):
        """Update for all offsets"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            # user change offset
            self.is_tr_off_last = True

            if not int(self.anim_mode):
                # creation mod
                row = self.row
                count = self.count
                alter = self.alter
            else:
                # animation mod
                row = self.anim_row
                count = self.anim_count
                alter = self.anim_alter

            # get scale calculation functions according to the choosen method
            fsc = aa.Fsc.sc[self.sc_method]

            aloc, asc, arot = aa.place_obj(
                row, count, alter, self.tr_offset, self.sc_offset,
                self.rot_offset, self.tr_second, self.sc_second,
                self.rot_second, self.ralign,
                (int(self.tr_axis), int(self.rot_axis)), fsc[1], fsc[2]
            )
            if aa.Larray.to_del:
                aa.display_error("(1)Invalid reference(s) : duplicates will be deleted.")
                aa.del_ref_n_copy(self.row, self.count, self.alter, aa.Larray.to_del)

            # since offset changes, global too
            self.tr_global = self.update_ui(aloc)
            self.sc_global = self.update_ui(asc)
            self.rot_global = self.update_ui(arot)
            self.call_random(context)

    def update_global(self, context):
        """Update for all globals"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            # user change global
            self.is_tr_off_last = False

            if not int(self.anim_mode):
                # creation mod
                row = self.row
                count = self.count
                alter = self.alter
            else:
                # animation mod
                row = self.anim_row
                count = self.anim_count
                alter = self.anim_alter

            toff = acf.find_tr_offset(count, self.tr_global)
            roff = acf.find_ro_offset(count, self.rot_global, bool(self.at_pivot))

            fsc = aa.Fsc.sc[self.sc_method]
            soff = fsc[0](count, self.sc_global)

            aa.place_obj(
                row, count, alter, toff, soff, roff, self.tr_second,
                self.sc_second, self.rot_second, self.ralign,
                (int(self.tr_axis), int(self.rot_axis)), fsc[1], fsc[2]
            )

            if aa.Larray.to_del:
                aa.display_error("(2)Invalid reference(s) : duplicates will be deleted.")
                aa.del_ref_n_copy(self.row, self.count, self.alter, aa.Larray.to_del)

            # since global changes, UI offset must be update
            self.tr_offset = self.update_ui(toff)
            self.sc_offset = self.update_ui(soff)
            self.rot_offset = self.update_ui(roff)
            self.call_random(context)

    def update_second(self, context):
        """Update the secondary transforms"""
        # linear method for scale
        if not int(self.sc_method):
            aa.place_obj(
                self.row, self.count, self.alter, self.tr_offset,
                self.sc_offset, self.rot_offset, self.tr_second,
                self.sc_second, self.rot_second, self.ralign,
                (int(self.tr_axis), int(self.rot_axis)),
                acf.scale_linear, acf.linear_global
            )
        else:
            aa.place_obj(
                self.row, self.count, self.alter, self.tr_offset,
                self.sc_offset, self.rot_offset, self.tr_second,
                self.sc_second, self.rot_second, self.ralign,
                (int(self.tr_axis), int(self.rot_axis)),
                acf.scale_calc, acf.calc_global
            )

        if aa.Larray.to_del:
            aa.display_error("(3)Invalid reference(s) : duplicates will be deleted.")
            aa.del_ref_n_copy(self.row, self.count, self.alter, aa.Larray.to_del)
        self.update_seed(context)

    def update_orient(self, context):
        """Recalculate transforms if changes append"""
        if self.is_tr_off_last:
            self.update_offset(context)
        else:
            self.update_global(context)

    # ----------------------- random part ---------------------------
    # ---------------------------------------------------------------
    def call_random(self, context):
        if self.at_mode == 'ADV':
            sc_min = (self.sc_min_x, self.sc_min_y, self.sc_min_z)
            sc_max = (self.sc_max_x, self.sc_max_y, self.sc_max_z)

            acf.at_random(
                self.at_seed, self.count, self.row, self.tr_min,
                self.tr_max, sc_min, sc_max, self.rot_min, self.rot_max,
                self.at_is_tr, self.at_is_sc, self.at_is_rot, self.sc_all,
                self.tr_offset, self.tr_second, self.sc_offset,
                self.sc_second, self.rot_offset, self.rot_second,
                self.alter, self.ralign, int(self.sc_method),
                int(self.tr_axis), int(self.rot_axis)
            )
        else:
            # simple mode
            vec = acf.xyz_axis()
            tr = self.tr_rand * vec
            sc = self.sc_rand * vec
            rot = self.rot_rand * vec
            acf.at_random(
                self.at_seed, self.count, self.row, -tr, tr, sc,
                100*vec, -rot, rot, self.at_is_tr, self.at_is_sc,
                self.at_is_rot, False, self.tr_offset, self.tr_second,
                self.sc_offset, self.sc_second, self.rot_offset,
                self.rot_second, self.alter, self.ralign,
                int(self.sc_method), int(self.tr_axis), int(self.rot_axis)
            )

    def update_seed(self, context):
        if self.is_tr_off_last:
            self.update_offset(context)
        else:
            self.update_global(context)

    def update_rtr(self, context):
        """random translation in simple mode update adv mode"""
        self.tr_max = self.tr_rand * Vector((1.0, 1.0, 1.0))
        self.tr_min = self.tr_rand * Vector((-1.0, -1.0, -1.0))

    def update_rsc(self, context):
        """random scale in simple mode update adv mode"""
        self.sc_max_x, self.sc_max_y, self.sc_max_z = (100.0, 100.0, 100.0)
        rand = self.sc_rand
        self.sc_min_x = rand
        self.sc_min_y = rand
        self.sc_min_z = rand

    def update_rrot(self, context):
        """random rotation in simple mode update adv mode"""
        self.rot_max = self.rot_rand * Vector((1.0, 1.0, 1.0))
        self.rot_min = self.rot_rand * Vector((-1.0, -1.0, -1.0))

    # -------------- update min and max -----------------------------
    # if user enter a max value < min, change min and vice versa
    def up_tr_min(self, context):
        """Update tr_max if tr_min is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            for i in range(3):
                if self.tr_min[i] > self.tr_max[i]:
                    self.is_prog_change = True
                    self.tr_max[i] = self.tr_min[i]

    def up_tr_max(self, context):
        """Update tr_min if tr_max is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            for i in range(3):
                if self.tr_min[i] > self.tr_max[i]:
                    self.is_prog_change = True
                    self.tr_min[i] = self.tr_max[i]

    def up_sc_min_x(self, context):
        """Update sc_max_x if sc_min_x is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_x > self.sc_max_x
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.sc_max_x = self.update_ui(self.sc_min_x)

                # with uniform : min_x = min_y = min_z same for max_
                self.sc_min_y = self.update_ui(self.sc_min_x)
                self.sc_min_z = self.update_ui(self.sc_min_x)
                self.sc_max_y = self.update_ui(self.sc_min_x)
                self.sc_max_z = self.update_ui(self.sc_min_x)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.sc_min_y = self.update_ui(self.sc_min_x)
                self.sc_min_z = self.update_ui(self.sc_min_x)
                self.sc_max_y = self.update_ui(self.sc_max_x)
                self.sc_max_z = self.update_ui(self.sc_max_x)
            elif test:
                # case : min > max and uniform = False
                self.sc_max_x = self.update_ui(self.sc_min_x)

    def up_sc_min_y(self, context):
        """Update sc_max_y if sc_min_y is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_y > self.sc_max_y
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.sc_max_y = self.update_ui(self.sc_min_y)
                # with uniform : min_x = min_y = min_z same for max_
                self.sc_min_x = self.update_ui(self.sc_min_y)
                self.sc_min_z = self.update_ui(self.sc_min_y)
                self.sc_max_x = self.update_ui(self.sc_min_y)
                self.sc_max_y = self.update_ui(self.sc_min_y)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.sc_min_x = self.update_ui(self.sc_min_y)
                self.sc_min_z = self.update_ui(self.sc_min_y)
                self.sc_max_x = self.update_ui(self.sc_max_y)
                self.sc_max_z = self.update_ui(self.sc_max_y)
            elif test:
                # case : min > max and uniform = False
                self.sc_max_y = self.update_ui(self.sc_min_y)

    def up_sc_min_z(self, context):
        """Update sc_max_z if sc_min_z is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_z > self.sc_max_z
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.sc_max_z = self.update_ui(self.sc_min_z)
                # with uniform : min_x = min_y = min_z same for max_
                self.sc_min_x = self.update_ui(self.sc_min_z)
                self.sc_min_y = self.update_ui(self.sc_min_z)
                self.sc_max_x = self.update_ui(self.sc_min_z)
                self.sc_max_y = self.update_ui(self.sc_min_z)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.sc_min_x = self.update_ui(self.sc_min_z)
                self.sc_min_y = self.update_ui(self.sc_min_z)
                self.sc_max_x = self.update_ui(self.sc_max_z)
                self.sc_max_y = self.update_ui(self.sc_max_z)
            elif test:
                # case : min > max and uniform = False
                self.sc_max_y = self.update_ui(self.sc_min_z)

    def up_sc_max_x(self, context):
        """Update sc_min_x if sc_max_x is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_x > self.sc_max_x
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.sc_min_x = self.update_ui(self.sc_max_x)
                # with uniform : min_x = min_y = min_z same for max_
                self.sc_max_y = self.update_ui(self.sc_max_x)
                self.sc_max_z = self.update_ui(self.sc_max_x)
                self.sc_min_y = self.update_ui(self.sc_max_x)
                self.sc_min_z = self.update_ui(self.sc_max_x)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.sc_max_y = self.update_ui(self.sc_max_x)
                self.sc_max_z = self.update_ui(self.sc_max_x)
                self.sc_min_y = self.update_ui(self.sc_min_x)
                self.sc_min_z = self.update_ui(self.sc_min_x)
            elif test:
                # case : min > max and uniform = False
                self.sc_min_x = self.update_ui(self.sc_max_x)

    def up_sc_max_y(self, context):
        """Update sc_min_y if sc_max_y is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_y > self.sc_max_y
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.sc_min_y = self.update_ui(self.sc_max_y)
                # with uniform : min_x = min_y = min_z same for max_
                self.sc_max_x = self.update_ui(self.sc_max_y)
                self.sc_max_z = self.update_ui(self.sc_max_y)
                self.sc_min_x = self.update_ui(self.sc_max_y)
                self.sc_min_z = self.update_ui(self.sc_max_y)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.sc_max_x = self.update_ui(self.sc_max_y)
                self.sc_max_z = self.update_ui(self.sc_max_y)
                self.sc_min_x = self.update_ui(self.sc_min_y)
                self.sc_min_z = self.update_ui(self.sc_min_y)
            elif test:
                # case : min > max and uniform = False
                self.sc_min_y = self.update_ui(self.sc_max_y)

    def up_sc_max_z(self, context):
        """Update sc_min_z if sc_max_z is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_z > self.sc_max_z
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.sc_min_z = self.update_ui(self.sc_max_z)
                # with uniform : min_x = min_y = min_z same for max_
                self.sc_max_x = self.update_ui(self.sc_max_z)
                self.sc_max_y = self.update_ui(self.sc_max_z)
                self.sc_min_x = self.update_ui(self.sc_max_z)
                self.sc_min_y = self.update_ui(self.sc_max_z)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.sc_max_x = self.update_ui(self.sc_max_z)
                self.sc_max_y = self.update_ui(self.sc_max_z)
                self.sc_min_x = self.update_ui(self.sc_min_z)
                self.sc_min_y = self.update_ui(self.sc_min_z)
            elif test:
                # case : min > max and uniform = False
                self.sc_min_z = self.update_ui(self.sc_max_z)

    def up_rot_min(self, context):
        """Update rot_max if rot_min is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            for i in range(3):
                if self.rot_min[i] > self.rot_max[i]:
                    self.is_prog_change = True
                    self.rot_max[i] = self.rot_min[i]

    def up_rot_max(self, context):
        """Update rot_min if rot_max is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            for i in range(3):
                if self.rot_min[i] > self.rot_max[i]:
                    self.is_prog_change = True
                    self.rot_min[i] = self.rot_max[i]

    # -------------------- Animation update -------------------------
    def update_anim_count(self, context):
        """Simulate a change of elements in column"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            """
            if self.anim_count > self.count:
                aa.display_error(f"Columns can't be higher than {self.count}")
                self.anim_count = self.update_ui(self.count)
                return
            """
            difference = self.anim_count - self.anim_old_count

            if difference < 0:
                """
                [0 .. anim_count] => visible
                [anim_count .. anim_old_count] => make invisible"""
                aa.to_hide(
                    0, self.anim_row, self.anim_count, self.anim_old_count,
                    self.anim_alter, self.anim_alter, True
                )
            elif difference > 0:
                """
                [anim_old_count .. anim_count] => make visible
                [anim_count .. count] => invisible"""
                # to_hide(old_row, row, old_col, col, old_alt, alt, is_hide)
                aa.to_hide(
                    0, self.anim_row, self.anim_old_count, self.anim_count,
                    self.anim_alter, self.anim_alter, False
                )
            else:
                return
            if self.is_tr_off_last:
                self.update_offset(context)
            else:
                self.update_global(context)

    def max_anim_row(self):
        if self.anim_alter >= 0:
            self.maxanimrow = self.anim_row
        else:
            ca = self.anim_count // -self.anim_alter
            self.maxanimrow = ca if self.anim_count % self.anim_alter == 0 else ca + 1

    def update_anim_row(self, context):
        """Simulate a change of elements in column"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            if self.anim_alter < 0 and self.maxanimrow < self.anim_row:
                aa.display_error("Maximun rows for \
                    these settings is : " + str(self.maxrow))
                self.anim_row = self.update_ui(self.maxanimrow)
                return

            difference = self.anim_row - self.anim_old_row

            if difference < 0:
                """
                [0 .. anim_row] => visible
                [anim_row .. old_row] => make invisible"""
                aa.to_hide(
                    self.anim_row, self.anim_old_row, 0,
                    self.anim_count, 0, self.anim_alter, True
                )
            elif difference > 0:
                """
                [0 .. anim_old_row] => visible
                [anim_old_row .. anim_row] => make visible"""
                aa.to_hide(
                    self.anim_old_row, self.anim_row, 0,
                    self.anim_count, 0, self.anim_alter, False
                )

            self.max_anim_row()

    def update_anim_alter(self, context):
        """Simulate a change of elements in column"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            if self.anim_alter < 0:
                """ (column + (row - 1)* alter) is the number of elements
                 of the last row and must be at least >= 1
                 """
                alter = int((1 - self.anim_count) / (self.anim_row - 1))
                if self.anim_alter < alter:
                    aa.display_error(
                        "Min variation is '" + str(alter) + 
                        "' for these settings."
                    )
                    self.anim_alter = self.update_ui(alter)
                    return

            difference = self.anim_alter - self.anim_old_alter

            if difference < 0:
                # hide elements
                aa.to_hide(
                    1, self.anim_row, self.anim_count, self.anim_count,
                    self.anim_alter, self.anim_old_alter, True
                )

            elif difference > 0:
                # unhide elements
                aa.to_hide(
                    1, self.anim_row, self.anim_count, self.anim_count,
                    self.anim_old_alter, self.anim_alter, False
                )
            else:
                return
            self.max_anim_row()

    def update_anim_mode(self, context):
        if not int(self.anim_mode):
            # animation mod
            pass
        else:
            # creation mod
            pass

    # ----------------------- Reset all properties ------------------
    def up_ui_reset(self):
        """Reset all UI properties"""
        self.count = self.update_ui(2)
        self.row = self.update_ui(1)
        self.is_copy = self.update_ui(False)
        self.tr_offset = self.update_ui(Vector((2.0, 0.0, 0.0)))
        self.tr_global = self.update_ui(Vector((2.0, 0.0, 0.0)))
        self.sc_offset = self.update_ui((100, 100, 100))
        self.sc_global = self.update_ui((100, 100, 100))
        self.rot_offset = self.update_ui(Vector((0.0, 0.0, 0.0)))
        self.rot_global = self.update_ui(Vector((0.0, 0.0, 0.0)))
        self.alter = self.update_ui(0)
        self.total = "2"
        self.erow = "2"
        self.anim_mode = "0"
        self.anim_count = self.update_ui(2)
        self.anim_row = self.update_ui(1)
        self.anim_alter = self.update_ui(0)

    # --------------------------- Columns ---------------------------
    count: bpy.props.IntProperty(
        name='Count',
        description="Number of elements, original count as one",
        default=2,
        soft_min=2,
        min=2,
        max=2000,
        get=get_count,
        set=set_count,
        update=update_count
    )

    old_count: bpy.props.IntProperty(default=1)

    # ---------------------------- Rows -----------------------------
    row: bpy.props.IntProperty(
        name="Row",
        description="Number of row(s)",
        default=1,
        soft_min=1,
        min=1,
        soft_max=1000,
        max=1000,
        get=get_row,
        set=set_row,
        update=update_row
    )

    old_row: bpy.props.IntProperty(default=0)
    maxrow: bpy.props.IntProperty(default=1)

    # ------------------------- Variations --------------------------
    """Allow a variation in the row :
    if row gets n elements, row +1 will get (n + variation) elements
    only if n + variation > 0
    """
    alter: bpy.props.IntProperty(
        name=" Row variation",
        description="""Variation in the number of elements in a row.
            (between -5 and 5).\nBe careful with it""",
        default=0,
        soft_min=-5,
        min=-5,
        soft_max=5,
        max=5,
        get=get_alter,
        set=set_alter,
        update=update_alter
    )

    old_alter: bpy.props.IntProperty(default=0)

    # if alter <> 0, how align the rows
    align: bpy.props.EnumProperty(
        name='Align',
        description="Align of rows when variation is not zero",
        items=[
            ('LEFT', 'Left', "Align to the left", 'ALIGN_LEFT', 0),
            ('CENTER', 'Center', "Align to the center", 'ALIGN_CENTER', 1),
            ('RIGHT', 'Right', "Align to the right", 'ALIGN_RIGHT', 2)
        ],
        default='LEFT',
        update=update_align
    )

    # Vector alignment depends on align
    ralign: bpy.props.FloatVectorProperty(
        subtype='TRANSLATION',
        unit='LENGTH',
        default=(0.0, 0.0, 0.0)
    )

    # ------------------------ Informations -------------------------
    total: bpy.props.StringProperty(
        name="Total",
        description="Total of elements in array",
        default="2"
    )

    erow: bpy.props.StringProperty(
        description="Number of elements in the current row.",
        default="2"
    )

    # ---------------------------- Mask -----------------------------
    at_nb_mask: bpy.props.IntProperty(
        name="Number to Mask",
        description="Number of elements to mask",
        soft_min=1,
        min=1,
        default=1
    )

    # -------------------------- Booleans ---------------------------
    """Boolean uses to know if user or prog have changed the value to avoid
    continuous loop. True for program.
    """
    is_prog_change: bpy.props.BoolProperty(default=False)

    """Which one between offset and global user calls last,
    True for offset and False for global. Default is offset.
    """
    is_tr_off_last: bpy.props.BoolProperty(default=True)

    # True if addon is initialised
    already_start: bpy.props.BoolProperty(default=False)

    # if the user need a single copy or a duplicate (link object)
    is_copy: bpy.props.BoolProperty(
        name="Copy only",
        description="Duplicate or copy, default is duplicate",
        default=False
    )

    # ------------------------ Translation --------------------------
    tr_axis: bpy.props.EnumProperty(
        name='Axis',
        description="Translation orientation",
        items=(
            ('0', 'Local', "Locals axes of the reference object"),
            ('1', 'World', "World axes")),
        default='0',
        update=update_orient
    )

    # translation vector offset
    tr_offset: bpy.props.FloatVectorProperty(
        name='Offset',
        description="Distance between elements",
        default=(2.0, 0.0, 0.0),
        subtype='TRANSLATION',
        unit='LENGTH',
        precision=2,
        step=50,
        options={'ANIMATABLE'},
        update=update_offset
    )

    # global translation distance
    tr_global: bpy.props.FloatVectorProperty(
        name='Global',
        description="Distance between the original and the last element",
        default=(2.0, 0.0, 0.0),
        subtype='TRANSLATION',
        unit='LENGTH',
        precision=2,
        step=50,
        options={'ANIMATABLE'},
        update=update_global
    )

    tr_second: bpy.props.FloatVectorProperty(
        name="Translation",
        description="Additional offset distance for rows",
        default=(0.0, 0.0, 0.0),
        subtype='TRANSLATION',
        unit='LENGTH',
        precision=2,
        step=50,
        update=update_second
    )
    # --------------------------- Pivot -----------------------------
    at_pivot: bpy.props.PointerProperty(
        name='Pivot',
        description="Object you want as pivot point. \
            If none, pivot point is the object's origin",
        type=bpy.types.Object
    )

    # --------------------------- Scale -----------------------------
    sc_method: bpy.props.EnumProperty(
        name='Method',
        description="Different methods for scale",
        items=(
            ('0', 'Linear', "Linear calculation. The scale is regular."),
            ('1', 'Factor', "Factor calculation.")),
        default='0',
        update=update_orient
    )
    # scaling vector offset
    sc_offset: bpy.props.FloatVectorProperty(
        name='Offset',
        description="Incremental scale of next elements",
        default=(100.0, 100.0, 100.0),
        subtype='XYZ',
        precision=1,
        step=100,
        options={'ANIMATABLE'},
        update=update_offset
    )

    # global scaling
    sc_global: bpy.props.FloatVectorProperty(
        name='Global',
        description="Scale of the last element",
        default=(100.0, 100.0, 100.0),
        subtype='XYZ',
        precision=1,
        step=100,
        options={'ANIMATABLE'},
        update=update_global
    )

    sc_second: bpy.props.FloatVectorProperty(
        name='Scale',
        description="Additionnal scale for rows",
        default=(100.0, 100.0, 100.0),
        subtype='XYZ',
        precision=1,
        step=100,
        options={'ANIMATABLE'},
        update=update_second
    )

# ------------------------------ Rotation ---------------------------
    rot_axis: bpy.props.EnumProperty(
        name='Axis',
        description="Rotation orientation",
        items=(
            ('0', 'Local', "Locals axes of the reference object"),
            ('1', 'World', "World axes")),
        default='0',
        update=update_orient
    )
    # rotation vector offset
    rot_offset: bpy.props.FloatVectorProperty(
        name='Offset',
        description="Angle between each element",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ',
        unit='ROTATION',
        step=500,  # = 5
        options={'ANIMATABLE'},
        update=update_offset
    )

    # global rotation
    rot_global: bpy.props.FloatVectorProperty(
        name='Global',
        description="Maximum angle from the reference to the last element",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ',
        unit='ROTATION',
        step=500,  # = 5
        options={'ANIMATABLE'},
        update=update_global
    )

    rot_second: bpy.props.FloatVectorProperty(
        name='Rotation',
        description="Additionnal rotation for rows",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ',
        unit='ROTATION',
        step=500,
        options={'ANIMATABLE'},
        update=update_second
    )

    # ------------------------ Random part --------------------------
    at_seed: bpy.props.IntProperty(
        name='Seed',
        description="Seed value for random",
        soft_min=0,
        default=0,
        update=update_seed
    )

    at_mode: bpy.props.EnumProperty(
        name="Mode",
        description="Choose between simple mode or advanced",
        items=(('SIM', 'Simple', "Simple mode"),
            ('ADV', 'Advanced', "Advanced mode")),
        default='SIM'
    )

    at_is_tr: bpy.props.BoolProperty(
        name="Add Translation",
        description="Add translation in random?",
        default=False
    )

    at_is_sc: bpy.props.BoolProperty(
        name="Add Scale",
        description="Add scale in random?",
        default=False
    )

    at_is_rot: bpy.props.BoolProperty(
        name="Add Rotation",
        description="Add rotation in random?",
        default=False
    )

    tr_min: bpy.props.FloatVectorProperty(
        name="Min",
        description="Minimum random value for translation",
        unit='LENGTH',
        default=(0.0, 0.0, 0.0),
        update=up_tr_min
    )

    tr_max: bpy.props.FloatVectorProperty(
        name="Max",
        description="Maximum random value for translation",
        unit='LENGTH',
        default=(0.0, 0.0, 0.0),
        update=up_tr_max
    )

    tr_rand: bpy.props.FloatProperty(
        name="Translation",
        description="Random values for all axis",
        unit='LENGTH',
        default=0.0,
        update=update_rtr
    )

    sc_all: bpy.props.BoolProperty(
        name="Uniform Scale",
        description="Uniform or non uniform scale, default is non uniform.",
        default=False
    )

    sc_min_x: bpy.props.IntProperty(
        name="Min",
        description="Minimum random value for x scale",
        default=100,
        update=up_sc_min_x
    )

    sc_min_y: bpy.props.IntProperty(
        name="Min",
        description="Minimum random value for y scale",
        default=100,
        update=up_sc_min_y
    )

    sc_min_z: bpy.props.IntProperty(
        name="Min",
        description="Minimum random value for z scale",
        default=100,
        update=up_sc_min_z
    )

    sc_max_x: bpy.props.IntProperty(
        name="Max",
        description="Maximum random value for x scale",
        default=100,
        update=up_sc_max_x
    )

    sc_max_y: bpy.props.IntProperty(
        name="Max",
        description="Maximum random value for y scale",
        default=100,
        update=up_sc_max_y
    )

    sc_max_z: bpy.props.IntProperty(
        name="Max",
        description="Maximum random value for z scale",
        default=100,
        update=up_sc_max_z
    )

    sc_rand: bpy.props.IntProperty(
        name="Scale",
        description="Random scale value for all axis",
        default=100,
        update=update_rsc
    )

    rot_min: bpy.props.FloatVectorProperty(
        name="Min",
        description="Minimum random value for rotation",
        unit='ROTATION',
        default=(0.0, 0.0, 0.0),
        update=up_rot_min
    )

    rot_max: bpy.props.FloatVectorProperty(
        name="Max",
        description="Maximum random value for rotation",
        unit='ROTATION',
        default=(0.0, 0.0, 0.0),
        update=up_rot_max
    )

    rot_rand: bpy.props.FloatProperty(
        name="Rotation",
        description="Random rotation for all axis",
        unit='ROTATION',
        default=0.0,
        update=update_rrot
    )

    # ----------------------- Selection part ------------------------
    reference: bpy.props.EnumProperty(
        name="Reference Objects",
        description="Select all duplicates for the choosen reference",
        items=items_refs,
        update=select_ref
    )
    # ----------------------- Animation part ------------------------
    anim_mode: bpy.props.EnumProperty(
        name='Mode',
        description="Switch between creation or animation",
        items=crea_anim,
        update=update_anim_mode
    )

    tr_anim: bpy.props.BoolProperty(
        name="Location",
        description="Add location in animation",
        default=True
    )

    sc_anim: bpy.props.BoolProperty(
        name="Scale",
        description="Add scale in animation",
        default=True
    )

    rt_anim: bpy.props.BoolProperty(
        name="Rotation",
        description="Add rotation in animation",
        default=True
    )

    render_anim: bpy.props.BoolProperty(
        name="Render",
        description="Add render visibility in animation",
        default=True
    )

    viewport_anim: bpy.props.BoolProperty(
        name="Viewport",
        description="Add viewport visibility in animation",
        default=True
    )

    anim_count: bpy.props.IntProperty(
        name='Column Qty',
        description="Simulate the number of elements in column",
        default=2,
        soft_min=2,
        min=2,
        max=2000,
        get=get_anim_count,
        set=set_anim_count,
        update=update_anim_count
    )

    anim_old_count: bpy.props.IntProperty()

    anim_row: bpy.props.IntProperty(
        name='Row Qty',
        description="Simulate the number of elements in row",
        default=1,
        soft_min=1,
        min=1,
        max=1000,
        get=get_anim_row,
        set=set_anim_row,
        update=update_anim_row
    )

    anim_old_row: bpy.props.IntProperty()
    maxanimrow: bpy.props.IntProperty(default=1)

    anim_alter: bpy.props.IntProperty(
        name='Variation Qty',
        description="Simulate the variation of elements",
        default=0,
        soft_min=-5,
        min=-5,
        soft_max=5,
        max=5,
        get=get_anim_alter,
        set=set_anim_alter,
        update=update_anim_alter
    )

    anim_old_alter: bpy.props.IntProperty()
