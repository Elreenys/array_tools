import math
import random

from mathutils import Matrix, Vector


def at_random_fill(min, max):
    first = random.uniform(min, max)
    second = random.uniform(min, max)
    if first <= second:
        return(first, second)
    else:
        return(second, first)


def at_random(seed, ref, elems, mint, maxt, mins, maxs, minr, maxr, btr, bsc, brot, uniform):
    """Random function for translation, scale and rotation,
        seed : seed for random
        ref : matrix_world of the elems
        elems : elements to be randomize
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
    """
    random.seed(seed)
    tr, sc, rot = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    j = 0
    for elem in elems:
        for i in range(3):
            tr[i] = random.uniform(mint[i], maxt[i])
            sc[i] = random.uniform(mins[i]/100, maxs[i]/100)
            rot[i] = random.uniform(minr[i], maxr[i])
        if uniform:
                sc[0] = sc[1] = sc[2]
        mt = Matrix.Translation(tr)
        ms = Matrix.Scale(sc[0], 4, (1, 0, 0)) @ Matrix.Scale(sc[1], 4, (0, 1, 0)) @ Matrix.Scale(sc[2], 4, (0, 0, 1))
        mr = Matrix.Rotation(rot[0], 4, (1, 0, 0)) @ Matrix.Rotation(rot[1], 4, (0, 1, 0)) @ Matrix.Rotation(rot[2], 4, (0, 0, 1))

        elem.matrix_world = ref[j]
        if btr:
            elem.matrix_world @= mt
        if bsc:
            elem.matrix_world @= ms
        if brot:
            elem.matrix_world @= mr
        j += 1


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


def at_all_in_one(ref, obj, angle, vecxyz, vec_tr, vec_sc, pivot):
    """Place and rotate with settings"""
    # Matrix is composed by location @ rotation @ scale
    loc_ref, rot_ref, sc_ref = ref.matrix_world.decompose()
    loc_ma = Matrix.Translation(loc_ref)
    rot_ma = rot_ref.to_matrix().to_4x4()
    sc_ma = Matrix.Scale(sc_ref[0], 4, (1, 0, 0)) @ Matrix.Scale(sc_ref[1], 4, (0, 1, 0)) @ Matrix.Scale(sc_ref[2], 4, (0, 0, 1))

    mt = Matrix.Translation(pivot-ref.location)
    mr = Matrix.Rotation(angle[0], 4, vecxyz[0]) @ Matrix.Rotation(angle[1], 4, vecxyz[1]) @ Matrix.Rotation(angle[2], 4, vecxyz[2])
    mra = mt @ mr @ mt.inverted()

    trm = Matrix.Translation(vec_tr)
    scm = Matrix.Scale(vec_sc[0], 4, (1, 0, 0)) @ Matrix.Scale(vec_sc[1], 4, (0, 1, 0)) @ Matrix.Scale(vec_sc[2], 4, (0, 0, 1))

    obj.matrix_world = loc_ma @ mra @ rot_ma @ trm @ scm @ sc_ma


def rotate_self(obj, angle, vecxyz):
    """Rotate obj around his own origin"""
    mr = Matrix.Rotation(angle[0], 4, vecxyz[0]) @ Matrix.Rotation(angle[1], 4, vecxyz[1]) @ Matrix.Rotation(angle[2], 4, vecxyz[2])
    obj.matrix_world @= mr


def fill_rotation(context):
    prop = context.scene.at_prop
    offset = prop.rot_offset

    for i in range(3):
        if offset[i] == 0.0:
            prop.rot_min[i], prop.rot_max[i] = at_random_fill(-math.pi, math.pi)
        else:
            prop.rot_min[i], prop.rot_max[i] = at_random_fill(-offset[i]*2, offset[i]*2)
