# -*- coding: utf-8 -*-
import bpy

# count values, contains only 2 values : old count and current
at_count_values = []
# row value, contains old row and current
at_row_values = []
# alter values, contains old and current
at_alter = []
# maximun row according to column and alter 
maxrow = 1
# list of the copies / list of lists
atools_objs = []
ref_mtx = [] # reference matrix
# collection name
col_name = "Array_collection"


def init_array_tool(context):
    """Initialisation of the array tools"""
    global at_count_values
    global at_row_values
    global at_alter
    global atools_objs
    global ref_mtx
    global col_name

    prop = context.scene.arraytools_prop
    name = col_name
    i = 1
    collect = bpy.data.collections.get(col_name)
    # create and link the new collection
    if collect is None:
        array_col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(array_col)
    else:
        # if a collection already exist, create a new one
        while bpy.data.collections.get(name) is not None:
            name = col_name + str(i)
            i += 1
        array_col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(array_col)
        col_name = name

    if not prop.already_start:
        at_count_values = [1, 2]
        at_row_values = [0, 1]
        at_alter = [0, 0]
        active = context.active_object
        prop.already_start = True
        prop.is_tr_off_last = True
        if active is not None:
            atools_objs.append([active.name])
            ref_mtx = active.matrix_world.copy()
            del active
            prop.add_in_column(prop.row)
        # no need anymore
        else:
            print("No object selected")
    else:
        print("Already started!")


def add_count(value):
    """Save the current count"""
    global at_count_values
    at_count_values.append(value)


def del_count():
    """Del the previous count"""
    global at_count_values
    del at_count_values[0]


def add_row(value):
    """Save the current row"""
    global at_row_values
    at_row_values.append(value)


def del_row():
    """ Del the previous row value"""
    global at_row_values
    del at_row_values[0]


def add_alter(value):
    """save the current variation"""
    global at_alter
    at_alter.append(value)


def del_alter():
    """Remove previous variation"""
    global at_alter
    del at_alter[0]


def display_error(msg):
    """Call the operator to display an error message"""
    bpy.ops.info.at_error('INVOKE_DEFAULT', info = msg)

