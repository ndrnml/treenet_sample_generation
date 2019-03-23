#!/usr/bin/env python3
# auxiliary functions for hdf5 operations

import h5py
from zipfile import ZipFile
from scipy import ndimage
from scipy.misc import toimage
from enum import Enum
import matplotlib.pyplot as plt
import math
import numpy as np

import utils

""" remove this line if no longer needed """
from fuel.datasets.hdf5 import H5PYDataset  # only needed for proof of concept

__author__ = "Andrin Jenal"
__copyright__ = "Copyright 2016, ETH Zurich"
__license__ = "GPL"  # Do you even know what a GPL license is?

FileType = Enum('file_type', 'HDF5 ZIP')


# Utils
def remove_file(file_path):
    utils.remove_file(file_path)
    print('file removed: ' + file_path + '\n')


def remove_files(file_list):
    for file in file_list:
        utils.remove_file(file)


def images_in_directory(path, image_format='.png'):
    return utils.get_files(path, image_format)


def files_in_directory(path, file_format):
    return utils.get_files(path, file_format)


# Files
def new_file(path_to_file, file_type):
    if file_type == FileType.HDF5:
        h5file = h5py.File(path_to_file + '.h5', 'w')
        return h5file

    elif file_type == FileType.ZIP:
        zip_file = ZipFile(path_to_file + '.zip', 'w')
        return zip_file

    else:
        print('file type: ' + file_type + ' not defined')


def save_to_hdf5(open_file, path, file_format, scipy_image_format):
    save_images_to_hdf5(open_file, path, scipy_format=scipy_image_format)


def save_to_zip(open_file, path, file_format):
    save_files_to_zip(open_file, path, file_format)


# ZIP Files
def save_files_to_zip(open_file, path, file_type, dir_name='samples'):
    file_list = files_in_directory(path, file_type)
    for image in file_list:
        open_file.write(image, dir_name + '/' + utils.get_filename_with_extension(image))

    # clean directory
    remove_files(file_list)


# HDF5 Files
def add_group(h5file, path):
    return h5file.create_group(utils.get_filename(path))


def save_images_to_hdf5(open_h5file, path, image_format='.png', scipy_format='L'):
    image_list = images_in_directory(path, image_format)

    for image in image_list:
        # 'L' (8-bit pixels, black and white)
        # 'P' (8-bit pixels, mapped to any other mode using a color palette)
        # 'RGB' (3x8-bit pixels, true color)
        # 'RGBA' (4x8-bit pixels, true color with transparency mask)
        # 'CMYK' (4x8-bit pixels, color separation)
        # 'YCbCr' (3x8-bit pixels, color video format)
        # 'I' (32-bit signed integer pixels)
        # 'F' (32-bit floating point pixels)
        img_data = ndimage.imread(image, mode=scipy_format)
        dataset = open_h5file.create_dataset(utils.get_filename(image), data=img_data, shape=img_data.shape)
        dataset.attrs['scipy_format'] = scipy_format

    # clean directory
    remove_files(image_list)


def load_image_batch(hdf5_file, dataset_batch_list):
    with h5py.File(hdf5_file, 'r') as _file:
        res = []
        for ds_name in dataset_batch_list:
            res.append(_file[ds_name].value)
        return np.array(res)


def next_batch(hdf5_file, image_list, batch_size):
    with h5py.File(hdf5_file, 'r') as _file:
        images = []
        for ds_name in image_list:
            images.append(_file[ds_name].value)
            if len(images) == batch_size:
                yield np.array(images)
                images = []


def load_dataset_list(hdf5_file):
    with h5py.File(hdf5_file, 'r') as _file:
        return [ds for ds in _file[_file.name]]


def preview_batch(image_batch, channels):
    if channels == 1:
        n, height, width = image_batch.shape
    else:
        n, height, width, _ = image_batch.shape

    W = int(width)
    H = int(height)
    N = math.ceil(np.sqrt(n))
    image_matrix = np.ones((N * H, N * H, channels))
    image_batch = np.reshape(image_batch, (n, height, width, channels))
    for i in range(0, N):
        for j in range(0, N):
            if i * N + j < n:
                image_matrix[i*H:(i+1)*H, j*W:(j+1)*W, :] = image_batch[i * N + j][0:H][0:W][:]

    return image_matrix


def shuffle(dataset_list):
    access_list = np.arange(len(dataset_list))
    np.random.shuffle(access_list)
    return dataset_list[access_list]


def glimpse(hdf5_file_name):
    batch_size = 64
    plt.ion()

    ds_list = np.array(load_dataset_list(hdf5_file_name))
    ds_list = shuffle(ds_list)

    fig, ax = plt.subplots()
    for imgs in next_batch(hdf5_file_name, ds_list, batch_size):
        if imgs.shape[-1] == 3:
            image_matrix = preview_batch(imgs, channels=3)
            plt.imshow(toimage(image_matrix))
        else:
            image_matrix = preview_batch(imgs, channels=1)
            image_matrix = np.reshape(image_matrix, image_matrix.shape[:-1])
            ax.matshow(image_matrix, cmap=plt.get_cmap('gray'))
        plt.draw()
        plt.pause(1)


def fuel_convert(hdf5_file_name):
    """
        proof of concept DRAW-jbornschein
        delete if no longer needed
    """
    fuel_file_name = 'fuel_' + utils.basename(hdf5_file_name)
    with h5py.File(hdf5_file_name, 'r') as _file:
        dataset = load_dataset_list(hdf5_file_name)
        fuel_dataset = []
        for img in dataset:
            _img = _file[img].value
            _true = _img < 255
            _false = _img == 255
            _img[_true] = 1
            _img[_false] = 0
            fuel_dataset.append(_img)
        fuel_dataset = np.array(fuel_dataset)
    with h5py.File(utils.create_filepath(utils.get_path(hdf5_file_name), fuel_file_name), 'w') as _file:
        batch_size = len(dataset)
        channels = 1
        image_size = 64
        image_features = _file.create_dataset('features', (batch_size, channels, image_size, image_size), dtype='uint8')
        image_features[...] = np.reshape(fuel_dataset, (batch_size, channels, image_size, image_size))
        image_features.dims[0].label = 'batch'
        image_features.dims[1].label = 'channel'
        image_features.dims[2].label = 'height'
        image_features.dims[3].label = 'width'

        train_proportion = int(0.8 * batch_size)
        test_proportion = int(0.1 * batch_size)

        split_dict = {
            'train': {'features': (0, train_proportion)},
            'test': {'features': (train_proportion, train_proportion + test_proportion)},
            'valid': {'features': ((train_proportion + test_proportion), batch_size)}
        }
        _file.attrs['split'] = H5PYDataset.create_split_array(split_dict)
        print('Successfully written:', _file.filename)


def test_fuel_convert(hdf5_file_name):
    batch_size = 49
    plt.ion()

    ds_list = load_dataset_list(hdf5_file_name)
    with h5py.File(hdf5_file_name) as _file:
        ds = _file[ds_list[0]].value

    ds = ds.reshape(ds.shape[0], ds.shape[2], ds.shape[3])
    for i in range(0, ds.shape[0], batch_size):
        plt.matshow(preview_batch(ds[i:i+batch_size]), fignum=0, cmap=plt.cm.gray)
        plt.draw()
        plt.pause(1)

def test_save_images():
    path = '/home/ajenal/Documents/masterthesis/project/source/scripts/blender/sapling3.0/3dsamples/'
    save_images_to_hdf5(None, path, scipy_format='RGB')

def test():
    #hdf5_file_name = '/home/ajenal/tree_all_28k_2k_1v_skel_64x64.h5'
    #hdf5_file_name = '/home/ajenal/Documents/masterthesis/project/tbone/fuel_tree_cedar_simple_5k_4views_skel_64x64.h5'
    #hdf5_file_name = '/home/ajenal/Documents/masterthesis/project/tbone/tree_cedar_simple_5k_4views_skel_64x64.h5'

    #glimpse(hdf5_file_name)
    #fuel_convert(hdf5_file_name)
    #test_fuel_convert(hdf5_file_name)
    test_save_images()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="file utils")
    parser.add_argument('-T', '--test', default=False, action='store_true', help='test file utils')
    parser.add_argument('-I', '--inspect', default=False, action='store_true', help='inspect hdf5 file')
    parser.add_argument('-F', '--file-path', help='path to hdf5 file')
    parser.add_argument('-C', '--convert', default=False, action='store_true', help='blubbi')
    args = parser.parse_args()

    if args.test:
        test()
    elif args.inspect and args.file_path:
        glimpse(args.file_path)
    elif args.convert and args.file_path:
        fuel_convert(args.file_path)
    else:
        parser.print_help()
