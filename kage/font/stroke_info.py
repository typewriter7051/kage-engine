from enum import Enum

class StrokeType(Enum):
    unknown_0       = 0 # XXX Find out what the unknowns are.
    straight_line   = 1
    curve           = 2
    bend_line       = 3
    otsu_curve      = 4
    complex_curve   = 6
    vertical_slash  = 7
    unknown_12      = 12 # Used in serif.py

class SerifType(Enum):
    free                = 0
    unknown_1           = 1 #
    connect_h           = 2
    hook_left           = 4
    hook_right          = 5
    unknown_6           = 6 #
    narrow              = 7
    stop_for_dot        = 8
    unknown_9           = 9 #
    top_left_corner     = 12
    bottom_left_corner  = 13
    unknown_14          = 14 #
    unknown_15          = 15 #
    top_right_corner    = 22
    bottom_right_corner = 23
    bottom_right_ht     = 24
    roofed_narrow       = 27
    connect             = 32
    connect_v           = 32
    unknown_132         = 132 #
    bottom_left_zh_old  = 313
    bottom_left_zh_new  = 413

