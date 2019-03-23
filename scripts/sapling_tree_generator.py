#!/usr/bin/env python3

# Generate and render silhouettes random trees
# Targeting blender 2.78 using the improved add_curve_sapling_3 add-on
# https://github.com/abpy/improved-sapling-tree-generator

import bpy # blender python module
import sys
import os
import argparse
import numpy as np
from math import radians

# ugly workaround to allow custom modules to be load by blender
dir_name = os.path.dirname(bpy.data.filepath)
if not dir_name in sys.path:
    sys.path.append(dir_name)
import utils
from treeconfigs import TreeConfig

__author__ = "Andrin Jenal"
__copyright__ = "Copyright 2016, ETH Zurich"
__license__ = "GPL"

# Parameters
BRANCH_LEVELS = 4
HEIGHT = 10
BRANCHES = 50

class TreeGenerator:
    def __init__(self, start_seed, pure_random, render_path, image_size, render_silhouette, views, export):
        # render specific
        self.render_engine = 'BLENDER_RENDER'  # BLENDER_RENDER, CYCLES
        self.export = export
        if self.export:
            self.file_extension = '.obj'
        else:
            self.file_extension = '.png'

        # random properties
        self.start_seed = start_seed
        self.pure_random = pure_random

        # set render image properties
        self.image_path = render_path
        self.image_width = image_size
        self.image_height = image_size
        self.render_silhouette = render_silhouette

        # colors
        self.white = (1, 1, 1)
        self.black = (0, 0, 0)
        self.blue = (0.7, 0.9, 1.0)
        self.brown = (0.7, 0.6, 0.4)
        self.green = (101.0 / 255.0, 143.0 / 255.0, 49.0 / 255.0)

        # materials
        if render_silhouette or self.export:
            self.tree_material = self.make_material('tree_mat', self.black, shadeless=True)
        else:
            self.tree_material = self.make_material('tree_mat', self.brown, shadeless=False)
            self.plane_material = self.make_material('plane_mat', self.green, shadeless=False)

        # prepare global scene
        self.scene = bpy.context.scene
        # tree object
        self.tree = None
        self.views = views

        # tree config
        self.tree_config = TreeConfig()
        # these parameters should be influenced by randmoness
        #self.tree_config.add_float_parameter('scaleV', 5, 5)
        #self.tree_config.add_float_list_parameter('splitAngleV', [-20, -100, 0, 0], [20, 100, 0, 0])
        #self.tree_config.add_float_list_parameter('rotateV', [-180, -180, 0, 0], [180, 180, 0, 0])
        #self.tree_config.add_float_list_parameter('lengthV', np.zeros(4), np.ones(4))
        #self.tree_config.add_float_list_parameter('downAngleV', -180 * np.ones(4), 180 * np.ones(4))
        #self.tree_config.add_float_list_parameter('curveV', -CURVATURE_VARIATION * np.ones(BRANCH_LEVELS), CURVATURE_VARIATION * np.ones(BRANCH_LEVELS))

        # these parameters are species relevant
        #tree_model['lengthV'] = self.tree_config.variation(tree_model['length'], tree_model['lengthV'], nth_sample)
        #tree_model['downAngleV'] = self.tree_config.variation(tree_model['downAngle'], tree_model['downAngleV'], nth_sample)
        #tree_model['curveV'] = self.tree_config.variation(tree_model['curve'], tree_model['curveV'], nth_sample)
        #self.tree_config.add_float_parameter('branchDist', 0.5, 4.0)
        #self.tree_config.add_float_parameter('ratio', 0.01, 0.05)
        #self.tree_config.add_float_parameter('scale0', 1.0, 6.0)
        #self.tree_config.add_float_parameter('scaleV0', 0.0, 1.0)
        #self.tree_config.add_float_parameter('ratioPower', 0.5, 2.0)
        #self.tree_config.add_float_parameter('minRadius', 0.0, 0.1)
        #self.tree_config.add_boolean_parameter('closeTip')
        #self.tree_config.add_float_list_parameter('taper', 0.9 * np.ones(4), np.ones(4))
        #self.tree_config.add_int_paramter('levels')
        #self.tree_config.add_float_parameter('baseSize', 0.0, 1.0)
        #self.tree_config.add_float_parameter('splitHeight', 0.0, 1.0)
        #self.tree_config.add_float_parameter('splitBias', -2.0, 2.0)
        #self.tree_config.add_float_parameter('splitByLen')
        #self.tree_config.add_int_list_parameter('branches', MIN_BRANCHES * np.ones(BRANCH_LEVELS), MAX_BRANCHES * np.ones(BRANCH_LEVELS))
        #self.tree_config.add_float_list_parameter('segSplits', np.zeros(BRANCH_LEVELS), [0.5, 1, 0, 0])
        #self.tree_config.add_float_list_parameter('splitAngle', [-5, 0, 0, 0], [20, 0, 0, 0])
        #self.tree_config.add_float_list_parameter('rotate', [-180, -180, 0, 0], [180, 180, 0, 0])
        #self.tree_config.add_float_list_parameter('attractOut', np.zeros(4), np.ones(4))
        #self.tree_config.add('rMode')
        #self.tree_config.add_float_parameter('taperCrown')
        #self.tree_config.add_float_list_parameter('length', [0.5, 0.1, 0.1, 0.1], [3.0, 1.0, 1.0, 1.0])
        #self.tree_config.add_float_list_parameter('downAngle', -180 * np.ones(4), 180 * np.ones(4))
        #self.tree_config.add_float_list_parameter('curve', -CURVATURE * np.ones(BRANCH_LEVELS), CURVATURE * np.ones(BRANCH_LEVELS))
        #self.tree_config.add_float_list_parameter('curveBack', -360 * np.ones(4), 360 * np.ones(4))
        #self.tree_config.add_float_list_parameter('attractUp', [-10, -90, 0, 0], [10, 90, 0, 0])

    def tree_model_defaults(self, tree_model):
        # sapling tree add-on specific fixed parameters
        tree_model['levels'] = 2
        tree_model['bevel'] = True
        tree_model['bevelRes'] = 4
        tree_model['resU'] = 4
        tree_model['handleType'] = '0'
        tree_model['curveRes'] = (8, 5, 3, 1)
        tree_model['showLeaves'] = False
        #tree_model['scale'] = HEIGHT

    def simple_random(self, tree_model):
        # add non variation parameters
        tree_model['branches'] = (0, 10, 0, 0)
        tree_model['segSplits'] = np.ones(BRANCH_LEVELS) * 0.1

        if tree_model['baseSplits'] > 0:
            self.tree_config.add_int_parameter('baseSplits', 1, 1)

    def random_variation(self, tree_model, nth_sample):
        """
        This function should be removed. Parameters should rather be registered as complexity parameters.
        """
        # parameters that depend on the loaded model presets
        # base splits
        if tree_model['baseSplits'] > 0:
            self.tree_config.add_int_parameter('baseSplits', 1, tree_model['baseSplits'] + 1)  # range[1, baseSplts + 1]
        # branch rings
        if tree_model['nrings'] > 0:
            self.tree_config.add_int_parameter('nrings', tree_model['nrings'] - 1,
                                               tree_model['nrings'] + 1)  # range[nrings - 1, nrings + 1]

        # add parameter variation which increases if the sample number increases
        tree_model['splitAngleV'] = self.tree_config.variation(tree_model['splitAngle'], tree_model['splitAngleV'], nth_sample)
        tree_model['rotateV'] = self.tree_config.variation(tree_model['rotate'], tree_model['rotateV'], nth_sample)

        # add non variation parameters
        branch_value = tree_model['branches']
        branch_variation = np.multiply(branch_value, 0.05)  # 5% variation
        tree_model['branches'] = tuple([np.asscalar(np.int32(b)) for b in np.add(branch_value, self.tree_config.variation(tree_model['branches'], branch_variation, nth_sample))])

        back_curvature_value = tree_model['curveBack']
        back_curvature_variation = np.multiply(back_curvature_value, 0.05)  # 5% variation
        tree_model['curveBack'] = tuple([np.asscalar(b) for b in np.add(back_curvature_value, self.tree_config.variation(back_curvature_value, np.ones(BRANCH_LEVELS) * back_curvature_variation, nth_sample))])

    def complexity_variation(self, tree_model, param, type_func, start_complexity, end_complexity, current_sample, total_samples):
        """
        Tree branch structure should vary in complexity. This is accomplished by varying certain parameters as the current
        tree sample number increases.
        """
        complexity_delta = current_sample / total_samples
        if type(tree_model[param]) is tuple:
            tree_model[param] = tuple([type_func(elem) for elem in (np.array(start_complexity) + complexity_delta * (np.array(end_complexity) - np.array(start_complexity)))])
        else:
            tree_model[param] = type_func(start_complexity + complexity_delta * (end_complexity - start_complexity))
        print(param, 'end complexity', end_complexity)
        print(param, 'complexity', tree_model[param])

    def clear_scene(self):
        # it is to say that blender operates in different scopes: global, scene, curves etc.
        # as objects get deleted in global, they seem to still reside in curves, meshes...
        # thus, we make sure everything gets deleted
        # NEITHER IS GUARANTEED THAT THIS IS THE CORRECT ORDER NOR WHETHER THIS IS THE RIGHT APPROACH
        # first unlink from scene
        for o in self.scene.objects:
            self.scene.objects.unlink(o)

        # remove globally
        for o in bpy.data.objects:
            o.select = True
        bpy.ops.object.delete(use_global=True)

        # remove from curves
        for c in bpy.data.curves:
            bpy.data.curves.remove(c, do_unlink=True)

    def rotate_object(self, obj, angle_degree, direction, point):
        from mathutils import Matrix
        R = Matrix.Rotation(radians(angle_degree), 4, direction)
        T = Matrix.Translation(point)
        M = T * R * T.inverted()
        obj.location = M * obj.location
        obj.rotation_euler.rotate(M)

    def make_material(self, name, color, shadeless=False):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = color
        if shadeless:
            mat.use_shadeless = True
        return mat

    def set_material(self, obj, mat):
        obj.data.materials.append(mat)

    def set_world_properties(self, color, env_light=True, env_light_color='PLAIN', energy=1.0):
        world = self.scene.world
        world.horizon_color = color
        if env_light:
            world.light_settings.use_environment_light = True
            world.light_settings.environment_color = env_light_color
            world.light_settings.environment_energy = energy

    def add_sapling_tree(self, tree_type, material):
        bpy.ops.curve.tree_add(**tree_type)
        # get the name of the curve (hopefully it is the most recent tree curve)
        tree_name = bpy.data.curves[-1].name
        tree_object = bpy.data.objects.get(tree_name)
        self.set_material(tree_object, material)
        return tree_object

    def add_ground_plane(self, material, rad=1000, loc=(0,0,0)):
        bpy.ops.mesh.primitive_plane_add(radius=rad, location=loc)
        plane_name = bpy.data.meshes[-1].name
        plane_object = bpy.data.objects.get(plane_name)
        self.set_material(plane_object, material)
        return plane_object

    def add_lamp(self, lamp_name='lamp', type='POINT', location=(0,0,50), rotation=(0,0,0)):
        lamp = bpy.data.lamps.new(lamp_name, type)
        lamp_object = bpy.data.objects.new(name=lamp.name, object_data=lamp)
        lamp_object.location.xyz = location
        lamp_object.rotation_euler.x = rotation[0]
        lamp_object.rotation_euler.y = rotation[1]
        lamp_object.rotation_euler.z = rotation[2]
        self.scene.objects.link(lamp_object)
        return lamp_object

    def add_camera(self, camera_name='camera', lens=35, sensor_fit='VERTICAL', sensor_h=32, sensor_w=32, rotation=(radians(90), 0, 0)):
        camera = bpy.data.cameras.new(camera_name)
        camera.lens = lens
        camera.sensor_fit = sensor_fit
        camera.sensor_height = sensor_h
        camera.sensor_width = sensor_w

        # rotate to horizontal (x-y) plane
        camera_object = bpy.data.objects.new(name=camera.name, object_data=camera)
        camera_object.rotation_euler.x = rotation[0]
        camera_object.rotation_euler.y = rotation[1]
        camera_object.rotation_euler.z = rotation[2]

        # link camera to scene
        self.scene.objects.link(camera_object)
        self.scene.camera = camera_object
        return camera_object

    # perspective from the ground or from vertical object center
    def camera_look_at_target(self, camera_name, target_obj, padding=0.8):
        target_obj.select = True
        # compute minimum distance of camera
        cam = bpy.data.cameras[camera_name]
        y_offset_height = -(cam.lens * target_obj.dimensions.z) / (padding * cam.sensor_height)
        y_offset_width = -(cam.lens * target_obj.dimensions.x) / (padding * cam.sensor_height)
        y_offset = min(y_offset_height, y_offset_width)
        cam_obj = bpy.data.objects[camera_name]
        cam_obj.location.y = y_offset
        cam_obj.location.z = 0.5
        cam_obj.rotation_euler.x += np.arctan(target_obj.dimensions.z * 0.5 / np.abs(y_offset))
        #cam_obj.location.z = target_obj.dimensions.z * 0.5 # vertical object center

    def create_new_scene(self, tree_config):
        # clear existing objects
        self.clear_scene()

        # add sapling tree
        self.tree = self.add_sapling_tree(tree_config, self.tree_material)

        # set uniform world color
        self.set_world_properties(self.white)

        """
            uncomment these two lines if you want a ground plane for preview reasons
        """
        #if not self.render_silhouette and not self.export:
        #    self.add_ground_plane(material=self.plane_material)

    def render_scene(self, seed):
        # add lamp
        self.add_lamp()

        # add and position camera
        camera = self.add_camera(lens=50)
        self.camera_look_at_target(camera.name, self.tree)

        # initialize random angles
        angles = np.random.choice(range(0, 360), self.views, replace=False)
        assert len(angles) == self.views

        # multi-view rendering
        for v in range(0, self.views):

            # rotate camera around z-axis for 360 / views degree
            origin = (0, 0, 0)
            self.rotate_object(camera, angles[v], 'Z', origin)

            # render and save image
            if self.image_path:
                render = self.scene.render
                render.engine = self.render_engine
                render.use_file_extension = True
                render.filepath = self.image_path + '_' + str(seed) + '_' + str(angles[v]) + self.file_extension
                render.resolution_x = self.image_width
                render.resolution_y = self.image_height
                render.resolution_percentage = 100.0
                bpy.ops.render.render(write_still=True)

    def export_scene(self, seed=0):
        filepath = self.image_path + '_' + str(seed) + self.file_extension
        bpy.ops.export_scene.obj(filepath=filepath, axis_forward='-Z', axis_up='Y', use_triangles=True, use_materials=False)
        return filepath

    def generate(self, model, number_samples, total_samples_species):
        # read tree model properties
        tree_model = utils.read_tree_model(model)

        # default tree model parameters
        self.tree_model_defaults(tree_model)

        # simple random creation, few branches, low variation
        #self.simple_random(tree_model)

        # for more random variation enable uncomment the following line - the variation increases as the sample number increases
        self.random_variation(tree_model, self.start_seed + number_samples)

        # store complexity parameters once per model
        branches_end_complexity = tree_model['branches']
        splits_end_complexity = tree_model['segSplits']
        radius_variance_end_complexity = tree_model['scale0'] * 0.5
        radius_start_complexity = tree_model['scale0']
        radius_end_complexity = tree_model['scale0'] * 1.3

        # generate as many samples as specified
        start_sample = self.start_seed
        for s in range(start_sample, start_sample + number_samples):
            # jitter parameters to enforce larger variance
            if self.pure_random:
                self.tree_config.jitter(tree_model)

            # complexity variation
            if self.pure_random:
                self.complexity_variation(tree_model, param='branches', type_func=int, start_complexity=(1, 3, 1, 1), end_complexity=branches_end_complexity, current_sample=s, total_samples=total_samples_species)
                self.complexity_variation(tree_model, param='segSplits', type_func=float, start_complexity=(0.0, 0.0, 0.0, 0.0), end_complexity=splits_end_complexity, current_sample=s, total_samples=total_samples_species)
                self.complexity_variation(tree_model, param='scale0', type_func=float, start_complexity=radius_start_complexity, end_complexity=radius_end_complexity, current_sample=s, total_samples=total_samples_species)
                self.complexity_variation(tree_model, param='scaleV0', type_func=float, start_complexity=0, end_complexity=radius_variance_end_complexity, current_sample=s, total_samples=total_samples_species)

            # render tree bone structure only
            """ this block is intentionally inside the loop, as we would like to overwrite any previous changes to the
            tree model """
            if self.render_silhouette:
                skeleton_radius_damper = 0.005
                tree_model['closeTip'] = False
                tree_model['minRadius'] = skeleton_radius_damper * tree_model['scale']  # skeleton radius should depend on tree size
                tree_model['scale0'] = 0.0

            """ be aware that s is always the same even for different runs which means the seed is fixed and thus the
                trees look exactly the same """
            tree_model['seed'] = s

            # create a new scene according to configuration
            self.create_new_scene(tree_model)

            if self.export:
                # export tree model
                self.export_scene(seed=s)
            else:
                # render a tree based on the tree model
                self.render_scene(seed=s)


def main():
    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if '--' not in argv:
        argv = []  # as if no args are passed
        print('For help run:\n\tpython ' + os.path.basename(__file__) + ' -- -h\n')
    else:
        argv = argv[argv.index('--') + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
            'Run blender in background mode with this script:\n'
            '\tblender --background --python ' + os.path.basename(__file__) + ' -- [options]'
            )

    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument('render_path', help='render image to a specific path')
    parser.add_argument('model', help='tree models')
    parser.add_argument('--total-samples', default=1000, type=int)
    parser.add_argument('-n', '--number-samples', type=int, default=1, help='number of samples that should be created')
    parser.add_argument('-f', '--filename', help='prefix name for the output files')
    parser.add_argument('-o', '--override', help='override existing image files', action='store_true')
    parser.add_argument('-size', '--image-size', type=int, default=64, help='output image size')
    parser.add_argument('-seed', '--start-seed', type=int, default=0, help='start number for the seed')
    parser.add_argument('-views', '--number-views', type=int, default=1, help='define number of views from which the tree should be rendered')
    parser.add_argument('-S', '--render-silhouette', help='render silhouette if enabled', action='store_true')
    parser.add_argument('-R', '--random', help='enable pure randomness', action='store_true')
    parser.add_argument('-E', '--export', help='export tree model as .obj file', action='store_true')

    args = parser.parse_args(argv)

    # check tree model
    if not utils.valid_file(args.model, parser.prog, message='%s: error: no valid tree model passed: %s'):
        return

    # set and check filename
    filename = utils.get_filename(args.model)
    if args.filename:
        filename = args.filename + '_' + filename

    # check file not already exists
    if utils.file_exists(args.render_path, filename, parser.prog) and not args.override:
        print('set the override flag -o if you want to proceed anyways')
        return

    tree_generator = TreeGenerator(args.start_seed, args.random, os.path.join(args.render_path, filename), args.image_size, args.render_silhouette, args.number_views, args.export)
    tree_generator.generate(args.model, args.number_samples, args.total_samples)

if __name__ == '__main__':
    main()
