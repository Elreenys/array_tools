
import bpy

from bpy.types import PropertyGroup
from mathutils import Vector

from . import cfg
from . import at_panel
from . import at_operators
from . at_calc_func import(
    local_x_axis,
    local_y_axis,
    local_z_axis,
    at_all_in_one,
    rotate_self,
    at_random
)


def update_seed(self, context):
    if self.at_mode == 'ADV':
        sc_min = (self.sc_min_x, self.sc_min_y, self.sc_min_z)
        sc_max = (self.sc_max_x, self.sc_max_y, self.sc_max_z)
        at_random(self.at_seed, cfg.mtx_list, cfg.list_duplicate, self.tr_min, self.tr_max, sc_min,
            sc_max, self.rot_min, self.rot_max, self.at_is_tr, self.at_is_sc, self.at_is_rot, self.sc_all)
    else:
        vec = Vector((1.0, 1.0, 1.0))
        tr = self.tr_rand * vec
        sc = self.sc_rand * vec
        rot = self.rot_rand * vec
        at_random(self.at_seed, cfg.mtx_list, cfg.list_duplicate, -tr, tr, sc, 100*vec, -rot, rot,
            self.at_is_tr, self.at_is_sc, self.at_is_rot, False)


def update_rtr(self, context):
    self.tr_max = self.tr_rand * Vector((1.0, 1.0, 1.0))
    self.tr_min = self.tr_rand * Vector((-1.0, -1.0, -1.0))


def update_rsc(self, context):
    self.sc_max_x, self.sc_max_y, self.sc_max_z = (100.0, 100.0, 100.0)
    rand = self.sc_rand
    self.sc_min_x, self.sc_min_y, self.sc_min_z = rand, rand, rand


def update_rrot(self, context):
    self.rot_max = self.rot_rand * Vector((1.0, 1.0, 1.0))
    self.rot_min = self.rot_rand * Vector((-1.0, -1.0, -1.0))


# ---------------------------- Properties ----------------------
class AT_props(PropertyGroup):
    """Property for array tools"""

    def add_at_element(self, nb_to_add=-1):
        """Add nb_to_add copy in the scene"""
        if nb_to_add == -1:
            nb_to_add = cfg.at_values[1] - cfg.at_values[0]
        obj = cfg.obj_ref
        print(f"add {nb_to_add} element(s) ")
        for i in range(nb_to_add):
            objcp = obj.copy()
            array_col = bpy.data.collections.get("Array_collection")
            array_col.objects.link(objcp)
            if self.is_copy:
                objcp.data = obj.data.copy()

            cfg.list_duplicate.append(objcp)

        cfg.add_matrix(nb_to_add, cfg.list_duplicate)

        if self.is_tr_off_last:
            self.update_offset(bpy.context)
        else:
            self.update_global(bpy.context)


    def at_del_element(self, nb_to_del=-1):
        """Delete copy from scene and from list"""
        if nb_to_del == -1:
            nb_to_del = cfg.at_values[0] - cfg.at_values[1]
        print(f"del {nb_to_del} element(s)")
        for i in range(nb_to_del):
            obj = cfg.list_duplicate.pop()
            array_col = bpy.data.collections.get("Array_collection")
            array_col.objects.unlink(obj)
            bpy.data.objects.remove(obj, do_unlink=True)

        cfg.del_matrix(nb_to_del)

        if self.is_tr_off_last:
            self.update_offset(bpy.context)
        else:
            self.update_global(bpy.context)


    def at_del_all(self):
        """Delete all copies and remove objects from lists"""
        bpy.ops.object.delete({"selected_objects": cfg.list_duplicate})
        cfg.list_duplicate.clear()
        cfg.mtx_list.clear()
        cfg.obj_ref = None
        print("Del_all done!")

    # ----------------------- UI update ----------------------
    # --------------------------------------------------------
    # ----------------------- count update -------------------
    def updateCount(self, context):
        """update the number of element(s)"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            cfg.add_value(int(self.count))
            cfg.del_value()

            # cfg.at_values[0] always get old count
            self.old_count = cfg.at_values[0]

            if self.old_count < self.count:
                self.add_at_element()
            elif self.old_count > self.count:
                self.at_del_element()

    def up_ui_updateCount(self, val):
        """Update the value of the property count in UI"""
        self.is_prog_change = True
        self.count = val

    # ----------------------- translation update --------------
    def up_ui_tr_offset(self, val):
        """Update the value of the property tr_offset in UI"""
        self.is_prog_change = True
        self.tr_offset = val

    def up_ui_tr_global(self, val):
        """Update the value of the property tr_global in UI"""
        self.is_prog_change = True
        self.tr_global = val

    # ----------------------- scale update --------------------
    def up_ui_sc_offset(self, val):
        """Update the value of the property sc_offset in UI"""
        self.is_prog_change = True
        self.sc_offset = val

    def up_ui_sc_global(self, val):
        """Update the value of the property sc_global in UI"""
        self.is_prog_change = True
        self.sc_global = val

    # ----------------------- rotation update -----------------
    def up_ui_rot_offset(self, val):
        """Update the value of the property rot_offset in UI
            val is a float """
        self.is_prog_change = True
        self.rot_offset = val

    def up_ui_rot_global(self, val):
        """Update the value of the property rot_global in UI"""
        self.is_prog_change = True
        self.rot_global = val

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


    # ---------------------------------------------------------
    def update_offset(self, context):
        """Update for all offsets"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            # user change offset
            self.is_tr_off_last = True
            i = 1

            loc_x = local_x_axis(cfg.obj_ref)
            loc_y = local_y_axis(cfg.obj_ref)
            loc_z = local_z_axis(cfg.obj_ref)
            localxyz = (loc_x, loc_y, loc_z)

            if self.at_pivot is not None:
                for elem in cfg.list_duplicate:
                    r_off = i * Vector((self.rot_offset))
                    t_off = i * self.tr_offset
                    s_off = Vector((1.0, 1.0, 1.0)) - (i * (cfg.obj_ref.scale - (self.sc_offset/100)))
                    at_all_in_one(cfg.obj_ref, elem, r_off, localxyz, t_off, s_off, self.at_pivot.location)
                    i += 1
            else:
                for elem in cfg.list_duplicate:
                    r_off = i * Vector((self.rot_offset))
                    t_off = i * self.tr_offset
                    s_off = Vector((1.0, 1.0, 1.0)) - (i * (cfg.obj_ref.scale-(self.sc_offset/100)))
                    at_all_in_one(cfg.obj_ref, elem, (0.0, 0.0, 0.0), localxyz, t_off, s_off, cfg.obj_ref.location)
                    rotate_self(elem, r_off, localxyz)
                    i += 1
            self.up_ui_tr_global(t_off)
            self.up_ui_sc_global(s_off * 100)
            # global rotation need to include reference object
            self.up_ui_rot_global(r_off + Vector((self.rot_offset)))

            cfg.update_matrix(context)


    def update_global(self, context):
        """Update for all globals"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            # user change global
            self.is_tr_off_last = False
            i = 1
            # local axis
            loc_x = local_x_axis(cfg.obj_ref)
            loc_y = local_y_axis(cfg.obj_ref)
            loc_z = local_z_axis(cfg.obj_ref)

            localxyz = (loc_x, loc_y, loc_z)

            translation_offset = Vector(self.tr_global) / (self.count - 1)
            scale_offset = (cfg.obj_ref.scale-(self.sc_global/100)) / (self.count - 1)
            rotation_offset = Vector((self.rot_global)) / self.count

            for elem in cfg.list_duplicate:
                r_off = i * Vector((rotation_offset))
                t_off = i * translation_offset
                s_off = Vector((1.0, 1.0, 1.0)) - (i*scale_offset)
                if self.at_pivot is not None:
                    at_all_in_one(cfg.obj_ref, elem, r_off, localxyz, t_off, s_off, self.at_pivot.location)
                else:
                    at_all_in_one(cfg.obj_ref, elem, (0.0, 0.0, 0.0), localxyz, t_off, s_off, cfg.obj_ref.location)
                    rotate_self(elem, r_off, localxyz)
                i += 1
            self.up_ui_tr_offset(translation_offset)
            self.up_ui_sc_offset(Vector((100.0, 100.0, 100.0)) - (scale_offset*100))
            self.up_ui_rot_offset(rotation_offset)

            cfg.update_matrix(context)


    # ----------------------- is_copy update ------------------
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
                for elem in cfg.list_duplicate:
                    elem.data = cfg.obj_ref.data.copy()
            else:  # since the value change (now duplicate) copies can't become duplicates, so need to rebuild
                nb_to_rebuild = len(cfg.list_duplicate)
                bpy.ops.object.delete({"selected_objects": cfg.list_duplicate})
                cfg.list_duplicate.clear()
                self.add_at_element(nb_to_rebuild)


    # -------------- update min and max ---------------
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
                self.up_ui_sc_max_x(self.sc_min_x)
                # with uniform : min_x = min_y = min_z same for max
                self.up_ui_sc_min_y(self.sc_min_x)
                self.up_ui_sc_min_z(self.sc_min_x)
                self.up_ui_sc_max_y(self.sc_min_x)
                self.up_ui_sc_max_z(self.sc_min_x)
            elif self.sc_all:
                self.up_ui_sc_min_y(self.sc_min_x)
                self.up_ui_sc_min_z(self.sc_min_x)
                self.up_ui_sc_max_y(self.sc_max_x)
                self.up_ui_sc_max_z(self.sc_max_x)
            elif test:
                self.up_ui_sc_max_x(self.sc_min_x)


    def up_sc_min_y(self, context):
        """Update sc_max_y if sc_min_y is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_y > self.sc_max_y
            if test and self.sc_all:
                self.up_ui_sc_max_y(self.sc_min_y)
                # with uniform : min_x = min_y = min_z same for max
                self.up_ui_sc_min_x(self.sc_min_y)
                self.up_ui_sc_min_z(self.sc_min_y)
                self.up_ui_sc_max_x(self.sc_min_y)
                self.up_ui_sc_max_y(self.sc_min_y)
            elif self.sc_all:
                self.up_ui_sc_min_x(self.sc_min_y)
                self.up_ui_sc_min_z(self.sc_min_y)
                self.up_ui_sc_max_x(self.sc_max_y)
                self.up_ui_sc_max_z(self.sc_max_y)
            elif test:
                self.up_ui_sc_max_y(self.sc_min_y)


    def up_sc_min_z(self, context):
        """Update sc_max_z if sc_min_z is higher"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_z > self.sc_max_z
            if test and self.sc_all:
                self.up_ui_sc_max_z(self.sc_min_z)
                # with uniform : min_x = min_y = min_z same for max
                self.up_ui_sc_min_x(self.sc_min_z)
                self.up_ui_sc_min_y(self.sc_min_z)
                self.up_ui_sc_max_x(self.sc_min_z)
                self.up_ui_sc_max_y(self.sc_min_z)
            elif self.sc_all:
                self.up_ui_sc_min_x(self.sc_min_z)
                self.up_ui_sc_min_y(self.sc_min_z)
                self.up_ui_sc_max_x(self.sc_max_z)
                self.up_ui_sc_max_y(self.sc_max_z)
            elif test:
                self.up_ui_sc_max_y(self.sc_min_z)


    def up_sc_max_x(self, context):
        """Update sc_min_x if sc_max_x is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_x > self.sc_max_x
            if test and self.sc_all:
                self.up_ui_sc_min_x(self.sc_max_x)
                # with uniform : min_x = min_y = min_z same for max
                self.up_ui_sc_max_y(self.sc_max_x)
                self.up_ui_sc_max_z(self.sc_max_x)
                self.up_ui_sc_min_y(self.sc_max_x)
                self.up_ui_sc_min_z(self.sc_max_x)
            elif self.sc_all:
                self.up_ui_sc_max_y(self.sc_max_x)
                self.up_ui_sc_max_z(self.sc_max_x)
                self.up_ui_sc_min_y(self.sc_min_x)
                self.up_ui_sc_min_z(self.sc_min_x)
            elif test:
                self.up_ui_sc_min_x(self.sc_max_x)


    def up_sc_max_y(self, context):
        """Update sc_min_y if sc_max_y is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_y > self.sc_max_y
            if test and self.sc_all:
                self.up_ui_sc_min_y(self.sc_max_y)
                # with uniform : min_x = min_y = min_z same for max
                self.up_ui_sc_max_x(self.sc_max_y)
                self.up_ui_sc_max_z(self.sc_max_y)
                self.up_ui_sc_min_x(self.sc_max_y)
                self.up_ui_sc_min_z(self.sc_max_y)
            elif self.sc_all:
                self.up_ui_sc_max_x(self.sc_max_y)
                self.up_ui_sc_max_z(self.sc_max_y)
                self.up_ui_sc_min_x(self.sc_min_y)
                self.up_ui_sc_min_z(self.sc_min_y)
            elif test:
                self.up_ui_sc_min_y(self.sc_max_y)


    def up_sc_max_z(self, context):
        """Update sc_min_z if sc_max_z is lower"""
        if self.is_prog_change:
            self.is_prog_change = False
        else:
            test = self.sc_min_z > self.sc_max_z
            if test and self.sc_all:
                self.up_ui_sc_min_z(self.sc_max_z)

                self.up_ui_sc_max_x(self.sc_max_z)
                self.up_ui_sc_max_y(self.sc_max_z)
                self.up_ui_sc_min_x(self.sc_max_z)
                self.up_ui_sc_min_y(self.sc_max_z)
            elif self.sc_all:
                self.up_ui_sc_max_x(self.sc_max_z)
                self.up_ui_sc_max_y(self.sc_max_z)
                self.up_ui_sc_min_x(self.sc_min_z)
                self.up_ui_sc_min_y(self.sc_min_z)
            elif test:
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


    # ----------------------- reset all properties ------------
    def up_ui_reset(self):
        """Reset all UI properties"""
        self.up_ui_updateCount(2)
        self.up_ui_is_copy()
        self.up_ui_tr_offset(Vector((2.0, 0.0, 0.0)))
        self.up_ui_tr_global(Vector((2.0, 0.0, 0.0)))
        self.up_ui_sc_offset((100, 100, 100))
        self.up_ui_sc_global((100, 100, 100))
        self.up_ui_rot_offset(Vector((0.0, 0.0, 0.0)))
        self.up_ui_rot_global(Vector((0.0, 0.0, 0.0)))

    # ------------------------ property list -------------------
    count: bpy.props.IntProperty(
        name='Count',
        description="Number of elements, original count as one",
        default=2,
        soft_min=2,
        update=updateCount
    )
    # keep the old count to compare later with the current
    old_count: bpy.props.IntProperty(default=2)

    # booleans use to know if user or prog change the value to avoid continuous loop
    is_prog_change: bpy.props.BoolProperty(default=False)  # True if prog change value

    # which one between offset and global user call last, True is offset, False global
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
        update=update_global
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
        update=update_global
    )

    # rotation vector offset
    rot_offset: bpy.props.FloatVectorProperty(
        name='Offset',
        description="Angle between each element",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ',
        unit='ROTATION',
        step=500,  # = 5
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
        update=update_global
    )

    # ----------------------- random part ----------------------
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

    at_is_rot:bpy.props.BoolProperty(
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

    rot_rand:bpy.props.FloatProperty(
        name="Rotation",
        description="Random rotation for all axis",
        unit='ROTATION',
        default=0.0,
        update=update_rrot
    )

