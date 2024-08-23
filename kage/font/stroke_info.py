from enum import Enum

class StrokeType(Enum):
    unknown_0       = 0
    straight_line   = 1
    curve           = 2
    bend_line       = 3
    otsu_curve      = 4
    complex_curve   = 6
    vertical_slash  = 7
    unknown_12      = 12 # Used in serif.py

class SerifType(Enum):
    free                = 0
    connect_h           = 2
    hook_left           = 4
    hook_right          = 5
    narrow              = 7
    stop_for_dot        = 8
    left_top_corner     = 12
    left_bottom_corner  = 13
    right_top_corner    = 22
    right_bottom_corner = 23
    right_bottom_ht     = 24
    roofed_narrow       = 27
    connect             = 32
    connect_v           = 32
    left_bottom_zh_old  = 313
    left_bottom_zh_new  = 413

