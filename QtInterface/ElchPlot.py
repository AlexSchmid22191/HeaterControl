from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.style
import numpy as np
import pubsub.pub


class ElchPlot(FigureCanvasQTAgg):
    def __init__(self, *args, **kwargs):
        matplotlib.style.use('QtInterface/App.mplstyle')
        super().__init__(Figure(figsize=(8, 6)), *args, **kwargs)

        ax = self.figure.subplots()
        ax2 = ax.twinx()

        ax.set_xlabel('Time (s)')
        ax2.set_ylabel('Power (%)')

        self.units = 'Temperature'
        self.axes = {'Power': ax2, 'Sensor PV': ax, 'Controller PV': ax, 'Setpoint': ax}
        self.colors = {'Power': '#86f9de', 'Sensor PV': '#86d7f8', 'Controller PV': '#9686f8', 'Setpoint': '#f488f9'}
        self.plots = {key: self.axes[key].plot([], color=self.colors[key], marker='')[0] for key in self.axes}

        self.figure.tight_layout()

    def add_data_point(self, status_values):
        for key, value in status_values.items():
            if key in self.plots:
                self.plots[key].set_data(np.append(self.plots[key].get_data()[0], value[1]),
                                         np.append(self.plots[key].get_data()[1], value[0]))

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
        self.axes['Sensor PV'].set_ylabel({'Temperature': 'Temperature (°C)', 'Voltage': 'Voltage (mV)'}[unit])
        self.figure.canvas.draw()
        self.figure.tight_layout()
