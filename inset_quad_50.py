import bpy
import bmesh


class MESH_OT_inset_quad_half(bpy.types.Operator):
    """Create an inset whose corners are halfway toward the face center."""

    bl_idname = "mesh.inset_quad_half"
    bl_label = "Inset Quad 50%"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = context.objects_in_mode
        if context.mode != 'EDIT_MESH' or len(objects) != 1:
            self.report({'WARNING'}, "Enter Edit Mode on one mesh object.")
            return {'CANCELLED'}

        mesh = objects[0].data
        bm = bmesh.from_edit_mesh(mesh)
        selected = [face for face in bm.faces if face.select and not face.hide]
        if len(selected) != 1 or len(selected[0].verts) != 4:
            self.report({'WARNING'}, "Select exactly one quad in Face Select mode.")
            return {'CANCELLED'}

        face = selected[0]
        corners = [vert.co.copy() for vert in face.verts]
        center = face.calc_center_median()
        if face.calc_area() <= 0 or len({tuple(co) for co in corners}) != 4:
            self.report({'WARNING'}, "Select a quad with four distinct corners and nonzero area.")
            return {'CANCELLED'}

        # Use Blender's inset topology and preserve the original face data.
        bmesh.ops.inset_individual(bm, faces=[face], thickness=0.0)
        for vert in face.verts:
            corner = min(corners, key=lambda co: (vert.co - co).length_squared)
            vert.co = corner.lerp(center, 0.5)

        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode = (False, False, True)
        face.select_set(True)
        bm.faces.active = face
        bm.select_history.clear()
        bm.select_history.add(face)
        bm.normal_update()
        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}


def run():
    # Allow rerunning this text with Alt+P without duplicate registration.
    previous = bpy.types.Operator.bl_rna_get_subclass_py(MESH_OT_inset_quad_half.__name__)
    if previous is not None:
        bpy.utils.unregister_class(previous)
    bpy.utils.register_class(MESH_OT_inset_quad_half)
    bpy.ops.mesh.inset_quad_half()


if __name__ == "__main__":
    run()
