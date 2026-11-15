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
    X_EXT_R_IN  = 15800
    X_EXT_R_OUT = 16000

    # Y Grid (mm):
    Y_TOP_OUT   = -200
    Y_TOP_IN    = 0
    Y_B2_N      = 3750
    Y_B2_S      = 3900
    Y_M_N       = 4950
    Y_M_S       = 5100
    Y_LAUND_N   = 5700
    Y_LAUND_S   = 5850
    Y_MBATH_N   = 6800
    Y_MBATH_S   = 6950
    Y_LW_N      = 7150
    Y_LW_S      = 7350
    Y_B1_N      = 10850
    Y_B1_S      = 11000
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
                wins.append([cx0, y0, cx1, y1])
            elif ctype == 'door':
                doors.append({'name': cdata['name'], 'rect': [cx0, y0, cx1, y1], 'h': cdata['h'], 'c': cdata['c'], 'o': cdata['o'], 'len': cdata['len'], 'entry': cdata.get('entry', False)})
            elif ctype == 'slide':
                slides.append({'rect': [cx0, y0, cx1, y1], 'v': False})
            curr = max(curr, cx1)
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
                wins.append([x0, cy0, x1, cy1])
            elif ctype == 'door':
                doors.append({'name': cdata['name'], 'rect': [x0, cy0, x1, cy1], 'h': cdata['h'], 'c': cdata['c'], 'o': cdata['o'], 'len': cdata['len'], 'entry': cdata.get('entry', False)})
            elif ctype == 'slide':
                slides.append({'rect': [x0, cy0, x1, cy1], 'v': True})
            curr = max(curr, cy1)
        if curr < y_end:
            add_rect_wall(x0, curr, x1, y_end, wtype)

    # -------------------------------------------------------------
    # 2. Exterior Envelope and Main Partitions
    # -------------------------------------------------------------
    # North Exterior Wall
    cuts_top_l = [(1500, 3100, 'win', None), (5300, 6900, 'win', None)]
    cut_h_wall(Y_TOP_OUT, Y_TOP_IN, X_EXT_L_OUT, X_CTR_MID, cuts_top_l, 'b')
    cuts_top_r = [(mirror_x(6900), mirror_x(5300), 'win', None), (mirror_x(3100), mirror_x(1500), 'win', None)]
    cut_h_wall(Y_TOP_OUT, Y_TOP_IN, X_CTR_MID, X_EXT_R_OUT, cuts_top_r, 'b')

    # West Exterior Wall
    cuts_ext_w = [
        (800, 1600, 'win', None),
        (5800, 6600, 'win', None),
        (8200, 9800, 'win', None),
        (12000, 13600, 'win', None),
        (15600, 17200, 'win', None),
        (18500, 19300, 'win', None),
        (20500, 22500, 'win', None),
    ]
    cut_v_wall(X_EXT_L_OUT, X_EXT_L_IN, Y_TOP_OUT, Y_REC_S, cuts_ext_w, 'b')

    # East Exterior Wall (Mirrored)
    cuts_ext_e = list(cuts_ext_w)
    cut_v_wall(X_EXT_R_IN, X_EXT_R_OUT, Y_TOP_OUT, Y_REC_S, cuts_ext_e, 'b')

    # South Exterior Walls with Balcony Sliding Doors
    cuts_front_l = [(1500, 3700, 'slide', None)]
    cut_h_wall(Y_REC_N, Y_REC_S, X_EXT_L_IN, X_M1_L_W, cuts_front_l, 'b')
    add_rect_wall(X_M1_L_W, Y_REC_N, X_CTR_W, Y_REC_S, 'b')
    cuts_front_r = [(mirror_x(3700), mirror_x(1500), 'slide', None)]
    cut_h_wall(Y_REC_N, Y_REC_S, X_M1_R_E, X_EXT_R_IN, cuts_front_r, 'b')
    add_rect_wall(X_CTR_E, Y_REC_N, X_M1_R_E, Y_REC_S, 'b')

    # Front Terraces Balustrades
    add_rect_wall(X_EXT_L_IN, Y_REC_S, X_EXT_L_IN + 150, Y_TERR_FRONT, 'low')
    add_rect_wall(X_EXT_L_IN, Y_TERR_FRONT - 150, X_M1_L_W, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_L_W - 150, Y_REC_S, X_M1_L_W, Y_TERR_FRONT, 'low')
    add_rect_wall(X_EXT_R_IN - 150, Y_REC_S, X_EXT_R_IN, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_R_E, Y_TERR_FRONT - 150, X_EXT_R_IN, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_R_E, Y_REC_S, X_M1_R_E + 150, Y_TERR_FRONT, 'low')

    # Central spine separating back bedrooms
    add_rect_wall(X_CTR_W, Y_TOP_IN, X_CTR_E, Y_LW_N, 'b')

    # Lightwell box
    add_rect_wall(X_LW_L_W, Y_LW_N, X_LW_R_E, Y_LW_S, 'b')
    lw_w_cuts = [(8600, 9800, 'win', None)]
    cut_v_wall(X_LW_L_W, X_LW_L_E, Y_LW_S, Y_B1_S, lw_w_cuts, 'b')
    lw_e_cuts = [(8600, 9800, 'win', None)]
    cut_v_wall(X_LW_R_W, X_LW_R_E, Y_LW_S, Y_B1_S, lw_e_cuts, 'b')
    add_rect_wall(X_LW_L_W, Y_B1_N, X_LW_R_E, Y_B1_S, 'b')

    # Staircase Core
    add_rect_wall(X_ST_L_W, Y_B1_S, X_ST_L_E, Y_ST_S, 'b')
    add_rect_wall(X_ST_R_W, Y_B1_S, X_ST_R_E, Y_ST_S, 'b')
    st_south_cuts = [
        (X_ST_L_E + 200, X_ST_L_E + 1200, 'door', {
            'name': 'مدخل الشقة اليسرى (Left Unit Entrance)',
            'h': [X_ST_L_E + 200, Y_ST_N], 'c': [1, 0], 'o': [0, 1], 'len': 950, 'entry': True
        }),
        (X_ST_R_W - 1200, X_ST_R_W - 200, 'door', {
            'name': 'مدخل الشقة اليمنى (Right Unit Entrance)',
            'h': [X_ST_R_W - 200, Y_ST_N], 'c': [-1, 0], 'o': [0, 1], 'len': 950, 'entry': True
        }),
    ]
    cut_h_wall(Y_ST_N, Y_ST_S, X_ST_L_W, X_ST_R_E, st_south_cuts, 'b')
    add_rect_wall(X_CTR_W, Y_ST_S, X_CTR_E, Y_REC_N, 'b')

    # Left Interior Partitions
    add_rect_wall(X_M1_L_W, Y_TOP_IN, X_M1_L_E, Y_M_S, 'n')
    add_rect_wall(X_EXT_L_IN, Y_M_N, X_M1_L_E, Y_M_S, 'n')
    b2_cuts_l = [(4600, 5500, 'door', {'name': 'باب غرفة نوم 2 (Left)', 'h': [4600, Y_B2_N], 'c': [1, 0], 'o': [0, -1], 'len': 850})]
    cut_h_wall(Y_B2_N, Y_B2_S, X_M1_L_E, X_CTR_W, b2_cuts_l, 'n')
    laund_cuts_l = [(4600, 5400, 'door', {'name': 'باب الغسيل (Left)', 'h': [4600, Y_LAUND_N], 'c': [1, 0], 'o': [0, 1], 'len': 750})]
    cut_h_wall(Y_LAUND_N, Y_LAUND_S, X_M1_L_E, X_CTR_W, laund_cuts_l, 'n')
    mbath_div_cuts = [(6000, 6750, 'door', {'name': 'باب حمام الماستر (Left)', 'h': [X_MBATH_DIV, 6000], 'c': [0, 1], 'o': [1, 0], 'len': 750})]
    cut_v_wall(X_MBATH_DIV - 100, X_MBATH_DIV, Y_M_S, Y_MBATH_N, mbath_div_cuts, 'n')
    add_rect_wall(X_EXT_L_IN, Y_MBATH_N, X_M1_L_E, Y_MBATH_S, 'n')
    b1_cuts_l = [(2600, 3500, 'door', {'name': 'باب غرفة نوم 1 (Left)', 'h': [3500, Y_B1_N], 'c': [-1, 0], 'o': [0, -1], 'len': 850})]
    cut_h_wall(Y_B1_N, Y_B1_S, X_EXT_L_IN, X_B1_L_E, b1_cuts_l, 'n')
    add_rect_wall(X_B1_L_W, Y_MBATH_S, X_B1_L_E, Y_B1_S, 'n')
    kit_n_cuts = [(2600, 3500, 'door', {'name': 'باب المطبخ (Left)', 'h': [2600, Y_LIV_S], 'c': [1, 0], 'o': [0, 1], 'len': 850})]
    cut_h_wall(Y_LIV_N, Y_LIV_S, X_EXT_L_IN, X_B1_L_E, kit_n_cuts, 'n')
    kit_e_cuts = [(15000, 16000, 'door', {'name': 'فتحة المطبخ (Left)', 'h': [X_B1_L_W, 15000], 'c': [0, 1], 'o': [1, 0], 'len': 900})]
    cut_v_wall(X_B1_L_W, X_B1_L_E, Y_LIV_S, Y_KIT_S, kit_e_cuts, 'n')
    add_rect_wall(X_EXT_L_IN, Y_KIT_N, X_B1_L_W, Y_KIT_S, 'n')
    gbath_div_cuts = [(18500, 19300, 'door', {'name': 'باب حمام الضيوف (Left)', 'h': [2600, 18500], 'c': [0, 1], 'o': [-1, 0], 'len': 750})]
    cut_v_wall(2500, 2600, Y_KIT_S, Y_GBATH_N, gbath_div_cuts, 'n')
    rec_entry_cuts_l = [(3000, 4200, 'door', {'name': 'باب صالون الاستقبال (Left)', 'h': [3000, Y_GBATH_N], 'c': [1, 0], 'o': [0, 1], 'len': 1050})]
    cut_h_wall(Y_GBATH_N, Y_GBATH_S, X_EXT_L_IN, X_B1_L_E, rec_entry_cuts_l, 'n')
    add_rect_wall(X_B1_L_W, Y_KIT_S, X_B1_L_E, Y_GBATH_S, 'n')

    # Right Interior Partitions (Mirrored)
    add_rect_wall(X_M1_R_W, Y_TOP_IN, X_M1_R_E, Y_M_S, 'n')
    add_rect_wall(X_M1_R_W, Y_M_N, X_EXT_R_IN, Y_M_S, 'n')
    b2_cuts_r = [(mirror_x(5500), mirror_x(4600), 'door', {'name': 'باب غرفة نوم 2 (Right)', 'h': [mirror_x(4600), Y_B2_N], 'c': [-1, 0], 'o': [0, -1], 'len': 850})]
    cut_h_wall(Y_B2_N, Y_B2_S, X_CTR_E, X_M1_R_W, b2_cuts_r, 'n')
    laund_cuts_r = [(mirror_x(5400), mirror_x(4600), 'door', {'name': 'باب الغسيل (Right)', 'h': [mirror_x(4600), Y_LAUND_N], 'c': [-1, 0], 'o': [0, 1], 'len': 750})]
    cut_h_wall(Y_LAUND_N, Y_LAUND_S, X_CTR_E, X_M1_R_W, laund_cuts_r, 'n')
    mbath_div_cuts_r = [(6000, 6750, 'door', {'name': 'باب حمام الماستر (Right)', 'h': [X_MBATH_DIV_R, 6000], 'c': [0, 1], 'o': [-1, 0], 'len': 750})]
    cut_v_wall(X_MBATH_DIV_R, X_MBATH_DIV_R + 100, Y_M_S, Y_MBATH_N, mbath_div_cuts_r, 'n')
    add_rect_wall(X_M1_R_W, Y_MBATH_N, X_EXT_R_IN, Y_MBATH_S, 'n')
    b1_cuts_r = [(mirror_x(3500), mirror_x(2600), 'door', {'name': 'باب غرفة نوم 1 (Right)', 'h': [mirror_x(3500), Y_B1_N], 'c': [1, 0], 'o': [0, -1], 'len': 850})]
    cut_h_wall(Y_B1_N, Y_B1_S, X_B1_R_W, X_EXT_R_IN, b1_cuts_r, 'n')
    add_rect_wall(X_B1_R_W, Y_MBATH_S, X_B1_R_E, Y_B1_S, 'n')
    kit_n_cuts_r = [(mirror_x(3500), mirror_x(2600), 'door', {'name': 'باب المطبخ (Right)', 'h': [mirror_x(2600), Y_LIV_S], 'c': [-1, 0], 'o': [0, 1], 'len': 850})]
    cut_h_wall(Y_LIV_N, Y_LIV_S, X_B1_R_W, X_EXT_R_IN, kit_n_cuts_r, 'n')
    kit_e_cuts_r = [(15000, 16000, 'door', {'name': 'فتحة المطبخ (Right)', 'h': [X_B1_R_E, 15000], 'c': [0, 1], 'o': [-1, 0], 'len': 900})]
    cut_v_wall(X_B1_R_W, X_B1_R_E, Y_LIV_S, Y_KIT_S, kit_e_cuts_r, 'n')
    add_rect_wall(X_B1_R_E, Y_KIT_N, X_EXT_R_IN, Y_KIT_S, 'n')
    gbath_div_cuts_r = [(18500, 19300, 'door', {'name': 'باب حمام الضيوف (Right)', 'h': [mirror_x(2600), 18500], 'c': [0, 1], 'o': [1, 0], 'len': 750})]
    cut_v_wall(mirror_x(2600), mirror_x(2500), Y_KIT_S, Y_GBATH_N, gbath_div_cuts_r, 'n')
    rec_entry_cuts_r = [(mirror_x(4200), mirror_x(3000), 'door', {'name': 'باب صالون الاستقبال (Right)', 'h': [mirror_x(3000), Y_GBATH_N], 'c': [-1, 0], 'o': [0, 1], 'len': 1050})]
    cut_h_wall(Y_GBATH_N, Y_GBATH_S, X_B1_R_W, X_EXT_R_IN, rec_entry_cuts_r, 'n')
    add_rect_wall(X_B1_R_W, Y_KIT_S, X_B1_R_E, Y_GBATH_S, 'n')

    def R_inner(x0, y0, x1, y1):
        return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

    rooms = [
        {"id": "m_bed_l", "name": "نوم رئيسية (Master L)", "poly": R_inner(X_EXT_L_IN, Y_TOP_IN, X_M1_L_W, Y_M_N), "mat": "wood", "at": [2000, 2400]},
        {"id": "m_bath_l", "name": "حمام ماستر (Bath L)", "poly": R_inner(X_EXT_L_IN, Y_M_S, X_MBATH_DIV - 100, Y_MBATH_N), "mat": "antislip", "at": [1000, 5900]},
        {"id": "m_closet_l", "name": "ملابس (Closet L)", "poly": R_inner(X_MBATH_DIV, Y_M_S, X_M1_L_W, Y_MBATH_N), "mat": "walnut", "at": [3100, 5900]},
        {"id": "bed2_l", "name": "نوم 2 (Bed 2 L)", "poly": R_inner(X_M1_L_E, Y_TOP_IN, X_CTR_W, Y_B2_N), "mat": "wood", "at": [5900, 1900]},
        {"id": "laund_l", "name": "غسيل (Laundry L)", "poly": R_inner(X_M1_L_E, Y_B2_S, X_CTR_W, Y_LAUND_N), "mat": "antislip", "at": [5900, 4800]},
        {"id": "cbath_l", "name": "حمام عائلي (Bath L)", "poly": R_inner(X_M1_L_E, Y_LAUND_S, X_CTR_W, Y_LW_N), "mat": "antislip", "at": [5900, 6500]},
        {"id": "bed1_l", "name": "نوم 1 (Bed 1 L)", "poly": R_inner(X_EXT_L_IN, Y_MBATH_S, X_B1_L_W, Y_B1_N), "mat": "wood", "at": [2100, 8900]},
        {"id": "living_l", "name": "معيشة (Living L)", "poly": R_inner(X_EXT_L_IN, Y_B1_S, X_B1_L_W, Y_LIV_N), "mat": "tile800", "at": [2100, 12700]},
        {"id": "kitchen_l", "name": "مطبخ (Kitchen L)", "poly": R_inner(X_EXT_L_IN, Y_LIV_S, X_B1_L_W, Y_KIT_N), "mat": "tile600", "at": [2100, 16300]},
        {"id": "gbath_l", "name": "حمام ضيوف (Guest Bath L)", "poly": R_inner(X_EXT_L_IN, Y_KIT_S, 2500, Y_GBATH_N), "mat": "antislip", "at": [1200, 18600]},
        {"id": "rec_l", "name": "استقبال (Reception L)", "poly": R_inner(X_EXT_L_IN, Y_GBATH_S, X_CTR_W, Y_REC_N), "mat": "marble", "at": [3900, 21800]},
        {"id": "terr_l", "name": "تراس (Terrace L)", "poly": R_inner(X_EXT_L_IN + 150, Y_REC_S, X_M1_L_W - 150, Y_TERR_FRONT - 150), "mat": "walnut", "at": [2100, 24900]},

        # Right Unit (Mirrored)
        {"id": "m_bed_r", "name": "نوم رئيسية (Master R)", "poly": R_inner(X_M1_R_E, Y_TOP_IN, X_EXT_R_IN, Y_M_N), "mat": "wood", "at": [13800, 2400]},
        {"id": "m_closet_r", "name": "ملابس (Closet R)", "poly": R_inner(X_M1_R_E, Y_M_S, X_MBATH_DIV_R, Y_MBATH_N), "mat": "walnut", "at": [12700, 5900]},
        {"id": "m_bath_r", "name": "حمام ماستر (Bath R)", "poly": R_inner(X_MBATH_DIV_R + 100, Y_M_S, X_EXT_R_IN, Y_MBATH_N), "mat": "antislip", "at": [14800, 5900]},
        {"id": "bed2_r", "name": "نوم 2 (Bed 2 R)", "poly": R_inner(X_CTR_E, Y_TOP_IN, X_M1_R_W, Y_B2_N), "mat": "wood", "at": [9900, 1900]},
        {"id": "laund_r", "name": "غسيل (Laundry R)", "poly": R_inner(X_CTR_E, Y_B2_S, X_M1_R_W, Y_LAUND_N), "mat": "antislip", "at": [9900, 4800]},
        {"id": "cbath_r", "name": "حمام عائلي (Bath R)", "poly": R_inner(X_CTR_E, Y_LAUND_S, X_M1_R_W, Y_LW_N), "mat": "antislip", "at": [9900, 6500]},
        {"id": "bed1_r", "name": "نوم 1 (Bed 1 R)", "poly": R_inner(X_B1_R_E, Y_MBATH_S, X_EXT_R_IN, Y_B1_N), "mat": "wood", "at": [13700, 8900]},
        {"id": "living_r", "name": "معيشة (Living R)", "poly": R_inner(X_B1_R_E, Y_B1_S, X_EXT_R_IN, Y_LIV_N), "mat": "tile800", "at": [13700, 12700]},
        {"id": "kitchen_r", "name": "مطبخ (Kitchen R)", "poly": R_inner(X_B1_R_E, Y_LIV_S, X_EXT_R_IN, Y_KIT_N), "mat": "tile600", "at": [13700, 16300]},
        {"id": "gbath_r", "name": "حمام ضيوف (Guest Bath R)", "poly": R_inner(mirror_x(2500), Y_KIT_S, X_EXT_R_IN, Y_GBATH_N), "mat": "antislip", "at": [14600, 18600]},
        {"id": "rec_r", "name": "استقبال (Reception R)", "poly": R_inner(X_CTR_E, Y_GBATH_S, X_EXT_R_IN, Y_REC_N), "mat": "marble", "at": [11900, 21800]},
        {"id": "terr_r", "name": "تراس (Terrace R)", "poly": R_inner(X_M1_R_E + 150, Y_REC_S, X_EXT_R_IN - 150, Y_TERR_FRONT - 150), "mat": "walnut", "at": [13700, 24900]},

        # Core
        {"id": "lightwell", "name": "منور (Lightwell)", "poly": R_inner(X_LW_L_E, Y_LW_S, X_LW_R_W, Y_B1_N), "mat": "antislip", "at": [X_CTR_MID, 9100]},
        {"id": "stairs_core", "name": "درج ومصعد (Stairs & Elevator)", "poly": R_inner(X_ST_L_E, Y_B1_S, X_ST_R_W, Y_ST_N), "mat": "marble", "at": [X_CTR_MID, 14000]},
    ]

    furniture = [
        # Left Master Bed
        ("bed", "سرير ماستر 1.8m", 2100, 2400, 1800, 2000, 0, "#c9d6df"),
        ("nightstand", "كومودينو", 1000, 1700, 450, 400, 0, None),
        ("nightstand", "كومودينو", 3200, 1700, 450, 400, 0, None),
        ("wardrobe", "دولاب ملابس", 3100, 5900, 2000, 600, 0, None),

        # Left Bedroom 2
        ("bed", "سرير 1.5m", 5900, 1900, 1500, 2000, 0, "#d8c7dc"),
        ("nightstand", "كومودينو", 5000, 1200, 450, 400, 0, None),
        ("desk", "مكتب دراسة", 7100, 2800, 1200, 600, 270, None),
        ("chair", "كرسي", 6600, 2800, 450, 480, 90, None),

        # Left Bedroom 1
        ("bed", "سرير 1.5m", 2100, 8900, 1500, 2000, 0, "#e8d5b5"),
        ("desk", "مكتب دراسة", 3900, 10100, 1200, 600, 180, None),

        # Left Living Room
        ("cornersofa", "كنبة زاوية عائلية", 2000, 12600, 2800, 1700, 0, "#b7c4b0"),
        ("coffeetable", "طاولة قهوة", 2200, 13500, 1300, 650, 0, None),
        ("tvstand", "وحدة تلفزيون", 4000, 12700, 2400, 400, 180, None),
        ("tv", "شاشة تلفزيون 65 بوصة", 4000, 12700, 1450, 80, 180, None),

        # Left Kitchen
        ("counter", "رخام مطبخ كاونتر", 700, 16300, 1600, 600, 0, None),
        ("stove", "بوتاجاز غاز", 1900, 15100, 750, 450, 0, None),
        ("ksink", "حوض غسيل", 2900, 15100, 800, 450, 0, None),
        ("fridge", "ثلاجة عائلية", 3900, 15500, 910, 700, 270, None),

        # Left Reception
        ("sofa", "طقم استقبال 3 مقاعد", 2000, 21400, 2400, 900, 90, "#b7c4b0"),
        ("sofa", "طقم استقبال 3 مقاعد", 5800, 21400, 2400, 900, 270, "#b7c4b0"),
        ("coffeetable", "طاولة رخام", 3900, 21400, 1400, 700, 0, None),
        ("rug", "سجادة صالون فاخرة", 3900, 21400, 3000, 2000, 0, None),

        # Right Master Bed
        ("bed", "سرير ماستر 1.8m", 13700, 2400, 1800, 2000, 0, "#c9d6df"),
        ("nightstand", "كومودينو", 12600, 1700, 450, 400, 0, None),
        ("nightstand", "كومودينو", 14800, 1700, 450, 400, 0, None),
        ("wardrobe", "دولاب ملابس", 12700, 5900, 2000, 600, 0, None),

        # Right Bedroom 2
        ("bed", "سرير 1.5m", 9900, 1900, 1500, 2000, 0, "#d8c7dc"),
        ("desk", "مكتب دراسة", 8700, 2800, 1200, 600, 90, None),

        # Right Bedroom 1
        ("bed", "سرير 1.5m", 13700, 8900, 1500, 2000, 0, "#e8d5b5"),

        # Right Living Room
        ("cornersofa", "كنبة زاوية عائلية", 13800, 12600, 2800, 1700, 270, "#b7c4b0"),

        # Right Kitchen
        ("counter", "رخام مطبخ كاونتر", 15100, 16300, 1600, 600, 180, None),
        ("fridge", "ثلاجة عائلية", 11900, 15500, 910, 700, 90, None),

        # Right Reception
        ("sofa", "طقم استقبال 3 مقاعد", 10000, 21400, 2400, 900, 90, "#b7c4b0"),
        ("sofa", "طقم استقبال 3 مقاعد", 13800, 21400, 2400, 900, 270, "#b7c4b0"),
        ("coffeetable", "طاولة رخام", 11900, 21400, 1400, 700, 0, None),
    ]

    return walls, wins, doors, slides, rooms, furniture

def build():
    walls, wins, doors, slides, rooms, furniture = build_refined_house()

    base_dir = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d"
    src_path = os.path.join(base_dir, "index.upstream-demo.html")
    house_path = os.path.join(base_dir, "house-3d.html")
    index_path = os.path.join(base_dir, "index.html")

    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. HTML Header and Font: Add Google Font Tajawal
    content = content.replace('<html lang="zh-CN">', '<html lang="ar" dir="rtl">')
    
    tajawal_head = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">"""
    
    content = re.sub(
        r'<meta charset="utf-8">\s*<meta name="viewport"[^>]+>',
        tajawal_head,
        content
    )
    
    old_css_font = 'font:13px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif'
    new_css_font = "font:14px/1.6 'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    content = content.replace(old_css_font, new_css_font)
    
    old_btn_font = 'button,input,select{font:inherit;color:inherit}'
    new_btn_font = "button,input,select{font-family:'Tajawal',inherit;font-size:inherit;color:inherit}"
    content = content.replace(old_btn_font, new_btn_font)
    
    old_svg_font = 'font-family="-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif"'
    new_svg_font = 'font-family="\'Tajawal\', -apple-system, sans-serif"'
    content = content.replace(old_svg_font, new_svg_font)

    # 2. Header and UI HTML Elements (Arabic text in tags)
    html_replacements = [
        ('>◧ 家具库<', '>◧ مكتبة الأثاث<'),
        ('>属性 ◨<', '>الخصائص ◨<'),
        ('data-en="◧ Library">◧ 家具库<', 'data-en="◧ Library">◧ مكتبة الأثاث<'),
        ('data-en="Properties ◨">属性 ◨<', 'data-en="Properties ◨">الخصائص ◨<'),
        ('三室两厅两卫 · 装修设计', 'عمارة سكنية فاخرة · شقتين متطابقتين'),
        ('data-en="3BR 2LR 2BA · Interior Design">三室两厅两卫 · 装修设计<', 'data-en="Luxury Twin Apartments · 3D Design">عمارة سكنية فاخرة · شقتين متطابقتين<'),
        ('原始户型 1:60 · 尺寸单位 mm', 'مخطط معماري تفاعلي 1:60 · الأبعاد بالمليمتر (mm)'),
        ('title="切换 2D / 3D (T)"', 'title="تبديل 2D / 3D (T)"'),
        ('>2D 平面<', '>مخطط 2D<'),
        ('>3D 场景<', '>مشهد 3D<'),
        ('title="选择 / 移动 (V)"', 'title="تحديد / تحريك (V)"'),
        ('>选择<', '>تحديد<'),
        ('title="测量 (M)"', 'title="قياس الأبعاد (M)"'),
        ('>测量<', '>قياس<'),
        ('title="拆改非承重墙 (X)"', 'title="تعديل الجدران (X)"'),
        ('>拆改墙体<', '>تعديل الجدران<'),
        ('title="缩小"', 'title="تصغير"'),
        ('title="放大"', 'title="تكبير"'),
        ('title="适应窗口 (F)"', 'title="ملاءمة الشاشة (F)"'),
        ('>适应<', '>ملاءمة<'),
        ('title="按 1:60 显示（与原图同比例）"', 'title="عرض بمقياس 1:60 (مطابق للمخطط الأصلي)"'),
        ('title="按 1:100 显示"', 'title="عرض بمقياس 1:100"'),
        ('>鸟瞰<', '>منظور علوي<'),
        ('>漫游<', '>جولة 3D<'),
        ('>斜视<', '>منظور مائل<'),
        ('>俯视<', '>مسقط رأسي<'),
        ('title="撤销 (Ctrl+Z)"', 'title="تراجع (Ctrl+Z)"'),
        ('>撤销<', '>تراجع<'),
        ('title="重做 (Ctrl+Shift+Z)"', 'title="إعادة (Ctrl+Shift+Z)"'),
        ('>重做<', '>إعادة<'),
        ('title="清空所有家具家电（可撤销）"', 'title="إفراغ جميع الأثاث (يمكن التراجع)"'),
        ('>清空布置<', '>إفراغ التأثيث<'),
        ('>尺寸<', '>الأبعاد<'),
        ('>房间<', '>الغرف<'),
        ('>家具<', '>الأثاث<'),
        ('>网格<', '>الشبكة<'),
        ('>承重墙<', '>جدران حاملة<'),
        ('title="拖动家具时贴墙吸附"', 'title="محاذاة ومغناطيسية للجدران أثناء السحب"'),
        ('>贴墙吸附<', '>محاذاة للجدار<'),
        ('>全高墙<', '>جدران كاملة<'),
        ('>剖切墙<', '>مقطع جدران<'),
        ('>房间名<', '>أسماء الغرف<'),
        ('>夜景<', '>وضع ليلي<'),
        ('>日照<', '>الشمس<'),
        ('<button class="btn chip" data-lang="zh" title="简体中文">简</button>\n      <button class="btn chip" data-lang="zht" title="繁體中文">繁</button>\n      <button class="btn chip" data-lang="en" title="English">EN</button>',
         '<button class="btn chip on" data-lang="ar" title="العربية">عربي</button>\n      <button class="btn chip" data-lang="en" title="English">EN</button>'),
        ('aria-label="Language / 语言"', 'aria-label="Language / اللغة"'),
        ('title="全屏 (Shift+F)"', 'title="ملء الشاشة (Shift+F)"'),
        ('>⛶ 全屏<', '>⛶ ملء الشاشة<'),
        ('>文件 ▾<', '>ملف ▾<'),
        ('>导出图片<', '>تصدير صورة PNG<'),
        ('>导出方案 JSON<', '>تصدير المخطط JSON<'),
        ('>导入方案<', '>استيراد مخطط<'),
        ('>重置为默认方案<', '>استعادة المخطط الافتراضي<'),
        ('>房间 · 点击飞到该房间<', '>الغرف · اضغط للانتقال إليها<'),
        ('>漫游模式<', '>وضع الجولة الافتراضية<'),
        ('>退出漫游<', '>إنهاء الجولة<'),
        ('>当前比例<', '>المقياس<'),
        ('/* 收起动画中内容不被挤压变形 */', '/* Prevent squeezing */'),
    ]
    for old_s, new_s in html_replacements:
        content = content.replace(old_s, new_s)

    # 3. Replace Translation Engine in Script Block (lines 348 to 386)
    # The block starts with "/* ======================= 多语言" and ends at "b.setAttribute('aria-pressed', on); });\n}"
    lang_start = content.find("/* ======================= 多语言")
    lang_end_marker = "b.setAttribute('aria-pressed', on); });\n}"
    lang_end = content.find(lang_end_marker, lang_start)
    assert lang_start != -1 and lang_end != -1, "Language block not found!"
    lang_end += len(lang_end_marker)

    new_engine = """/* ======================= اللغة (العربية / English - الافتراضي: العربية) ======================= */
const LANG_KEY = 'twin-apartment-lang-ar-v3';
const LANGS = ['ar', 'en'];
let LANG = (() => { try { const l = localStorage.getItem(LANG_KEY); return LANGS.includes(l) ? l : 'ar'; } catch(e) { return 'ar'; } })();

const tr = (ar, en) => LANG === 'en' ? en : ar;

const NAMES_EN = {
  'غرف النوم':'Bedrooms', 'الصالون والمعيشة':'Living Room', 'المطبخ وتناول الطعام':'Dining & Kitchen',
  'الحمامات':'Bathrooms', 'الأجهزة المنزلية':'Appliances', 'المكتب والترفيه':'Study & Leisure',
  'خشب باركيه بلوط':'Oak Flooring', 'خشب باركيه جوز فاخر':'Walnut Flooring', 'بورسلين 80×80':'800 Porcelain Tile',
  'سيراميك 60×60':'600 Ceramic Tile', 'رخام كلكتا إيطالي فاخر':'Calacatta Italian Marble', 'بلاط حجري مانع للانزلاق':'Anti-slip Stone Tile',
  'تيرازو مصقول':'Polished Terrazzo', 'موكيت سجاد فاخر':'Luxury Carpet',
  'نوم رئيسية (Master L)':'Master Bedroom (L)', 'حمام ماستر (Bath L)':'Master Bath (L)', 'ملابس (Closet L)':'Walk-in Closet (L)',
  'نوم 2 (Bed 2 L)':'Bedroom 2 (L)', 'غسيل (Laundry L)':'Laundry Room (L)', 'حمام عائلي (Bath L)':'Family Bath (L)',
  'نوم 1 (Bed 1 L)':'Bedroom 1 (L)', 'معيشة (Living L)':'Living Room (L)', 'مطبخ (Kitchen L)':'Kitchen (L)',
  'حمام ضيوف (Guest Bath L)':'Guest Bath (L)', 'استقبال (Reception L)':'Reception Salon (L)', 'تراس (Terrace L)':'Terrace (L)',
  'نوم رئيسية (Master R)':'Master Bedroom (R)', 'حمام ماستر (Bath R)':'Master Bath (R)', 'ملابس (Closet R)':'Walk-in Closet (R)',
  'نوم 2 (Bed 2 R)':'Bedroom 2 (R)', 'غسيل (Laundry R)':'Laundry Room (R)', 'حمام عائلي (Bath R)':'Family Bath (R)',
  'نوم 1 (Bed 1 R)':'Bedroom 1 (R)', 'معيشة (Living R)':'Living Room (R)', 'مطبخ (Kitchen R)':'Kitchen (R)',
  'حمام ضيوف (Guest Bath R)':'Guest Bath (R)', 'استقبال (Reception R)':'Reception Salon (R)', 'تراس (Terrace R)':'Terrace (R)',
  'منور (Lightwell)':'Lightwell', 'درج ومصعد (Stairs & Elevator)':'Stairs & Elevator Core',
  'سرير ماستر 1.8m':'Master Bed 1.8m', 'سرير 1.5m':'Bed 1.5m', 'سرير مفرد':'Single Bed',
  'كومودينو':'Nightstand', 'دولاب ملابس':'Wardrobe', 'مكتب دراسة':'Study Desk', 'كرسي':'Chair',
  'كنبة 3 مقاعد':'3-Seat Sofa', 'طاولة رخام':'Marble Coffee Table', 'سجادة صالون فاخرة':'Luxury Rug',
  'كنبة زاوية عائلية':'Family Corner Sofa', 'طقم استقبال 3 مقاعد':'Reception Sofa 3-Seat',
  'رخام مطبخ كاونتر':'Kitchen Countertop', 'بوتاجاز غاز':'Gas Stove', 'حوض غسيل':'Kitchen Sink', 'ثلاجة عائلية':'Family Refrigerator',
  'طاولة طعام 4 كراسي':'Dining Table 4-Seat', 'طاولة طعام 6 مقاعد':'Dining Table 6-Seat', 'طاولة طعام دائرية':'Round Dining Table',
  'كرسي طعام':'Dining Chair', 'جزيرة مطبخ رخامية':'Kitchen Island', 'كرسي بار مرتفع':'Bar Stool',
  'مرحاض معلق':'Wall-hung Toilet', 'وحدة حوض حمام':'Bathroom Vanity', 'وحدة حوض مزدوجة':'Double Vanity',
  'كابينة شاور':'Glass Shower', 'حوض استحمام بانيو':'Bathtub', 'غسالة ملابس':'Washing Machine', 'سخان مياه':'Water Heater',
  'شاشة تلفزيون 65 بوصة':'65" 4K TV', 'شاشة تلفزيون 55 بوصة':'55" 4K TV', 'مكيف سبليت':'Split AC', 'مكيف دولابي عمودي':'Tower AC',
  'غسالة أطباق':'Dishwasher', 'دولاب أفران مدمجة':'Built-in Oven Tower', 'مجفف ملابس':'Dryer', 'منقي هواء':'Air Purifier',
  'طاولة مكتب عمل':'Office Desk', 'كرسي مكتب تنفيذي':'Executive Chair', 'خزانة كتب جدارية':'Wall Bookshelf',
  'بيانو كلاسيكي':'Upright Piano', 'جهاز سير رياضي':'Treadmill', 'كرسي قراءة واسترخاء':'Reading Chair',
  'طاولة شاي وجلسة':'Tea Table', 'كرسي استرخاء شيزلونج':'Lounge Chair',
  'كامل المبنى':'Whole Building'
};

const nm = s => LANG === 'en' ? (NAMES_EN[s] ?? s) : s;

function applyStaticLang(){
  document.documentElement.lang = LANG;
  document.documentElement.dir = LANG === 'ar' ? 'rtl' : 'ltr';
  document.title = tr('عمارة سكنية فاخرة · شقتين متطابقتين (3D)', 'Twin Luxury Apartments 3D Floor Plan');
  document.querySelectorAll('[data-en]').forEach(el => {
    el.dataset.ar ??= el.textContent;
    el.textContent = tr(el.dataset.ar, el.dataset.en);
  });
  document.querySelectorAll('[data-en-title]').forEach(el => {
    el.dataset.arTitle ??= el.title;
    el.title = tr(el.dataset.arTitle, el.dataset.enTitle);
  });
  document.querySelectorAll('#langSel [data-lang]').forEach(b => {
    const on = b.dataset.lang === LANG;
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
}"""

    content = content[:lang_start] + new_engine + content[lang_end:]

    # 4. Replace Architecture: WALLS to ROOMS
    arch_lines = [
        "const WALLS = [\n" + ",\n".join(f"  {json.dumps(w)}" for w in walls) + "\n];",
        "const WINS = [\n" + ",\n".join(f"  {json.dumps(w)}" for w in wins) + "\n];",
        "const DOORS = [\n" + ",\n".join(f"  {json.dumps(d, ensure_ascii=False)}" for d in doors) + "\n];",
        "const SLIDES = [\n" + ",\n".join(f"  {json.dumps(s)}" for s in slides) + "\n];",
        "const R = (x0,y0,x1,y1) => [[x0,y0],[x1,y0],[x1,y1],[x0,y1]];",
        "const ROOMS = [\n" + ",\n".join(f"  {{id:{json.dumps(r['id'])}, name:{json.dumps(r['name'], ensure_ascii=False)}, poly:{json.dumps(r['poly'])}, mat:{json.dumps(r['mat'])}, at:{json.dumps(r['at'])}}}" for r in rooms) + "\n];"
    ]
    arch_block = "\n\n".join(arch_lines)
    pattern_arch = r"const WALLS = \[[\s\S]*?const ROOMS = \[[\s\S]*?\];"
    content = re.sub(pattern_arch, arch_block, content)

    # 5. Replace MATS
    old_mats = """const MATS = {
  wood:    {name:'橡木地板', price:320, sw:'#d8b88a'},
  walnut:  {name:'胡桃木地板', price:380, sw:'#9b7250'},
  tile800: {name:'800 地砖', price:220, sw:'#ebe6dc'},
  tile600: {name:'600 地砖', price:160, sw:'#dfe3e1'},
  marble:  {name:'大理石', price:650, sw:'#f1eee8'},
  antislip:{name:'300 防滑砖', price:140, sw:'#d3d8d4'},
  terrazzo:{name:'水磨石', price:280, sw:'#e6dfd3'},
  carpet:  {name:'满铺地毯', price:200, sw:'#c9c3d3'},
};"""
    new_mats = """const MATS = {
  wood:    {name:'خشب باركيه بلوط', price:320, sw:'#d8b88a'},
  walnut:  {name:'خشب باركيه جوز فاخر', price:380, sw:'#9b7250'},
  tile800: {name:'بورسلين 80×80', price:220, sw:'#ebe6dc'},
  tile600: {name:'سيراميك 60×60', price:160, sw:'#dfe3e1'},
  marble:  {name:'رخام كلكتا إيطالي فاخر', price:650, sw:'#f1eee8'},
  antislip:{name:'بلاط حجري مانع للانزلاق', price:140, sw:'#d3d8d4'},
  terrazzo:{name:'تيرازو مصقول', price:280, sw:'#e6dfd3'},
  carpet:  {name:'موكيت سجاد فاخر', price:200, sw:'#c9c3d3'},
};"""
    content = content.replace(old_mats, new_mats)

    # 6. Replace LIB (Furniture library)
    old_lib_pattern = r"// 家具库：\[类型, 名称, 宽, 深, 颜色\]\s*const LIB = \[[\s\S]*?\];\s*const typeColor"
    new_lib = """// مكتبة الأثاث: [النوع, الاسم, العرض, العمق, اللون]
const LIB = [
  {cat:'غرف النوم', items:[
    ['bed','سرير ماستر 1.8m',1800,2000,'#c9d6df'],['bed','سرير 1.5m',1500,2000,'#d8c7dc'],['bed','سرير مفرد',1200,2000,'#e8d5b5'],
    ['crib','سرير أطفال',1250,700,'#efe3d0'],['nightstand','كومودينو',450,400,'#e8dccb'],['wardrobe','دولاب ملابس',2000,600,'#efe6d8'],
    ['wardrobe','خزانة صغيرة',1200,550,'#efe6d8'],['dresser','تسريحة ومرآة',1000,450,'#efe6d8'],['desk','مكتب دراسة',1200,600,'#e2cfb4'],
    ['chair','كرسي مكتب',450,480,'#cfc6b8'],['bookshelf','مكتبة رفوف كتب',800,300,'#e2cfb4'],['baycushion','جلسة شباك بانوراما',520,1800,'#e7dccd']]},
  {cat:'الصالون والمعيشة', items:[
    ['sofa','كنبة 3 مقاعد',2400,900,'#b7c4b0'],['sofa','كنبة ثنائية',1700,880,'#c3cbd6'],['cornersofa','كنبة زاوية عائلية',2800,1700,'#b7c4b0'],
    ['armchair','أريكة مفردة فوتيه',850,850,'#d6b99a'],['beanbag','بين باج مريح',800,800,'#e0b98f'],['coffeetable','طاولة رخام',1300,650,'#e8dccb'],
    ['sidetable','طاولة جانبية',500,500,'#d9c3a3'],['tvstand','وحدة تلفزيون جدارية',2400,400,'#e2cfb4'],['rug','سجادة صالون فاخرة',2400,1700,'#d9cbb8'],
    ['shoecab','خزانة أحذية',1000,350,'#efe6d8'],['shoecab','كونسول مدخل',1400,380,'#e6dccc'],['floorlamp','مصباح أرضي مودرن',450,450,'#3d3a34'],
    ['plant','نبات داخلي',500,500,'#a9c39b'],['plant','نبات زينة كبير',700,700,'#9dbb8c']]},
  {cat:'المطبخ وتناول الطعام', items:[
    ['table','طاولة طعام 4 كراسي',1400,800,'#e2cfb4'],['table','طاولة طعام 6 مقاعد',1800,900,'#d8c2a2'],['roundtable','طاولة طعام دائرية',1000,1000,'#e2cfb4'],
    ['chair','كرسي طعام',450,480,'#cfc6b8'],['island','جزيرة مطبخ رخامية',1800,900,'#e9e5de'],['barstool','كرسي بار مرتفع',420,420,'#6b5d4c'],
    ['counter','رخام مطبخ كاونتر',1600,600,'#e9e5de'],['stove','بوتاجاز غاز',750,450,'#dcdcdc'],['ksink','حوض غسيل',800,450,'#e1e6ea'],
    ['fridge','ثلاجة عائلية',700,700,'#dfe4e8'],['cabinet','بوفيه تقديم',1600,400,'#efe6d8']]},
  {cat:'الحمامات', items:[
    ['toilet','مرحاض معلق',400,700,'#ffffff'],['vanity','وحدة حوض حمام',800,500,'#eef1f3'],['vanity','وحدة حوض مزدوجة',1200,500,'#eef1f3'],
    ['shower','كابينة شاور',900,900,'#e4edf2'],['bathtub','حوض استحمام بانيو',1600,750,'#eef3f6'],['washer','غسالة ملابس',600,600,'#e6ebee'],
    ['waterheater','سخان مياه',800,450,'#f4f4f2'],['cabinet','خزانة حمام',1000,400,'#efe6d8']]},
  {cat:'الأجهزة المنزلية', items:[
    ['tv','شاشة تلفزيون 65 بوصة',1450,80,'#1d1d1f'],['tv','شاشة تلفزيون 55 بوصة',1230,80,'#1d1d1f'],['fridge','ثلاجة عائلية',910,700,'#c9ced3'],
    ['aircon','مكيف دولابي عمودي',500,380,'#f6f7f8'],['acwall','مكيف سبليت',900,250,'#f6f7f8'],['dishwasher','غسالة أطباق',600,600,'#dfe3e6'],
    ['cabinet','دولاب أفران مدمجة',600,600,'#2a2a2c'],['washer','مجفف ملابس',600,600,'#e6ebee'],['airpurifier','منقي هواء',350,350,'#ffffff']]},
  {cat:'المكتب والترفيه', items:[
    ['desk','طاولة مكتب عمل',1600,750,'#e2cfb4'],['chair','كرسي مكتب تنفيذي',600,600,'#3a3835'],['bookshelf','خزانة كتب جدارية',1200,350,'#e2cfb4'],
    ['piano','بيانو كلاسيكي',1500,650,'#1a1918'],['treadmill','جهاز سير رياضي',1800,800,'#2c2b2a'],['armchair','كرسي قراءة واسترخاء',800,850,'#c2b09a'],
    ['teatable','طاولة شاي وجلسة',1400,700,'#966b49'],['loungechair','كرسي استرخاء شيزلونج',700,1600,'#8f969b']]},
];
const typeColor"""
    content = re.sub(old_lib_pattern, new_lib, content)

    # 7. Replace defaultFurniture()
    furn_lines = []
    for f in furniture:
        t, nm, cx, cy, w, d, rot, c = f
        col = f",'{c}'" if c else ""
        furn_lines.append(f"  F('{t}','{nm}',{cx},{cy},{w},{d},{rot}{col})")
    furn_block = "function defaultFurniture(){\n  return [\n" + ",\n".join(furn_lines) + "\n  ];\n}"
    pattern_furn = r"function defaultFurniture\(\)\{[\s\S]*?\];\}"
    content = re.sub(pattern_furn, furn_block, content)

    # 8. Replace BOUNDS
    content = re.sub(
        r"const BOUNDS = \{x:[^,]+, y:[^,]+, w:[^,]+, h:[^}]+\};",
        "const BOUNDS = {x:-2000, y:-2000, w:19800, h:30200};",
        content
    )

    # 9. Replace OX, OY, H
    content = re.sub(
        r"const OX = \d+, OY = \d+, H = [^,]+, FOV = \d+;",
        "const OX = 7900, OY = 13100, H = 2.8, FOV = 45;",
        content
    )

    # 10. Enrich floor textures in TEX
    old_tex = (
        "const TEX = {\n"
        "  wood:{sx:1.8, sy:.36, base:'#d6b58a', rough:.55}, walnut:{sx:1.8, sy:.36, base:'#9a6f4b', rough:.5},\n"
        "  tile800:{sx:.8, sy:.8, base:'#ebe6dd', grout:'#cfc6b7', rough:.3}, tile600:{sx:.6, sy:.6, base:'#dfe3e0', grout:'#bfc6c1', rough:.35},\n"
        "  antislip:{sx:.3, sy:.3, base:'#d3d8d4', grout:'#aab2ac', rough:.8}, marble:{sx:1.2, sy:1.2, base:'#f2efe9', grout:'#d9d2c4', rough:.18},\n"
        "  terrazzo:{sx:.5, sy:.5, base:'#e6dfd3', rough:.4}, carpet:{sx:.3, sy:.3, base:'#c6bfd2', rough:1},\n"
        "};"
    )
    new_tex = (
        "const TEX = {\n"
        "  wood:{sx:1.6, sy:.28, base:'#c4945a', rough:.45}, walnut:{sx:1.6, sy:.28, base:'#7a4f32', rough:.4},\n"
        "  tile800:{sx:.8, sy:.8, base:'#e8e4db', grout:'#8c8275', rough:.22}, tile600:{sx:.6, sy:.6, base:'#d2d7d5', grout:'#7f8783', rough:.28},\n"
        "  antislip:{sx:.3, sy:.3, base:'#4a5568', grout:'#2d3748', rough:.6}, marble:{sx:1.4, sy:1.4, base:'#faf8f5', grout:'#d4cdc0', rough:.12},\n"
        "  terrazzo:{sx:.5, sy:.5, base:'#e2dbce', rough:.35}, carpet:{sx:.3, sy:.3, base:'#b8b0c4', rough:1},\n"
        "};"
    )
    content = content.replace(old_tex, new_tex)

    # 11. Ensure unique STORE key
    content = content.replace("const STORE = 'huxing-design-v1';", "const STORE = 'twin-apartment-house-3d-v5';")

    # 12. Shadow camera & orbit limits
    content = content.replace(
        "Object.assign(sun.shadow.camera, {left:-11, right:11, top:11, bottom:-11, near:1, far:60});",
        "Object.assign(sun.shadow.camera, {left:-18, right:18, top:18, bottom:-18, near:1, far:90});"
    )
    content = content.replace(
        "orbit.enableDamping = true; orbit.maxPolarAngle = Math.PI*.495; orbit.minDistance = 1.5; orbit.maxDistance = 45;",
        "orbit.enableDamping = true; orbit.maxPolarAngle = Math.PI*.495; orbit.minDistance = 1.5; orbit.maxDistance = 85;"
    )

    # 13. TopWhole & walkthrough pose
    content = content.replace(
        "const topWhole = () => pose(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 19, 1e-4));",
        "const topWhole = () => pose(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 30, 1e-4));"
    )
    content = content.replace(
        "camera.position.set(wx(4200), 1.6, wz(8755)); camera.lookAt(wx(7000), 1.5, wz(8755));   // 入户门外",
        "camera.position.set(wx(7900), 1.6, wz(15200)); camera.lookAt(wx(7900), 1.5, wz(13000));   // Apartment landing"
    )

    # 14. Clean bay window lintels
    content = content.replace(
        "[[10270,800,10510,2600], 2.4], [[10270,4260,10510,5740], 2.4]",
        ""
    )

    # 15. Add 3D U-shaped Stairs and Panoramic Glass Elevator
    stairs_arch_code = """
  // --- U-SHAPED STAIRCASE & PANORAMIC GLASS ELEVATOR CORE ---
  function buildStairsAndElevator(archUp, archFloor, top){
    const stairMarbleMat = mat('#faf8f5', {roughness: 0.18, metalness: 0.05});
    const stairRiserMat = mat('#ebe6dd', {roughness: 0.45});
    const stairNoseMat = mat('#d4af37', {roughness: 0.3, metalness: 0.7});
    const handrailMat = mat('#2b2622', {roughness: 0.35, metalness: 0.5});
    const steelMat = mat('#2d3135', {roughness: 0.25, metalness: 0.85});
    const cabinWallMat = mat('#d4d9de', {roughness: 0.2, metalness: 0.88});
    const mirrorMat = mat('#f0f4f8', {roughness: 0.05, metalness: 0.98});
    const ceilGlowMat = new THREE.MeshStandardMaterial({color: '#ffffff', emissive: '#fff6e0', emissiveIntensity: 0.6});
    const doorLeafMat = mat('#c2c7cc', {roughness: 0.28, metalness: 0.85});
    const displayMat = new THREE.MeshStandardMaterial({color: '#1a202c', emissive: '#38b2ac', emissiveIntensity: 0.9});
    const buttonMat = new THREE.MeshStandardMaterial({color: '#ffffff', emissive: '#f6ad55', emissiveIntensity: 0.85});

    // 1. Mid-Landing at y = 1.40m
    const midH = 1.40;
    if (top >= 0.3){
      const baseH = Math.min(midH - 0.16, top);
      if (baseH > 0){
        archFloor.add(box(3.72, baseH, 1.20, mat('#f3efe8', {roughness: 0.8}), 0, 0, -1.50));
      }
      if (top >= midH){
        archUp.add(box(3.72, 0.16, 1.20, stairMarbleMat, 0, midH - 0.16, -1.50));
      }
    }

    // 2. Left Flight (Climbing North from Entrance Landing wz=+0.30 to Mid-Landing wz=-0.90)
    const riserH = 0.175, numSteps = 7, runLen = 1.20, treadDepth = 0.20;
    const leftX = -1.31, flightW = 1.08;

    for (let i = 0; i < numSteps; i++){
      const yBot = i * riserH;
      const yTop = (i + 1) * riserH;
      if (yBot >= top) break;
      const z = 0.30 - (i + 0.5) * (runLen / numSteps);

      const th = Math.min(0.035, top - (yTop - 0.035));
      if (th > 0){
        archUp.add(box(flightW, th, treadDepth, stairMarbleMat, leftX, yTop - 0.035, z));
        archUp.add(box(flightW, Math.min(0.015, th), 0.015, stairNoseMat, leftX, yTop - 0.015, z + treadDepth/2));
      }
      const rh = Math.min(riserH - 0.035, top - yBot);
      if (rh > 0){
        archUp.add(box(flightW, rh, 0.03, stairRiserMat, leftX, yBot, z + treadDepth/2 - 0.015));
      }
      if (yBot > 0){
        archFloor.add(box(flightW - 0.02, Math.min(yBot, top), treadDepth, mat('#ebe5dc', {roughness: 0.85}), leftX, 0, z));
      }
    }

    // Left Flight Glass Balustrade & Handrail
    if (top >= 0.8){
      const railPts = 4;
      for (let k = 0; k < railPts; k++){
        const rz = 0.30 - k * (runLen / (railPts - 1));
        const ry = (k / (railPts - 1)) * 1.22;
        const ph = Math.min(0.90, top - ry);
        if (ph > 0.1){
          archUp.add(box(0.03, ph, 0.03, steelMat, -0.77, ry, rz));
        }
      }
      const gH = Math.min(0.85, top - 0.5);
      if (gH > 0.2){
        archUp.add(box(0.012, gH, runLen, glassMat, -0.77, 0.35, -0.30));
      }
      const hrH = Math.min(0.04, top - 0.9);
      if (hrH > 0){
        const hr = box(0.04, 0.04, runLen * 1.05, handrailMat, -0.77, 0.90, -0.30);
        hr.rotation.x = -Math.atan2(1.22, runLen);
        archUp.add(hr);
      }
    }

    // 3. Right Flight (Climbing South from Mid-Landing wz=-0.90 to Upper wz=+0.30)
    const rightX = 1.31;
    for (let i = 0; i < numSteps; i++){
      const yBot = midH + i * riserH;
      const yTop = midH + (i + 1) * riserH;
      if (yBot >= top) break;
      const z = -0.90 + (i + 0.5) * (runLen / numSteps);

      const th = Math.min(0.035, top - (yTop - 0.035));
      if (th > 0){
        archUp.add(box(flightW, th, treadDepth, stairMarbleMat, rightX, yTop - 0.035, z));
        archUp.add(box(flightW, Math.min(0.015, th), 0.015, stairNoseMat, rightX, yTop - 0.015, z - treadDepth/2));
      }
      const rh = Math.min(riserH - 0.035, top - yBot);
      if (rh > 0){
        archUp.add(box(flightW, rh, 0.03, stairRiserMat, rightX, yBot, z - treadDepth/2 + 0.015));
      }
    }

    // Right Flight Glass Balustrade & Handrail
    if (top >= 1.6){
      const railPts = 4;
      for (let k = 0; k < railPts; k++){
        const rz = -0.90 + k * (runLen / (railPts - 1));
        const ry = midH + (k / (railPts - 1)) * 1.22;
        const ph = Math.min(0.90, top - ry);
        if (ph > 0.1){
          archUp.add(box(0.03, ph, 0.03, steelMat, 0.77, ry, rz));
        }
      }
      const gH = Math.min(0.85, top - 1.8);
      if (gH > 0.2){
        archUp.add(box(0.012, gH, runLen, glassMat, 0.77, 1.75, -0.30));
      }
      if (top >= 2.2){
        const hr = box(0.04, 0.04, runLen * 1.05, handrailMat, 0.77, 2.30, -0.30);
        hr.rotation.x = Math.atan2(1.22, runLen);
        archUp.add(hr);
      }
    }

    // 4. Central Panoramic Glass Elevator
    const shH = Math.min(top, 2.80);
    colliders.push([wx(7140), wz(11900), wx(8660), wz(13400)]);

    // 4 Corner structural posts
    [[-0.74, -1.18], [0.74, -1.18], [-0.74, 0.28], [0.74, 0.28]].forEach(([px, pz]) => {
      archUp.add(box(0.05, shH, 0.05, steelMat, px, 0, pz));
    });

    // Shaft Glass Walls
    archUp.add(box(0.012, shH, 1.42, glassMat, -0.74, 0, -0.45));
    archUp.add(box(0.012, shH, 1.42, glassMat, 0.74, 0, -0.45));
    archUp.add(box(1.42, shH, 0.012, glassMat, 0, 0, -1.18));

    // Mid Transoms
    if (shH >= 1.40){
      archUp.add(box(0.03, 0.04, 1.42, steelMat, -0.74, 1.40, -0.45));
      archUp.add(box(0.03, 0.04, 1.42, steelMat, 0.74, 1.40, -0.45));
      archUp.add(box(1.42, 0.04, 0.03, steelMat, 0, 1.40, -1.18));
    }
    if (top >= 2.75){
      archUp.add(box(0.04, 0.06, 1.46, steelMat, -0.74, 2.74, -0.45));
      archUp.add(box(0.04, 0.06, 1.46, steelMat, 0.74, 2.74, -0.45));
      archUp.add(box(1.46, 0.06, 0.04, steelMat, 0, 2.74, -1.18));
      archUp.add(box(1.46, 0.06, 0.04, steelMat, 0, 2.74, 0.28));
    }

    // South Front Face: Elevator Landing Doors at Z = +0.28
    const dH = Math.min(2.15, top);
    archUp.add(box(0.20, shH, 0.06, steelMat, -0.64, 0, 0.28));
    archUp.add(box(0.20, shH, 0.06, steelMat, 0.64, 0, 0.28));
    if (top > 2.15){
      archUp.add(box(1.08, top - 2.15, 0.06, steelMat, 0, 2.15, 0.28));
    }
    // Stainless Steel Sliding Doors
    archUp.add(box(0.53, dH - 0.05, 0.03, doorLeafMat, -0.27, 0, 0.28));
    archUp.add(box(0.53, dH - 0.05, 0.03, doorLeafMat, 0.27, 0, 0.28));
    archUp.add(box(0.008, dH - 0.05, 0.032, mat('#1a1a1a'), 0, 0, 0.28));

    // Call Button Plate & Indicator
    if (top >= 1.2){
      archUp.add(box(0.07, 0.16, 0.015, steelMat, 0.64, 0.97, 0.315));
      archUp.add(box(0.025, 0.025, 0.02, buttonMat, 0.64, 1.05, 0.315));
    }
    if (top >= 2.25){
      archUp.add(box(0.28, 0.09, 0.02, displayMat, 0, 2.18, 0.315));
    }

    // 5. Cabin Interior
    const cabH = Math.min(2.10, top);
    archFloor.add(box(1.34, 0.03, 1.28, mat('#2d3748', {roughness: 0.3}), 0, 0.01, -0.45));
    archUp.add(box(0.02, cabH, 1.26, cabinWallMat, -0.65, 0.04, -0.45));
    archUp.add(box(0.02, cabH, 1.26, cabinWallMat, 0.65, 0.04, -0.45));
    archUp.add(box(1.28, cabH, 0.01, mirrorMat, 0, 0.04, -1.08));
    if (top >= 1.1){
      archUp.add(box(1.10, 0.03, 0.03, steelMat, 0, 0.90, -1.05));
    }
    if (top >= 2.10){
      archUp.add(box(1.26, 0.03, 1.22, ceilGlowMat, 0, 2.07, -0.45));
      const cabLight = new THREE.PointLight(0xfff3db, 0.8, 3.5, 1.5);
      cabLight.position.set(0, 1.95, -0.45);
      archUp.add(cabLight);
    }
  }
"""

    old_arch_end = "  applyLight(); applyGrow();\n}"
    new_arch_end = "  buildStairsAndElevator(archUp, archFloor, top);\n  applyLight(); applyGrow();\n}\n" + stairs_arch_code
    assert old_arch_end in content, "old_arch_end not found!"
    content = content.replace(old_arch_end, new_arch_end)

    # 16. Add 2D Staircase, Elevator & Dual Unit Entrance SVG in renderOpenings()
    old_entry_svg = (
        '  // 入户标识\n'
        '  s += `<path d="M3350 8755H4350M4150 8600L4400 8755L4150 8910" fill="none" stroke="#b5653a" stroke-width="2" vector-effect="non-scaling-stroke"/>\n'
        '        <text x="3380" y="8600" font-size="200" fill="#b5653a">${tr(\'入户\',\'Entry\')}</text>`;'
    )
    new_entry_svg = """
    // --- 2D STAIRCASE & ELEVATOR ARCHITECTURAL DRAWING ---
    // Elevator Shaft & Cabin
    s += `<rect x="7140" y="11900" width="1520" height="1500" fill="#f7f9fa" stroke="#2d3748" stroke-width="2" vector-effect="non-scaling-stroke"/>`;
    s += `<line x1="7140" y1="11900" x2="8660" y2="13400" stroke="#a0aec0" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
    s += `<line x1="8660" y1="11900" x2="7140" y2="13400" stroke="#a0aec0" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
    s += `<rect x="7360" y="13340" width="1080" height="80" fill="#fff" stroke="#2d3748" stroke-width="1.8" vector-effect="non-scaling-stroke"/>`;
    s += `<text x="7900" y="12550" font-size="180" font-weight="700" text-anchor="middle" fill="#2d3748">ELEVATOR</text>`;
    s += `<text x="7900" y="12770" font-size="170" font-weight="600" text-anchor="middle" fill="#4a5568">مصعد</text>`;

    // Left Flight Treads (Climb UP North towards mid-landing)
    for (let i = 0; i <= 7; i++){
      const y = 13400 - i * (1200 / 7);
      s += `<line x1="6040" y1="${y}" x2="7140" y2="${y}" stroke="#718096" stroke-width="1.2" vector-effect="non-scaling-stroke"/>`;
    }
    // Right Flight Treads (Climb UP South from mid-landing)
    for (let i = 0; i <= 7; i++){
      const y = 12200 + i * (1200 / 7);
      s += `<line x1="8660" y1="${y}" x2="9760" y2="${y}" stroke="#718096" stroke-width="1.2" vector-effect="non-scaling-stroke"/>`;
    }
    // Mid-Landing Outline
    s += `<rect x="6040" y="11000" width="3720" height="1200" fill="none" stroke="#a0aec0" stroke-width="1.2" stroke-dasharray="8 5" vector-effect="non-scaling-stroke"/>`;
    s += `<text x="7900" y="11550" font-size="160" font-weight="600" text-anchor="middle" fill="#718096">بسطة نصف الدور +1.40m</text>`;

    // Stair Flight Climb Arrow
    s += `<path d="M6590 13350 L6590 11600 L9210 11600 L9210 13350" fill="none" stroke="#b5653a" stroke-width="2.5" vector-effect="non-scaling-stroke"/>`;
    s += `<circle cx="6590" cy="13350" r="45" fill="#b5653a"/>`;
    s += `<polygon points="9210,13430 9155,13330 9265,13330" fill="#b5653a"/>`;
    s += `<text x="6590" y="12550" font-size="170" font-weight="700" text-anchor="middle" fill="#b5653a" transform="rotate(-90 6590 12550)">صعود UP</text>`;

    // Dual Unit Entrance Indicators
    s += `<path d="M6700 14850 L6700 14650 M6600 14750 L6700 14650 L6800 14750" fill="none" stroke="#b5653a" stroke-width="2.5" vector-effect="non-scaling-stroke"/>`;
    s += `<text x="6700" y="15100" font-size="180" font-weight="700" text-anchor="middle" fill="#b5653a">مدخل الشقة اليسرى</text>`;
    s += `<path d="M9100 14850 L9100 14650 M9000 14750 L9100 14650 L9200 14750" fill="none" stroke="#b5653a" stroke-width="2.5" vector-effect="non-scaling-stroke"/>`;
    s += `<text x="9100" y="15100" font-size="180" font-weight="700" text-anchor="middle" fill="#b5653a">مدخل الشقة اليمنى</text>`;"""

    assert old_entry_svg in content, "old_entry_svg not found!"
    content = content.replace(old_entry_svg, new_entry_svg)

    # 17. Localize all tr(...) calls and prompts across the entire codebase
    tr_dict = {
        "'没有可撤销的操作'": "'لا توجد عمليات للتراجع عنها'",
        "'拖动旋转（Shift 自由角度）'": "'اسحب للتدوير (Shift لزاوية حرة)'",
        "'拖动调整尺寸'": "'اسحب لتعديل الحجم'",
        "'房间面积'": "'مساحات الغرف'",
        "'点击查看 / 更换地面'": "'اضغط للاستعراض وتغيير الأرضية'",
        "'套内使用面积'": "'إجمالي المساحة الصافية'",
        "'* 飘窗不计入使用面积；面积按墙体内净尺寸计算'": "'* المساحات محسوبة من الأوجه الداخلية الصافية للجدران'",
        "'地面材料估算'": "'حساب تكلفة وتوزيع الأرضيات'",
        "'含 5% 损耗'": "'شامل 5% نسبة هالك'",
        "'地面材料合计'": "'إجمالي تكلفة الأرضيات'",
        "'方案统计'": "'إحصائيات المخطط'",
        "'家具数量'": "'عدد قطع الأثاث'",
        "'拆除墙体'": "'الجدران المعدلة'",
        "'清除测量'": "'مسح القياسات'",
        "'清空布置'": "'إفراغ التأثيث'",
        "'旋转'": "'تدوير'",
        "'复制'": "'تكرار'",
        "'删除'": "'حذف'",
        "'属性'": "'الخصائص'",
        "'完成'": "'تم'",
        "'地面 / 属性'": "'الأرضية / الخصائص'",
        "'当前没有布置任何家具'": "'لا توجد أي قطع أثاث حالياً'",
        "'已清空布置，可点「撤销」恢复'": "'تم إفراغ الأثاث، يمكنك الضغط على «تراجع» للاستعادة'",
        "'房间'": "'الغرفة'",
        "'名称'": "'الاسم'",
        "'使用面积'": "'المساحة'",
        "'周长'": "'المحيط'",
        "'开间'": "'العرض'",
        "'进深'": "'العمق'",
        "'地面材料'": "'نوع الأرضية'",
        "'材料估价'": "'التكلفة التقديرية'",
        "'房间内家具'": "'الأثاث في الغرفة'",
        "'暂无'": "'لا يوجد'",
        "'← 返回总览'": "'← العودة للنظرة العامة'",
        "'家具属性'": "'خصائص الأثاث'",
        "'宽'": "'العرض'",
        "'深'": "'العمق'",
        "'中心'": "'المركز'",
        "'旋转 90°'": "'تدوير 90°'",
        "'置于顶层'": "'إحضار للأمام'",
        "'置于底层'": "'إرسال للخلف'",
        "'← 返回'": "'← عودة'",
        "'承重墙（黑色）不可拆除'": "'الجدران الحاملة الإنشائية لا يمكن إزالتها'",
        "'外墙属于建筑外围护结构，不建议拆除'": "'الجدران الخارجية واجهة معمارية لا يمكن إزالتها'",
        "'已恢复墙体'": "'تمت استعادة الجدار'",
        "'请拖到地面上'": "'يرجى الإسقاط داخل أرضية الغرفة'",
        "'户型装修方案'": "'مخطط-العمارة-السكنية'",
        "'3D 引擎仍在加载或加载失败（需要联网加载 three.js）'": "'جارِ تحميل محرك 3D...'",
        "'无法进入全屏'": "'تعذر تفعيل وضع ملء الشاشة'",
        "'退出全屏'": "'الخروج من ملء الشاشة'",
        "'全屏'": "'ملء الشاشة'",
        "'方案已导入'": "'تم استيراد المخطط بنجاح'",
        "'文件格式不正确'": "'صيغة الملف غير صحيحة'",
        "'恢复为默认设计方案？（可撤销）'": "'هل تريد استعادة التصميم الافتراضي؟ (يمكن التراجع)'",
        "'全屋'": "'كامل المبنى'",
        "'点或拖动家具库添加 · 单指拖动平移 · 双指缩放 · 选中家具后底部工具条可旋转 / 复制 / 删除'": "'اختر من مكتبة الأثاث للإضافة · اسحب بإصبع للتحريك · إصبعان للتكبير · اضغط الأثاث للتدوير أو الحذف'",
        "'单指旋转 · 双指缩放 / 平移 · 点家具或地面编辑 · 点门开关'": "'إصبع للتدوير 3D · إصبعان للتكبير/التحريك · انقر الأثاث لتعديله · انقر الأبواب لفتحها'",
        "'拖动左侧家具到平面图 · 滚轮缩放 · 拖动空白处平移 · T 切换 3D'": "'اسحب الأثاث من القائمة إلى المخطط · العجلة للتكبير · اسحب للتحريك · مفتاح T للتبديل ثلاثي الأبعاد'",
        "'3D 场景与平面方案实时同步 · 右侧面板修改会立即生效 · T 返回 2D'": "'المشهد ثلاثي الأبعاد متزامن فورياً مع المخطط · التعديلات تنطبق مباشرة · T للعودة 2D'",
        "'单指旋转 · 双指缩放 / 平移 · 点选家具后可拖动摆放 · 点门开关'": "'إصبع للتدوير · إصبعان للتقريب · انقر الأثاث لتعديله · انقر الأبواب لفتحها وإغلاقها'",
        "'左键旋转 · 右键平移 · 滚轮缩放 · 选中家具后拖动可摆放 · 点击门开关'": "'زر الماوس الأيسر للتدوير · الأيمن للتحريك · عجلة الماوس للتقريب · انقر الأبواب لفتحها'",
        "'左下摇杆移动 · 拖动画面转向 · 点门开关'": "'عصا التحكم باليسار للحركة · اسحب الشاشة للنظر · انقر الأبواب لفتحها'",
        "'WASD 移动 · 鼠标转向 · Shift 快走 · E 开关门 · Esc 暂停'": "'تحرك بمفاتيح WASD · حرك الماوس للنظر · Shift للسرعة · E لفتح الأبواب · Esc إيقاف مؤقت'",
        "'点击开始，从入户门进入'": "'اضغط للبدء، الدخول من ردهة الأبواب والمصعد'",
        "'左下摇杆移动 · 在画面上拖动转向'": "'استخدم عصا التحكم للحركة · اسحب في الشاشة لتغيير اتجاه النظر'",
        "'点门开关 · 点「退出漫游」回到鸟瞰'": "'انقر الأبواب لفتحها · اضغط «إنهاء الجولة» للعودة للمنظور العلوي'",
        "'<kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> 移动 · 鼠标转向 · <kbd>Shift</kbd> 快走'": "'<kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> للحركة · حرك الماوس للنظر · <kbd>Shift</kbd> للمشي السريع'",
        "'<kbd>E</kbd> 开关正前方的门 · <kbd>Esc</kbd> 暂停'": "'<kbd>E</kbd> أو النقر لفتح الأبواب أمامك · <kbd>Esc</kbd> إيقاف مؤقت'",
        "'颜色'": "'اللون'",
        "'占地面积'": "'المساحة المشغولة'",
    }
    for zh, ar in tr_dict.items():
        content = content.replace(f"tr({zh},", f"tr({ar},")

    # 18. Replace subtitle, touch, kbd, confirm, and specific multiline blocks
    old_sub = "  $('#subtitle').textContent = tr(`套内使用面积约 ${fmt(tot)} m² · 尺寸单位 mm · 原图比例 1:60`, `Net floor area ≈ ${fmt(tot)} m² · Units: mm · Original scale 1:60`);"
    new_sub = "  $('#subtitle').textContent = tr(`إجمالي المساحة الصافية حوالي ${fmt(tot)} م² · الأبعاد بالمليمتر · مقياس 1:60`, `Net floor area ≈ ${fmt(tot)} m² · Units: mm · Original scale 1:60`);"
    content = content.replace(old_sub, new_sub)

    pattern_touch = r"\$\{COARSE \? tr\(`<section><h3>触屏操作</h3>[\s\S]*?`\) : ''\}"
    new_touch = """${COARSE ? tr(`<section><h3>إيماءات اللمس</h3><div class="kbd">
    <kbd>سحب بإصبع</kbd><span>تحريك المخطط في المساحات الفارغة</span><kbd>إصبعان</kbd><span>تكبير وتصغير وتحريك المخطط</span>
    <kbd>مكتبة الأثاث</kbd><span>اضغط للإضافة في المركز، أو اسحب لموضع معين</span>
    <kbd>تحديد الأثاث</kbd><span>اسحب للتحريك؛ اسحب النقطة للتدوير، والزاوية للحجم</span>
    <kbd>شريط الأدوات</kbd><span>خيارات التدوير / التكرار / الحذف بالأسفل</span>
    <kbd>القياس</kbd><span>اسحب لرسم خط القياس، أو انقر نقطتين</span>
    <kbd>جولة 3D</kbd><span>عصا التحكم باليسار للحركة، اسحب للنظر، انقر الأبواب للفتح</span>
  </div></section>`, `<section><h3>Touch Controls</h3><div class="kbd">
    <kbd>1-finger drag</kbd><span>Pan the canvas</span><kbd>2-finger</kbd><span>Pinch to zoom / pan</span>
    <kbd>Library</kbd><span>Tap to place in center, or drag to target</span>
    <kbd>Tap item</kbd><span>Drag to move; drag top dot to rotate, corner to resize</span>
    <kbd>Toolbar</kbd><span>Rotate / duplicate / delete at bottom</span>
    <kbd>Measure</kbd><span>Drag a line or tap two points</span>
    <kbd>3D walk</kbd><span>Joystick moves, drag screen looks, tap doors</span>
  </div></section>`) : ''}"""
    content = re.sub(pattern_touch, new_touch, content)

    pattern_kbd = r"\$\{tr\(`<section><h3>键盘快捷键</h3>[\s\S]*?`\)\}"
    new_kbd = """${tr(`<section><h3>اختصارات لوحة المفاتيح</h3><div class="kbd">
    <kbd>سحب الأثاث</kbd><span>اسحب من المكتبة إلى المخطط</span><kbd>V</kbd><span>تحديد / تحريك</span><kbd>M</kbd><span>قياس الأبعاد (Shift للأفقي/العمودي)</span>
    <kbd>X</kbd><span>تعديل الجدران (الأسود جدار حامل)</span><kbd>R</kbd><span>تدوير 90° (Shift للعكس)</span><kbd>الأسهم</kbd><span>تحريك دقيق 10mm (مع Shift 100mm)</span>
    <kbd>Ctrl+D</kbd><span>تكرار العنصر</span><kbd>Delete</kbd><span>حذف</span><kbd>Ctrl+Z</kbd><span>تراجع</span><kbd>T</kbd><span>تبديل 2D / 3D</span><kbd>F</kbd><span>ملاءمة الشاشة</span><kbd>Esc</kbd><span>إلغاء التحديد</span>
  </div></section>`, `<section><h3>Keyboard Shortcuts</h3><div class="kbd">
    <kbd>Drag</kbd><span>Drag furniture onto the plan</span><kbd>V</kbd><span>Select / move</span><kbd>M</kbd><span>Measure (Shift: horizontal/vertical)</span>
    <kbd>X</kbd><span>Demolish non-bearing walls</span><kbd>R</kbd><span>Rotate 90° (Shift: reverse)</span><kbd>Arrow keys</kbd><span>Nudge 10mm (Shift: 100mm)</span>
    <kbd>Ctrl+D</kbd><span>Duplicate</span><kbd>Delete</kbd><span>Delete</span><kbd>Ctrl+Z</kbd><span>Undo</span><kbd>T</kbd><span>Toggle 2D / 3D</span><kbd>F</kbd><span>Fit to window</span><kbd>Esc</kbd><span>Deselect</span>
  </div></section>`)}"""
    content = re.sub(pattern_kbd, new_kbd, content)

    old_confirm = "if (!confirm(tr(`确定清空全部 ${n} 件家具 / 家电吗？\\n墙体、地面材料和测量线会保留，可点「撤销」恢复。`, `Remove all ${n} furniture / appliance items?\\nWalls, flooring and measurements are kept. You can Undo this.`))) return;"
    new_confirm = "if (!confirm(tr(`هل أنت متأكد من تفريغ كافة قطع الأثاث (${n} قطعة)؟\\nالجدران، خامات الأرضيات، وخطوط القياس ستبقى، ويمكن التراجع.`, `Remove all ${n} furniture / appliance items?\\nWalls, flooring and measurements are kept. You can Undo this.`))) return;"
    content = content.replace(old_confirm, new_confirm)

    old_tglib = "vis('lib') ? tr('收起家具库 ( [ )', 'Hide library ( [ )') : tr('展开家具库 ( [ )', 'Show library ( [ )')"
    new_tglib = "vis('lib') ? tr('إخفاء مكتبة الأثاث ( [ )', 'Hide library ( [ )') : tr('عرض مكتبة الأثاث ( [ )', 'Show library ( [ )')"
    content = content.replace(old_tglib, new_tglib)

    old_tgpanel = "vis('panel') ? tr('收起属性面板 ( ] )', 'Hide properties ( ] )') : tr('展开属性面板 ( ] )', 'Show properties ( ] )')"
    new_tgpanel = "vis('panel') ? tr('إخفاء لوحة الخصائص ( ] )', 'Hide properties ( ] )') : tr('عرض لوحة الخصائص ( ] )', 'Show properties ( ] )')"
    content = content.replace(old_tgpanel, new_tgpanel)

    old_wall = "<div class=\"muted\">${tr(`墙面面积（层高 2.8m，未扣门窗）约 ${fmt(perim(r.poly)*2.8,1)} m²`, `Wall area (2.8m ceiling, openings not deducted) ≈ ${fmt(perim(r.poly)*2.8,1)} m²`)}</div></section>"
    new_wall = "<div class=\"muted\">${tr(`مساحة الجدران (ارتفاع 2.8m، دون خصم الفتحات) حوالي ${fmt(perim(r.poly)*2.8,1)} م²`, `Wall area (2.8m ceiling, openings not deducted) ≈ ${fmt(perim(r.poly)*2.8,1)} م²`)}</div></section>"
    content = content.replace(old_wall, new_wall)

    content = content.replace("tr(`${inside.length} 件`, `${inside.length} items`)", "tr(`${inside.length} قطعة`, `${inside.length} items`)")

    old_snap_tip = '<section class="muted" style="font-size:12px">${tr(\'拖动家具移动；拖动上方圆点旋转；拖动右下角方块调整尺寸。开启「贴墙吸附」后靠近墙面会自动贴齐。\', \'Drag to move; drag the top dot to rotate; drag the bottom-right square to resize. With "Wall snap" on, items snap flush to nearby walls.\')}</section>'
    new_snap_tip = '<section class="muted" style="font-size:12px">${tr(\'اسحب القطعة للتحريك، اسحب النقطة العلوية للتدوير، واسحب الزاوية لتعديل المقاس. تفعيل «محاذاة للجدار» يجعل الأثاث يلتصق بالجدار تلقائياً.\', \'Drag to move; drag the top dot to rotate; drag the bottom-right square to resize. With "Wall snap" on, items snap flush to nearby walls.\')}</section>'
    content = content.replace(old_snap_tip, new_snap_tip)

    content = content.replace(
        'toast(tr(`已添加「${name}」${w}×${d}`, `Added "${nm(name)}" ${w}×${d}`));',
        'toast(tr(`تمت إضافة «${nm(name)}» ${w}×${d}`, `Added "${nm(name)}" ${w}×${d}`));'
    )
    old_dem_toast = 'toast(on ? tr(\'已恢复墙体\', \'Wall restored\') : tr(`已标记拆除 ${Math.max(w[2]-w[0], w[3]-w[1])} mm 墙体`, `Marked ${Math.max(w[2]-w[0], w[3]-w[1])} mm of wall for removal`));'
    new_dem_toast = 'toast(on ? tr(\'تمت استعادة الجدار\', \'Wall restored\') : tr(`تم تحديد إزالة ${Math.max(w[2]-w[0], w[3]-w[1])} mm من الجدار`, `Marked ${Math.max(w[2]-w[0], w[3]-w[1])} mm of wall for removal`));'
    content = content.replace(old_dem_toast, new_dem_toast)

    old_md_hints = """    measure:COARSE ? tr('按住拖出测量线，或依次点两点 · 靠近墙面自动吸附 · 点「选择」退出', 'Hold and drag a line, or tap two points · snaps to walls · tap "Select" to exit')
      : tr('点击两点（或按住拖动）测量距离 · 靠近墙面自动吸附 · Shift 锁定水平/垂直 · Esc 取消', 'Click two points (or drag) to measure · snaps to walls · Shift locks horizontal/vertical · Esc cancels'),
    demolish:tr('点击灰色非承重墙标记拆除，再次点击恢复 · 黑色承重墙不可拆', 'Click a grey non-bearing wall to remove it, click again to restore · black bearing walls cannot be removed')};"""
    new_md_hints = """    measure:COARSE ? tr('اسحب لرسم خط القياس، أو انقر نقطتين · محاذاة تلقائية للجدران · اضغط «تحديد» للخروج', 'Hold and drag a line, or tap two points · snaps to walls · tap "Select" to exit')
      : tr('انقر نقطتين (أو اسحب) لقياس المسافة · محاذاة تلقائية للجدران · Shift لقفل الاتجاه أفقي/عمودي · Esc للإلغاء', 'Click two points (or drag) to measure · snaps to walls · Shift locks horizontal/vertical · Esc cancels'),
    demolish:tr('انقر على الجدار غير الحامل لتحديده للإزالة، وانقر ثانية للاستعادة · الجدران الحاملة الإنشائية لا يمكن إزالتها', 'Click a grey non-bearing wall to remove it, click again to restore · black bearing walls cannot be removed')};"""
    content = content.replace(old_md_hints, new_md_hints)

    old_lib_item = 'return `<div class="item" data-key="${ci}:${ii}" title="${tr(\'点击添加，或拖到平面图中的指定位置\', \'Click to add, or drag onto the plan\')}">'
    new_lib_item = 'return `<div class="item" data-key="${ci}:${ii}" title="${tr(\'اضغط للإضافة، أو اسحب للموضع المطلوب في المخطط\', \'Click to add, or drag onto the plan\')}">'
    content = content.replace(old_lib_item, new_lib_item)

    old_lib_desc = "`家具按真实尺寸（mm）绘制。${COARSE ? '点一下放到画面中央，或按住向右拖到平面图 / 3D 地面上的指定位置（上下滑动为滚动列表）。' : '点击添加到画面中央，或直接拖到平面图 / 3D 地面上。'}添加后可在右侧修改宽深与颜色。`"
    new_lib_desc = "`الأثاث مرسوم بمقاساته الحقيقية (mm). ${COARSE ? 'اضغط للإضافة في المركز، أو اسحب للموضع المطلوب داخل المخطط.' : 'اضغط للإضافة في المركز، أو اسحب مباشرة إلى المخطط أو المشهد ثلاثي الأبعاد.'} يمكنك تعديل المقاسات والألوان من لوحة الخصائص.`"
    content = content.replace(old_lib_desc, new_lib_desc)

    old_s60 = "toast(tr('已按 1:60 显示（与原始户型图同比例）', 'Showing at 1:60 (same scale as the original plan)'))"
    new_s60 = "toast(tr('معروض بمقياس 1:60 (مطابق لمقياس المخطط الأصلي)', 'Showing at 1:60 (same scale as the original plan)'))"
    content = content.replace(old_s60, new_s60)

    old_fs = 'if (!req) return toast(tr(\'当前浏览器不支持网页全屏，可在 Safari 中「添加到主屏幕」后以全屏方式打开\', \'Fullscreen is not supported here — in Safari, use "Add to Home Screen" to open it fullscreen\'));'
    new_fs = 'if (!req) return toast(tr(\'المتصفح الحالي لا يدعم وضع ملء الشاشة، يمكن إضافته للشاشة الرئيسية للاستمتاع بملء الشاشة\', \'Fullscreen is not supported here — in Safari, use "Add to Home Screen" to open it fullscreen\'));'
    content = content.replace(old_fs, new_fs)

    # 19. Currency replacement
    content = content.replace("¥${Math.round(c).toLocaleString()}", "${Math.round(c).toLocaleString()} ر.س")
    content = content.replace("¥${Math.round(cost).toLocaleString()}", "${Math.round(cost).toLocaleString()} ر.س")
    content = content.replace("¥${Math.round(area(r.poly)*MATS[st.mat].price*1.05).toLocaleString()}", "${Math.round(area(r.poly)*MATS[st.mat].price*1.05).toLocaleString()} ر.س")

    # Write files
    with open(house_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Clean build successful!")
    print(f"Generated {len(walls)} walls, {len(wins)} windows, {len(doors)} doors, {len(slides)} sliding doors.")
    print(f"Generated {len(rooms)} rooms, {len(furniture)} furniture items.")

if __name__ == '__main__':
    build()
