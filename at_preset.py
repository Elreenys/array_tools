import bpy
import os

from bl_operators.presets import AddPresetBase 


class AT_MT_preset_menu(bpy.types.Menu): 
    bl_label = 'Presets'
    bl_idname = 'AT_MT_preset_menu'
    preset_subdir = 'array_tools/presets'
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset
    
class AT_OT_AddPreset(AddPresetBase, bpy.types.Operator):
    """Add or remove a preset"""
    bl_idname = 'scene.at_add_preset'
    bl_label = 'Add a preset'
    bl_options = {'REGISTER', 'UNDO'}
    preset_menu = 'AT_MT_preset_menu' 

    preset_defines = [ "props = bpy.context.scene.arraytools_prop"] 
    
    preset_values = [ 
        'props.count',
        'props.row',
        'props.tr_offset',
        'props.tr_global',
        'props.tr_second',
        'props.sc_offset',
        'props.sc_global',
        'props.sc_second',
        'props.sc_method',
        'props.at_pivot',
        'props.rot_offset',
        'props.rot_global',
        'props.rot_second',
        'props.rot_axis',
        
        'props.at_seed',
        'props.at_mode',
        'props.at_is_tr',
        'props.at_is_sc',
        'props.at_is_rot',
        'props.tr_min',
        'props.tr_max',
        'props.tr_rand',
        'props.sc_all',
        'props.sc_min_x',
        'props.sc_min_y',
        'props.sc_min_z',
        'props.sc_max_x',
        'props.sc_max_y',
        'props.sc_max_z',
        'props.sc_rand',
        'props.rot_min',
        'props.rot_max',
        'props.rot_rand'
    ] 
    
    # directory of presets 
    preset_subdir = os.path.join('array_tools', 'presets')