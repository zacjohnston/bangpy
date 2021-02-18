"""Compare multiple simulations
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# flashbang
from . import simulation
from . import plot_tools
from . import load_save


class Comparison:
    """Object for holding multiple models to compare
    """
    def __init__(self,
                 runs,
                 models,
                 model_sets,
                 config,
                 verbose=True):
        """

        Parameters
        ----------
        runs : [str]
        models : [str]
        model_sets : [str]
        config : str
        """
        self.sims = {}
        self.verbose = verbose
        self.config = load_save.load_config(config, verbose=self.verbose)

        for i, model in enumerate(models):
            self.sims[model] = simulation.Simulation(run=runs[i],
                                                     model=model,
                                                     model_set=model_sets[i],
                                                     config=config)

    # =======================================================
    #                      Plot
    # =======================================================
    def plot_profile(self, chk, y_var,
                     x_var='r',
                     y_scale=None, x_scale=None,
                     ylims=None, xlims=None,
                     y_factor=1,
                     ax=None,
                     marker=None,
                     trans=False,
                     title=True,
                     legend=True,
                     linestyle='-',
                     title_str=None,
                     data_only=False):
        """Plot profile comparison

        Returns : fig

        Parameters
        ----------
        chk : int
        y_var : str
            variable to plot on y-axis (from Simulation.profile)
        x_var : str
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        y_factor : float
            Divide y-values by this factor
        ax : Axes
        legend : bool
        trans : bool
        title : bool
        ylims : [min, max]
        xlims : [min, max]
        linestyle : str
        marker : str
        title_str : str
        data_only : bool
            only plot data, neglecting all titles/labels/scales
        """
        fig, ax = plot_tools.setup_fig(ax=ax)

        for model, sim in self.sims.items():
            sim.plot_profile(chk=chk, y_var=y_var, x_var=x_var,
                             y_factor=y_factor, marker=marker, trans=trans,
                             linestyle=linestyle, ax=ax, label=model,
                             data_only=True)

        if not data_only:
            self._set_ax_all(ax, x_var=x_var, y_var=y_var, xlims=xlims, ylims=ylims,
                             x_scale=x_scale, y_scale=y_scale, chk=chk, title=title,
                             title_str=title_str, legend=legend)
        return fig

    def plot_profile_slider(self, y_var,
                            x_var='r',
                            y_scale=None, x_scale=None,
                            xlims=None, ylims=None,
                            y_factor=1,
                            trans=False,
                            title=True,
                            legend=True,
                            linestyle='-',
                            marker=''):
        """Plot interactive profile comparison

        Returns : fig, slider

        Parameters
        ----------
        y_var : str
        x_var : str
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        trans : bool
            plot helmholtz transitions
        title : bool
        xlims : [min, max]
        ylims : [min, max]
        legend : bool
        linestyle : str
        marker : str
        y_factor : float
        """
        fig, profile_ax, slider_ax = plot_tools.setup_slider_fig()
        chk_min, chk_max = self._get_slider_chk()
        slider = Slider(slider_ax, 'chk', chk_min, chk_max, valinit=chk_max, valstep=1)

        self.plot_profile(chk=chk_max,
                          y_var=y_var, x_var=x_var,
                          y_scale=y_scale, x_scale=x_scale,
                          ylims=ylims, xlims=xlims,
                          ax=profile_ax, legend=legend,
                          trans=trans, title=title,
                          linestyle=linestyle,
                          marker=marker, y_factor=y_factor)

        self._set_ax_legend(ax=profile_ax, legend=legend)

        def update(chk):
            idx = int(chk)
            for i, sim in enumerate(self.sims.values()):
                profile = sim.profiles.sel(chk=idx)
                y_profile = profile[y_var] / y_factor

                profile_ax.lines[i].set_ydata(y_profile)
                profile_ax.lines[i].set_xdata(profile[x_var])
                # sim._set_ax_title(profile_ax, chk=idx, title=title)

                # if trans:
                #     for i, key in enumerate(sim.trans_dens):
                #         x, y = sim._get_trans_xy(chk=idx, key=key,
                #                                  x_var=x_var, y=y_profile)
                #         profile_ax.lines[i+1].set_xdata(x)
                #         profile_ax.lines[i+1].set_ydata(y)

                fig.canvas.draw_idle()

        slider.on_changed(update)
        return fig, slider

    def plot_dat(self,
                 y_var,
                 **kwargs):
        """Plot comparison dat
        """
        fig, ax = plt.subplots()

        for model, sim in self.sims.items():
            sim.plot_dat(y_var=y_var, ax=ax, label=model,
                         **kwargs)
        ax.legend()
        return fig

    # =======================================================
    #                      Plotting Tools
    # =======================================================
    def _set_ax_all(self, ax, x_var, y_var, x_scale, y_scale,
                    xlims, ylims, title, legend, loc=None,
                    chk=None, title_str=None):
        """Set all axis properties

        Parameters
        ----------
        ax : Axes
        x_var : str
        y_var : str
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        chk : int
        title : bool
        title_str : str
        xlims : [min, max]
        ylims : [min, max]
        legend : bool
        loc : int or str
        """
        self._set_ax_title(ax, chk=chk, title=title, title_str=title_str)
        self._set_ax_lims(ax, xlims=xlims, ylims=ylims)
        self._set_ax_labels(ax, x_var=x_var, y_var=y_var)
        self._set_ax_legend(ax, legend=legend, loc=loc)
        self._set_ax_scales(ax, x_var=x_var, y_var=y_var,
                            x_scale=x_scale, y_scale=y_scale)

    def _set_ax_scales(self, ax, y_var, x_var, y_scale, x_scale):
        """Set axis scales (linear, log)

        Parameters
        ----------
        ax : Axes
        y_var : str
        x_var : str
        y_scale : 'log' or 'linear'
        x_scale : 'log' or 'linear'
        """
        def get_scale(var):
            if var in self.config['plotting']['ax_scales']['log']:
                return 'log'
            else:
                return 'linear'

        if x_scale is None:
            x_scale = get_scale(x_var)
        if y_scale is None:
            y_scale = get_scale(y_var)

        ax.set_xscale(x_scale)
        ax.set_yscale(y_scale)

    def _set_ax_title(self, ax, title, chk=None, title_str=None):
        """Set axis title

        Parameters
        ----------
        ax : Axes
        chk : int
        title : bool
        title_str : str
        """
        # TODO: use chk_table from master model
        if title:
            if (title_str is None) and (chk is not None):
                # timestep = self.chk_table.loc[chk, 'time'] - self.bounce_time
                dt = self.config['plotting']['scales']['chk_dt']
                timestep = dt * chk
                title_str = f't = {timestep:.3f} s'

            ax.set_title(title_str)

    def _set_ax_lims(self, ax, xlims, ylims):
        """Set x and y axis limits

        Parameters
        ----------
        ax : Axes
        xlims : [min, max]
        ylims : [min, max]
        """
        if ylims is not None:
            ax.set_ylim(ylims)
        if xlims is not None:
            ax.set_xlim(xlims)

    def _set_ax_labels(self, ax, x_var, y_var):
        """Set axis labels

        Parameters
        ----------
        ax : Axes
        x_var : str
        y_var : str
        """
        def get_label(key):
            return self.config['plotting']['labels'].get(key, key)

        ax.set_xlabel(get_label(x_var))
        ax.set_ylabel(get_label(y_var))

    def _set_ax_legend(self, ax, legend, loc=None):
        """Set axis labels

        Parameters
        ----------
        ax : Axes
        legend : bool
        loc : int or str
        """
        if legend:
            ax.legend(loc=loc)

    def _get_slider_chk(self):
        """Return largest chk range common to all models
        """
        mins = []
        maxes = []

        for sim in self.sims.values():
            mins += [sim.chk_table.index.min()]
            maxes += [sim.chk_table.index.max()]

        chk_min = max(mins)
        chk_max = min(maxes)
        return chk_min, chk_max
