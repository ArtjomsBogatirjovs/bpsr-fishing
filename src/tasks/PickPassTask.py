import re

from src.tasks.SRTriggerTask import SRTriggerTask

class PickPassTask(SRTriggerTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动领取月卡"
        self.description = "弹出月卡界面后自动领取月卡"
        self.trigger_count = 0

    def run(self):
        if box:=self.ocr(0.44, 0.94, 0.56, 1, match='点击空白处关闭'):
            self.click_box(box)
        return