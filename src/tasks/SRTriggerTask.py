from ok import TriggerTask


class SRTriggerTask(TriggerTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_mouse_down = False

    def my_mouse_down(self, x, y):
        if self.is_mouse_down:
            return
        self.is_mouse_down = True

        TriggerTask.mouse_down(self, self.width_of_screen(x), self.height_of_screen(y))

    def my_mouse_up(self):
        if not self.is_mouse_down:
            return
        self.is_mouse_down = False

        TriggerTask.mouse_up(self)

    def my_mouse_switch(self, x, y):
        if self.is_mouse_down:
            self.my_mouse_up()
        else:
            self.my_mouse_down(x, y)

    def get_config_value(self, key: str):
        setting = self._settings_map.get(key)
        if setting:
            return self.config.get(setting['label'], setting['default'])
        return None
