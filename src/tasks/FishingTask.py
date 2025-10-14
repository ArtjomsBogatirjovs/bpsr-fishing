import time
import datetime
import re
import threading

from ok import og

from src.tasks.SRTriggerTask import SRTriggerTask

class FishingTask(SRTriggerTask):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "автоматическая рыбалка"
        self.description = "Автоматическая рыбалка после взаимодействия с местами рыбалки."
        
        self.settings = [
            {'key': 'ignore_tension_spam_click', 'label': 'Не обращайте внимания на натяжение лески и подключайтесь непосредственно к точке (замедлите скорость протягивания лески и уменьшите случайный обрыв лески).', 'default': False},
            {'key': 'switch_rod_key', 'label': 'Кнопка переключения удочки', 'default': "m"}
        ]
        
        self.default_config.update({
            setting['label']: setting['default'] for setting in self.settings
        })
        
        self._settings_map = {s['key']: s for s in self.settings}
        
        self.trigger_count = 0

        # Переменные состояния мини-игры «Летающая рыба».
        self.pos = 0
        self.last_update_time = None
        self.key_a_pressed = False
        self.key_d_pressed = False
        self.fish_pos_from_game = 0

        self.last_start_time = None
        self.last_reeling_time = None
        self.last_continue_time = None
        self.last_switch_time = None

        # Используется для асинхронного поиска всплесков
        self._splash_finder_thread = None
        self._fish_pos_lock = threading.Lock()

        self.regex_map = {
            'chinese': {
                'add_rod': re.compile('添加鱼竿'),
                'continue_fishing': re.compile('继续钓鱼'),
                'use': re.compile('使用'),
            },
            'english': {
                'add_rod': re.compile('pole'),
                'continue_fishing': re.compile('Continue fishing'),
                'use': re.compile('Use'),
            }
        }

    def _splash_finder_worker(self):
        """
        Задача поиска брызг воды выполняется асинхронно.
        """
        splash_box = self.find_splash()
        if splash_box:
            with self._fish_pos_lock:
                self.fish_pos_from_game = splash_box[0].center()[0] / (self.width / 2) - 1 + 0.04

    def run(self):
        """
        Основной цикл выполнения рыболовной задачи.
        Вызовите соответствующую функцию обработки в соответствии с текущим состоянием игры.
        """
        if self._handle_minigame():
            return
        if self._handle_start_and_rod_change():
            return
        if self._handle_hook_fish():
            return
        if self._handle_continue_fishing():
            return

    def _handle_start_and_rod_change(self) -> bool:
        """Проверьте первоначальный интерфейс ловли, чтобы забросить удочку или заменить поврежденную удочку."""
        now = time.time()
        if self.last_start_time is not None and now - self.last_start_time <= 3:
            return False
        if self._find_fishing_level():
            self.sleep(0.5)
            # 检查鱼竿是否损坏
            if self.ocr(0.90, 0.92, 0.96, 0.96, match=self.get_regex('add_rod')):
                self.log_info('更换鱼竿', notify=False)
                self.send_key(self.get_config_value('switch_rod_key'))
                use_boxes = self.wait_ocr(box=None, match=self.get_regex('use'), log=False, threshold=0.8, time_out=15)
                if use_boxes:
                    self.log_info('点击使用鱼竿', notify=False)
                    center = use_boxes[0].center()
                    self.click(center[0] / self.width, center[1] / self.height)
                else:
                    self.log_info('没有鱼竿了', notify=True)
                    self.screenshot()
                    raise Exception("没有鱼竿了,需要实现买鱼竿")
            else:
                self.log_info('抛竿', notify=False)
                self.click(0.5, 0.5)
                self.last_start_time = now
            return True
        return False

    def _handle_hook_fish(self) -> bool:
        """检查鱼上钩的提示，并点击开始收线。"""
        now = time.time()
        if self.last_reeling_time is not None and now - self.last_reeling_time <= 3:
            return False
        if self.find_one("hint_fishing_click", threshold=0.5):
            self.log_info('鱼上钩了', notify=False)
            self.my_mouse_down(0.5, 0.5)
            self.last_update_time = time.time()
            self.pos = 0
            self.last_reeling_time = now
            return True
        return False

    def _handle_continue_fishing(self) -> bool:
        # 每秒最多点击一次继续钓鱼
        now = time.time()
        if self.last_continue_time is not None and now - self.last_continue_time <= 1:
            return False
        if self._match_continue_fishing():
            self.log_info('点击继续钓鱼', notify=False)
            self.click(0.82, 0.90)
            self.last_continue_time = now
            return True
        return False

    def _handle_minigame(self) -> bool:
        """管理收线和溜鱼"""
        # 如果“鱼线张力”文本可见，则需要收线。
        if self.find_one("box_fishing_icon", box=self.box_of_screen(0.33, 0.80, 0.37, 0.87)):
            if self.get_config_value('ignore_tension_spam_click') or self.find_one("box_stop_pull", box=self.box_of_screen(0.50, 0.75, 0.70, 0.92), threshold=0.5):
                self.my_mouse_switch(0.5, 0.5)
            else:
                self.my_mouse_down(0.5, 0.5)
            # 获取鱼的实际位置
            if self._splash_finder_thread is None or not self._splash_finder_thread.is_alive():
                self._splash_finder_thread = threading.Thread(target=self._splash_finder_worker)
                self._splash_finder_thread.start()
            fish_pos_for_minigame = 0
            with self._fish_pos_lock:
                fish_pos_for_minigame = self.fish_pos_from_game
            self._play_the_fish(fish_pos_for_minigame)
            return True
        elif self.last_update_time:
            # 如果小游戏未激活，确保松开鼠标和按键。
            self._reset_minigame_state()
            return True
        return False

    def _play_the_fish(self, fish_pos: float):
        delta_time = self._update_time()

        normalized_fish_pos = min(max(fish_pos / 0.7, -1.3), 1.3)

        self._update_rod_position(delta_time)
        self._update_key_presses(normalized_fish_pos)

    def _update_time(self) -> float:
        """计算并返回自上次更新以来的时间差（delta_time）。"""
        current_time = time.time()
        if self.last_update_time is None:
            self.last_update_time = current_time
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        return delta_time

    def _update_key_presses(self, normalized_fish_pos: float):
        """根据鱼的位置决定按下或释放哪个按键。"""
        if abs(self.pos - normalized_fish_pos) < 0.06:
            return
        if normalized_fish_pos < self.pos:
            # 鱼在竿左边，竿在屏幕右边松开D键
            if self.pos > 0 and self.key_d_pressed:
                self.send_key_up('d')
                self.key_d_pressed = False
            # 鱼在竿左边，竿在屏幕左边按下A键
            if self.pos <= 0 and not self.key_a_pressed:
                self.send_key_down('a')
                self.key_a_pressed = True
        else: 
            # 鱼在竿右边，竿在屏幕左边松开A键
            if self.pos < 0 and self.key_a_pressed:
                self.send_key_up('a')
                self.key_a_pressed = False
            # 鱼在竿右边，竿在屏幕右边按下D键
            if self.pos >= 0 and not self.key_d_pressed:
                self.send_key_down('d')
                self.key_d_pressed = True

    def _update_rod_position(self, delta_time: float):
        """更新鱼竿的位置。"""
        # 未按任何键时，向中心点漂移
        if not self.key_a_pressed and not self.key_d_pressed:
            if self.pos > 0: 
                self.pos -= 1.0 * delta_time
                if self.pos < 0: self.pos = 0
            else : 
                self.pos += 1.0 * delta_time
                if self.pos > 0: self.pos = 0
        
        # 当按下 'A' 键且 pos < 0 时，向 -1 移动
        if self.key_a_pressed and self.pos <= 0:
            self.pos -= 0.5 * delta_time
            
        # 当按下 'D' 键且 pos > 0 时，向 1 移动
        if self.key_d_pressed and self.pos >= 0:
            self.pos += 0.5 * delta_time
            
        # 将位置限制在 [-1, 1] 的范围内
        self.pos = min(max(self.pos, -1.0), 1.0)
    
    def _reset_minigame_state(self):
        """在拉鱼结束时重置溜鱼状态。"""
        self.log_info('重置溜鱼', notify=False)
        self.my_mouse_up()
        if self.key_a_pressed:
            self.send_key_up('a')
            self.key_a_pressed = False
        if self.key_d_pressed:
            self.send_key_up('d')
            self.key_d_pressed = False
        self.last_update_time = None
        self.fish_pos_from_game = 0

    def find_splash(self, threshold=0.5):
        ret = og.my_app.yolo_detect(self.frame, threshold=threshold, label=0)
        # for box in ret:
        #     self.log_info(box, notify=False)
        #     self.screenshot('splash', show_box=True, frame_box=box)
        return ret

    def _find_fishing_level(self):
        if self.get_game_language() == 'chinese':
            return self.find_one("box_fishing_level", box=self.box_of_screen(0.56, 0.91, 0.60, 0.96))
        else:
            return self.find_one("box_fishing_level_eng", box=self.box_of_screen(0.56, 0.91, 0.60, 0.96))

    def _match_continue_fishing(self):
        lang = self.get_game_language()
        if lang == 'chinese':
            return self.ocr(0.79, 0.88, 0.87, 0.93, match=self.get_regex('continue_fishing'))
        else:
            return self.ocr(0.76, 0.88, 0.90, 0.93, match=self.get_regex('continue_fishing'))
