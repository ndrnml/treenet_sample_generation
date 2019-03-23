# The TreeNet Database of Tree Skeletons and Silhouettes
Andrin Jenal, ETH Zurich

The TreeNet database is a collection of artificially created tree silhouettes using Blender and the sapling add-on.
It is useful for people who are interestd in learning techniques and pattern recognition on tree skeleton data.

The tree samples are available in two different formats: **hdf5** and **png**.
Default dataset: *datasets_hdf5/tree_skel_all_15k_250_4v_64x64.h5*

There are other formats and other datasets available.
The raw png files will be zipped.
Additionally, there is a dataset with larger images for higher resolution training available.

### About The Dataset
The main dataset consists of 15'000 binarized 64x64 black and white images of tree silhouettes.
The pixel value range is between 0 and 255.
All samples are generated in a complete random fashion.
Tree characteristic parameters are changed randomly.
There are 15 tree species that serve as presets created manually by a human.
An increasing sample number in the database means also a more complex tree.
This means that the tree skeletons are added linearly increasing complexity.
E.g. more second level branches, or trunk splits, more curved branches etc.
Internally Blender creates a 3D model of a tree in a procedural fashion and renders it from different angles.
Then it captures the tree silhouette from these specific angles from where the median axis along the branches are computed.
This results skeleton stored in the database.

### How To Read The Numbers
Example name of dataset: *tree_skel_all_15k_250_4v_64x64.h5*
*all* means it contains all tree species
*15k* is the total number of samples
*250* signifies the number of diferent 3D trees created
*4v* states the number of random captures of the same tree while the camera moves aroun the tree
*64x64* is the image size

## More About he Presets
The presets are created using a photograph of a real tree and making the 3D tree model look identical to the tree on the photograph.
The following tree species are used as model:
* Acacia
* Beech
* Callistemon
* Cedar
* Chestnut
* Elm
* Japanese Maple
* Kauri
* Larch
* Linden
* Pine
* Quaking Aspen
* Small Maple
* Teak
* White Birch

