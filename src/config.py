import os

from ok import ConfigOption

version = "dev"

key_config_option = ConfigOption(
    "Game Settings",
    {
        "Language": "English",
    },
    description="Game Settings",
    config_type={
        "Language": {
            "type": "drop_down",
            "options": ["English"],
        }
    },
)

config = {
    'debug': False,  # Optional, default: False
    'use_gui': True,
    'config_folder': 'configs',
    'global_configs': [key_config_option],
    'gui_icon': 'icons/airona.png',
    'wait_until_before_delay': 0,
    'wait_until_check_delay': 0,
    'wait_until_settle_time': 0.2,
    'ocr': {
        'lib': 'onnxocr',
        'params': {
            'use_openvino': True,
        }
    },
    'windows': {
        'exe': ['Star.exe', 'BPSR.exe', 'BPSR_STEAM.exe'],
        'interaction': 'Pynput',
        'can_bit_blt': True,  # default false, opengl games does not support bit_blt
        'bit_blt_render_full': True,
        'check_hdr': True,  # Prompt the user when AutoHDR is enabled, but do not prohibit its use
        'force_no_hdr': False,  # True=Disabled when user turns on AutoHDR
        'require_bg': True  # Request to use background screenshots
    },
    'start_timeout': 60,
    'window_size': {
        'width': 1200,
        'height': 800,
        'min_width': 600,
        'min_height': 450,
    },
    'supported_resolution': {
        'ratio': '16:9',
        'min_size': (1280, 720),
        'resize_to': [(2560, 1440), (1920, 1080), (1600, 900), (1280, 720)],
    },
    'links': {
        'default': {
            'github': 'https://github.com/ArtjomsBogatirjovs/bpsr-fishing',
        }
    },
    'screenshots_folder': "screenshots",
    'gui_title': 'Blue protocol: Star Resonance auto-fishing',
    'template_matching': {
        'coco_feature_json': os.path.join('assets', 'result.json'),
        'default_horizontal_variance': 0.002,
        'default_vertical_variance': 0.002,
        'default_threshold': 0.8,
    },
    'version': version,
    'my_app': ['src.globals', 'Globals'],
    'onetime_tasks': [
        ["ok", "DiagnosisTask"],
    ],
    'trigger_tasks': [
        ["src.tasks.FishingTask", "FishingTask"],
    ]
}
