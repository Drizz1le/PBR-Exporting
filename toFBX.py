import bpy
import sys
import os

# List of specific objects to delete
objects_to_delete = [
    "body_A_1_2", "body_C", "body_D"
]

# List of animations to delete
animations_to_delete = [
    "tx_sleep", "tx_wakeup", "tx_wink"
]

# Directory to export FBX files
export_directory = "C:\\Users\\Drizzle\\Desktop\\PBR Animations\\pkmn-fbx"

def delete_all_objects():
    # Select and delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def delete_specific_objects(objects_to_delete):
    # Select and delete specific objects by name
    for obj_name in objects_to_delete:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None  # Clear the active object
        for obj in bpy.data.objects:
            if obj_name in obj.name:
                obj.select_set(True)
        bpy.ops.object.delete()

def delete_specific_animations(animations_to_delete):
    # Delete specific animations by name
    for action_name in animations_to_delete:
        action = bpy.data.actions.get(action_name)
        if action:
            bpy.data.actions.remove(action)

def delete_all_animations():
    # Delete all actions (animations)
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
    # Clear animation data from objects
    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()

def find_last_movement_frame(action):
    last_movement_frame = float('inf')
    bone_with_earliest_last_movement = None

    # Get the active object (armature)
    armature = bpy.context.object
    if not armature or armature.type != 'ARMATURE':
        print("No armature found or selected object is not an armature.")
        return last_movement_frame, bone_with_earliest_last_movement
    
    # Iterate through all bones in the armature
    for bone in armature.pose.bones:
        for fcurve in action.fcurves:
            if fcurve.data_path == f'pose.bones["{bone.name}"].location':
                keyframes = sorted(kp.co[0] for kp in fcurve.keyframe_points)
                if keyframes:
                    bone_last_frame = keyframes[-1]
                    if bone_last_frame < last_movement_frame:
                        last_movement_frame = bone_last_frame
                        bone_with_earliest_last_movement = bone.name
    
    return last_movement_frame, bone_with_earliest_last_movement

def trim_animation_to_last_movement():
    for action in bpy.data.actions:
        last_frame, bone_name = find_last_movement_frame(action)
        if last_frame != float('inf'):
            # Calculate frames to trim off
            frames_to_trim = action.frame_range[1] - last_frame
            print(f"Trimmed {frames_to_trim} frames from action '{action.name}' based on bone '{bone_name}'")
            
            # Remove keyframes beyond last_frame
            for fcurve in action.fcurves:
                for keyframe in reversed(fcurve.keyframe_points):
                    if keyframe.co[0] > last_frame:
                        fcurve.keyframe_points.remove(keyframe)

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    folder_number = folder_name.split("_")[-1]

    # Delete all objects
    delete_all_objects()
    
    # Delete specific objects by name
    delete_specific_objects(objects_to_delete)
    
    # Delete all animations
    delete_all_animations()

    # Import model
    import_path = os.path.join(folder_path, f"pkx_{folder_number} 0000.sdr")
    bpy.ops.pbr.pbrimport(filepath=import_path)
    
    # Delete specific animations
    delete_specific_animations(animations_to_delete)
    
    # Trim animations
    trim_animation_to_last_movement()
    
    # Export model
    export_path = os.path.join(export_directory, f"{folder_number}.fbx")
    bpy.ops.export_scene.fbx(filepath=export_path)
    
    print(f"Model exported to {export_path}")

if __name__ == "__main__":
    folder_path = sys.argv[-1]
    process_folder(folder_path)
