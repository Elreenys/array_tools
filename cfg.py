import bpy

# global variable stock count, contains only 2 values old count and actual
at_values = []
# reference object
obj_ref = None
# list of the copies
list_duplicate = []
# copies of the matrix_world of elements
mtx_list = []


def init_array_tool(context):
    """Initialisation of the array tools"""
    prop = context.scene.at_prop
    # create and link the new collection
    col_name = "Array_collection"
    if bpy.data.collections.get(col_name) is None:
        array_col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(array_col)

    if not prop.already_start:
        global at_values
        at_values = [1, 2]
        global obj_ref
        active = context.active_object
        prop.already_start = True
        if active is not None:
            obj_ref = active
            prop.add_at_element()
        # no need anymore
        else:
            print("No object selected")
    else:
        print("Already started!")


def add_value(value):
    """Save the actual count"""
    at_values.append(value)


def del_value():
    """Del the previous count"""
    del at_values[0]


def add_matrix(nb, elems):
    for i in range(-nb, 0):
        mtx_list.append(elems[i].matrix_world.copy())


def del_matrix(nb):
    for i in range(nb):
        mtx_list.pop()


def update_matrix(context):
    count = context.scene.at_prop.count - 1
    if (len(list_duplicate) == count) and (len(mtx_list) == count):
        for i in range(count):
            mtx_list[i] = list_duplicate[i].matrix_world.copy()
    else:
        display_miss_error()
        print("Error : counts aren't not the same !")


def draw_error(self, context):
    self.layout.label(text="One or more elements are missing! Continue at your own risks.")


def display_miss_error():
    bpy.context.window_manager.popup_menu(draw_error, title="Error", icon='ERROR')
