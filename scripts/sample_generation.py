#!/usr/bin/env python3

import os
import argparse
from subprocess import Popen, DEVNULL
from time import time, sleep
import numpy as np

import file_utils

__author__ = "Andrin Jenal"
__copyright__ = "Copyright 2016, ETH Zurich"
__license__ = "GPL"
__version__ = "0.1"

JOB_CHUNK_SIZE = 500  # number of samples a single process will generate

job_times = []


def human_readable_time(seconds):
    if seconds <= 0:
        seconds = 0
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%dh %2dm %2ds" % (h, m, s)


def run_subprocess(args):
    start_time = time()
    proc = Popen(args, stdout=DEVNULL)  # pipe standard output to DEVNULL (discard standard output)
    out = proc.communicate()[0]  # for now keep the process in foreground
    end_time = time()
    elapsed_time = '%.3f' % (end_time - start_time)
    job_times.append(end_time - start_time)
    print('Done: ' + str(args), flush=True)
    print('Elapsed time: ' + elapsed_time + ' seconds\n', flush=True)


def job_arguments_chunk(pars_args, total_samples, chunk_size, seed, export):
    args = list(pars_args)
    args.append('--total-samples')
    args.append(str(total_samples))  # nifty way to tell total number of samples for species
    args.append('-n')
    args.append(str(chunk_size))
    args.append('-seed')
    args.append(str(seed))
    args.append('-S')  # enable silhouette
    args.append('-R')  # enable randomness
    if export:
        args.append('-E')  # export as .OBJ file
    return args


def job_arguments_model(script_args, model, image_size, number_views):
    model_args = list(script_args)
    model_args.append(model)
    model_args.append('-o')
    model_args.append('-size')
    model_args.append(str(image_size))
    model_args.append('-views')
    model_args.append(str(number_views))
    return model_args


def job_arguments_default(output_path):
    script_args = list()
    script_args.append('/home/ajenal/Apps/blender2.78/blender')
    script_args.append('--background')
    script_args.append('--python')
    script_args.append('sapling_tree_generator.py')
    script_args.append('--')
    script_args.append(output_path)
    return script_args


def save_to_file(open_file, path, file_format, scipy_image_format):
    # save generated images
    file_utils.save_to_hdf5(open_file, path, file_format, scipy_image_format)


def save_to_zip(open_file, path, file_format):
    # save generated images
    file_utils.save_to_zip(open_file, path, file_format)


def create_job_list(script_args, models, num_samples, image_size, num_views, chunk_size, export):
    job_list = []

    for model in models:
        model_args = job_arguments_model(script_args, model, image_size, num_views)

        chunks = int(num_samples / chunk_size)

        # for each junk create job arguments
        for n in range(chunks):
            job_list.append(job_arguments_chunk(model_args, num_samples, chunk_size, (n * chunk_size), export))

        # process remaining renders
        if (num_samples - chunks * chunk_size) > 0:
            job_list.append(job_arguments_chunk(model_args, num_samples, (num_samples - chunks * chunk_size), (chunks * chunk_size), export))

    return job_list


def run_sequential_code(output_path, file_name, job_list, export, file_type=file_utils.FileType.ZIP, image_format='L'):
    with file_utils.new_file(os.path.abspath(os.path.join(output_path, file_name)), file_type=file_type) as open_file:
        file_path_name = str(open_file.filename)

        for job in job_list:
            # start blender script
            run_subprocess(job)

            if file_type == file_utils.FileType.ZIP:
                if export:
                    file_format = '.obj'
                else:
                    file_format = '.png'
                save_to_zip(open_file, output_path, file_format)
            else:
                # save generated images as hdf5
                save_to_file(open_file, output_path, '.hd5', scipy_image_format=image_format)

            print('estimated remaining time:', human_readable_time((np.mean(job_times) * len(job_list)) - np.sum(job_times)), '\n', flush=True)

    return file_path_name


def main():

    usage_text = (
            'This script is an auxiliary script for fast and large tree sample generation:'
            '  python' + __file__ + ' [options]'
            )

    parser = argparse.ArgumentParser(description=usage_text)
    parser.add_argument('output_path', help='save generated samples into a specific location')
    parser.add_argument('number_samples', type=int, help='number of samples that should be created')
    parser.add_argument('models_path', help='tree template model')
    parser.add_argument('-S', '--image-size', type=int, default=64, help='optionally pass image size')
    parser.add_argument('-V', '--number-views', type=int, default=1, help='define number of views from which the tree should be rendered')
    parser.add_argument('-H', '--hdf5', default=False, action='store_true', help='set this flag to enforce hdf5 storage')
    parser.add_argument('-F', '--filename', default='samples', help='samples file name')
    parser.add_argument('-E', '--export', default=False, action='store_true', help='export file as .obj file')

    args = parser.parse_args()

    print('start sample generation script v' + __version__ + '\n', flush=True)

    # accept model files or model directories
    if os.path.isdir(args.models_path):
        models = [os.path.abspath(os.path.join(args.models_path, f)) for f in os.listdir(args.models_path) if
                  os.path.isfile(os.path.join(args.models_path, f))]
    elif os.path.isfile(args.models_path):
        models = [os.path.abspath(args.models_path)]
    else:
        print('file not exists:', args.models_path)
        return

    # choose file type
    file_type = file_utils.FileType.ZIP
    if args.hdf5:
        file_type = file_utils.FileType.HDF5

    # enforce correct path formatting
    output_path = os.path.join(args.output_path, '')

    # create output path if not exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print('created directory:', output_path, '\n')

    # rendered images will be written to output path
    script_args = job_arguments_default(output_path)
    # create job list with all required script arguments
    job_list = create_job_list(script_args, models, args.number_samples, args.image_size, args.number_views, JOB_CHUNK_SIZE, args.export)

    file_name = run_sequential_code(output_path, args.filename, job_list, args.export, file_type, image_format='L')

    print('done with sample generation, saved to:', file_name)

if __name__ == '__main__':
    start = time()
    main()
    end = time()
    elapsed = (end - start)
    print('Total time: ' + human_readable_time(elapsed) + '\n')
