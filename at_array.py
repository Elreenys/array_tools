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
from mathutils import Matrix, Vector
import random

from . import at_calc_func as acf

"""
 ~ Simulate a 2D array containing names lists of all objects (refs + copies) ~

Exemple : count = 6, row = 3, alter = 2 {position 0,0 contains all ref objects}

           columns (count)             alter
     ________________________                                   _________
    /   /   /   /   /   /   /|                                 / name 1 /|
   /___/___/___/___/___/___/ |     ________                   / name 2 / |
   |0,0|   |   |   |   |0,5| |    /   /   /|                 / name n /  |
 R |___|___|___|___|___|___|/|   /___/___/ |_______         /________/   /
 o |   |   |   |   |   |   | |   |1,6|1,7| /  /   /|        |        |  /
 w |___|___|___|___|___|___|/| + |___|___|/__/___/ |        |        | /
   |2,0|   |   |   |   |2,5| |   |2,6|   |   |2,9| /        |________|/
   |___|___|___|___|___|___|/    |___|___|___|___|/

- add column : i=[0..row], j=[old_column + i*alter..column + i*alter]
- add alter : i=[1..row], j=[column + i*old_alter..column + i*alter]
- add row : i=[old_row..row], j=[0..column + i*alter]
- del column : i=[row-1..-1], j=[column-1..column-nb_column-1]
- del alter : i=[row-1, 0], j=[column + i*old_alter..column + i*alter]
- del row : i=[old_row-1..row-1], j=[0..1]

For two selected objects, 'Cube' and 'Cylinder', bank could look like this:
bank = [
    [['Cube', 'Cylinder'], ... , ['Cube.005', 'Cylinder.005']],     # 6 columns
    [['Cube.006', 'Cylinder.006'], ... , ['Cube.013', 'Cylinder.013']],  # 8
    [['Cube.014', 'Cylinder.014'], ... , ['Cube.023', 'Cylinder.023']],  # 10
]
"""


class Larray(object):
    """Lists array"""

    # class variables :
    # 3d array (2d array containing lists of names)
    bank = [[[]]]
    # collection name
    grp_name = "Array_collection"
    # set of objects to mask
    mask = set()
    # contains invalid reference object's name
    to_del = {}
    # Reference name for Reference enumProperty
    items = ()


class ReferenceMissing(Exception):
    """Raised when all reference objects have been deleted or renamed"""
    def __init__(self, message):
        cancel_at(message)


class Fsc(object):
    """Functions according to scale calculation"""
    sc = {
        '0': (acf.linear_offset, acf.scale_linear, acf.linear_global),
        '1': (acf.calc_offset, acf.scale_calc, acf.calc_global)
    }


def add_new_col(row):
    """Add a new empty list at the end of row"""
    Larray.bank[row].append([])


def add_new_row(_):
    """Add a new empty row to the bank"""
    Larray.bank.append([[]])


def add_bk_copy(row, column, name):
    """Store object name at the given position"""
    Larray.bank[row][column].append(name)


def pop_column(row):
    """Return the names list of the last column for the given row
    Return:
    (list)
    """
    return Larray.bank[row].pop()


def pop_row(_):
    """Return a list of elements of the last row"""
    return list(sum(Larray.bank.pop(), []))


def pr(data, message=""):
    """Print the bank"""
    if message != "":
        print(message, data)
    for i in range(len(Larray.bank)):
        print(Larray.bank[i])


def cancel_at(message):
    """Reset the addon"""
    display_error(message)
    bpy.ops.scene.at_cancel()


def new_collection(name):
    """Create and link a new collection"""
    collect = bpy.data.collections.get(name)
    grp_name = name
    i = 1
    if collect is None:
        grp = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(grp)
    else:
        # if a collection already exist, create a new one
        while bpy.data.collections.get(grp_name) is not None:
            grp_name = name + str(i)
            i += 1
        grp = bpy.data.collections.new(grp_name)
        bpy.context.scene.collection.children.link(grp)
    return grp_name


# ------------------------- Initialisation --------------------------
def init_array_tools(context):
    """Initialisation of the array tools"""
    prop = bpy.context.scene.arraytools_prop
    # start in creation mode
    prop.anim_mode = '0'
    Larray.bank = [[[]]]

    Larray.grp_name = new_collection(Larray.grp_name)
    if not prop.already_start:
        tmp = []
        # get all reference names
        active = bpy.context.selected_objects

        prop.already_start = True
        prop.is_tr_off_last = True
        if active:
            for index, elem in enumerate(active):
                Larray.bank[0][0].append(elem.name)
                tmp.append((str(index), elem.name, ''))

            add_column(Larray.bank[0][0], Larray.grp_name, 1, 1, 2, 0)
            Larray.items = list(tmp)
            prop.update_offset(context)
        # no need anymore
        else:
            print("No object selected")
    else:
        print("Already started!")


# ----------------------- Copy objects part -------------------------
def add_obj(nrefs, ngrp, rows, rowe, cnts, p1, cnte, p2, func):
    """Duplicate, link in array collection and store in bank

    Parameters:
    nrefs      -- names of all references objects
    ngrp       -- name of the array collection
    rows       -- start row
    rowe       -- end row
    cnts       -- start count(column)
    cnte       -- end count
    p1         -- start alter
    p2         -- end alter
    func       -- add empty list or empty list of list
    """
    refs_tmp = []
    grp = bpy.data.collections.get(ngrp)
    if grp is None:
        grp = bpy.context.scene.collection

    # Try to find invalid reference object
    for index, ref_name in enumerate(nrefs):
        ref = bpy.data.objects.get(ref_name)
        if ref is None:
            Larray.to_del[ref_name] = index
            continue
        refs_tmp.append(ref)

    if not refs_tmp:
        raise ReferenceMissing("No reference found, Addon will reset.")

    # remove all duplicates without reference (avoid name reassignment error)
    if Larray.to_del:
        display_error("Invalid reference(s) : duplicates will be deleted.")
        for i in range(len(Larray.bank)):
            for j in range(len(Larray.bank[i])):
                for index in Larray.to_del.values():
                    del_by_name(Larray.bank[i][j].pop(index))
        Larray.to_del.clear()

    # print(f"i=[{rows}..{rowe}], j=[{cnts} + i*{p1}..{cnte} + i*{p2}]")
    for i in range(rows, rowe):
        func(i)
        tmp = cnte + i*p2
        # print(f"add : i=[{rows} .. {rowe-1}]   j=[{cnts+i*p1} .. {tmp-1}]")
        for j in range(cnts + i*p1, tmp-1):
            for ref_obj in refs_tmp:
                objcp = ref_obj.copy()
                grp.objects.link(objcp)
                add_bk_copy(i, j, objcp.name)
            add_new_col(i)
        for ref_obj in refs_tmp:
            objcp = ref_obj.copy()
            grp.objects.link(objcp)
            add_bk_copy(i, -1, objcp.name)


def add_column(nrefs, ngrp, row, old_count, count, alter):
    """Duplicate and store elements in new column(s)"""
    # add_obj(refs, grp, start_r, end_r, start_c, alt1, end_c, alt2, func)
    add_obj(nrefs, ngrp, 0, row, old_count, alter, count, alter, add_new_col)


def add_alt(nrefs, ngrp, row, count, old_alter, alter):
    """Duplicate and store elements"""
    # add_obj(refs, grp, start_r, end_r, start_c, alt1, end_c, alt2, func)
    add_obj(nrefs, ngrp, 1, row, count, old_alter, count, alter, add_new_col)


def add_row(nrefs, ngrp, old_row, row, count, alter):
    """Duplicate and store elements in new row(s)"""
    # add_obj(refs, grp, start_r, end_r, start_c, alt1, end_c, alt2, func)
    add_obj(nrefs, ngrp, old_row, row, 0, 0, count, alter, add_new_row)


# ---------------------- delete part --------------------------------
def del_ref_n_copy(row, column, alter, ref_name):
    """Remove duplicates without reference"""
    for index in ref_name.values():
        Larray.items.pop(index)
        for i in range(row):
            for j in range(column + i*alter):
                del_by_name(Larray.bank[i][j].pop(index))
    ref_name.clear()


def del_by_name(name):
    """Delete and unlink object from the given name"""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return False
    # retrieve the collection from object
    grp = obj.users_collection[0]
    grp.objects.unlink(obj)
    bpy.data.objects.remove(obj, do_unlink=True)
    return True


def del_obj(rows, rowe, stp1, cnts, p1, cnte, p2, stp2, func):
    """Remove elements

    Parameters:
    rows       -- start row
    rowe       -- end row
    stp1       -- step for row
    cnts       -- start count(column)
    cnte       -- end count
    p1         -- start alter
    p2         -- end alter
    stp2       -- step for column
    func       -- function pop_row or pop_column
    """
    for i in range(rows, rowe, stp1):
        for j in range(cnts + i*p1, cnte + i*p2, stp2):
            for name in func(i):
                del_by_name(name)
                # print(name, "deleted !")


def del_col(row, column, nb_column):
    """Remove elements in column"""
    # del_obj(start_r, end_r, step1, start_c, alt1, end_c, alt2, step2, func)
    del_obj(row-1, -1, -1, column-1, 0, column-nb_column-1, 0, -1, pop_column)


def del_alt(row, column, old_alter, alter):
    # del_obj(start_r, end_r, step1, start_c, alt1, end_c, alt2, step2, func)
    del_obj(row-1, 0, -1, column, old_alter, column, alter, -1, pop_column)


def del_row(old_row, row):
    """Remove elements in row"""
    # del_obj(start_r, end_r, step1, start_c, alt1, end_c, alt2, step2, func)
    del_obj(old_row-1, row-1, -1, 0, 0, 1, 0, 1, pop_row)


# -------------------------- Message box ----------------------------
def display_error(msg):
    """Call the operator to display an error message"""
    bpy.ops.info.at_error('INVOKE_DEFAULT', info=msg)


# -------------------------- Mask part ------------------------------
def mask_obj(collection, nb_to_mask):
    """Get a random list of objects to mask"""
    if collection is None:
        return
    nb_elems = len(collection.objects)
    if nb_elems < nb_to_mask:
        nb_to_mask = nb_elems
    if collection is not None:
        reset_mask()
        Larray.mask = random.sample(collection.objects.keys(), nb_to_mask)
        for name in Larray.mask:
            bpy.data.objects[name].hide_viewport = True


def reset_mask():
    """Unhide masked objects"""
    if Larray.mask:
        for name in Larray.mask:
            bpy.data.objects[name].hide_viewport = False
        Larray.mask.clear()


def del_obj_mask():
    """Delete masked objects"""
    collection = bpy.data.collections.get(Larray.grp_name)
    if collection is None:
        return
    if Larray.mask:
        for name in Larray.mask:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                collection.objects.unlink(obj)
                bpy.data.objects.remove(obj, do_unlink=True)
        Larray.mask.clear()


# ----------------------------- Set-up ------------------------------
def place_obj(
    row, col, alt, vtr1, vsc1, vro1, vtr2, vsc2, vro2, valign, is_lsr,
    func1, func2
):
    """Place valid objects according to their position in bank

    Parameters:
    row    -- number of rows in column gives by user
    col    -- number of columns gives by user
    alt    -- alter gives by user
    vtr1   -- translation vector in column gives by user
    vsc1   -- scale vector gives in column by user
    vro1   -- rotation vector in column gives by user
    vtr2   -- translation vector in row gives by user
    vsc2   -- scale vector gives in row by user
    vro2   -- rotation vector in row gives by user
    valign -- align vector
    is_lsr -- contains states for translation and rotation
    func1  -- calculation for scale : scale_linear() or scale_calc()
    func2  -- retrieve global transforms according to scale method
    """
    p = bpy.context.scene.arraytools_prop
    nb_refs = 0

    tr_global = (0, 0, 0)
    vecxyz = (acf.x_axis(), acf.y_axis(), acf.z_axis())

    for index, name in enumerate(Larray.bank[0][0]):
        ref = bpy.data.objects.get(name)
        if ref is None:
            # store the invalid ref name to remove duplicates later
            Larray.to_del[name] = index
            continue
        nb_refs += 1

        mtx = ref.matrix_world.copy()
        loc_ref, rot_ref, sc_ref = mtx.decompose()

        pivot = mtx.translation if p.at_pivot is None else p.at_pivot.location

        loc_ma = Matrix.Translation(loc_ref)
        rot_ma = rot_ref.to_matrix().to_4x4()
        mt = Matrix.Translation(pivot - loc_ref)
        # if rotation is local
        if not is_lsr[1]:
            vecxyz = (
                acf.local_axis(mtx, acf.x_axis()),
                acf.local_axis(mtx, acf.y_axis()),
                acf.local_axis(mtx, acf.z_axis())
            )
        for i in range(row):
            for j in range(col + i*alt):
                # print("i=",i,"j=",j)
                obj = bpy.data.objects.get(Larray.bank[i][j][index])
                if obj is None:
                    continue

                vtr = j * vtr1 + i * vtr2 + i * valign

                trm = Matrix.Translation(vtr)
                m0 = Matrix.Translation((0, 0, 0))
                # if translation uses world axis
                if is_lsr[0]:
                    m0, trm = trm, m0

                sc_ma = Matrix.Scale(sc_ref[0], 4, (1, 0, 0)) @ \
                    Matrix.Scale(sc_ref[1], 4, (0, 1, 0)) @ \
                    Matrix.Scale(sc_ref[2], 4, (0, 0, 1))

                angle = j * Vector(vro1) + i * Vector(vro2)

                mr = Matrix.Rotation(angle[0], 4, vecxyz[0]) @ \
                    Matrix.Rotation(angle[1], 4, vecxyz[1]) @ \
                    Matrix.Rotation(angle[2], 4, vecxyz[2])
                mra = mt @ mr @ mt.inverted()

                vsc = func1(i, j, vsc2, vsc1)

                scm = Matrix.Scale(vsc[0], 4, (1, 0, 0)) @ \
                    Matrix.Scale(vsc[1], 4, (0, 1, 0)) @ \
                    Matrix.Scale(vsc[2], 4, (0, 0, 1))

                if pivot == loc_ref:
                    mw = m0 @ loc_ma @ rot_ma @ trm @ scm @ sc_ma @ mr
                else:
                    mw = m0 @ loc_ma @ mra @ rot_ma @ trm @ scm @ sc_ma

                obj.matrix_world = mw

    if not nb_refs:
        raise ReferenceMissing("No reference found, Addon will reset.")
    return func2(col, vtr1, vsc1, vro1)


# -------------------------------------------------------------------
def select_all(row, column, alter, index):
    """Select copies and reference for the given index"""
    collection = bpy.data.collections.get(Larray.grp_name)
    if collection is None:
        print("No one to select! ")
        return

    ref_name = Larray.bank[0][0][index]

    ref = bpy.data.objects.get(ref_name)
    if ref is None:
        Larray.to_del[ref_name] = index
        del_ref_n_copy(row, column, alter, Larray.to_del)
        return

    # unselect all first
    for objs in bpy.context.selected_objects:
        objs.select_set(state=False)

    # select all copies
    for i in range(row-1, -1, -1):
        for j in range(column-1 + i*alter, -1, -1):
            name = Larray.bank[i][j][index]
            obj = bpy.data.objects.get(name)
            if obj is None:
                continue
            else:
                obj.select_set(state=True)

    # and the reference
    bpy.context.view_layer.objects.active = obj


# --------------------------- update modifiers ----------------------
def add_del_modifiers(self):
    """Add or remove modifiers"""

    index = int(self.reference)
    ref_name = Larray.bank[0][0][index]
    ref = bpy.data.objects.get(ref_name)
    if ref is None:
        return

    collection = bpy.data.collections.get(Larray.grp_name)
    if collection is None:
        return
    for i in range(self.row):
        for j in range(self.count + i*self.alter):
            # no need to select the ref
            if i == 0 and j == 0:
                continue
            elem = Larray.bank[i][j][index]
            obj = bpy.data.objects.get(elem)
            if obj is not None:
                # remove all modifiers
                for m in obj.modifiers:
                    obj.modifiers.remove(m)
                # add modifiers
                for m_src in ref.modifiers.values():
                    m_dest = obj.modifiers.new(name=m_src.name, type=m_src.type)
                    # and copy attributes
                    for attr in m_src.bl_rna.properties:
                        if not attr.is_readonly:
                            setattr(
                                m_dest, attr.identifier,
                                getattr(m_src, attr.identifier)
                            )


def make_single(row, column, alter):
    """Make link duplicates into copies"""
    for index, name in enumerate(Larray.bank[0][0]):
        ref = bpy.data.objects.get(name)
        if ref is None:
            continue
        for i in range(row):
            for j in range(column + i*alter):
                if i == 0 and j == 0:
                    continue
                objcp = bpy.data.objects.get(Larray.bank[i][j][index])
                if objcp is not None:
                    objcp.data = ref.data.copy()


# -------------------------------------------------------------------
def to_hide(old_row, row, old_col, col, old_alt, alt, is_hide):
    for i in range(old_row, row):
        for j in range(old_col + i*old_alt, col + i*alt):
            for name in Larray.bank[i][j]:
                obj = bpy.data.objects.get(name)
                if obj is None or name in Larray.mask:
                    continue
                obj.hide_viewport = is_hide
                obj.hide_render = is_hide
