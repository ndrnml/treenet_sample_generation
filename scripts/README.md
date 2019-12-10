# Sample Tree Generation Script for Blender

This is a simple tree silhouette generation script that uses Blender's python *bpy* bindings.
The script uses an improved version of the [Sapling addon](https://github.com/abpy/improved-sapling-tree-generator).
The script prerequisites must be installed manually.
Tested with Blender 2.78

## Requirements
Install Python 3.4 or later
Install Blender 2.78 or later
Install h5py dependencies (libhdf5-dev) and h5py
Install improved sapling addon (https://github.com/abpy/improved-sapling-tree-generator)

*Note: The provided sapling addon in Blender was adapted for the scripts to work properly.
Change the file: .../blender-2.78/2.78/scripts/addons/add_curve_sapling/utils.py accordingly
At line number 1424 starting with bend = ... was commented out*

## Usage

### 1. Individual tree generation
Call the tree generation script directly.
This python script is executed within a Blender session.

**Run:**
```bash
    $ blender2.78 --background --python sapling_tree_generator.py -- -h
```
Example:
```bash
    $ blender2.78 --background --python sapling_tree_generator.py -- tmp/ presets/tree.py -o -n 5 -size 128
```
**Note the double dash -- between the script an its arguments.**

### 2. Automated tree generation
This auxiliary script is intended to generate large image databases.
It runs Blender in the background and depending on the number of samples and your machine it will take some time.

**Run:**
Get help text:
```bash
    $ python3 sample_generation.py -h
```

For example, the command below creates 5000 tree skeletons and saves it to "name_of_output.h5" in the "samples/" directory.
```bash
    $ python3 sample_generation.py samples/ 5000 presets/tree.py -H -F "name_of_output"
```

*or*

To to create a zip file with 5000 samples per template run the command below.
Each tree model is captured at 4 different angles and the outupt size is 64 by 64 pixels run the command below.
This will create 5000 samples for each template in the directory "presets/".

```bash
    $ python3 sample_generation.py samples/ 5000 presets/ -V 4 -S 64
```

Create the **default dataset**:
```bash
    $ python3 sample_generation.py samples/ 250 presets/ -V 4 -H -S 64 -F tree_skel_all_15k_250_4v_64x64
```
