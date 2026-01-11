# 3DS-UE5 Asset Integration Tool

A Python script designed for **Autodesk 3ds Max** to streamline the workflow of exporting 3D assets directly into an **Unreal Engine 5** project.

## Features

- **Batch Export**: Processes multiple selected objects simultaneously.
- **Automated Organization**: Creates a dedicated subfolder for each exported model within the target directory.
- **Texture Handling**: Automatically detects and copies all associated bitmaps (textures) to the model's folder.
- **Unreal-Ready FBX**: Configures FBX export settings (Z-up, centimeters, smoothing groups, tangents/binormals) specifically for Unreal Engine.
- **Workflow Memory**: Remembers the last used export path for faster iteration.

## Prerequisites

- **Autodesk 3ds Max** (tested on recent versions supporting `pymxs`).
- **Unreal Engine 5** project (or any target directory structure).

## Installation

1. Clone this repository or download the `Scripts/MaxExporter.py` file.
2. Place the script in a known location on your machine.
3. Open 3ds Max.
4. Go to **Scripting > Run Script...** and select `MaxExporter.py`.
   - *Optional*: You can drag and drop the script into the viewport or create a macro button for quick access.

## Usage

1. Open your scene in 3ds Max.
2. Select the objects you wish to export.
3. Run the script.
4. A dialog will prompt you to select your Unreal Project's **Content** folder (or a specific subfolder within it).
5. The script will:
   - Create a folder for each object (e.g., `Content/MyChair/`).
   - Export `MyChair.fbx` into that folder.
   - Copy any textures used by `MyChair` into the same folder.

## Script Reference

### `Scripts/MaxExporter.py`
The core script for the tool.
- **`get_last_path()` / `save_last_path()`**: Manages the persistence of the export directory using an `.ini` file.
- **`get_all_textures(material)`**: Recursively traverses 3ds Max material trees (Standard, Multi/Sub-Object, etc.) to find all linked `BitmapTexture` files.
- **`export_to_unreal()`**: The main function that orchestrates the user input, folder creation, file copying, and FBX export calls.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Copyright (c) 2026 ARGUS