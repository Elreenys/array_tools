# -*- coding: utf-8 -*-
import bpy
import math

from bpy.types import PropertyGroup
from mathutils import Vector

from . import cfg
from . import at_panel
from . import at_operators
from . at_calc_func import(
    x_axis,
    y_axis,
    z_axis,
    xyz_axis,
    at_all_in_one,
    at_random,
    sum_serie,
    tsr
)

"""not used yet
if check on update, may really slow the addon """
def check_list(alist):
    """check all the objects"""
    for elem in alist:
        if elem in bpy.data.objects:
            pass
        else:
            cfg.display_error(str(elem)+" isn't valid.")
            print("Check_list : a name isn't valid ", elem)
            return False
    return True


def elem_in_row(column, row, indice):
    """Number of elements in a row"""
    elements = column + (row - 1) * indice
    # print("row elements =", elements)
    return elements


# ---------------------------- Properties ---------------------------
class ArrayTools_props(PropertyGroup):
    """Properties for array tools"""

    def add_in_column(self, row, nb_column=-1):
        """Add nb_column element(s) in each row"""
        column = cfg.at_count_values[0]
        if nb_column == -1:
            nb_column = cfg.at_count_values[1] - column

        ref_name = cfg.atools_objs[0][0]
        if ref_name in bpy.data.objects:
            ref_obj = bpy.data.objects[ref_name]
            # update the ref_mtx if object's transforms have changed
            cfg.ref_mtx = ref_obj.matrix_world.copy()
            # with offset no need to replace all elements, only the last
            if self.is_tr_off_last:
                for i in range(row):
                    col = column + i*self.alter
                    for j in range(col, col + nb_column):
                        objcp = ref_obj.copy()
                        array_col = bpy.data.collections.get(cfg.col_name)
                        array_col.objects.link(objcp)
                        if self.is_copy:
                            objcp.data = ref_obj.data.copy()
                        cfg.atools_objs[i].append(objcp.name)

                        self.transforms_lsr(j, i, cfg.ref_mtx, objcp.name)
                # update the global ui
                tr, sc, rot = self.calc_global()
                self.up_ui_tr_global(tr)
                self.up_ui_sc_global(sc)
                self.up_ui_rot_global(rot)

            else: # replace all elements
                for i in range(row):
                    col = column + i*self.alter
                    for j in range(col, col + nb_column):
                        objcp = ref_obj.copy()
                        array_col = bpy.data.collections.get(cfg.col_name)
                        array_col.objects.link(objcp)
                        if self.is_copy:
                            objcp.data = ref_obj.data.copy()
                        cfg.atools_objs[i].append(objcp.name)
                self.update_global(bpy.context)
            del objcp
            del ref_obj
        else:
            message = "Problem with reference object's name."
            cfg.display_error(message)
            print("Error in 'add_in_column' : ", message)


    def del_in_column(self, row, nb_column=-1):
        """Remove nb_column element(s) in each row"""
        if nb_column == -1:
            nb_column = cfg.at_count_values[0] - cfg.at_count_values[1]
        array_col = bpy.data.collections.get(cfg.col_name)
        for i in range(row-1, -1, -1):
            for j in range(nb_column):
                del_name = cfg.atools_objs[i].pop()
                if del_name in bpy.data.objects:
                    obj = bpy.data.objects[del_name]
                    array_col.objects.unlink(obj)
                    bpy.data.objects.remove(obj, do_unlink=True)
                else:
                    cfg.display_error(del_name + " doesn't exist anymore.")
                    print("Error in 'del_in_column' : ", del_name)

                # if no more element in list, remove the row
                if not cfg.atools_objs[i]:
                    cfg.atools_objs.pop()
                    self.up_ui_updateRow(row - 1)
                    continue
        if not self.is_tr_off_last:
            # if global is used last
            self.update_global(bpy.context)
        else:
            tr, sc, rot = self.calc_global()
            self.up_ui_tr_global(tr)
            self.up_ui_sc_global(sc)
            self.up_ui_rot_global(rot)


    def add_in_col_alter(self, row, nb_column):
        """Add elements in all rows except the first for variation"""
        array_col = bpy.data.collections.get(cfg.col_name)
        ref_name = cfg.atools_objs[0][0]
        column = self.count
        if ref_name in bpy.data.objects:
            ref_obj = bpy.data.objects[ref_name]
            cfg.ref_mtx = ref_obj.matrix_world.copy()
            if self.is_tr_off_last:
                for i in range(1, row):
                    for j in range(column, column + i * nb_column):
                        objcp = ref_obj.copy()
                        array_col = bpy.data.collections.get(cfg.col_name)
                        array_col.objects.link(objcp)
                        if self.is_copy:
                            objcp.data = ref_obj.data.copy()
                        cfg.atools_objs[i].append(objcp.name)
                        # print("objs=", cfg.atools_objs)

                self.update_offset(bpy.context)
            else: # replace all elements
                for i in range(1, row):
                    for j in range(column, column + i * nb_column):
                        objcp = ref_obj.copy()
                        array_col = bpy.data.collections.get(cfg.col_name)
                        array_col.objects.link(objcp)
                        if self.is_copy:
                            objcp.data = ref_obj.data.copy()
                        cfg.atools_objs[i].append(objcp.name)
                self.update_global(bpy.context)
            del objcp
            del ref_obj
        else:
            message = "Problem with reference object's name."
            cfg.display_error(message)
            print("Error in 'add_in_column' : ", message)


    def del_in_col_alter(self, row, nb_column):
        """Remove elements in all rows except the first"""
        array_col = bpy.data.collections.get(cfg.col_name)
        for i in range(row -1 , 0, -1):
            for j in range(nb_column * i):
                del_name = cfg.atools_objs[i].pop()
                # print("del name=", del_name)
                if del_name in bpy.data.objects:
                    obj = bpy.data.objects[del_name]
                    array_col.objects.unlink(obj)
                    bpy.data.objects.remove(obj, do_unlink=True)
                else:
                    cfg.display_error(del_name + " doesn't exist anymore.")
                    print("Error in 'del_in_column' : ", del_name)
        if self.is_tr_off_last:
            self.update_offset(bpy.context)
        else:
            self.update_global(bpy.context)

    def add_in_row(self, column, nb_row=-1):
        """Add column elements in nb_row new row(s)"""
        row = cfg.at_row_values[0]
        if nb_row == -1:
            nb_row = cfg.at_row_values[1] - row

        ref_name = cfg.atools_objs[0][0]
        if ref_name in bpy.data.objects:
            ref_obj = bpy.data.objects[ref_name]
            cfg.ref_mtx = ref_obj.matrix_world.copy()
            if self.is_tr_off_last:
                for i in range(row, row + nb_row):
                    cfg.atools_objs.append([])
                    for j in range(column + i*self.alter):
                        objcp = ref_obj.copy()
                        array_col = bpy.data.collections.get(cfg.col_name)
                        array_col.objects.link(objcp)
                        if self.is_copy:
                            objcp.data = ref_obj.data.copy()
                        cfg.atools_objs[i].append(objcp.name)
                        self.transforms_lsr(j, i, cfg.ref_mtx, objcp.name)
            else:
                for i in range(row, row + nb_row):
                    cfg.atools_objs.append([])
                    for j in range(column):
                        objcp = ref_obj.copy()
                        array_col = bpy.data.collections.get(cfg.col_name)
                        array_col.objects.link(objcp)
                        if self.is_copy:
                            objcp.data = ref_obj.data.copy()
                        cfg.atools_objs[i].append(objcp.name)
                self.update_global(bpy.context)
        else:
            message = "Problem with reference object's name."
            cfg.display_error(message)
            print("Error in 'add in row' : ", message)


    def del_in_row(self, nb_row=-1):
        """Remove nb_row row(s) : (column * nb_row) elements"""
        if nb_row == -1:
            nb_row = cfg.at_row_values[0] - cfg.at_row_values[1]
        array_col = bpy.data.collections.get(cfg.col_name)
        for i in range(nb_row):
            names = cfg.atools_objs.pop()
            for del_name in names:
                if del_name in bpy.data.objects:
                    obj = bpy.data.objects[del_name]
                    array_col.objects.unlink(obj)
                    bpy.data.objects.remove(obj, do_unlink=True)
                else:
                    cfg.display_error(del_name + " doesn't exist anymore.")
                    print("Error in 'del_in_column' : ", del_name)


    def at_del_all(self, del_rall):
        """Delete all copies and remove objects from lists
        del_rall : boolean, True to del reference object from list
        """
        array_col = bpy.data.collections.get(cfg.col_name)
        ref_name = cfg.atools_objs[0][0]
        for i in range(self.row):
            names = cfg.atools_objs.pop()
            for obj_name in reversed(names):
                if obj_name == ref_name:
                    continue
                # test if object exist
                if obj_name in bpy.data.objects:
                    obj = bpy.data.objects[obj_name]
                    array_col.objects.unlink(obj)
                    bpy.data.objects.remove(obj, do_unlink=True)
                else:
                    cfg.display_error(obj_name + " not exist!")
                    print("Error in 'del_all' : ", obj_name)

        if del_rall:
            cfg.atools_objs.clear()

            # removing the collection if empty
            if not array_col.objects:
                bpy.data.collections.remove(array_col)
        else:
            cfg.atools_objs.append([ref_name])
        # print("Del_all done!")

    # ----------------------- UI update -----------------------------
    # ---------------------------------------------------------------
    # ----------------------- count update --------------------------
    def updateCount(self, context):
        """update the number of element(s) in column"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            cfg.add_count(int(self.count))
            cfg.del_count()

            # cfg.count_values[0] always store old count value
            difference = self.count - cfg.at_count_values[0]

            self.update_infos()

            if difference > 0:
                self.add_in_column(self.row, difference)
            elif difference < 0:
                self.del_in_column(self.row, -difference)
        # print("objs =", cfg.atools_objs)


    def up_ui_updateCount(self, val):
        """Update the value of the property count in UI"""
        self.is_prog_change = True
        self.count = val

    # ----------------------- row update ----------------------------
    def update_row(self, context):
        """Update row property"""
        cfg.add_row(self.row)
        cfg.del_row()
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            if self.alter < 0 and cfg.maxrow < self.row:
                cfg.display_error("Maximun rows for these setting is : " + str(cfg.maxrow))
                self.up_ui_updateRow(cfg.maxrow)
                return

            # cfg.at_row_values[0] always store old row value
            difference = self.row - cfg.at_row_values[0]
            if difference > 0:
                self.add_in_row(self.count, difference)
            elif difference < 0:
                self.del_in_row(-difference)

            line = elem_in_row(self.count, self.row, self.alter)

            self.update_infos()

    def up_ui_updateRow(self, val):
        """Update the value of the property row in UI"""
        self.is_prog_change = True
        self.row = val

    def update_alter(self, context):
        """Update alter property"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            # alter must have at least 2 rows
            if self.row == 1 and self.alter != 0:
                cfg.display_error("Add more rows first.")
                self.up_ui_updateAlter(0)
                return
            if self.alter < 0:
                # (column + (row-1)* variation) is the number of elements
                # of the last row and must be at least >= 1
                alter = int((1 - self.count) / (self.row - 1))
                if self.alter < alter:
                    cfg.display_error("Min variation is '"+str(alter)+"' for these settings.")
                    self.up_ui_updateAlter(alter)
                    return

            cfg.add_alter(self.alter)
            cfg.del_alter()
            self.update_ralign()

            difference = self.alter - cfg.at_alter[0]
            if difference > 0:
                self.add_in_col_alter(self.row, difference)
            elif difference < 0:
                self.del_in_col_alter(self.row, -difference)
            # print(f"count={self.count}, row={self.row}, alter={self.alter}")
            line = elem_in_row(self.count, self.row, self.alter)
            # print("elems in row =", line)

            self.update_infos()


    def up_ui_updateAlter(self, val):
        """Update the value of the property alter in UI"""
        self.is_prog_change = True
        self.alter = val


    def update_ralign(self):
        """Update the value of ralign"""
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
            self.update_offset(bpy.context)
        else:
            self.update_global(bpy.context)


    def update_infos(self):
        """Update properties total and erow"""
        sum = sum_serie(self.row, self.alter)
        square = self.count * self.row
        if self.alter >= 0:
            cfg.maxrow = self.row
        else:
            ca = self.count // -self.alter
            cfg.maxrow = ca if self.count % self.alter == 0 else ca + 1
        self.total = str(int(square + sum))
        self.erow = str(elem_in_row(self.count, self.row, self.alter))

    # ----------------------- translation update --------------------
    def up_ui_tr_offset(self, val):
        """Update the value of the property tr_offset in UI"""
        self.is_prog_change = True
        self.tr_offset = val

    def up_ui_tr_global(self, val):
        """Update the value of the property tr_global in UI"""
        self.is_prog_change = True
        self.tr_global = val

    # ----------------------- scale update --------------------------
    def up_ui_sc_offset(self, val):
        """Update the value of the property sc_offset in UI"""
        self.is_prog_change = True
        self.sc_offset = val

    def up_ui_sc_global(self, val):
        """Update the value of the property sc_global in UI"""
        self.is_prog_change = True
        self.sc_global = val

    # ----------------------- rotation update -----------------------
    def up_ui_rot_offset(self, val):
        """Update the value of the property rot_offset in UI"""
        self.is_prog_change = True
        self.rot_offset = val

    def up_ui_rot_global(self, val):
        """Update the value of the property rot_global in UI"""
        self.is_prog_change = True
        self.rot_global = val

    # ---------------------------------------------------------------
    def calc_global(self):
        """Calculate global for column"""
        tg = (self.count-1) * self.tr_offset
        sg = (xyz_axis() - (self.count-1) *
            (cfg.ref_mtx.to_scale() - (self.sc_offset/100))) * 100
        rg = self.count * Vector(self.rot_offset)
        return tg,sg,rg


    def transforms_lsr(self, column, row, mat, ename):
        """Calculate transforms according to the position of the element
        column : indice of the element's column
        row : indice of the element's row
        mat : matrix of the reference object
        ename : element's name to put in place
        """
        localxyz = (x_axis(), y_axis(), z_axis())

        translate, scaling, rotate = tsr(mat, column, row, self.tr_offset, self.tr_second,
            self.sc_offset, self.sc_second, self.rot_offset, self.rot_second, self.ralign)
        if ename in bpy.data.objects:
            obj = bpy.data.objects[ename]
        if self.at_pivot is not None:
            obj.matrix_world = at_all_in_one(mat, rotate, localxyz, translate,
                scaling, self.at_pivot.location)
        else:
            obj.matrix_world = at_all_in_one(mat, rotate, localxyz, translate,
                scaling, mat.translation)


    def apply_transforms(self, matx, nb_column, nb_row, tr, sc, rot):
        """Move, scale and rotate the selected elements
        tr : translation offset of the first row
        sc : scale offset of the first row
        rot : rotation offset of the first row
        return global transforms
        """
        # local axis always (1,0,0) (0,1,0) (0,0,1)
        localxyz = (x_axis(), y_axis(), z_axis())

        ref_scale = matx.to_scale()
        # duplicate code but avoid looping the test
        if self.at_pivot is not None:
            for i in range(nb_row):
                for j in range(nb_column + i*self.alter):
                    elem = cfg.atools_objs[i][j]
                    if elem in bpy.data.objects:
                        obj = bpy.data.objects[elem]
                    else:
                        cfg.display_error(elem + " no more exist !")
                        print("Error in 'apply_transforms', name no more exist : ", elem)
                        continue
                    t_off, s_off, r_off = tsr(matx, j, i, tr, self.tr_second, sc,
                        self.sc_second, rot, self.rot_second, self.ralign)

                    obj.matrix_world = at_all_in_one(matx, r_off,
                        localxyz, t_off, s_off, self.at_pivot.location)
        else:
            for i in range(nb_row):
                for j in range(nb_column + i*self.alter):
                    ref_loc = cfg.ref_mtx.translation
                    elem = cfg.atools_objs[i][j]
                    if elem in bpy.data.objects:
                        obj = bpy.data.objects[elem]
                    else:
                        cfg.display_error(elem + " no more exist !")
                        print("Error in 'apply_transforms', name no more exist : ", elem)
                        continue
                    t_off, s_off, r_off = tsr(matx, j, i, tr, self.tr_second, sc,
                        self.sc_second, rot, self.rot_second, self.ralign)

                    obj.matrix_world = at_all_in_one(matx, r_off,
                        localxyz, t_off, s_off, ref_loc)
        tr_col,sc_col,rot_col = self.calc_global()
        return(tr_col, sc_col, rot_col)

    def update_offset(self, context):
        """Update for all offsets"""
        if self.is_prog_change:
            self.is_prog_change = False
        else: # user change offset
            self.is_tr_off_last = True

            ref_name = cfg.atools_objs[0][0]
            if bpy.data.objects[ref_name]:
                cfg.ref_mtx = bpy.data.objects[ref_name].matrix_world.copy()
            aloc, asc, arot = self.apply_transforms(cfg.ref_mtx, self.count, self.row,
                self.tr_offset, self.sc_offset, Vector(self.rot_offset))

            # since offset changes, global too
            self.up_ui_tr_global(aloc)
            self.up_ui_sc_global(asc)
            self.up_ui_rot_global(arot)


    def update_global(self, context):
        """Update for all globals"""
        if self.is_prog_change:
            self.is_prog_change = False
        else: # user change global
            self.is_tr_off_last = False

            ref_name = cfg.atools_objs[0][0]
            if bpy.data.objects[ref_name]:
                cfg.ref_mtx = bpy.data.objects[ref_name].matrix_world.copy()
            ref_scale = cfg.ref_mtx.to_scale()

            translation_offset = Vector(self.tr_global) / (self.count - 1)
            scale_offset = ref_scale - ((ref_scale-(self.sc_global/100)) / (self.count - 1))
            rotation_offset = Vector(self.rot_global) / self.count

            self.apply_transforms(cfg.ref_mtx, self.count, self.row, translation_offset,
                Vector(scale_offset)*100, rotation_offset)

            # since global changes, offset too
            self.up_ui_tr_offset(translation_offset)
            self.up_ui_sc_offset(Vector(scale_offset*100))
            self.up_ui_rot_offset(rotation_offset)


    def update_second(self, context):
        """Update the secondary transforms"""
        ref_name = cfg.atools_objs[0][0]
        if bpy.data.objects[ref_name]:
            cfg.ref_mtx = bpy.data.objects[ref_name].matrix_world.copy()
        self.apply_transforms(cfg.ref_mtx, self.count, self.row, self.tr_offset,
            self.sc_offset, self.rot_offset)


    # ----------------------- is_copy update ------------------------
    def up_ui_is_copy(self):
        """Update the value of the property is_copy in UI"""
        self.is_prog_change = True
        self.is_copy = False


    def update_is_copy(self, context):
        """Allow a copy or duplicate(copy link by default)"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            if self.is_copy:  # no need to rebuild all
                for i in range(self.row):
                    for j in range(self.count):
                        if i == 0 and j == 0:
                            continue
                        ref_name = cfg.atools_objs[0][0]
                        elem_name = cfg.atools_objs[i][j]
                        bpy.data.objects[elem_name].data = bpy.data.objects[ref_name].data.copy()
            else:  # since the value change (now duplicate), need to rebuild
                count = self.count
                row = self.row
                ref_name = cfg.atools_objs[0][0]
                array_col = bpy.data.collections.get(cfg.col_name)

                # DO NOT USE BLENDER CRASH WITH IT
                # self.at_del_all(False)

                bpy.ops.object.delete({"selected_objects": array_col.objects})
                cfg.atools_objs.clear()
                cfg.atools_objs.append([ref_name])

                ref_obj = bpy.data.objects[ref_name]
                for i in range(row):
                    if i != 0:
                        cfg.atools_objs.append([])
                    for j in range(count + i*self.alter):
                        objcp = ref_obj.copy()
                        array_col.objects.link(objcp)
                        cfg.atools_objs[i].append(objcp.name)
                del objcp
                del ref_obj

                if self.is_tr_off_last:
                    self.update_offset(bpy.context)
                else:
                    self.update_global(bpy.context)

                print("Rebuild done!")

    # ----------------------- random part ---------------------------
    # ---------------------------------------------------------------
    def update_seed(self, context):
        if self.at_mode == 'ADV':
            sc_min = (self.sc_min_x, self.sc_min_y, self.sc_min_z)
            sc_max = (self.sc_max_x, self.sc_max_y, self.sc_max_z)
            at_random(self.at_seed, self.count, self.row, self.tr_min, self.tr_max, sc_min,
                sc_max, self.rot_min, self.rot_max, self.at_is_tr, self.at_is_sc, self.at_is_rot,
                self.sc_all, self.tr_offset, self.tr_second, self.sc_offset, self.sc_second,
                self.rot_offset, self.rot_second, self.at_pivot, self.alter, self.ralign)
        else: # simple mode
            vec = xyz_axis()
            tr = self.tr_rand * vec
            sc = self.sc_rand * vec
            rot = self.rot_rand * vec
            at_random(self.at_seed, self.count, self.row, -tr, tr, sc, 100*vec, -rot, rot,
                self.at_is_tr, self.at_is_sc, self.at_is_rot, False, self.tr_offset,
                self.tr_second, self.sc_offset, self.sc_second, self.rot_offset,
                self.rot_second, self.at_pivot, self.alter, self.ralign)


    def update_rtr(self, context):
        """rtr in simple mode update adv mode"""
        self.tr_max = self.tr_rand * Vector((1.0, 1.0, 1.0))
        self.tr_min = self.tr_rand * Vector((-1.0, -1.0, -1.0))


    def update_rsc(self, context):
        """rsc in simple mode update adv mode"""
        self.sc_max_x, self.sc_max_y, self.sc_max_z = (100.0, 100.0, 100.0)
        rand = self.sc_rand
        self.sc_min_x = rand
        self.sc_min_y = rand
        self.sc_min_z = rand


    def update_rrot(self, context):
        """rrot in simple mode update adv mode"""
        self.rot_max = self.rot_rand * Vector((1.0, 1.0, 1.0))
        self.rot_min = self.rot_rand * Vector((-1.0, -1.0, -1.0))


    def up_ui_sc_min_x(self, val):
        """Update the value of the property sc_min_x in UI"""
        self.is_prog_change = True
        self.sc_min_x = val


    def up_ui_sc_min_y(self, val):
        """Update the value of the property sc_min_y in UI"""
        self.is_prog_change = True
        self.sc_min_y = val


    def up_ui_sc_min_z(self, val):
        """Update the value of the property sc_min_z in UI"""
        self.is_prog_change = True
        self.sc_min_z = val


    def up_ui_sc_max_x(self, val):
        """Update the value of the property sc_max_x in UI"""
        self.is_prog_change = True
        self.sc_max_x = val


    def up_ui_sc_max_y(self, val):
        """Update the value of the property sc_max_y in UI"""
        self.is_prog_change = True
        self.sc_max_y = val


    def up_ui_sc_max_z(self, val):
        """Update the value of the property sc_max_z in UI"""
        self.is_prog_change = True
        self.sc_max_z = val

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
                self.up_ui_sc_max_x(self.sc_min_x)
                # with uniform : min_x = min_y = min_z same for max_
                self.up_ui_sc_min_y(self.sc_min_x)
                self.up_ui_sc_min_z(self.sc_min_x)
                self.up_ui_sc_max_y(self.sc_min_x)
                self.up_ui_sc_max_z(self.sc_min_x)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.up_ui_sc_min_y(self.sc_min_x)
                self.up_ui_sc_min_z(self.sc_min_x)
                self.up_ui_sc_max_y(self.sc_max_x)
                self.up_ui_sc_max_z(self.sc_max_x)
            elif test:
                # case : min > max and uniform = False
                self.up_ui_sc_max_x(self.sc_min_x)

    def up_sc_min_y(self, context):
        """Update sc_max_y if sc_min_y is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_y > self.sc_max_y
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.up_ui_sc_max_y(self.sc_min_y)
                # with uniform : min_x = min_y = min_z same for max_
                self.up_ui_sc_min_x(self.sc_min_y)
                self.up_ui_sc_min_z(self.sc_min_y)
                self.up_ui_sc_max_x(self.sc_min_y)
                self.up_ui_sc_max_y(self.sc_min_y)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.up_ui_sc_min_x(self.sc_min_y)
                self.up_ui_sc_min_z(self.sc_min_y)
                self.up_ui_sc_max_x(self.sc_max_y)
                self.up_ui_sc_max_z(self.sc_max_y)
            elif test:
                # case : min > max and uniform = False
                self.up_ui_sc_max_y(self.sc_min_y)

    def up_sc_min_z(self, context):
        """Update sc_max_z if sc_min_z is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_z > self.sc_max_z
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.up_ui_sc_max_z(self.sc_min_z)
                # with uniform : min_x = min_y = min_z same for max_
                self.up_ui_sc_min_x(self.sc_min_z)
                self.up_ui_sc_min_y(self.sc_min_z)
                self.up_ui_sc_max_x(self.sc_min_z)
                self.up_ui_sc_max_y(self.sc_min_z)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.up_ui_sc_min_x(self.sc_min_z)
                self.up_ui_sc_min_y(self.sc_min_z)
                self.up_ui_sc_max_x(self.sc_max_z)
                self.up_ui_sc_max_y(self.sc_max_z)
            elif test:
                # case : min > max and uniform = False
                self.up_ui_sc_max_y(self.sc_min_z)

    def up_sc_max_x(self, context):
        """Update sc_min_x if sc_max_x is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_x > self.sc_max_x
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.up_ui_sc_min_x(self.sc_max_x)
                # with uniform : min_x = min_y = min_z same for max_
                self.up_ui_sc_max_y(self.sc_max_x)
                self.up_ui_sc_max_z(self.sc_max_x)
                self.up_ui_sc_min_y(self.sc_max_x)
                self.up_ui_sc_min_z(self.sc_max_x)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.up_ui_sc_max_y(self.sc_max_x)
                self.up_ui_sc_max_z(self.sc_max_x)
                self.up_ui_sc_min_y(self.sc_min_x)
                self.up_ui_sc_min_z(self.sc_min_x)
            elif test:
                # case : min > max and uniform = False
                self.up_ui_sc_min_x(self.sc_max_x)

    def up_sc_max_y(self, context):
        """Update sc_min_y if sc_max_y is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_y > self.sc_max_y
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.up_ui_sc_min_y(self.sc_max_y)
                # with uniform : min_x = min_y = min_z same for max_
                self.up_ui_sc_max_x(self.sc_max_y)
                self.up_ui_sc_max_z(self.sc_max_y)
                self.up_ui_sc_min_x(self.sc_max_y)
                self.up_ui_sc_min_z(self.sc_max_y)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.up_ui_sc_max_x(self.sc_max_y)
                self.up_ui_sc_max_z(self.sc_max_y)
                self.up_ui_sc_min_x(self.sc_min_y)
                self.up_ui_sc_min_z(self.sc_min_y)
            elif test:
                # case : min > max and uniform = False
                self.up_ui_sc_min_y(self.sc_max_y)

    def up_sc_max_z(self, context):
        """Update sc_min_z if sc_max_z is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_z > self.sc_max_z
            if test and self.sc_all:
                # case : min > max and uniform = True
                self.up_ui_sc_min_z(self.sc_max_z)
                # with uniform : min_x = min_y = min_z same for max_
                self.up_ui_sc_max_x(self.sc_max_z)
                self.up_ui_sc_max_y(self.sc_max_z)
                self.up_ui_sc_min_x(self.sc_max_z)
                self.up_ui_sc_min_y(self.sc_max_z)
            elif self.sc_all:
                # case : min < max and uniform = True
                self.up_ui_sc_max_x(self.sc_max_z)
                self.up_ui_sc_max_y(self.sc_max_z)
                self.up_ui_sc_min_x(self.sc_min_z)
                self.up_ui_sc_min_y(self.sc_min_z)
            elif test:
                # case : min > max and uniform = False
                self.up_ui_sc_min_z(self.sc_max_z)

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

    # ----------------------- reset all properties ------------------
    def up_ui_reset(self):
        """Reset all UI properties"""
        self.up_ui_updateCount(2)
        self.up_ui_updateRow(1)
        self.up_ui_is_copy()
        self.up_ui_tr_offset(Vector((2.0, 0.0, 0.0)))
        self.up_ui_tr_global(Vector((2.0, 0.0, 0.0)))
        self.up_ui_sc_offset((100, 100, 100))
        self.up_ui_sc_global((100, 100, 100))
        self.up_ui_rot_offset(Vector((0.0, 0.0, 0.0)))
        self.up_ui_rot_global(Vector((0.0, 0.0, 0.0)))
        self.up_ui_updateAlter(0)
        self.total = "2"
        self.erow = "2"


    count: bpy.props.IntProperty(
        name='Count',
        description="Number of elements, original count as one",
        default=2,
        soft_min=2,
        update=updateCount
    )

    row: bpy.props.IntProperty(
        name="Row",
        description="Number of row(s)",
        default=1,
        soft_min=1,
        soft_max=100,
        update=update_row
    )

    """Allow a variation in the row :
    if row gets n elements, row +1 will get (n + variation) elements
    only if n + variation > 0
    """
    alter: bpy.props.IntProperty(
        name=" Row variation",
        description="""Variation in the number of elements in a row. (between -5 and 5).
            \n Be careful with it""",
        default=0,
        soft_min=-5,
        soft_max=5,
        update=update_alter
    )

    total: bpy.props.StringProperty(
        name="Total",
        description="Total of elements in array",
        default="2"
    )

    erow: bpy.props.StringProperty(
        description="Number of elements in the current row.",
        default="2"
    )

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

    # booleans use to know if user or prog change the value to avoid continuous loop
    is_prog_change: bpy.props.BoolProperty(default=False)  # True if prog change value

    # which one between offset and global user calls last, True is offset, False global
    is_tr_off_last: bpy.props.BoolProperty(default=True)

    # True if addon is initialised
    already_start: bpy.props.BoolProperty(default=False)

    # if the user need a single copy or a duplicate (link object)
    is_copy: bpy.props.BoolProperty(
        name="Copy only",
        description="Duplicate or copy, default is duplicate",
        default=False,
        update=update_is_copy
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

    at_pivot: bpy.props.PointerProperty(
        name='Pivot',
        description="Object you want as pivot point. If none, pivot point is the object's origine",
        type=bpy.types.Object
    )

    # scaling vector offset
    sc_offset: bpy.props.FloatVectorProperty(
        name='Offset',
        description="Incremental scale of the next elements",
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

    # ----------------------- random part ---------------------------
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
        name="Add translation",
        description="Add translation in random?",
        default=False
    )

    at_is_sc: bpy.props.BoolProperty(
        name="Add scale",
        description="Add scale in random?",
        default=False
    )

    at_is_rot: bpy.props.BoolProperty(
        name="Add rotation",
        description="Add rotation in random?",
        default=False
    )

    tr_min: bpy.props.FloatVectorProperty(
        name="min",
        description="Minimum random value for translation",
        unit='LENGTH',
        default=(0.0, 0.0, 0.0),
        update=up_tr_min
    )

    tr_max: bpy.props.FloatVectorProperty(
        name="max",
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
        name="uniform scale",
        description="Uniform or non uniform scale, default is non uniform.",
        default=False
    )

    sc_min_x: bpy.props.IntProperty(
        name="min",
        description="Minimum random value for x scale",
        default=100,
        update=up_sc_min_x
    )

    sc_min_y: bpy.props.IntProperty(
        name="min",
        description="Minimum random value for y scale",
        default=100,
        update=up_sc_min_y
    )

    sc_min_z: bpy.props.IntProperty(
        name="min",
        description="Minimum random value for z scale",
        default=100,
        update=up_sc_min_z
    )

    sc_max_x: bpy.props.IntProperty(
        name="max",
        description="Maximum random value for x scale",
        default=100,
        update=up_sc_max_x
    )

    sc_max_y: bpy.props.IntProperty(
        name="max",
        description="Maximum random value for y scale",
        default=100,
        update=up_sc_max_y
    )

    sc_max_z: bpy.props.IntProperty(
        name="max",
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
        name="min",
        description="Minimum random value for rotation",
        unit='ROTATION',
        default=(0.0, 0.0, 0.0),
        update=up_rot_min
    )

    rot_max: bpy.props.FloatVectorProperty(
        name="max",
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
