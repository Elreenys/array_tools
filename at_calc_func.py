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
import random

from mathutils import Matrix
from mathutils import Vector

from . import at_array as aa


def at_random_fill(min, max):
    """Returns two random reals in ascending order"""
    first = random.uniform(min, max)
    second = random.uniform(min, max)
    if first <= second:
        return(first, second)
    else:
        return(second, first)


def at_random(
    seed, totalc, totalr, mint, maxt, mins, maxs, minr, maxr,
    btr, bsc, brot, uniform, tr1, tr2, sc1, sc2, r1, r2, varia, valign,
    mscale, t_axis, r_axis
):
    """Random function for translation, scale and rotation

    Parameters:
    seed    -- seed for random
    totalc  -- number of columns
    totalr  -- number of rows
    mint    -- minimum for translation
    maxt    -- maximum for translation
    mins    -- minimum for scale
    maxs    -- maximum for scale
    minr    -- minimum for rotation
    maxr    -- maximun for rotation
    btr     -- (boolean) use translation or not
    bsc     -- (boolean) use scale or not
    brot    -- (boolean) use rotation or not
    uniform -- (boolean) use uniform scale or not
    tr1     -- translation offset of the column
    tr2     -- translation offset of the row
    sc1     -- scale offset of the column
    sc2     -- scale offset of the row
    r1      -- rotation offset of the column
    r2      -- rotation offset of the row
    varia   -- variation of rows
    valign  -- Vector of align of rows
    mscale  -- calculation method for scale
    t_axis  -- orientation axis for translation
    r_axis  -- orientation axis for rotation
    """
    if not btr and not bsc and not brot:
        # no need to continue if all are False
        return
    tr, sc, rot = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    random.seed(seed)
    for j in range(totalr):
        for k in range(totalc + j*varia):
            if j == 0 and k == 0:
                continue
            for name in aa.Larray.bank[j][k]:
                elem = bpy.data.objects.get(name)

                if elem is not None:
                    for i in range(3):
                        tr[i] = random.uniform(mint[i], maxt[i])
                        sc[i] = random.uniform(mins[i]/100, maxs[i]/100)
                        rot[i] = random.uniform(minr[i], maxr[i])
                    if uniform:
                        sc[0] = sc[1] = sc[2]
                    mt = Matrix.Translation(tr)
                    ms = Matrix.Scale(sc[0], 4, (1, 0, 0)) @ \
                        Matrix.Scale(sc[1], 4, (0, 1, 0)) @ \
                        Matrix.Scale(sc[2], 4, (0, 0, 1))
                    mr = Matrix.Rotation(rot[0], 4, (1, 0, 0)) @ \
                        Matrix.Rotation(rot[1], 4, (0, 1, 0)) @ \
                        Matrix.Rotation(rot[2], 4, (0, 0, 1))

                    if btr:
                        elem.matrix_world @= mt
                    if bsc:
                        elem.matrix_world @= ms
                    if brot:
                        elem.matrix_world @= mr


def x_axis():
    """Get the x axis"""
    return Vector((1.0, 0.0, 0.0))


def y_axis():
    """Get the y axis"""
    return Vector((0.0, 1.0, 0.0))


def z_axis():
    """Get the z axis"""
    return Vector((0.0, 0.0, 1.0))


def xyz_axis():
    """Get the xyz axis"""
    return Vector((1.0, 1.0, 1.0))


def local_axis(obj_mat, axis):
    """Return the world coordinates of axis from obj space"""
    return axis @ obj_mat.inverted()

'''
def at_all_in_one(ref, angle, vecxyz, vec_tr, vec_sc, pivot):
    """Return the matrix of transformations"""
    # Matrix is composed by location @ rotation @ scale
    loc_ref, rot_ref, sc_ref = ref.decompose()

    loc_ma = Matrix.Translation(loc_ref)
    rot_ma = rot_ref.to_matrix().to_4x4()
    sc_ma = Matrix.Scale(sc_ref[0], 4, (1, 0, 0)) @ \
        Matrix.Scale(sc_ref[1], 4, (0, 1, 0)) @ \
        Matrix.Scale(sc_ref[2], 4, (0, 0, 1))

    mt = Matrix.Translation(pivot - loc_ref)
    mr = Matrix.Rotation(angle[0], 4, vecxyz[0]) @ \
        Matrix.Rotation(angle[1], 4, vecxyz[1]) @ \
        Matrix.Rotation(angle[2], 4, vecxyz[2])
    mra = mt @ mr @ mt.inverted()

    trm = Matrix.Translation(vec_tr)
    scm = Matrix.Scale(vec_sc[0], 4, (1, 0, 0)) @ \
        Matrix.Scale(vec_sc[1], 4, (0, 1, 0)) @ \
        Matrix.Scale(vec_sc[2], 4, (0, 0, 1))

    if pivot == loc_ref:
        mw = loc_ma @ rot_ma @ trm @ scm @ sc_ma @ mr
    else:
        mw = loc_ma @ mra @ rot_ma @ trm @ scm @ sc_ma
    return mw
'''


def fill_rotation(context):
    prop = context.scene.arraytools_prop
    offset = prop.rot_offset

    for i in range(3):
        if offset[i] == 0.0:
            prop.rot_min[i], prop.rot_max[i] = \
                at_random_fill(-math.pi, math.pi)
        else:
            prop.rot_min[i], prop.rot_max[i] = \
                at_random_fill(-offset[i]*2, offset[i]*2)


def sum_serie(n, factor):
    """Return the sum of the serie 1+2+3+4+...+n with a factor """
    return ((n * (n - 1)) / 2) * factor

'''
# (T)ranslate (S)cale (R)otation vector
def tsr(ref_sc, col, row, tcol, trow, scol, srow, rcol, rrow, ralign):
    """Return the translation, scale and rotation vector according
    to the position in the array

    Parameters:
    ref_sc -- scale of the reference object
    col    -- position in column
    row    -- position in row
    tcol   -- translate offset in column
    trow   -- translate offset in row
    scol   -- scale offset in column
    srow   -- scale offset in row
    rcol   -- rotation offset in column
    rrow   -- rotation offset in row
    ralign -- vector for row align

    Return:
    3 Vectors (translation, scale, rotation)
    """
    translate = col * tcol + row * trow + row * ralign
    #print("in tsr :")
    #print(f"translate = {translate}, col = {col}, row = {row}")
    rotate = col * Vector(rcol) + row * Vector(rrow)
    s1 = col * (ref_sc - (scol/100))
    s2 = row * (ref_sc - (srow/100))
    scale = xyz_axis() - s1 - s2

    sc1col = (scol[0]/100)**(col)
    sc2col = (scol[1]/100)**(col)
    sc3col = (scol[2]/100)**(col)
    sc1row = (srow[0]/100)**(row)
    sc2row = (srow[1]/100)**(row)
    sc3row = (srow[2]/100)**(row)

    sc1 = sc1col * sc1row
    sc2 = sc2col * sc2row
    sc3 = sc3col * sc3row
    sc = Vector((sc1, sc2, sc3))
    return translate, sc, rotate
'''


# ------------ scale offset calculation from position ---------------
def scale_linear(row, col, scale_row, scale_col):
    """Linear scale for offset

    Return :
    vector (scale of the element at position row, column in bank)
    """
    s1 = col * (xyz_axis() - (scale_col/100))
    s2 = row * (xyz_axis() - (scale_row/100))
    return xyz_axis() - s1 - s2


def scale_calc(row, col, scale_row, scale_col):
    """Factor scale for offset

    Return :
    vector (scale of the element at position row, column in bank)
    """
    sc1 = ((scale_col[0]/100)** (col)) * ((scale_row[0]/100)** (row))
    sc2 = ((scale_col[1]/100)** (col)) * ((scale_row[1]/100)** (row))
    sc3 = ((scale_col[2]/100)** (col)) * ((scale_row[2]/100)** (row))
    return Vector((sc1, sc2, sc3))


# --------- global calculation from offset informations -------------
def find_tr_global(column, toff):
    """Return global translation from offset"""
    return (column-1) * toff


def find_ro_global(column, roff):
    """Return global rotation from offset"""
    return column * Vector(roff)


def find_sc1_global(column, soff):
    """Return global scale from offset with linear method"""
    return (xyz_axis() - (column-1) * (xyz_axis() - (soff/100))) * 100


def linear_global(column, toff, soff, roff):
    return find_tr_global(column, toff), find_sc1_global(column, soff), \
        find_ro_global(column, roff)


def find_sc2_global(column, soff):
    """Return global scale from offset with factor method"""
    sx, sy, sz = soff[0] / 100, soff[1] / 100, soff[2] / 100
    s0, s1, s2 = sx ** column, sy ** column, sz ** column
    return Vector((s0, s1, s2)) * 100


def calc_global(column, toff, soff, roff):
    return find_tr_global(column, toff), find_sc2_global(column, soff), \
       find_ro_global(column, roff)


# --------- offset calculation from global informations -------------
def find_tr_offset(column, tglo):
    """Return offset translation from global"""
    return tglo / (column - 1)


def find_ro_offset(column, rglo, is_pivot):
    """Return offset rotation from global"""
    """
    - Beware -
    With 360° in global and with a pivot, reference object must be included
    """
    return Vector(rglo) / (column) if is_pivot else Vector(rglo) / (column-1)


def linear_offset(column, sglo):
    """Return offset scale from global with linear scale"""
    return (xyz_axis() - ((xyz_axis() - (sglo/100)) / (column - 1))) * 100


def calc_offset(column, sglo):
    """Return offset scale from global with factor scale"""
    sc1, sc2, sc3 = abs(sglo[0]), abs(sglo[1]), abs(sglo[2])
    vec1 = sglo[0] / sc1 * 100
    vec2 = sglo[1] / sc2 * 100
    vec3 = sglo[2] / sc3 * 100
    sb1 = math.pow(sc1/100, 1/column) * vec1
    sb2 = math.pow(sc2/100, 1/column) * vec2
    sb3 = math.pow(sc3/100, 1/column) * vec3
    return Vector((sb1, sb2, sb3))
