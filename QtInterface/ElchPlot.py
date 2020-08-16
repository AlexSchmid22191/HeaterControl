from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.style
import math


class ElchPlot(FigureCanvas):
    def __init__(self, *args, **kwargs):
        matplotlib.style.use('QtInterface/App.mplstyle')
        super().__init__(Figure(figsize=(8, 6)), *args, **kwargs)

        self.units = 'Temperature'

        self.ax = self.figure.subplots()
        self.ax2 = self.ax.twinx()

        self.colors = {'Power': '#86f9de', 'Sensor PV': '#86d7f8', 'Controller PV': '#9686f8'}
        self.fake_data = {'Power': [math.sin(x/8) for x in range(30)], 'Sensor PV': [math.sin(x/8+1) for x in range(30)], 'Controller PV': [math.sin(x/8+2) for x in range(30)]}
        self.plots = {key: self.ax.plot(self.fake_data[key], color=self.colors[key])
                      for key in self.colors}

        self.ax.set_xlabel('Time (min)')
        self.ax2.set_ylabel('Power (%)')
        self.ax.set_ylabel('Temperature (°C)')

        self.figure.tight_layout()
