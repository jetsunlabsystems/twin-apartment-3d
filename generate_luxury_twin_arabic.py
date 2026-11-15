# -*- coding: utf-8 -*-
"""
Script to generate the luxury furnished twin apartment with:
1. High-end floor textures (Calacatta marble, warm oak parquet, slate tiles, non-slip stone, terrazzo).
2. Architectural windows (bay windows, panoramic sliding doors, black aluminum mullions, sills).
3. Millwork doors (frames/architraves, walnut entry doors with vertical handles, oak interior doors with lever handles).
4. Full interior design furniture package for both Left and Right apartments.
5. Clean, elegant Tajawal Arabic labels with zero overlap.
"""
import json
import re
import os

def build_refined_house():
    # -------------------------------------------------------------
    # 1. Coordinate Grid System (mm)
    # -------------------------------------------------------------
    # Left Apartment X:
    X_EXT_L_OUT = -200
    X_EXT_L_IN  = 0
    X_M1_L_W    = 4100
    X_M1_L_E    = 4250
    X_B1_L_W    = 4300
    X_B1_L_E    = 4450
    X_LW_L_W    = 5640
    X_LW_L_E    = 5840
    X_ST_L_W    = 5840
    X_ST_L_E    = 6040
    X_CTR_W     = 7800
    X_CTR_E     = 8000

    # Right Apartment X (Mirrored):
    X_CTR_MID   = 7900
    def mirror_x(x):
        return 15800 - x

    X_ST_R_W    = mirror_x(X_ST_L_E) # 9760
    X_ST_R_E    = mirror_x(X_ST_L_W) # 9960
    X_LW_R_W    = mirror_x(X_LW_L_E) # 9960
    X_LW_R_E    = mirror_x(X_LW_L_W) # 10160
    X_B1_R_W    = mirror_x(X_B1_L_E) # 11350
    X_B1_R_E    = mirror_x(X_B1_L_W) # 11500
    X_M1_R_W    = mirror_x(X_M1_L_E) # 11550
    X_M1_R_E    = mirror_x(X_M1_L_W) # 11700
    X_EXT_R_IN  = mirror_x(X_EXT_L_IN) # 15800
    X_EXT_R_OUT = mirror_x(X_EXT_L_OUT) # 16000

    # Y Grid (mm):
    Y_TOP_OUT   = -200
    Y_TOP_IN    = 0
    Y_M_N       = 4950
    Y_M_S       = 5100
    Y_LAUND_N   = 5700
    Y_LAUND_S   = 5850
    Y_MBATH_N   = 6800
    Y_MBATH_S   = 6950
    Y_LW_N      = 7150
    Y_LW_S      = 7350
    Y_LIV_N     = 14550
    Y_LIV_S     = 14700
    Y_ST_N      = 14650
    Y_ST_S      = 14850
    Y_KIT_N     = 17850
    Y_KIT_S     = 18000
    Y_GBATH_N   = 19350
    Y_GBATH_S   = 19500
    Y_REC_N     = 24250
    Y_REC_S     = 24400
    Y_TERR_FRONT= 25500
    Y_BOT_OUT   = 25700

    X_MBATH_DIV = 2200
    X_MBATH_DIV_R = mirror_x(X_MBATH_DIV)

    walls = []
    wins = []
    doors = []
    slides = []

    def add_rect_wall(x0, y0, x1, y1, wtype='b'):
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        walls.append([x0, y0, x1, y1, wtype])

    def cut_h_wall(y0, y1, x_start, x_end, cuts, wtype='b'):
        if y0 > y1: y0, y1 = y1, y0
        if x_start > x_end: x_start, x_end = x_end, x_start
        sorted_cuts = sorted(cuts, key=lambda c: c[0])
        curr = x_start
        for cx0, cx1, ctype, cdata in sorted_cuts:
            if cx0 > curr:
                add_rect_wall(curr, y0, cx0, y1, wtype)
            if ctype == 'win':
                # win format: [x0, y0, x1, y1, sill, head]
                sill = cdata.get('sill', 0.9) if cdata else 0.9
                head = cdata.get('head', 2.4) if cdata else 2.4
                wins.append([cx0, y0, cx1, y1, sill, head])
            elif ctype == 'door':
                doors.append(cdata)
            elif ctype == 'slide':
                slides.append({'rect': [cx0, y0, cx1, y1], 'v': False})
            curr = cx1
        if curr < x_end:
            add_rect_wall(curr, y0, x_end, y1, wtype)

    def cut_v_wall(x0, x1, y_start, y_end, cuts, wtype='b'):
        if x0 > x1: x0, x1 = x1, x0
        if y_start > y_end: y_start, y_end = y_end, y_start
        sorted_cuts = sorted(cuts, key=lambda c: c[0])
        curr = y_start
        for cy0, cy1, ctype, cdata in sorted_cuts:
            if cy0 > curr:
                add_rect_wall(x0, curr, x1, cy0, wtype)
            if ctype == 'win':
                sill = cdata.get('sill', 0.9) if cdata else 0.9
                head = cdata.get('head', 2.4) if cdata else 2.4
                wins.append([x0, cy0, x1, cy1, sill, head])
            elif ctype == 'door':
                doors.append(cdata)
            elif ctype == 'slide':
                slides.append({'rect': [x0, cy0, x1, cy1], 'v': True})
            curr = cy1
        if curr < y_end:
            add_rect_wall(x0, curr, x1, y_end, wtype)

    # -------------------------------------------------------------
    # 2. Exterior Envelope Walls & Windows
    # -------------------------------------------------------------
    # North Exterior Wall (Back):
    # Master Bedroom Bay Windows (sill=0.45, head=2.4) + Bedroom 2 Windows (sill=0.9, head=2.4)
    cuts_north = [
        # Left Master Bed Bay Window (wide panoramic alcove)
        (1200, 3200, 'win', {'sill': 0.45, 'head': 2.4, 'bay': True}),
        # Left Bed 2 Window
        (5100, 7100, 'win', {'sill': 0.9, 'head': 2.4}),
        # Right Bed 2 Window
        (mirror_x(7100), mirror_x(5100), 'win', {'sill': 0.9, 'head': 2.4}),
        # Right Master Bed Bay Window
        (mirror_x(3200), mirror_x(1200), 'win', {'sill': 0.45, 'head': 2.4, 'bay': True}),
    ]
    cut_h_wall(Y_TOP_OUT, Y_TOP_IN, X_EXT_L_OUT, X_EXT_R_OUT, cuts_north, 'b')

    # West Exterior Wall:
    cuts_ext_w = [
        (800, 1800, 'win', {'sill': 0.9, 'head': 2.4}),       # Master bath window
        (5800, 6600, 'win', {'sill': 1.4, 'head': 2.4}),      # Master closet/high window
        (8200, 10200, 'win', {'sill': 0.9, 'head': 2.4}),     # Bed 1 window
        (11800, 13800, 'win', {'sill': 0.85, 'head': 2.4}),   # Living Room panoramic window
        (15400, 17200, 'win', {'sill': 1.0, 'head': 2.4}),    # Kitchen window
        (18500, 19300, 'win', {'sill': 1.5, 'head': 2.4}),    # Guest bath window
        (20500, 23000, 'win', {'sill': 0.75, 'head': 2.4}),   # Reception side picture window
    ]
    cut_v_wall(X_EXT_L_OUT, X_EXT_L_IN, Y_TOP_OUT, Y_REC_S, cuts_ext_w, 'b')

    # East Exterior Wall (Mirrored):
    cuts_ext_e = list(cuts_ext_w)
    cut_v_wall(X_EXT_R_IN, X_EXT_R_OUT, Y_TOP_OUT, Y_REC_S, cuts_ext_e, 'b')

    # South Exterior Walls with Panoramic Balcony Sliding Doors:
    # 4-panel black aluminum sliding patio doors (sill=0, floor-to-ceiling glass)
    cuts_front_l = [
        (1200, 3800, 'slide', None),
        (4600, 7200, 'win', {'sill': 0.6, 'head': 2.4}), # Reception front picture window
    ]
    cut_h_wall(Y_REC_N, Y_REC_S, X_EXT_L_IN, X_CTR_W, cuts_front_l, 'b')

    cuts_front_r = [
        (mirror_x(7200), mirror_x(4600), 'win', {'sill': 0.6, 'head': 2.4}),
        (mirror_x(3800), mirror_x(1200), 'slide', None),
    ]
    cut_h_wall(Y_REC_N, Y_REC_S, X_CTR_E, X_EXT_R_IN, cuts_front_r, 'b')

    # Front Terraces Balustrades (Modern low curb + glass railing in 3D):
    add_rect_wall(X_EXT_L_IN, Y_REC_S, X_EXT_L_IN + 150, Y_TERR_FRONT, 'low')
    add_rect_wall(X_EXT_L_IN, Y_TERR_FRONT - 150, X_M1_L_W, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_L_W - 150, Y_REC_S, X_M1_L_W, Y_TERR_FRONT, 'low')

    add_rect_wall(X_EXT_R_IN - 150, Y_REC_S, X_EXT_R_IN, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_R_E, Y_TERR_FRONT - 150, X_EXT_R_IN, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_R_E, Y_REC_S, X_M1_R_E + 150, Y_TERR_FRONT, 'low')

    # Central spine separating back bedrooms
    add_rect_wall(X_CTR_W, Y_TOP_IN, X_CTR_E, Y_LW_N, 'b')

    # Lightwell box
    cuts_lw_w = [(8600, 9800, 'win', {'sill': 1.1, 'head': 2.4})]
    cut_v_wall(X_LW_L_W, X_LW_L_E, Y_LW_N, Y_LW_S, cuts_lw_w, 'b')
    cuts_lw_e = [(8600, 9800, 'win', {'sill': 1.1, 'head': 2.4})]
    cut_v_wall(X_LW_R_W, X_LW_R_E, Y_LW_N, Y_LW_S, cuts_lw_e, 'b')
    add_rect_wall(X_LW_L_W, Y_LW_N, X_LW_R_E, Y_LW_N + 150, 'b')
    add_rect_wall(X_LW_L_W, Y_LW_S - 150, X_LW_R_E, Y_LW_S, 'b')

    # Staircase and Entrance Lobby
    add_rect_wall(X_ST_L_W, Y_LW_S, X_ST_L_E, Y_ST_N, 'b')
    add_rect_wall(X_ST_R_W, Y_LW_S, X_ST_R_E, Y_ST_N, 'b')

    # Entrance Corridor South Wall with Luxury Unit Entry Doors:
    cuts_st_south = [
        (6240, 7240, 'door', {
            "name": "مدخل الشقة اليسرى",
            "rect": [6240, 14650, 7240, 14850],
            "h": [6240, 14650],
            "c": [1, 0],
            "o": [0, 1],
            "len": 950,
            "entry": True
        }),
        (8560, 9560, 'door', {
            "name": "مدخل الشقة اليمنى",
            "rect": [8560, 14650, 9560, 14850],
            "h": [9560, 14650],
            "c": [-1, 0],
            "o": [0, 1],
            "len": 950,
            "entry": True
        })
    ]
    cut_h_wall(Y_ST_N, Y_ST_S, X_ST_L_W, X_ST_R_E, cuts_st_south, 'b')
    add_rect_wall(X_CTR_W, Y_ST_S, X_CTR_E, Y_REC_N, 'b')

    # -------------------------------------------------------------
    # 3. Left Interior Partitions & Doors
    # -------------------------------------------------------------
    add_rect_wall(X_M1_L_W, Y_TOP_IN, X_M1_L_E, Y_M_S, 'n')
    add_rect_wall(X_EXT_L_IN, Y_M_N, X_M1_L_W, Y_M_S, 'n')

    cuts_mbath_l = [(6000, 6750, 'door', {
        "name": "باب حمام الماستر",
        "rect": [2100, 6000, 2200, 6750],
        "h": [2200, 6000],
        "c": [0, 1],
        "o": [1, 0],
        "len": 750,
        "entry": False
    })]
    cut_v_wall(X_MBATH_DIV - 100, X_MBATH_DIV, Y_M_S, Y_MBATH_N, cuts_mbath_l, 'n')
    add_rect_wall(X_EXT_L_IN, Y_MBATH_N, X_M1_L_W, Y_MBATH_S, 'n')

    cuts_b2_door_l = [(4600, 5450, 'door', {
        "name": "باب غرفة نوم 2",
        "rect": [4600, 3750, 5500, 3900],
        "h": [4600, 3750],
        "c": [1, 0],
        "o": [0, -1],
        "len": 850,
        "entry": False
    })]
    cut_h_wall(3750, 3900, X_M1_L_E, X_CTR_W, cuts_b2_door_l, 'n')

    cuts_laund_door_l = [(4600, 5350, 'door', {
        "name": "باب الغسيل",
        "rect": [4600, 5700, 5400, 5850],
        "h": [4600, 5700],
        "c": [1, 0],
        "o": [0, 1],
        "len": 750,
        "entry": False
    })]
    cut_h_wall(Y_LAUND_N, Y_LAUND_S, X_M1_L_E, X_CTR_W, cuts_laund_door_l, 'n')
    add_rect_wall(X_M1_L_E, Y_LW_N - 150, X_LW_L_W, Y_LW_N, 'n')

    cuts_b1_door_l = [(2600, 3450, 'door', {
        "name": "باب غرفة نوم 1",
        "rect": [2600, 10850, 3500, 11000],
        "h": [3500, 10850],
        "c": [-1, 0],
        "o": [0, -1],
        "len": 850,
        "entry": False
    })]
    cut_h_wall(10850, 11000, X_EXT_L_IN, X_B1_L_W, cuts_b1_door_l, 'n')
    add_rect_wall(X_B1_L_W, Y_MBATH_S, X_B1_L_E, Y_LIV_S, 'n')

    cuts_kit_l = [(2600, 3450, 'door', {
        "name": "باب المطبخ",
        "rect": [2600, 14550, 3500, 14700],
        "h": [2600, 14700],
        "c": [1, 0],
        "o": [0, 1],
        "len": 850,
        "entry": False
    })]
    cut_h_wall(Y_LIV_N, Y_LIV_S, X_EXT_L_IN, X_B1_L_W, cuts_kit_l, 'n')

    cuts_kit_open_l = [(15000, 15900, 'door', {
        "name": "مدخل المطبخ",
        "rect": [4300, 15000, 4450, 16000],
        "h": [4300, 15000],
        "c": [0, 1],
        "o": [1, 0],
        "len": 900,
        "entry": False
    })]
    cut_v_wall(X_B1_L_W, X_B1_L_E, Y_LIV_S, Y_KIT_S, cuts_kit_open_l, 'n')
    add_rect_wall(X_EXT_L_IN, Y_KIT_N, X_B1_L_W, Y_KIT_S, 'n')

    cuts_gbath_l = [(18500, 19250, 'door', {
        "name": "باب حمام الضيوف",
        "rect": [2500, 18500, 2600, 19300],
        "h": [2600, 18500],
        "c": [0, 1],
        "o": [-1, 0],
        "len": 750,
        "entry": False
    })]
    cut_v_wall(2500, 2600, Y_KIT_S, Y_GBATH_N, cuts_gbath_l, 'n')

    cuts_rec_door_l = [(3000, 4050, 'door', {
        "name": "باب صالون الاستقبال",
        "rect": [3000, 19350, 4200, 19500],
        "h": [3000, 19350],
        "c": [1, 0],
        "o": [0, 1],
        "len": 1050,
        "entry": False
    })]
    cut_h_wall(Y_GBATH_N, Y_GBATH_S, X_EXT_L_IN, X_CTR_W, cuts_rec_door_l, 'n')

    # -------------------------------------------------------------
    # 4. Right Interior Partitions & Doors (Mirrored)
    # -------------------------------------------------------------
    add_rect_wall(X_M1_R_W, Y_TOP_IN, X_M1_R_E, Y_M_S, 'n')
    add_rect_wall(X_M1_R_E, Y_M_N, X_EXT_R_IN, Y_M_S, 'n')

    cuts_mbath_r = [(6000, 6750, 'door', {
        "name": "باب حمام الماستر",
        "rect": [13600, 6000, 13700, 6750],
        "h": [13600, 6000],
        "c": [0, 1],
        "o": [-1, 0],
        "len": 750,
        "entry": False
    })]
    cut_v_wall(X_MBATH_DIV_R, X_MBATH_DIV_R + 100, Y_M_S, Y_MBATH_N, cuts_mbath_r, 'n')
    add_rect_wall(X_M1_R_E, Y_MBATH_N, X_EXT_R_IN, Y_MBATH_S, 'n')

    cuts_b2_door_r = [(mirror_x(5450), mirror_x(4600), 'door', {
        "name": "باب غرفة نوم 2",
        "rect": [10300, 3750, 11200, 3900],
        "h": [11200, 3750],
        "c": [-1, 0],
        "o": [0, -1],
        "len": 850,
        "entry": False
    })]
    cut_h_wall(3750, 3900, X_CTR_E, X_M1_R_W, cuts_b2_door_r, 'n')

    cuts_laund_door_r = [(mirror_x(5350), mirror_x(4600), 'door', {
        "name": "باب الغسيل",
        "rect": [10400, 5700, 11200, 5850],
        "h": [11200, 5700],
        "c": [-1, 0],
        "o": [0, 1],
        "len": 750,
        "entry": False
    })]
    cut_h_wall(Y_LAUND_N, Y_LAUND_S, X_CTR_E, X_M1_R_W, cuts_laund_door_r, 'n')
    add_rect_wall(X_LW_R_E, Y_LW_N - 150, X_M1_R_W, Y_LW_N, 'n')

    cuts_b1_door_r = [(mirror_x(3450), mirror_x(2600), 'door', {
        "name": "باب غرفة نوم 1",
        "rect": [12300, 10850, 13200, 11000],
        "h": [12300, 10850],
        "c": [1, 0],
        "o": [0, -1],
        "len": 850,
        "entry": False
    })]
    cut_h_wall(10850, 11000, X_B1_R_E, X_EXT_R_IN, cuts_b1_door_r, 'n')
    add_rect_wall(X_B1_R_W, Y_MBATH_S, X_B1_R_E, Y_LIV_S, 'n')

    cuts_kit_r = [(mirror_x(3450), mirror_x(2600), 'door', {
        "name": "باب المطبخ",
        "rect": [12300, 14550, 13200, 14700],
        "h": [13200, 14700],
        "c": [-1, 0],
        "o": [0, 1],
        "len": 850,
        "entry": False
    })]
    cut_h_wall(Y_LIV_N, Y_LIV_S, X_B1_R_E, X_EXT_R_IN, cuts_kit_r, 'n')

    cuts_kit_open_r = [(15000, 15900, 'door', {
        "name": "مدخل المطبخ",
        "rect": [11350, 15000, 11500, 16000],
        "h": [11500, 15000],
        "c": [0, 1],
        "o": [-1, 0],
        "len": 900,
        "entry": False
    })]
    cut_v_wall(X_B1_R_W, X_B1_R_E, Y_LIV_S, Y_KIT_S, cuts_kit_open_r, 'n')
    add_rect_wall(X_B1_R_E, Y_KIT_N, X_EXT_R_IN, Y_KIT_S, 'n')

    cuts_gbath_r = [(18500, 19250, 'door', {
        "name": "باب حمام الضيوف",
        "rect": [13200, 18500, 13300, 19300],
        "h": [13200, 18500],
        "c": [0, 1],
        "o": [1, 0],
        "len": 750,
        "entry": False
    })]
    cut_v_wall(mirror_x(2600), mirror_x(2500), Y_KIT_S, Y_GBATH_N, cuts_gbath_r, 'n')

    cuts_rec_door_r = [(mirror_x(4050), mirror_x(3000), 'door', {
        "name": "باب صالون الاستقبال",
        "rect": [11600, 19350, 12800, 19500],
        "h": [12800, 19350],
        "c": [-1, 0],
        "o": [0, 1],
        "len": 1050,
        "entry": False
    })]
    cut_h_wall(Y_GBATH_N, Y_GBATH_S, X_CTR_E, X_EXT_R_IN, cuts_rec_door_r, 'n')

    # -------------------------------------------------------------
    # 5. Room Definitions with High-End Materials
    # -------------------------------------------------------------
    def R_inner(x0, y0, x1, y1):
        return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

    # Only show tidy 3D tags on primary rooms (at: [x,y])
    rooms = [
        # Left Unit
        {"id": "m_bed_l", "name": "جناح النوم الرئيسي", "poly": R_inner(X_EXT_L_IN, Y_TOP_IN, X_M1_L_W, Y_M_N), "mat": "wood", "at": [2000, 2400]},
        {"id": "m_bath_l", "name": "حمام ماستر", "poly": R_inner(X_EXT_L_IN, Y_M_S, X_MBATH_DIV - 100, Y_MBATH_N), "mat": "antislip", "at": None},
        {"id": "m_closet_l", "name": "ملابس", "poly": R_inner(X_MBATH_DIV, Y_M_S, X_M1_L_W, Y_MBATH_N), "mat": "walnut", "at": None},
        {"id": "bed2_l", "name": "غرفة نوم 2", "poly": R_inner(X_M1_L_E, Y_TOP_IN, X_CTR_W, Y_B2_N := 3750), "mat": "wood", "at": [6000, 1800]},
        {"id": "laund_l", "name": "غسيل", "poly": R_inner(X_M1_L_E, 3900, X_CTR_W, Y_LAUND_N), "mat": "antislip", "at": None},
        {"id": "cbath_l", "name": "حمام عائلي", "poly": R_inner(X_M1_L_E, Y_LAUND_S, X_CTR_W, Y_LW_N), "mat": "antislip", "at": [6000, 6500]},
        {"id": "bed1_l", "name": "غرفة نوم 1", "poly": R_inner(X_EXT_L_IN, Y_MBATH_S, X_B1_L_W, 10850), "mat": "wood", "at": [2000, 8900]},
        {"id": "living_l", "name": "غرفة المعيشة", "poly": R_inner(X_EXT_L_IN, 11000, X_B1_L_W, Y_LIV_N), "mat": "tile800", "at": [2100, 12800]},
        {"id": "kitchen_l", "name": "المطبخ", "poly": R_inner(X_EXT_L_IN, Y_LIV_S, X_B1_L_W, Y_KIT_N), "mat": "tile600", "at": [2100, 16300]},
        {"id": "gbath_l", "name": "حمام ضيوف", "poly": R_inner(X_EXT_L_IN, Y_KIT_S, 2500, Y_GBATH_N), "mat": "antislip", "at": None},
        {"id": "rec_l", "name": "صالون الاستقبال", "poly": R_inner(X_EXT_L_IN, Y_GBATH_S, X_CTR_W, Y_REC_N), "mat": "marble", "at": [4200, 21800]},
        {"id": "terr_l", "name": "التراس", "poly": R_inner(X_EXT_L_IN + 150, Y_REC_S, X_M1_L_W - 150, Y_TERR_FRONT - 150), "mat": "walnut", "at": [2000, 24900]},

        # Right Unit (Mirrored)
        {"id": "m_bed_r", "name": "جناح النوم الرئيسي", "poly": R_inner(X_M1_R_E, Y_TOP_IN, X_EXT_R_IN, Y_M_N), "mat": "wood", "at": [13800, 2400]},
        {"id": "m_closet_r", "name": "ملابس", "poly": R_inner(X_M1_R_E, Y_M_S, X_MBATH_DIV_R, Y_MBATH_N), "mat": "walnut", "at": None},
        {"id": "m_bath_r", "name": "حمام ماستر", "poly": R_inner(X_MBATH_DIV_R + 100, Y_M_S, X_EXT_R_IN, Y_MBATH_N), "mat": "antislip", "at": None},
        {"id": "bed2_r", "name": "غرفة نوم 2", "poly": R_inner(X_CTR_E, Y_TOP_IN, X_M1_R_W, 3750), "mat": "wood", "at": [9800, 1800]},
        {"id": "laund_r", "name": "غسيل", "poly": R_inner(X_CTR_E, 3900, X_M1_R_W, Y_LAUND_N), "mat": "antislip", "at": None},
        {"id": "cbath_r", "name": "حمام عائلي", "poly": R_inner(X_CTR_E, Y_LAUND_S, X_M1_R_W, Y_LW_N), "mat": "antislip", "at": [9800, 6500]},
        {"id": "bed1_r", "name": "غرفة نوم 1", "poly": R_inner(X_B1_R_E, Y_MBATH_S, X_EXT_R_IN, 10850), "mat": "wood", "at": [13800, 8900]},
        {"id": "living_r", "name": "غرفة المعيشة", "poly": R_inner(X_B1_R_E, 11000, X_EXT_R_IN, Y_LIV_N), "mat": "tile800", "at": [13700, 12800]},
        {"id": "kitchen_r", "name": "المطبخ", "poly": R_inner(X_B1_R_E, Y_LIV_S, X_EXT_R_IN, Y_KIT_N), "mat": "tile600", "at": [13700, 16300]},
        {"id": "gbath_r", "name": "حمام ضيوف", "poly": R_inner(mirror_x(2500), Y_KIT_S, X_EXT_R_IN, Y_GBATH_N), "mat": "antislip", "at": None},
        {"id": "rec_r", "name": "صالون الاستقبال", "poly": R_inner(X_CTR_E, Y_GBATH_S, X_EXT_R_IN, Y_REC_N), "mat": "marble", "at": [11600, 21800]},
        {"id": "terr_r", "name": "التراس", "poly": R_inner(X_M1_R_E + 150, Y_REC_S, X_EXT_R_IN - 150, Y_TERR_FRONT - 150), "mat": "walnut", "at": [13800, 24900]},

        # Core
        {"id": "lightwell", "name": "منور", "poly": R_inner(X_LW_L_E, Y_LW_S, X_LW_R_W, 10850), "mat": "antislip", "at": None},
        {"id": "stairs_core", "name": "الدرج والمصعد", "poly": R_inner(X_ST_L_E, 11000, X_ST_R_W, Y_ST_N), "mat": "marble", "at": [X_CTR_MID, 13700]},
    ]

    # -------------------------------------------------------------
    # 6. Complete Interior Design Furniture Package (Both Units)
    # -------------------------------------------------------------
    furniture = [
        # ================= LEFT UNIT =================
        # Master Bedroom
        ("bed", "سرير كينج 1.8m", 2100, 2400, 1800, 2000, 0, "#b8c9d9"),
        ("nightstand", "كومودينو أيسر", 950, 1500, 450, 400, 0, "#e8dfd3"),
        ("nightstand", "كومودينو أيمن", 3250, 1500, 450, 400, 0, "#e8dfd3"),
        ("wardrobe", "دولاب ملابس كبير", 3100, 5900, 2000, 600, 0, "#e2cfb4"),
        ("dresser", "تسريحة ماستر ومرآة", 1000, 4300, 1100, 450, 90, "#efe6d8"),
        ("baycushion", "جلسة شباك بانوراما", 2200, 250, 1800, 520, 0, "#d8c7dc"),

        # Master Bath
        ("vanity", "مغسلة ديكور رخام", 1050, 5500, 900, 520, 0, "#ffffff"),
        ("toilet", "مرحاض معلق مودرن", 1050, 6400, 400, 680, 0, "#ffffff"),
        ("shower", "شاور زجاجي فاخر", 1750, 6400, 900, 900, 0, "#ffffff"),

        # Bedroom 2
        ("bed", "سرير كوين 1.5m", 6000, 2000, 1500, 2000, 0, "#c4d1c9"),
        ("nightstand", "كومودينو", 5050, 1300, 450, 400, 0, "#e8dfd3"),
        ("desk", "مكتب دراسة", 7200, 2600, 1200, 600, 270, "#e2cfb4"),
        ("chair", "كرسي مكتب مريح", 6650, 2600, 450, 480, 90, "#3d3a34"),
        ("wardrobe", "دولاب ملابس", 7200, 1200, 1200, 550, 270, "#efe6d8"),

        # Bedroom 1
        ("bed", "سرير كوين 1.5m", 2100, 8900, 1500, 2000, 0, "#e2d1c3"),
        ("nightstand", "كومودينو", 1000, 8200, 450, 400, 0, "#e8dfd3"),
        ("desk", "مكتب دراسة", 3800, 9900, 1200, 600, 180, "#e2cfb4"),
        ("chair", "كرسي مكتب", 3800, 9400, 450, 480, 0, "#3d3a34"),
        ("wardrobe", "دولاب ملابس", 1100, 10200, 1400, 550, 0, "#efe6d8"),

        # Family Bath
        ("vanity", "مغسلة عائلية", 6000, 6150, 900, 520, 180, "#ffffff"),
        ("toilet", "مرحاض", 7100, 6600, 400, 680, 270, "#ffffff"),
        ("shower", "شاور", 6000, 6900, 900, 900, 180, "#ffffff"),

        # Living Room
        ("cornersofa", "كنبة زاوية عائلية مودرن", 2100, 12500, 2800, 1700, 0, "#9bb0a5"),
        ("coffeetable", "طاولة قهوة رخام", 2300, 13400, 1300, 650, 0, "#e8dccb"),
        ("rug", "سجادة صالون مودرن", 2400, 13100, 2400, 1700, 0, "#dfd9d0"),
        ("tvstand", "وحدة تلفزيون جدارية", 4000, 12600, 2400, 400, 180, "#4a3c31"),
        ("tv", "شاشة تلفزيون 65 بوصة", 4000, 12600, 1450, 80, 180, "#111111"),
        ("floorlamp", "مصباح أرضي مودرن", 800, 11500, 450, 450, 0, "#222222"),
        ("plant", "نبات زينة داخلي", 3900, 11500, 500, 500, 0, "#7fa377"),

        # Kitchen
        ("counter", "كاونتر مطبخ رخام", 800, 16300, 1600, 600, 0, "#ffffff"),
        ("ksink", "حوض غسيل ستانلس", 2400, 15100, 800, 450, 0, "#cccccc"),
        ("stove", "بوتاجاز غاز مسطح", 3400, 15100, 750, 450, 0, "#333333"),
        ("fridge", "ثلاجة دولابي", 3900, 16300, 910, 700, 270, "#a0a5aa"),

        # Guest Bath
        ("vanity", "مغسلة ضيوف", 1100, 18300, 700, 450, 0, "#ffffff"),
        ("toilet", "مرحاض ضيوف", 1900, 18300, 400, 680, 0, "#ffffff"),

        # Reception Salon (Luxury Majlis)
        ("sofa", "طقم استقبال فاخر 3 مقاعد", 1800, 21500, 2400, 900, 90, "#6e7f78"),
        ("sofa", "طقم استقبال ثنائي", 5800, 21500, 1800, 900, 270, "#6e7f78"),
        ("armchair", "كرسي فوتيه مذهب", 3800, 20200, 850, 850, 0, "#d4af37"),
        ("armchair", "كرسي فوتيه مذهب", 3800, 22800, 850, 850, 180, "#d4af37"),
        ("coffeetable", "طاولة رخام كالاتا", 3800, 21500, 1400, 750, 0, "#fcfbf9"),
        ("rug", "سجادة استقبال فاخرة", 3800, 21500, 2800, 2000, 0, "#d8cfc4"),
        ("plant", "نبات فيكس ديكور", 7200, 20200, 700, 700, 0, "#5b8a54"),
        ("table", "طاولة طعام 6 كراسي", 6600, 23000, 1800, 900, 90, "#5c4033"),

        # Left Terrace
        ("coffeetable", "طاولة شرفة خارجية", 2000, 24900, 900, 600, 0, "#444444"),
        ("armchair", "كرسي استرخاء خارجي", 1000, 24900, 750, 750, 90, "#888888"),
        ("armchair", "كرسي استرخاء خارجي", 3000, 24900, 750, 750, 270, "#888888"),
        ("plant", "أحواض نباتات شرفة", 500, 25200, 500, 500, 0, "#4f8045"),

        # ================= RIGHT UNIT (Mirrored) =================
        # Master Bedroom
        ("bed", "سرير كينج 1.8m", mirror_x(2100), 2400, 1800, 2000, 0, "#b8c9d9"),
        ("nightstand", "كومودينو أيمن", mirror_x(950), 1500, 450, 400, 0, "#e8dfd3"),
        ("nightstand", "كومودينو أيسر", mirror_x(3250), 1500, 450, 400, 0, "#e8dfd3"),
        ("wardrobe", "دولاب ملابس كبير", mirror_x(3100), 5900, 2000, 600, 0, "#e2cfb4"),
        ("dresser", "تسريحة ماستر ومرآة", mirror_x(1000), 4300, 1100, 450, 270, "#efe6d8"),
        ("baycushion", "جلسة شباك بانوراما", mirror_x(2200), 250, 1800, 520, 0, "#d8c7dc"),

        # Master Bath
        ("vanity", "مغسلة ديكور رخام", mirror_x(1050), 5500, 900, 520, 0, "#ffffff"),
        ("toilet", "مرحاض معلق مودرن", mirror_x(1050), 6400, 400, 680, 0, "#ffffff"),
        ("shower", "شاور زجاجي فاخر", mirror_x(1750), 6400, 900, 900, 0, "#ffffff"),

        # Bedroom 2
        ("bed", "سرير كوين 1.5m", mirror_x(6000), 2000, 1500, 2000, 0, "#c4d1c9"),
        ("nightstand", "كومودينو", mirror_x(5050), 1300, 450, 400, 0, "#e8dfd3"),
        ("desk", "مكتب دراسة", mirror_x(7200), 2600, 1200, 600, 90, "#e2cfb4"),
        ("chair", "كرسي مكتب مريح", mirror_x(6650), 2600, 450, 480, 270, "#3d3a34"),
        ("wardrobe", "دولاب ملابس", mirror_x(7200), 1200, 1200, 550, 90, "#efe6d8"),

        # Bedroom 1
        ("bed", "سرير كوين 1.5m", mirror_x(2100), 8900, 1500, 2000, 0, "#e2d1c3"),
        ("nightstand", "كومودينو", mirror_x(1000), 8200, 450, 400, 0, "#e8dfd3"),
        ("desk", "مكتب دراسة", mirror_x(3800), 9900, 1200, 600, 180, "#e2cfb4"),
        ("chair", "كرسي مكتب", mirror_x(3800), 9400, 450, 480, 0, "#3d3a34"),
        ("wardrobe", "دولاب ملابس", mirror_x(1100), 10200, 1400, 550, 0, "#efe6d8"),

        # Family Bath
        ("vanity", "مغسلة عائلية", mirror_x(6000), 6150, 900, 520, 180, "#ffffff"),
        ("toilet", "مرحاض", mirror_x(7100), 6600, 400, 680, 90, "#ffffff"),
        ("shower", "شاور", mirror_x(6000), 6900, 900, 900, 180, "#ffffff"),

        # Living Room
        ("cornersofa", "كنبة زاوية عائلية مودرن", mirror_x(2100), 12500, 2800, 1700, 0, "#9bb0a5"),
        ("coffeetable", "طاولة قهوة رخام", mirror_x(2300), 13400, 1300, 650, 0, "#e8dccb"),
        ("rug", "سجادة صالون مودرن", mirror_x(2400), 13100, 2400, 1700, 0, "#dfd9d0"),
        ("tvstand", "وحدة تلفزيون جدارية", mirror_x(4000), 12600, 2400, 400, 180, "#4a3c31"),
        ("tv", "شاشة تلفزيون 65 بوصة", mirror_x(4000), 12600, 1450, 80, 180, "#111111"),
        ("floorlamp", "مصباح أرضي مودرن", mirror_x(800), 11500, 450, 450, 0, "#222222"),
        ("plant", "نبات زينة داخلي", mirror_x(3900), 11500, 500, 500, 0, "#7fa377"),

        # Kitchen
        ("counter", "كاونتر مطبخ رخام", mirror_x(800), 16300, 1600, 600, 180, "#ffffff"),
        ("ksink", "حوض غسيل ستانلس", mirror_x(2400), 15100, 800, 450, 0, "#cccccc"),
        ("stove", "بوتاجاز غاز مسطح", mirror_x(3400), 15100, 750, 450, 0, "#333333"),
        ("fridge", "ثلاجة دولابي", mirror_x(3900), 16300, 910, 700, 90, "#a0a5aa"),

        # Guest Bath
        ("vanity", "مغسلة ضيوف", mirror_x(1100), 18300, 700, 450, 0, "#ffffff"),
        ("toilet", "مرحاض ضيوف", mirror_x(1900), 18300, 400, 680, 0, "#ffffff"),

        # Reception Salon (Luxury Majlis)
        ("sofa", "طقم استقبال فاخر 3 مقاعد", mirror_x(1800), 21500, 2400, 900, 270, "#6e7f78"),
        ("sofa", "طقم استقبال ثنائي", mirror_x(5800), 21500, 1800, 900, 90, "#6e7f78"),
        ("armchair", "كرسي فوتيه مذهب", mirror_x(3800), 20200, 850, 850, 0, "#d4af37"),
        ("armchair", "كرسي فوتيه مذهب", mirror_x(3800), 22800, 850, 850, 180, "#d4af37"),
        ("coffeetable", "طاولة رخام كالاتا", mirror_x(3800), 21500, 1400, 750, 0, "#fcfbf9"),
        ("rug", "سجادة استقبال فاخرة", mirror_x(3800), 21500, 2800, 2000, 0, "#d8cfc4"),
        ("plant", "نبات فيكس ديكور", mirror_x(7200), 20200, 700, 700, 0, "#5b8a54"),
        ("table", "طاولة طعام 6 كراسي", mirror_x(6600), 23000, 1800, 900, 90, "#5c4033"),

        # Right Terrace
        ("coffeetable", "طاولة شرفة خارجية", mirror_x(2000), 24900, 900, 600, 0, "#444444"),
        ("armchair", "كرسي استرخاء خارجي", mirror_x(1000), 24900, 750, 750, 270, "#888888"),
        ("armchair", "كرسي استرخاء خارجي", mirror_x(3000), 24900, 750, 750, 90, "#888888"),
        ("plant", "أحواض نباتات شرفة", mirror_x(500), 25200, 500, 500, 0, "#4f8045"),
    ]

    return walls, wins, doors, slides, rooms, furniture

print("Python module loaded successfully.")
