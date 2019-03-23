#!/usr/bin/env python3

import numpy as np
from collections import OrderedDict


class IntParameter:
    
    def __init__(self, min_max):
        self.min_val, self.max_val = min_max

    def get_random(self):
        if self.min_val == self.max_val:
            return self.min_val
        else:
            return np.random.randint(self.min_val, self.max_val)

    def get_jitter(self):
        return self.get_random()


class IntListParameter(IntParameter):

    def __init__(self, int_params):
        self.int_params = int_params

    def get_random(self):
        res = list()
        for i in self.int_params:
            res.append(i.get_random())
        return tuple(res)

    def get_jitter(self):
        res = list()
        for k,i in enumerate(self.int_params):
            res.append(i.get_jitter())
        return tuple(res)


class FloatParameter():

    def __init__(self, min_max):
        self.min_val, self.max_val = min_max

    def get_random(self):
        return self.min_val + (self.max_val - self.min_val) * np.random.random()

    def get_jitter(self):
        if self.min_val == 0 and self.max_val == 0:
            return 0.0

        while True:
            res = np.random.uniform(self.min_val, self.max_val)
            if self.min_val <= res <= self.max_val:
                return res


class FloatListParameter(FloatParameter):
    
    def __init__(self, float_params):
        self.float_params = float_params

    def get_random(self):
        res = list()
        for f in self.float_params:
            res.append(f.get_random())
        return tuple(res)

    def get_jitter(self):
        res = list()
        for k, f in enumerate(self.float_params):
            res.append(f.get_jitter())
        return tuple(res)


class TreeConfig:
    
    def __init__(self):
        self.tree_parameters = OrderedDict()  # ordered dict ensures random jitter is applied in the same order
        np.random.seed(0)

    def add_int_parameter(self, name, min_val, max_val):
        self.tree_parameters[name] = IntParameter((int(min_val), int(max_val)))

    def add_float_parameter(self, name, min_val, max_val):
        self.tree_parameters[name] = FloatParameter((min_val, max_val))

    def add_int_list_parameter(self, name, min_vec, max_vec):
        min_vec = [int(v) for v in min_vec]
        max_vec = [int(v) for v in max_vec]
        zip_vec = zip(min_vec, max_vec)
        int_params = [IntParameter(i) for i in zip_vec]
        self.tree_parameters[name] = IntListParameter(int_params)

    def add_float_list_parameter(self, name, min_vec, max_vec):
        zip_vec = zip(min_vec, max_vec)
        float_params = [FloatParameter(f) for f in zip_vec]
        self.tree_parameters[name] = FloatListParameter(float_params)
    
    def jitter(self, tree_model):
        for param in self.tree_parameters:
            tree_model[param] = self.tree_parameters[param].get_jitter()
    
    def shuffle(self, tree_model):
        for param in self.tree_parameters:
            tree_model[param] = self.tree_parameters[param].get_random()

    @staticmethod
    def variation(param_default, param_variation, nth_sample):
        """
        This function doesn't really make sense. Nor does the moment when it is used.
        """
        # increase variation every 100th sample by 1
        increase_step = 0.01
        # variation / value ratio
        with np.errstate(divide='ignore', invalid='ignore'):
            var_val_ratio = np.nan_to_num(np.abs(np.divide(param_variation, param_default)))
        # return linearly increased variation
        return param_variation + np.sign(param_variation) * var_val_ratio * increase_step * nth_sample


def test():
    tree_model = {}
    param_name = 'scale'
    param_var_name = 'scaleV'
    tree_model[param_name] = 20
    tree_model[param_var_name] = -5

    param_list_name = 'splitAngle'
    param_list_var_name = 'splitAngleV'
    tree_model[param_list_name] = [20, 100, 0, 0]
    tree_model[param_list_var_name] = [2, 10, 0, 0]

    for i in range(0, 10000):
        if i % 1000 == 0:
            print('step:', i)
            print('param value:', tree_model[param_name])
            print('param variation:', tree_model[param_var_name])
            print('random variation:', TreeConfig.variation(tree_model[param_name], tree_model[param_var_name], i))

            print('param value:', tree_model[param_list_name])
            print('param variation:', tree_model[param_list_var_name])
            print('random variation:', TreeConfig.variation(tree_model[param_list_name], tree_model[param_list_var_name], i))


if __name__ == '__main__':
    test()
