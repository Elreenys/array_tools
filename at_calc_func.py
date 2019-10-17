# -*- coding: utf-8 -*-
import bpy
import math
import random

from mathutils import Matrix
from mathutils import Vector

from . import cfg


def at_random_fill(min, max):
    first = random.uniform(min, max)
    second = random.uniform(min, max)
    if first <= second:
        return(first, second)
    else:
        return(second, first)


def at_random(seed, totalc, totalr, mint, maxt, mins, maxs, minr, maxr, btr, bsc, brot, uniform,
    tr1, tr2, sc1, sc2, r1, r2, pivot, varia, valign):
    """Random function for translation, scale and rotation,
        seed : seed for random
        totalc : number of elements in column
        totalr : number of elements in row
        mint : minimum for translation
        maxt : maximum for translation
        mins : minimum for scale
        maxs : maximum for scale
        minr : minimum for rotation
        maxr : maximun for rotation
        btr : (boolean) use translation or not
        bsc : (boolean) use scale or not
        brot : (boolean) use rotation or not
        uniform : (boolean) use uniform scale or not
        tr1 : translation offset of the column
        tr2 : translation offset of the row
        sc1 : scale offset of the column
        sc2 : scale offset of the row
        r1 : rotation offset of the column
        r2 : rotation offset of the row
        pivot : pivot
        varia : variation of rows
        valign : Vector of align of rows
    """
    random.seed(seed)
    tr, sc, rot = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    xyz_vec = (x_axis(), y_axis(), z_axis())
    ref_name = cfg.atools_objs[0][0]
    for j in range(totalr):
        for k in range(totalc + j*varia):
            elem_name = cfg.atools_objs[j][k]
            if elem_name == ref_name:
                continue
            elem = bpy.data.objects[elem_name]
            for i in range(3):
                tr[i] = random.uniform(mint[i], maxt[i])
                sc[i] = random.uniform(mins[i]/100, maxs[i]/100)
                rot[i] = random.uniform(minr[i], maxr[i])
            if uniform:
                    sc[0] = sc[1] = sc[2]
            mt = Matrix.Translation(tr)
            ms = Matrix.Scale(sc[0], 4, (1, 0, 0)) @ Matrix.Scale(sc[1], 4, (0, 1, 0)) @ Matrix.Scale(sc[2], 4, (0, 0, 1))
            mr = Matrix.Rotation(rot[0], 4, (1, 0, 0)) @ Matrix.Rotation(rot[1], 4, (0, 1, 0)) @ Matrix.Rotation(rot[2], 4, (0, 0, 1))

            # recalculate the position...
            vt, vs, vr = tsr(cfg.ref_mtx, k, j, tr1, tr2, sc1, sc2, Vector(r1), Vector(r2), valign)
            
            if pivot is not None:
                emat = at_all_in_one(cfg.ref_mtx, vr, xyz_vec, vt, vs, pivot.location)
            else:
                emat = at_all_in_one(cfg.ref_mtx, vr, xyz_vec, vt, vs, cfg.ref_mtx.translation)
            elem.matrix_world = emat
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


def at_all_in_one(ref, angle, vecxyz, vec_tr, vec_sc, pivot):
    """Return the matrix of transformations"""
    # Matrix is composed by location @ rotation @ scale
    loc_ref, rot_ref, sc_ref = ref.decompose()
    # ref_location = bpy.data.objects[cfg.atools_objs[0][0]].location

    loc_ma = Matrix.Translation(loc_ref)
    rot_ma = rot_ref.to_matrix().to_4x4()
    sc_ma = Matrix.Scale(sc_ref[0], 4, (1, 0, 0)) @ Matrix.Scale(sc_ref[1], 4, (0, 1, 0)) @ Matrix.Scale(sc_ref[2], 4, (0, 0, 1))

    mt = Matrix.Translation(pivot - loc_ref)
    mr = Matrix.Rotation(angle[0], 4, vecxyz[0]) @ Matrix.Rotation(angle[1], 4, vecxyz[1]) @ Matrix.Rotation(angle[2], 4, vecxyz[2])
    mra = mt @ mr @ mt.inverted()

    trm = Matrix.Translation(vec_tr)
    scm = Matrix.Scale(vec_sc[0], 4, (1, 0, 0)) @ Matrix.Scale(vec_sc[1], 4, (0, 1, 0)) @ Matrix.Scale(vec_sc[2], 4, (0, 0, 1))

    if pivot == loc_ref:
        mw = loc_ma @ rot_ma @ trm @ scm @ sc_ma @ mr
    else:
        mw = loc_ma @ mra @ rot_ma @ trm @ scm @ sc_ma
    return mw


def fill_rotation(context):
    prop = context.scene.arraytools_prop
    offset = prop.rot_offset

    for i in range(3):
        if offset[i] == 0.0:
            prop.rot_min[i], prop.rot_max[i] = at_random_fill(-math.pi, math.pi)
        else:
            prop.rot_min[i], prop.rot_max[i] = at_random_fill(-offset[i]*2, offset[i]*2)


def sum_serie(n, factor):
    """Return the sum of the serie 1+2+3+4+...+n
    with a factor
    """
    return ((n * (n - 1)) / 2) * factor


# (T)ranslate (S)cale (R)otation vector
def tsr(mat, col, row, tcol, trow, scol, srow, rcol, rrow, ralign):
    """Retrieve the translation, scale and rotation vector according
    to the position in the array
        mat : matrix of the reference object
        col : position in column
        row : position in row
        tcol : translate offset in column
        trow : translate offset in row
        scol : scale offset in column
        srow : scale offset in row
        rcol : rotation offset in column
        rrow : rotation offset in row
        ralign : row align
    """
    translate = col * tcol + row * trow + row * ralign
    rotate = col * Vector(rcol) + row * Vector(rrow)
    s1 = col * (mat.to_scale() - (scol/100))
    s2 = row * (mat.to_scale() - (srow/100))
    scale = xyz_axis() - s1 - s2
    return translate, scale, rotate
