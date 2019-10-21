import os
import numpy as np
import matplotlib.pyplot as plt

# bangpy
from . import paths
from . import load_save

# TODO:
#   - plotly slider


class BangSim:
    def __init__(self, model, basename=None, runs_path=None, config='default',
                 xmax=1e12, dim=1, output_dir='output', verbose=True,
                 load_all=True):
        self.verbose = verbose
        self.runs_path = runs_path
        self.path = paths.model_path(model=model, runs_path=runs_path)
        self.output_path = os.path.join(self.path, output_dir)

        self.model = model
        self.basename = basename
        self.dim = dim
        self.xmax = xmax

        self.config = None
        self.dat = None
        self.profiles = {}

        self.load_config(config=config)
        self.chk_idxs = load_save.find_chk(path=self.output_path)

        if load_all:
            self.load_dat()

    def printv(self, string):
        if self.verbose:
            print(string)

    def load_config(self, config='default'):
        """Load config file
        """
        filepath = paths.config_filepath(name=config)
        config = load_save.load_config(filepath, verbose=self.verbose)
        self.config = config

    def load_dat(self):
        """Load .dat file
        """
        self.dat = load_save.load_dat(self.basename, model=self.model,
                                      cols_dict=self.config['dat_columns'])

    def load_all_profiles(self, reload=False, save=True):
        """Load profiles for all available checkpoints

        parameters
        ----------
        reload : bool
        save : bool
        """
        # TODO: parallelize (refer to burst_pipeline in pyburst)
        for chk_i in self.chk_idxs:
            self.load_profile(chk_i, reload=reload, save=save)

    def load_profile(self, chk_i, reload=False, save=True):
        """Load checkpoint data file

        parameters
        ----------
        chk_i : int
            checkpoint ID to load
        reload : bool
        save : bool
        """
        self.profiles[chk_i] = load_save.extract_profile(
                                    self.basename, chk_i=chk_i, model=self.model,
                                    xmax=self.xmax, o_path=self.output_path,
                                    params=self.config['profile']['params'],
                                    reload=reload, save=save, verbose=self.verbose)

    def plot(self, chk_i, var, y_log=True, x_log=True):
        """Plot given variable
        """
        # TODO:
        #       - autoload chk_i
        #       - check if var exists in profile

        fig, ax = plt.subplots()
        profile = self.profiles[chk_i]
        ax.plot(profile['x'], profile[var])

        if y_log:
            ax.set_yscale('log')
        if x_log:
            ax.set_xscale('log')

    def plot_dat(self, var, y_log=True, display=True):
        """Plots quantity from dat file
        """
        fig, ax = plt.subplots()
        if y_log:
            ax.set_yscale('log')

        ax.plot(self.dat['time'], self.dat[var])

        ax.set_xlabel('$t$ (s)')
        ax.set_ylabel(var)

        if display:
            plt.show(block=False)
