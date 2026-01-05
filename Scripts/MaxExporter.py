from pymxs import runtime as rt
import os
import shutil
import configparser

# --- Configuration Management ---
CONFIG_FILE = os.path.join(rt.pathConfig.getDir(rt.name("userscripts")), "MaxToUnrealExporter.ini")

def get_last_path():
    """Reads the last used export path from the config file."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config.get('Settings', 'last_path', fallback=rt.getDir(rt.name("export")))
    return rt.getDir(rt.name("export"))

def save_last_path(path):
    """Saves the last used export path to the config file."""
    config = configparser.ConfigParser()
    config['Settings'] = {'last_path': path}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def get_all_textures(material):
    """
    Recursively finds all BitmapTexture files in a material tree.
    This handles standard materials, multi/sub-object materials, and nested maps.
    """
    texture_paths = set()

    def find_textures_recursive(mat):
        if not mat:
            return
        
        if rt.isKindOf(mat, rt.MultiMaterial):
            for i in range(mat.numsubs):
                sub_mat = mat.materialList[i]
                find_textures_recursive(sub_mat)
        else:
            for prop_name in rt.getPropNames(mat):
                try:
                    prop_value = getattr(mat, prop_name)
                    if rt.isKindOf(prop_value, rt.Texmap):
                        if rt.isKindOf(prop_value, rt.BitmapTexture):
                            if prop_value.filename and os.path.exists(prop_value.filename):
                                texture_paths.add(prop_value.filename)
                        else:
                            find_textures_recursive(prop_value)
                except Exception:
                    continue

    find_textures_recursive(material)
    return list(texture_paths)

def export_to_unreal():
    """
    Exports selected models to subfolders in an Unreal project, creating a
    folder for each model containing the FBX and its textures.
    Remembers the last used export location.
    """
    try:
        # --- 1. Get Base Destination Path from User ---
        last_path = get_last_path()
        base_export_path = rt.getSavePath(caption="Select Unreal Project's Content Folder", initialDir=last_path)
        
        if not base_export_path:
            print("Export cancelled by user.")
            return
            
        save_last_path(base_export_path)

        # --- 2. Get Selected Objects ---
        original_selection = list(rt.selection)
        if not original_selection:
            rt.messageBox("Please select one or more objects to export.")
            return

        print(f"Starting export for {len(original_selection)} objects to base path: {base_export_path}")

        # --- 3. Configure FBX Export Settings ---
        rt.FBXExporterSetParam("UpAxis", "Z")
        rt.FBXExporterSetParam("ScaleFactor", 1.0)
        rt.FBXExporterSetParam("ConvertUnit", "cm")
        rt.FBXExporterSetParam("SmoothingGroups", True)
        rt.FBXExporterSetParam("TangentsandBinormals", True)
        rt.FBXExporterSetParam("EmbedMedia", False)
        rt.FBXExporterSetParam("Animation", False)
        rt.FBXExporterSetParam("GenerateLog", False)

        exported_models = 0
        total_textures_copied = 0

        # --- 4. Process Each Selected Object ---
        for obj in original_selection:
            print(f"\nProcessing: {obj.name}")
            
            # --- Create a dedicated subfolder for the model ---
            model_export_path = os.path.join(base_export_path, obj.name)
            if not os.path.exists(model_export_path):
                os.makedirs(model_export_path)
            print(f"  Created subfolder: {model_export_path}")

            # --- Handle Textures ---
            if obj.material:
                textures = get_all_textures(obj.material)
                if textures:
                    print(f"  Found {len(textures)} textures for {obj.name}.")
                    for texture_path in textures:
                        try:
                            shutil.copy(texture_path, model_export_path)
                            print(f"    Copied texture: {os.path.basename(texture_path)}")
                            total_textures_copied += 1
                        except Exception as e:
                            print(f"    ERROR: Failed to copy texture {texture_path}. Reason: {e}")
                else:
                    print("  No textures found on material.")

            # --- Export FBX into its subfolder ---
            file_name = f"{obj.name}.fbx"
            export_path = os.path.join(model_export_path, file_name)
            
            rt.select(obj)
            
            print(f"  Exporting {obj.name} to {export_path}...")
            rt.exportFile(export_path, rt.name("noPrompt"), selected=True, using=rt.FBXEXP)
            exported_models += 1

        # --- 5. Restore Original Selection and Final Report ---
        rt.select(original_selection)
        
        summary_message = f"Export to Unreal Complete!\n\n"
        summary_message += f"Base Path: {base_export_path}\n"
        summary_message += f"Exported {exported_models} models into individual subfolders.\n"
        summary_message += f"Copied a total of {total_textures_copied} texture files."
        
        rt.messageBox(summary_message)
        print(f"\n{summary_message}")

    except Exception as e:
        error_message = f"An error occurred during export:\n\n{e}"
        print(f"FATAL ERROR: {e}")
        rt.messageBox(error_message, title="Export Script Error")
        if 'original_selection' in locals() and original_selection:
            rt.select(original_selection)

export_to_unreal()
