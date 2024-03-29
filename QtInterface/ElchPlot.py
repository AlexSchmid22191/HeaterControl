import matplotlib.font_manager as fm
import matplotlib.style
import matplotlib.ticker
import numpy as np
import pubsub.pub
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

colors = {'blue': '#86b3f9', 'green': '#86f8ab', 'pink': '#f488f9', 'yellow': '#faf0b1', 'purple': '#9686f8'}


class ElchPlot(FigureCanvasQTAgg):
    def __init__(self):
        matplotlib.style.use('QtInterface/App.mplstyle')
        super().__init__(Figure(figsize=(8, 6)))

        ax = self.figure.subplots()
        ax2 = ax.twinx()

        self.toolbar = NavigationToolbar2QT(self, self)
        self.toolbar.hide()

        ax.set_xlabel('Time (s)', fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=14))
        ax2.set_ylabel('Power (%)', fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=14))

        ax.set_xticks(range(11))
        ax.set_yticks(range(11))
        ax2.set_yticks(range(11))
        ax.set_xticklabels(range(11), fontproperties=fm.FontProperties(fname='Fonts/Roboto-Light.ttf', size=11))
        ax.set_yticklabels(range(11), fontproperties=fm.FontProperties(fname='Fonts/Roboto-Light.ttf', size=11))
        ax2.set_yticklabels(range(11), fontproperties=fm.FontProperties(fname='Fonts/Roboto-Light.ttf', size=11))
        ax.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())
        ax.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())
        ax2.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())
        ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax2.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        self.units = 'Temperature'
        self.axes = {'Power': ax2, 'Sensor PV': ax, 'Controller PV': ax, 'Setpoint': ax}
        self.colors = {'Power': colors['green'], 'Sensor PV': colors['blue'],
                       'Controller PV': colors['pink'], 'Setpoint': colors['yellow']}
        self.plots = {key: self.axes[key].plot([], color=self.colors[key], marker='')[0] for key in self.axes}

        self.autoscale = True
        self.figure.tight_layout()

    def add_data_point(self, status_values):
        for key, value in status_values.items():
            self.plots[key].set_data(np.append(self.plots[key].get_data()[0], value[1]),
                                     np.append(self.plots[key].get_data()[1], value[0]))

            if self.autoscale:
                self.axes[key].relim()
                self.axes[key].autoscale()
            self.figure.canvas.draw()
            self.figure.tight_layout()

    def set_plot_visibility(self, plot, visible):
        self.plots[plot.objectName()].set_linestyle('-' if visible else '')

    def start_plotting(self, plotting):
        if plotting:
            pubsub.pub.subscribe(self.add_data_point, 'engine.answer.status')
        else:
            pubsub.pub.unsubscribe(self.add_data_point, 'engine.answer.status')

    def clear_plot(self):
        for plot in self.plots.values():
            plot.set_data([], [])
        self.figure.canvas.draw()

    def set_units(self, unit):
        self.axes['Sensor PV'].set_ylabel({'Temperature': 'Temperature (°C)', 'Voltage': 'Voltage (mV)'}[unit],
                                          fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=14))
        self.figure.canvas.draw()
        self.figure.tight_layout()

    def toggle_autoscale(self):
        self.autoscale = not self.autoscale
