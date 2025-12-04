bl_info = {
    "name": "Sabrina's LOD Simplifier",
    "author": "ChatGPT (GPT-5) & Sabrina",
    "version": (2, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Sabrina's LOD Simplifier",
    "description": (
        "Generate decimated LOD meshes (1–10 levels) with slider-controlled ratios. "
        "All LODs are independent and grouped under an Export_LODs collection."
    ),
    "category": "Object",
}

import bpy

# ------------------------------------------------------------------------
# Operator
# ------------------------------------------------------------------------
class OBJECT_OT_generate_lods(bpy.types.Operator):
    """Generate multiple LOD levels with slider-controlled decimation ratios"""
    bl_idname = "object.sabrinas_generate_lods"
    bl_label = "Generate LODs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        lod_count = scene.sabrinas_lod_slider_count
        prefix = scene.sabrinas_lod_prefix.strip()

        if not prefix:
            self.report({'ERROR'}, "Prefix is required! Please type a prefix.")
            return {'CANCELLED'}

        ratios = [getattr(scene, f"sabrinas_lod_ratio_{i}") for i in range(1, lod_count + 1)]
        selected_objs = [o for o in context.selected_objects if o.type == 'MESH']

        if not selected_objs:
            self.report({'WARNING'}, "No mesh objects selected.")
            return {'CANCELLED'}

        # Collection for LODs
        lod_collection_name = "Export_LODs"
        lod_collection = bpy.data.collections.get(lod_collection_name)
        if not lod_collection:
            lod_collection = bpy.data.collections.new(lod_collection_name)
            context.scene.collection.children.link(lod_collection)

        for obj in selected_objs:
            # LOD0 independent copy
            lod0 = obj.copy()
            lod0.data = obj.data.copy()
            lod0_name = f"{prefix}{obj.name}_LOD0"
            lod0.name = lod0_name
            lod_collection.objects.link(lod0)

            # LOD1 → LODn
            for i, ratio in enumerate(ratios, start=1):
                lod_obj = lod0.copy()
                lod_obj.data = lod0.data.copy()
                lod_name = f"{prefix}{obj.name}_LOD{i}"
                lod_obj.name = lod_name
                lod_collection.objects.link(lod_obj)

                dec = lod_obj.modifiers.new(name=f"Decimate_LOD{i}", type='DECIMATE')
                dec.ratio = ratio
                bpy.context.view_layer.objects.active = lod_obj
                bpy.ops.object.modifier_apply(modifier=dec.name)

            # Optionally hide original mesh
            obj.hide_set(True)

        self.report({'INFO'}, f"Generated {lod_count} LOD(s) under Export_LODs collection.")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# UI Panel
# ------------------------------------------------------------------------
class OBJECT_PT_sabrinas_lod_panel(bpy.types.Panel):
    """UI Panel for sabrina's LOD Simplifier"""
    bl_label = "sabrina's LOD Simplifier"
    bl_idname = "OBJECT_PT_sabrinas_lod_simplifier"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "sabrina's LOD"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Generate LODs for selected meshes:")
        layout.prop(scene, "sabrinas_lod_slider_count")

        box = layout.box()
        box.label(text="Set Decimation Ratios:")
        for i in range(1, scene.sabrinas_lod_slider_count + 1):
            box.prop(scene, f"sabrinas_lod_ratio_{i}", text=f"LOD{i} Ratio")

        layout.prop(scene, "sabrinas_lod_prefix", text="Prefix")

        layout.operator("object.sabrinas_generate_lods", text="Generate LODs", icon="MOD_DECIM")

# ------------------------------------------------------------------------
# Property update
# ------------------------------------------------------------------------
def update_lod_count(self, context):
    """Ensure unused ratios reset to default when decreasing LOD count."""
    count = context.scene.sabrinas_lod_slider_count
    for i in range(1, 11):
        if i > count:
            setattr(context.scene, f"sabrinas_lod_ratio_{i}", 0.5)

# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------
classes = (
    OBJECT_OT_generate_lods,
    OBJECT_PT_sabrinas_lod_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sabrinas_lod_slider_count = bpy.props.IntProperty(
        name="LOD Levels",
        description="Number of LOD levels (1–10)",
        default=3,
        min=1,
        max=10,
        update=update_lod_count,
    )
    bpy.types.Scene.sabrinas_lod_prefix = bpy.props.StringProperty(
        name="Prefix",
        description="Required prefix to prepend to all generated LOD objects",
        default="",
    )
    # Explicitly register all LOD ratio properties
    for i in range(1, 11):
        default_ratio = 0.5 if i == 1 else max(0.1, 1.0 - i * 0.15)
        setattr(
            bpy.types.Scene,
            f"sabrinas_lod_ratio_{i}",
            bpy.props.FloatProperty(
                name=f"LOD{i} Ratio",
                description=f"Decimation ratio for LOD{i} (0–1, smaller = more reduction)",
                default=default_ratio,
                min=0.05,
                max=1.0,
            )
        )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.sabrinas_lod_slider_count
    del bpy.types.Scene.sabrinas_lod_prefix
    for i in range(1, 11):
        delattr(bpy.types.Scene, f"sabrinas_lod_ratio_{i}")

if __name__ == "__main__":
    register()

