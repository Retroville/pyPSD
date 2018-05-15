import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider

class Plotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

    def plot(self, obj):
        self.obj = obj
        self.l = plt.plot(obj.t,obj.series())
        _vars = obj.get_variables()
        plt.subplots_adjust(bottom=0.03*(len(_vars)+2))
        self.sliders = []
        for i,var in enumerate(_vars):
            self.add_slider(i*0.03, var[0], var[1], var[2])
        plt.show()

    def add_slider(self, pos, name, min, max):
        ax = plt.axes([0.1, 0.02+pos, 0.8, 0.02], axisbg='lightgoldenrodyellow')
        slider = Slider(ax, name, min, max, valinit=getattr(self.obj, name))
        self.sliders.append(slider)
        def update(val):
            setattr(self.obj, name, val)
            self.l[0].set_ydata(self.obj.series())
            self.fig.canvas.draw_idle()
        slider.on_changed(update)

class SinFunction:
    def __init__(self):
        self.freq = 1.0
        self.amp = 0.5
        self.t = np.arange(0.0, 1.0, 0.001)

    def series(self):
        return self.amp*np.sin(2*np.pi*self.freq*self.t)

    def get_variables(self):
        return [
            ('freq', 0.1, 10),
            ('amp', 0.1, 1)
        ]

k = Plotter()
k.plot(SinFunction())