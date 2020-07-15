from datetime import datetime

import os
import matplotlib
import wx
from pubsub.pub import sendMessage, subscribe, unsubscribe
from serial.tools.list_ports import comports

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.style import use
from ThreadDecorators import in_main_thread
from numpy import append

use('App.mplstyle')


class HeaterInterface(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SetTitle('Heater Control')
        self.SetIcon(wx.Icon('Icons/Logo.ico'))

        if os.name == 'nt':
            self.SetBackgroundColour('White')

        self.status_bar = wx.StatusBar(parent=self)
        self.SetStatusBar(statusBar=self.status_bar)

        subscribe(listener=self.update_status_bar, topicName='engine.status')

        menu_bar = Menubar()
        self.SetMenuBar(menu_bar)

        self.Bind(event=wx.EVT_MENU, handler=self.on_quit, id=wx.ID_CLOSE)

        self.status = StatusWindow(parent=self)
        self.oven_ctrl = OvenControl(parent=self)
        plot_ctrl = PlottingControl(parent=self)
        log_ctrl = LogginControl(parent=self)
        matplot = MatplotWX(parent=self)

        self.Bind(wx.EVT_BUTTON, source=plot_ctrl.start_btn, handler=matplot.start_plotting)
        self.Bind(wx.EVT_BUTTON, source=plot_ctrl.stop_btn, handler=matplot.stop_plotting)
        self.Bind(wx.EVT_BUTTON, source=plot_ctrl.clear_btn, handler=matplot.clear_plot)
        self.Bind(wx.EVT_BUTTON, source=plot_ctrl.resume_btn, handler=matplot.cont_plotting)

        hbox = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox.Add(self.status, flag=wx.EXPAND | wx.RIGHT, border=10)
        hbox.Add(log_ctrl, flag=wx.EXPAND | wx.RIGHT, border=10)
        hbox.Add(plot_ctrl, flag=wx.EXPAND)

        vbox = wx.BoxSizer(orient=wx.VERTICAL)
        vbox.Add(self.oven_ctrl, flag=wx.BOTTOM | wx.EXPAND, border=10)
        vbox.Add(hbox)

        hbox_2 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox_2.Add(vbox, flag=wx.ALL, border=10)
        hbox_2.Add(matplot, flag=wx.EXPAND | wx.FIXED_MINSIZE, proportion=1)

        hbox_2.Fit(self)
        self.SetSizer(hbox_2)

        self.SetMinSize((800, self.GetSize()[1]))
        self.Show(True)

    @in_main_thread
    def update_status_bar(self, text):
        self.status_bar.SetStatusText(text)
        wx.CallLater(millis=4000, callableObj=self.status_bar.SetStatusText, text='')

    def on_quit(self, *args):
        self.Close()


class LogginControl(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_btn = wx.Button(self, wx.ID_ANY, 'Start')
        self.stop_btn = wx.Button(self, wx.ID_ANY, 'Stop')
        self.cont_btn = wx.Button(self, wx.ID_ANY, 'Pause')

        self.start_btn.Bind(event=wx.EVT_BUTTON, source=self.start_btn, handler=self.start_log)
        self.stop_btn.Bind(event=wx.EVT_BUTTON, source=self.stop_btn, handler=self.stop_log)
        self.cont_btn.Bind(event=wx.EVT_BUTTON, source=self.cont_btn, handler=self.pause_log)

        box = wx.StaticBox(parent=self, label='Data logging')
        boxsizer = wx.StaticBoxSizer(box, orient=wx.VERTICAL)

        for button in [self.start_btn, self.stop_btn, self.cont_btn]:
            boxsizer.Add(button, flag=wx.EXPAND | wx.ALL, border=2.5)

        self.SetSizer(boxsizer)

    def start_log(self, *args):
        log_path = 'default.txt'

        dlg = wx.FileDialog(self, message="Choose log file destination", defaultDir='./', style=wx.FD_SAVE | wx.FD_CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            log_path = dlg.GetPath()
        dlg.Destroy()

        sendMessage(topicName='gui.log.filename', filename=log_path)
        sendMessage(topicName='gui.log.start')
        args[0].Skip()

    @staticmethod
    def stop_log(*args):
        sendMessage(topicName='gui.log.stop')

    @staticmethod
    def pause_log(*args):
        sendMessage(topicName='gui.log.continue')


class OvenControl(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        temp_label = wx.StaticText(parent=self, label='Temperature')
        ramp_label = wx.StaticText(parent=self, label='Ramp')
        power_label = wx.StaticText(parent=self, label='Power')
        self.temp_entry = wx.SpinCtrlDouble(parent=self, value='0', min=0, max=1200, inc=1, style=wx.SP_ARROW_KEYS,
                                            size=(70, -1))
        self.ramp_entry = wx.SpinCtrlDouble(parent=self, value='15', min=0, max=480, inc=1, style=wx.SP_ARROW_KEYS,
                                            size=(70, -1))
        self.power_entry = wx.SpinCtrlDouble(parent=self, value='0', min=0, max=100, inc=1, style=wx.SP_ARROW_KEYS,
                                             size=(70, -1))

        set_power_btn = wx.Button(parent=self, id=wx.ID_ANY, label='Set')
        set_temp_btn = wx.Button(parent=self, id=wx.ID_ANY, label='Set')
        set_ramp_btn = wx.Button(parent=self, id=wx.ID_ANY, label='Set')

        set_power_btn.Bind(event=wx.EVT_BUTTON, handler=self.set_power, source=set_power_btn)
        set_temp_btn.Bind(event=wx.EVT_BUTTON, handler=self.set_temp, source=set_temp_btn)
        set_ramp_btn.Bind(event=wx.EVT_BUTTON, handler=self.set_ramp, source=set_ramp_btn)

        entry_box = wx.FlexGridSizer(rows=3, cols=3, hgap=5, vgap=5)
        entry_box.Add(temp_label, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(self.temp_entry, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(set_temp_btn, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(ramp_label, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(self.ramp_entry, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(set_ramp_btn, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(power_label, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(self.power_entry, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        entry_box.Add(set_power_btn, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        self.mode_box = wx.RadioBox(parent=self, label='Operation Mode', choices=['Manual', 'Automatic'], majorDimension=1)
        self.mode_box.Bind(event=wx.EVT_RADIOBOX, handler=self.set_mode, source=self.mode_box)

        pid_button = wx.Button(parent=self, id=wx.ID_ANY, label='P\nI\nD')
        pid_button.Bind(wx.EVT_BUTTON, handler=self.show_pid)

        box = wx.StaticBox(parent=self, label='Oven Control')
        boxsizer = wx.StaticBoxSizer(box, orient=wx.HORIZONTAL)

        boxsizer.Add(entry_box, flag=wx.ALL, border=5)
        boxsizer.Add(self.mode_box, flag=wx.ALL | wx.EXPAND, border=5)
        boxsizer.Add(pid_button, flag=wx.ALL | wx.EXPAND, border=5)

        self.SetSizerAndFit(boxsizer)

    def set_ramp(self, *args):
        rate = self.ramp_entry.GetValue()
        sendMessage(topicName='gui.set.rate', rate=rate)

    def set_temp(self, *args):
        temp = self.temp_entry.GetValue()
        sendMessage(topicName='gui.set.target_setpoint', temp=temp)

    def set_power(self, *args):
        power = self.power_entry.GetValue()
        sendMessage(topicName='gui.set.manual_power', power=power)

    def set_mode(self, *args):
        label = self.mode_box.GetStringSelection()
        if label == 'Automatic':
            sendMessage(topicName='gui.set.automatic_mode')
        else:
            sendMessage(topicName='gui.set.manual_mode')

    @staticmethod
    def show_pid(*args):
        pid = PIDFrame(parent=None)
        pid.Show()


class PIDFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if os.name == 'nt':
            self.SetBackgroundColour('White')

        parameters = {'P': 'Proportional band', 'I': 'Integral time (s)', 'D': 'Derivative time (s)'}
        self.labels = {key: wx.StaticText(parent=self, label=value) for (key, value) in parameters.items()}
        self.entries = {key: wx.SpinCtrl(parent=self, min=0, max=9999, initial=1) for key in parameters}
        self.set_button = wx.Button(parent=self, id=wx.ID_ANY, label='Set')

        grid_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=5, vgap=5)
        [(grid_sizer.Add(self.labels[parameter]),grid_sizer.Add(self.entries[parameter])) for parameter in parameters]

        boxsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        boxsizer.Add(grid_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        boxsizer.Add(self.set_button, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(boxsizer)
        self.Show()

    def set_pid_parameters(self):
        sendMessage(topicName='gui.set.pid_p', p=self.entries['P'].Getvalue())
        sendMessage(topicName='gui.set.pid_i', i=self.entries['I'].Getvalue())
        sendMessage(topicName='gui.set.pid_d', d=self.entries['D'].Getvalue())


class StatusWindow(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timer = wx.Timer()
        self.timer.Bind(event=wx.EVT_TIMER, handler=self.request_data)
        self.timer.Start(milliseconds=1000)

        temp_oven_label = wx.StaticText(parent=self, label='Oven Tempearture (°C)')
        temp_sens_label = wx.StaticText(parent=self, label='Sensor Temperature (°C)')
        set_temp_label = wx.StaticText(parent=self, label='Set Temperature (°C)')
        power_label = wx.StaticText(parent=self, label='Oven Power (%)')

        self.temp_oven_value = wx.StaticText(parent=self, label='23.5')
        self.temp_sens_value = wx.StaticText(parent=self, label='42.24')
        self.set_temp_value = wx.StaticText(parent=self, label='625')
        self.power_value = wx.StaticText(parent=self, label='10.5')

        subscribe(listener=self.update_oven_power, topicName='engine.answer.oven_working_output')
        subscribe(listener=self.update_oven_setpoint, topicName='engine.answer.oven_working_setpoint')
        subscribe(listener=self.update_oven_temperature, topicName='engine.answer.oven_temp')
        subscribe(listener=self.update_sensor_temperature, topicName='engine.answer.sensor_temp')

        grid_sizer = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=20)

        grid_sizer.AddMany([temp_oven_label, (self.temp_oven_value, 0, wx.ALIGN_RIGHT),
                            temp_sens_label, (self.temp_sens_value, 0, wx.ALIGN_RIGHT),
                            set_temp_label, (self.set_temp_value, 0, wx.ALIGN_RIGHT),
                            power_label, (self.power_value, 0, wx.ALIGN_RIGHT)])

        box = wx.StaticBox(parent=self, label='Status')
        boxsizer = wx.StaticBoxSizer(box)
        boxsizer.Add(grid_sizer, flag=wx.ALL, border=5)

        self.SetSizer(boxsizer)

    @staticmethod
    def request_data(*args):
        sendMessage(topicName='gui.request.oven_temp')
        sendMessage(topicName='gui.request.working_output')
        sendMessage(topicName='gui.request.working_setpoint')
        sendMessage(topicName='gui.request.sensor_temp')

    @in_main_thread
    def update_oven_temperature(self, temp):
        self.temp_oven_value.SetLabel(label='{:4.1f}'.format(temp))

    @in_main_thread
    def update_oven_power(self, output):
        self.power_value.SetLabel(label='{:3.1f}'.format(output))

    @in_main_thread
    def update_oven_setpoint(self, setpoint):
        self.set_temp_value.SetLabel(label='{:4.1f}'.format(setpoint))

    @in_main_thread
    def update_sensor_temperature(self, temp):
        self.temp_sens_value.SetLabel(label='{:4.1f}'.format(temp))


class PlottingControl(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_btn = wx.Button(self, wx.ID_ANY, 'Start')
        self.stop_btn = wx.Button(self, wx.ID_ANY, 'Stop')
        self.clear_btn = wx.Button(self, wx.ID_ANY, 'Clear')
        self.resume_btn = wx.Button(self, wx.ID_ANY, 'Resume')

        box = wx.StaticBox(parent=self, label='Data Plotting')
        boxsizer = wx.StaticBoxSizer(box, orient=wx.VERTICAL)

        for button in [self.start_btn, self.stop_btn, self.resume_btn, self.clear_btn]:
            boxsizer.Add(button, flag=wx.EXPAND | wx.ALL, border=2.5)

        self.SetSizer(boxsizer)


class MatplotWX(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_plotting = False

        self.startime = datetime.now()

        self.figure = Figure(figsize=(3, 2.5))

        self.axes = self.figure.add_subplot(111)
        self.paxes = self.axes.twinx()

        self.paxes.set_ylabel('Power (%)')
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Temperature (°C)')

        self.sens_temp_plot, = self.axes.plot([], marker='o', color='dodgerblue', label='Sensor Temperature')
        self.oven_temp_plot, = self.axes.plot([], marker='s', color='orangered', label='Heater Temperature')
        self.oven_pwr_plot, = self.paxes.plot([], marker='^', color='springgreen', label='Heater Power')

        self.figure.legend(handles=[self.sens_temp_plot, self.oven_temp_plot, self.oven_pwr_plot],
                           loc='lower center', ncol=2)

        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, flag=wx.GROW | wx.FIXED_MINSIZE, proportion=2)
        self.SetSizer(self.sizer)
        self.figure.subplots_adjust(0.2, 0.275, 0.8, 0.95)
        self.Fit()

    @in_main_thread
    def add_sensor_temp_point(self, temp):
        time = (datetime.now() - self.startime).seconds

        self.sens_temp_plot.set_xdata(append(self.sens_temp_plot.get_xdata(), time))
        self.sens_temp_plot.set_ydata(append(self.sens_temp_plot.get_ydata(), temp))

        self.axes.relim()
        self.axes.autoscale_view()
        self.figure.canvas.draw()
        
    @in_main_thread
    def add_oven_temp_point(self, temp):
        time = (datetime.now() - self.startime).seconds

        self.oven_temp_plot.set_xdata(append(self.oven_temp_plot.get_xdata(), time))
        self.oven_temp_plot.set_ydata(append(self.oven_temp_plot.get_ydata(), temp))

        self.axes.relim()
        self.axes.autoscale_view()
        self.figure.canvas.draw()
    
    @in_main_thread
    def add_oven_power_point(self, output):
        time = (datetime.now() - self.startime).seconds

        self.oven_pwr_plot.set_xdata(append(self.oven_pwr_plot.get_xdata(), time))
        self.oven_pwr_plot.set_ydata(append(self.oven_pwr_plot.get_ydata(), output))

        self.paxes.relim()
        self.paxes.autoscale_view()
        self.figure.canvas.draw()

    def start_plotting(self, *args):
        if not self.is_plotting:
            self.is_plotting = True
            self.startime = datetime.now()
            subscribe(topicName='engine.answer.sensor_temp', listener=self.add_sensor_temp_point)
            subscribe(topicName='engine.answer.oven_temp', listener=self.add_oven_temp_point)
            subscribe(topicName='engine.answer.oven_working_output', listener=self.add_oven_power_point)

    def stop_plotting(self, *args):
        self.is_plotting = False
        unsubscribe(topicName='engine.answer.sensor_temp', listener=self.add_sensor_temp_point)

    def cont_plotting(self, *args):
        self.is_plotting = True
        subscribe(topicName='engine.answer.sensor_temp', listener=self.add_sensor_temp_point)

    def clear_plot(self, args):
        for plot in (self.sens_temp_plot, self.oven_temp_plot, self.oven_pwr_plot):
            plot.set_xdata([])
            plot.set_ydata([])
        self.figure.canvas.draw()


class Menubar(wx.MenuBar):
    def __init__(self, _=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        filemenu = wx.Menu()
        filemenu.Append(item='New log', id=wx.ID_ANY)
        filemenu.Append(item='Save plot', id=wx.ID_ANY)
        filemenu.Append(item='Quit', id=wx.ID_CLOSE)

        dev_menu = DeviceMenu()
        self.Append(filemenu, 'File')
        self.Append(dev_menu, 'Devices')


class DeviceMenu(wx.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.heater_type_menu = heater_menu = wx.Menu()
        self.heater_type_menu.Append(item='Eurotherm3216', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.heater_type_menu.Append(item='Eurotherm3508', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.heater_type_menu.Append(item='Eurotherm3200', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.heater_type_menu.Append(item='Eurotherm3210', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.heater_type_menu.Append(item='Omega Pt', id=wx.ID_ANY, kind=wx.ITEM_RADIO)

        self.heater_com_menu = PortMenu()

        self.sensor_type_menu = wx.Menu()
        self.sensor_type_menu.Append(item='Thermolino', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.sensor_type_menu.Append(item='Thermoplatino', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.sensor_type_menu.Append(item='Pyrometer', id=wx.ID_ANY, kind=wx.ITEM_RADIO)
        self.sensor_type_menu.Append(item='Keithly 2000', id=wx.ID_ANY, kind=wx.ITEM_RADIO)

        self.sensor_com_menu = PortMenu()

        self.AppendSubMenu(text='Heater type', submenu=heater_menu)
        self.AppendSubMenu(text='Heater port', submenu=self.heater_com_menu)
        heater_connect = self.Append(id=wx.ID_ANY, item='Connect heater', kind=wx.ITEM_CHECK)
        self.AppendSeparator()
        self.AppendSubMenu(text='Sensor type', submenu=self.sensor_type_menu)
        self.AppendSubMenu(text='Sensor port', submenu=self.sensor_com_menu)
        sensor_connect = self.Append(id=wx.ID_ANY, item='Connect sensor', kind=wx.ITEM_CHECK)

        self.Bind(event=wx.EVT_MENU, handler=self.connect_heater, source=heater_connect)
        self.Bind(event=wx.EVT_MENU, handler=self.connect_sensor, source=sensor_connect)

    def connect_heater(self, event):

        item = self.FindItemById(event.GetId())

        if item.IsChecked():
            heater_port, heater_type = None, None
            for port_item in self.heater_com_menu.GetMenuItems():
                if port_item.IsChecked():
                    heater_port = self.heater_com_menu.port_dict[port_item.GetItemLabelText()]

            for type_item in self.heater_type_menu.GetMenuItems():
                if type_item.IsChecked():
                    heater_type = type_item.GetItemLabelText()

            sendMessage(topicName='gui.con.connect_heater', heater_type=heater_type, heater_port=heater_port)

        else:
            sendMessage(topicName='gui.con.disconnect_heater')

    def connect_sensor(self, event):
        item = self.FindItemById(event.GetId())

        if item.IsChecked():
            sensor_port, sensor_type = None, None
            for port_item in self.sensor_com_menu.GetMenuItems():
                if port_item.IsChecked():
                    sensor_port = self.sensor_com_menu.port_dict[port_item.GetItemLabelText()]

            for type_item in self.sensor_type_menu.GetMenuItems():
                if type_item.IsChecked():
                    sensor_type = type_item.GetItemLabelText()

            sendMessage(topicName='gui.con.connect_sensor', sensor_type=sensor_type, sensor_port=sensor_port)

        else:
            sendMessage(topicName='gui.con.disconnect_sensor')


class PortMenu(wx.Menu):
    def __init__(self):
        super().__init__()

        self.portdict = self.port_dict = {port[1]: port[0] for port in comports()}
        self.portItems = [wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=port, kind=wx.ITEM_RADIO)
                          for port in list(self.port_dict.keys())]

        for item in self.portItems:
            self.Append(item)