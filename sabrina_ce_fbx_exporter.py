bl_info = {
    "name": "Sabrina's CE FBX Exporter",
    "author": "Sabrina",
    "version": (1, 4),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > FBX SM Export",
    "description": "Export each selected object as FBX with hardcoded settings (max 10 objects)",
    "category": "Import-Export",
}

import bpy
import os

# === Hardcoded FBX export settings ===
FBX_EXPORT_SETTINGS = {
    "use_selection": True,
    "use_visible": False,
    "use_active_collection": False,
    "collection": "",
    "global_scale": 1.0,
    "apply_unit_scale": True,
    "apply_scale_options": 'FBX_SCALE_NONE',
    "use_space_transform": True,
    "bake_space_transform": False,
    "object_types": {'LIGHT', 'MESH', 'ARMATURE', 'OTHER', 'EMPTY', 'CAMERA'},
    "use_mesh_modifiers": True,
    "use_mesh_modifiers_render": True,
    "mesh_smooth_type": 'FACE',
    "colors_type": 'SRGB',
    "prioritize_active_color": False,
    "use_subsurf": False,
    "use_mesh_edges": False,
    "use_tspace": False,
    "use_triangles": False,
    "use_custom_props": False,
    "add_leaf_bones": False,
    "primary_bone_axis": '-X',
    "secondary_bone_axis": 'Y',
    "use_armature_deform_only": False,
    "armature_nodetype": 'NULL',
    "bake_anim": False,
    "bake_anim_use_all_bones": True,
    "bake_anim_use_nla_strips": True,
    "bake_anim_use_all_actions": True,
    "bake_anim_force_startend_keying": True,
    "bake_anim_step": 1.0,
    "bake_anim_simplify_factor": 1.0,
    "path_mode": 'AUTO',
    "embed_textures": False,
    "batch_mode": 'OFF',
    "use_batch_own_dir": True,
    "axis_forward": '-Z',
    "axis_up": 'Y',
}

# === Operator ===
class OBJECT_OT_export_fbx_individual(bpy.types.Operator):
    bl_idname = "object.export_fbx_individual"
    bl_label = "Export Selected Objects as FBX"
    bl_options = {'REGISTER', 'UNDO'}

    MAX_EXPORT = 10  # Maximum objects allowed

    def execute(self, context):
        scene = context.scene
        export_folder = bpy.path.abspath(scene.Sabrinas_export_folder)  # absolute path

        if not export_folder or not os.path.exists(export_folder):
            self.report({'ERROR'}, f"Invalid export folder: {export_folder}")
            return {'CANCELLED'}

        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}

        if len(selected_objects) > self.MAX_EXPORT:
            self.report({'ERROR'}, f"Cannot export more than {self.MAX_EXPORT} objects at once")
            return {'CANCELLED'}

        for obj in selected_objects:
            obj_name = bpy.path.clean_name(obj.name)
            export_path = os.path.join(export_folder, f"{obj_name}.fbx")

            # Deselect all and select the current object
            for o in context.view_layer.objects:
                o.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj

            try:
                bpy.ops.export_scene.fbx(filepath=export_path, **FBX_EXPORT_SETTINGS)
                self.report({'INFO'}, f"Exported {obj_name} to {export_folder}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to export {obj_name}: {e}")

        return {'FINISHED'}

# === Sidebar Panel ===
class VIEW3D_PT_export_fbx_panel(bpy.types.Panel):
    bl_label = "CE FBX SM Export"  # Panel name
    bl_idname = "VIEW3D_PT_export_fbx_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FBX SM Export"  # Tab name

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Show absolute path
        abs_path = bpy.path.abspath(scene.Sabrinas_export_folder)
        layout.prop(scene, "Sabrinas_export_folder", text="Export Folder")
        layout.label(text=f"Resolved Path: {abs_path}")
        layout.operator("object.export_fbx_individual", text="Export Selected Objects")

# === Registration ===
classes = [OBJECT_OT_export_fbx_individual, VIEW3D_PT_export_fbx_panel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Sabrinas_export_folder = bpy.props.StringProperty(
        name="Export Folder",
        subtype='DIR_PATH'
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.Sabrinas_export_folder

if __name__ == "__main__":
    register()

