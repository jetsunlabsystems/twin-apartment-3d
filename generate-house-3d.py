import json
import re

# Building Dimensions (mm):
# Width: 15800 mm
# Depth: 26210 mm
# Center X: 7900 mm

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
    Y_KIT_N     = 17950
    Y_KIT_S     = 18100
    Y_GBATH_N   = 19250
    Y_GBATH_S   = 19400
    Y_REC_N     = 24200
    Y_REC_S     = 24400
    Y_TERR_FRONT= 25500

    # -------------------------------------------------------------
    # 2. Cutout-Aware Wall System
    # -------------------------------------------------------------
    # Every wall is defined as a span with thickness, and cut by openings!
    walls = []
    wins = []
    doors = []
    slides = []

    def add_rect_wall(x0, y0, x1, y1, wtype='e'):
        rx0, rx1 = min(x0, x1), max(x0, x1)
        ry0, ry1 = min(y0, y1), max(y0, y1)
        if rx1 - rx0 < 1 or ry1 - ry0 < 1:
            return
        walls.append([rx0, ry0, rx1, ry1, wtype])

    def cut_h_wall(y0, y1, x_start, x_end, cuts, wtype='e'):
        """Cuts a horizontal wall [x_start..x_end] along Y [y0..y1] with openings."""
        # cuts is list of (c_x0, c_x1, kind, data)
        cuts = sorted(cuts, key=lambda c: c[0])
        cur_x = x_start
        for cx0, cx1, kind, data in cuts:
            if cx0 > cur_x:
                add_rect_wall(cur_x, y0, cx0, y1, wtype)
            # Add opening
            rect = [min(cx0, cx1), min(y0, y1), max(cx0, cx1), max(y0, y1)]
            if kind == 'win':
                wins.append(rect)
            elif kind == 'door':
                data['rect'] = rect
                doors.append(data)
            elif kind == 'slide':
                slides.append({'rect': rect, 'v': False})
            cur_x = cx1
        if cur_x < x_end:
            add_rect_wall(cur_x, y0, x_end, y1, wtype)

    def cut_v_wall(x0, x1, y_start, y_end, cuts, wtype='e'):
        """Cuts a vertical wall [y_start..y_end] along X [x0..x1] with openings."""
        cuts = sorted(cuts, key=lambda c: c[0])
        cur_y = y_start
        for cy0, cy1, kind, data in cuts:
            if cy0 > cur_y:
                add_rect_wall(x0, cur_y, x1, cy0, wtype)
            rect = [min(x0, x1), min(cy0, cy1), max(x0, x1), max(cy0, cy1)]
            if kind == 'win':
                wins.append(rect)
            elif kind == 'door':
                data['rect'] = rect
                doors.append(data)
            elif kind == 'slide':
                slides.append({'rect': rect, 'v': True})
            cur_y = cy1
        if cur_y < y_end:
            add_rect_wall(x0, cur_y, x1, y_end, wtype)

    # --- TOP EXTERIOR WALL (Y: -200 to 0) ---
    top_cuts_l = [
        (1200, 2600, 'win', None), # Master Bed Window
        (5200, 6600, 'win', None), # Bedroom 2 Window
    ]
    cut_h_wall(Y_TOP_OUT, Y_TOP_IN, X_EXT_L_OUT, X_CTR_MID, top_cuts_l, 'b')

    top_cuts_r = [
        (mirror_x(6600), mirror_x(5200), 'win', None), # Bedroom 2 Window
        (mirror_x(2600), mirror_x(1200), 'win', None), # Master Bed Window
    ]
    cut_h_wall(Y_TOP_OUT, Y_TOP_IN, X_CTR_MID, X_EXT_R_OUT, top_cuts_r, 'b')

    # --- LEFT EXTERIOR WALL (X: -200 to 0) ---
    left_cuts = [
        (1600, 3200, 'win', None),   # Master Bed left window
        (8200, 9800, 'win', None),   # Bedroom 1 left window
        (12200, 14000, 'win', None), # Living Room window
        (15600, 17000, 'win', None), # Kitchen window
        (20600, 22600, 'win', None), # Reception window
    ]
    cut_v_wall(X_EXT_L_OUT, X_EXT_L_IN, Y_TOP_IN, Y_REC_S, left_cuts, 'b')

    # --- RIGHT EXTERIOR WALL (X: 15800 to 16000) ---
    right_cuts = [
        (1600, 3200, 'win', None),
        (8200, 9800, 'win', None),
        (12200, 14000, 'win', None),
        (15600, 17000, 'win', None),
        (20600, 22600, 'win', None),
    ]
    cut_v_wall(X_EXT_R_IN, X_EXT_R_OUT, Y_TOP_IN, Y_REC_S, right_cuts, 'b')

    # --- FRONT RECEPTION WALLS & TERRACES ---
    # Left Reception Front (Y: 24200 to 24400)
    front_cuts_l = [
        (800, 3400, 'slide', None),  # Terrace Sliding Glass Door
        (4800, 6800, 'win', None),   # Reception Front Window
    ]
    cut_h_wall(Y_REC_N, Y_REC_S, X_EXT_L_IN, X_CTR_MID, front_cuts_l, 'b')

    # Right Reception Front (Y: 24200 to 24400)
    front_cuts_r = [
        (mirror_x(6800), mirror_x(4800), 'win', None),
        (mirror_x(3400), mirror_x(800), 'slide', None),
    ]
    cut_h_wall(Y_REC_N, Y_REC_S, X_CTR_MID, X_EXT_R_IN, front_cuts_r, 'b')

    # Terrace Balcony Parapets (low glass / wall railing at 1.0m)
    add_rect_wall(X_EXT_L_IN, Y_REC_S, X_EXT_L_IN + 150, Y_TERR_FRONT, 'low')
    add_rect_wall(X_EXT_L_IN, Y_TERR_FRONT - 150, X_M1_L_W, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_L_W - 150, Y_REC_S, X_M1_L_W, Y_TERR_FRONT, 'low')

    add_rect_wall(X_M1_R_E, Y_REC_S, X_M1_R_E + 150, Y_TERR_FRONT, 'low')
    add_rect_wall(X_M1_R_E, Y_TERR_FRONT - 150, X_EXT_R_IN, Y_TERR_FRONT, 'low')
    add_rect_wall(X_EXT_R_IN - 150, Y_REC_S, X_EXT_R_IN, Y_TERR_FRONT, 'low')

    # --- CENTRAL SPINE WALL (Y: 0 to Y_LW_N: 7150) ---
    add_rect_wall(X_CTR_W, Y_TOP_IN, X_CTR_E, Y_LW_N, 'b')

    # --- LIGHTWELL (منور) BOX (Y_LW_N to Y_B1_S, X_LW_L_W to X_LW_R_E) ---
    # Top Wall of Lightwell
    add_rect_wall(X_LW_L_W, Y_LW_N, X_LW_R_E, Y_LW_S, 'b')
    # West Wall of Lightwell with window
    lw_w_cuts = [(8600, 9800, 'win', None)]
    cut_v_wall(X_LW_L_W, X_LW_L_E, Y_LW_S, Y_B1_S, lw_w_cuts, 'b')
    # East Wall of Lightwell with window
    lw_e_cuts = [(8600, 9800, 'win', None)]
    cut_v_wall(X_LW_R_W, X_LW_R_E, Y_LW_S, Y_B1_S, lw_e_cuts, 'b')
    # South Wall of Lightwell
    add_rect_wall(X_LW_L_W, Y_B1_N, X_LW_R_E, Y_B1_S, 'b')

    # --- STAIRCASE & ENTRANCE CORE (Y_B1_S to Y_ST_S, X_ST_L_W to X_ST_R_E) ---
    add_rect_wall(X_ST_L_W, Y_B1_S, X_ST_L_E, Y_ST_S, 'b')
    add_rect_wall(X_ST_R_W, Y_B1_S, X_ST_R_E, Y_ST_S, 'b')
    # South Landing Wall with Two Main Apartment Entrance Doors
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

    # Central party wall separating receptions (Y_ST_S to Y_REC_N)
    add_rect_wall(X_CTR_W, Y_ST_S, X_CTR_E, Y_REC_N, 'b')

    # --- LEFT APARTMENT INTERIOR PARTITIONS ---
    # Master Bedroom Divider (Vertical)
    add_rect_wall(X_M1_L_W, Y_TOP_IN, X_M1_L_E, Y_M_S, 'n')
    # Master Bedroom South Wall (Horizontal)
    add_rect_wall(X_EXT_L_IN, Y_M_N, X_M1_L_E, Y_M_S, 'n')
    # Bedroom 2 South Wall (with Door)
    b2_cuts_l = [
        (4600, 5500, 'door', {
            'name': 'باب غرفة نوم 2 (Left)',
            'h': [4600, Y_B2_N], 'c': [1, 0], 'o': [0, -1], 'len': 850
        })
    ]
    cut_h_wall(Y_B2_N, Y_B2_S, X_M1_L_E, X_CTR_W, b2_cuts_l, 'n')

    # Master Bathroom & Walk-in Closet (ملابس وحمام)
    X_MBATH_DIV = (X_EXT_L_IN + X_M1_L_W) // 2
    mbath_div_cuts = [
        (5600, 6400, 'door', {
            'name': 'باب حمام الماستر (Left)',
            'h': [X_MBATH_DIV, 5600], 'c': [0, 1], 'o': [-1, 0], 'len': 780
        })
    ]
    cut_v_wall(X_MBATH_DIV - 100, X_MBATH_DIV, Y_M_S, Y_MBATH_N, mbath_div_cuts, 'n')

    mbath_s_cuts = [
        (2600, 3600, 'door', {
            'name': 'باب جناح الماستر (Left)',
            'h': [3600, Y_MBATH_N], 'c': [-1, 0], 'o': [0, -1], 'len': 900
        })
    ]
    cut_h_wall(Y_MBATH_N, Y_MBATH_S, X_EXT_L_IN, X_M1_L_E, mbath_s_cuts, 'n')

    # Laundry & Central Bath
    laund_cuts = [
        (4600, 5400, 'door', {
            'name': 'باب الغسيل (Left)',
            'h': [4600, Y_LAUND_N], 'c': [1, 0], 'o': [0, -1], 'len': 750
        })
    ]
    cut_h_wall(Y_LAUND_N, Y_LAUND_S, X_M1_L_E, X_CTR_W, laund_cuts, 'n')

    cbath_cuts = [
        (4600, 5400, 'door', {
            'name': 'باب الحمام العائلي (Left)',
            'h': [4600, Y_LW_N], 'c': [1, 0], 'o': [0, -1], 'len': 750
        })
    ]
    cut_h_wall(Y_LW_N, Y_LW_S, X_M1_L_E, X_CTR_W, cbath_cuts, 'n')
    add_rect_wall(X_M1_L_W, Y_B2_S, X_M1_L_E, Y_LW_S, 'n')

    # Bedroom 1 (East Wall with Door & South Wall)
    b1_e_cuts = [
        (9600, 10500, 'door', {
            'name': 'باب غرفة نوم 1 (Left)',
            'h': [X_B1_L_E, 10500], 'c': [0, -1], 'o': [-1, 0], 'len': 850
        })
    ]
    cut_v_wall(X_B1_L_W, X_B1_L_E, Y_MBATH_S, Y_B1_S, b1_e_cuts, 'n')
    add_rect_wall(X_EXT_L_IN, Y_B1_N, X_B1_L_W, Y_B1_S, 'n')

    # Living Room South Wall
    add_rect_wall(X_EXT_L_IN, Y_LIV_N, X_B1_L_W, Y_LIV_S, 'n')

    # Kitchen (East Wall with Door & South Wall)
    kit_e_cuts = [
        (16600, 17500, 'door', {
            'name': 'باب المطبخ (Left)',
            'h': [X_B1_L_E, 16600], 'c': [0, 1], 'o': [-1, 0], 'len': 850
        })
    ]
    cut_v_wall(X_B1_L_W, X_B1_L_E, Y_LIV_S, Y_KIT_S, kit_e_cuts, 'n')
    add_rect_wall(X_EXT_L_IN, Y_KIT_N, X_B1_L_W, Y_KIT_S, 'n')

    # Guest Bathroom & Reception Doorway
    gbath_div_cuts = [
        (18500, 19300, 'door', {
            'name': 'باب حمام الضيوف (Left)',
            'h': [2600, 18500], 'c': [0, 1], 'o': [-1, 0], 'len': 750
        })
    ]
    cut_v_wall(2500, 2600, Y_KIT_S, Y_GBATH_N, gbath_div_cuts, 'n')

    rec_entry_cuts_l = [
        (3000, 4200, 'door', {
            'name': 'باب صالون الاستقبال (Left)',
            'h': [3000, Y_GBATH_N], 'c': [1, 0], 'o': [0, 1], 'len': 1050
        })
    ]
    cut_h_wall(Y_GBATH_N, Y_GBATH_S, X_EXT_L_IN, X_B1_L_E, rec_entry_cuts_l, 'n')
    add_rect_wall(X_B1_L_W, Y_KIT_S, X_B1_L_E, Y_GBATH_S, 'n')

    # --- RIGHT APARTMENT INTERIOR PARTITIONS (MIRRORED) ---
    add_rect_wall(X_M1_R_W, Y_TOP_IN, X_M1_R_E, Y_M_S, 'n')
    add_rect_wall(X_M1_R_W, Y_M_N, X_EXT_R_IN, Y_M_S, 'n')

    b2_cuts_r = [
        (mirror_x(5500), mirror_x(4600), 'door', {
            'name': 'باب غرفة نوم 2 (Right)',
            'h': [mirror_x(4600), Y_B2_N], 'c': [-1, 0], 'o': [0, -1], 'len': 850
        })
    ]
    cut_h_wall(Y_B2_N, Y_B2_S, X_CTR_E, X_M1_R_W, b2_cuts_r, 'n')

    X_MBATH_DIV_R = mirror_x(X_MBATH_DIV)
    mbath_div_cuts_r = [
        (5600, 6400, 'door', {
            'name': 'باب حمام الماستر (Right)',
            'h': [X_MBATH_DIV_R, 5600], 'c': [0, 1], 'o': [1, 0], 'len': 780
        })
    ]
    cut_v_wall(X_MBATH_DIV_R, X_MBATH_DIV_R + 100, Y_M_S, Y_MBATH_N, mbath_div_cuts_r, 'n')

    mbath_s_cuts_r = [
        (mirror_x(3600), mirror_x(2600), 'door', {
            'name': 'باب جناح الماستر (Right)',
            'h': [mirror_x(3600), Y_MBATH_N], 'c': [1, 0], 'o': [0, -1], 'len': 900
        })
    ]
    cut_h_wall(Y_MBATH_N, Y_MBATH_S, X_M1_R_W, X_EXT_R_IN, mbath_s_cuts_r, 'n')

    laund_cuts_r = [
        (mirror_x(5400), mirror_x(4600), 'door', {
            'name': 'باب الغسيل (Right)',
            'h': [mirror_x(4600), Y_LAUND_N], 'c': [-1, 0], 'o': [0, -1], 'len': 750
        })
    ]
    cut_h_wall(Y_LAUND_N, Y_LAUND_S, X_CTR_E, X_M1_R_W, laund_cuts_r, 'n')

    cbath_cuts_r = [
        (mirror_x(5400), mirror_x(4600), 'door', {
            'name': 'باب الحمام العائلي (Right)',
            'h': [mirror_x(4600), Y_LW_N], 'c': [-1, 0], 'o': [0, -1], 'len': 750
        })
    ]
    cut_h_wall(Y_LW_N, Y_LW_S, X_CTR_E, X_M1_R_W, cbath_cuts_r, 'n')
    add_rect_wall(X_M1_R_W, Y_B2_S, X_M1_R_E, Y_LW_S, 'n')

    b1_e_cuts_r = [
        (9600, 10500, 'door', {
            'name': 'باب غرفة نوم 1 (Right)',
            'h': [X_B1_R_W, 10500], 'c': [0, -1], 'o': [1, 0], 'len': 850
        })
    ]
    cut_v_wall(X_B1_R_W, X_B1_R_E, Y_MBATH_S, Y_B1_S, b1_e_cuts_r, 'n')
    add_rect_wall(X_B1_R_E, Y_B1_N, X_EXT_R_IN, Y_B1_S, 'n')

    add_rect_wall(X_B1_R_E, Y_LIV_N, X_EXT_R_IN, Y_LIV_S, 'n')

    kit_e_cuts_r = [
        (16600, 17500, 'door', {
            'name': 'باب المطبخ (Right)',
            'h': [X_B1_R_W, 16600], 'c': [0, 1], 'o': [1, 0], 'len': 850
        })
    ]
    cut_v_wall(X_B1_R_W, X_B1_R_E, Y_LIV_S, Y_KIT_S, kit_e_cuts_r, 'n')
    add_rect_wall(X_B1_R_E, Y_KIT_N, X_EXT_R_IN, Y_KIT_S, 'n')

    gbath_div_cuts_r = [
        (18500, 19300, 'door', {
            'name': 'باب حمام الضيوف (Right)',
            'h': [mirror_x(2600), 18500], 'c': [0, 1], 'o': [1, 0], 'len': 750
        })
    ]
    cut_v_wall(mirror_x(2600), mirror_x(2500), Y_KIT_S, Y_GBATH_N, gbath_div_cuts_r, 'n')

    rec_entry_cuts_r = [
        (mirror_x(4200), mirror_x(3000), 'door', {
            'name': 'باب صالون الاستقبال (Right)',
            'h': [mirror_x(3000), Y_GBATH_N], 'c': [-1, 0], 'o': [0, 1], 'len': 1050
        })
    ]
    cut_h_wall(Y_GBATH_N, Y_GBATH_S, X_B1_R_W, X_EXT_R_IN, rec_entry_cuts_r, 'n')
    add_rect_wall(X_B1_R_W, Y_KIT_S, X_B1_R_E, Y_GBATH_S, 'n')

    # -------------------------------------------------------------
    # 3. Clean Interior Floor Polygons (Inside Wall Clearances)
    # -------------------------------------------------------------
    def R_inner(x0, y0, x1, y1):
        return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

    rooms = [
        # Left Unit
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

    # -------------------------------------------------------------
    # 4. Refined Furniture Placements (Centered and Realistic)
    # -------------------------------------------------------------
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
        ("tv", "65 寸电视", 4000, 12700, 1450, 80, 180, None),

        # Left Kitchen
        ("counter", "رخام مطبخ كاونتر", 700, 16300, 1600, 600, 0, None),
        ("stove", "بوتجاز غاز", 1900, 15100, 750, 450, 0, None),
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

def generate():
    walls, wins, doors, slides, rooms, furniture = build_refined_house()

    import os
    src_path = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d\index.upstream-demo.html"
    if not os.path.exists(src_path):
        src_path = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d\index.html"
    dst_path = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d\house-3d.html"
    index_path = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d\index.html"

    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Format architecture
    arch_lines = [
        "const WALLS = [\n" + ",\n".join(f"  {json.dumps(w)}" for w in walls) + "\n];",
        "const WINS = [\n" + ",\n".join(f"  {json.dumps(w)}" for w in wins) + "\n];",
        "const DOORS = [\n" + ",\n".join(f"  {json.dumps(d, ensure_ascii=False)}" for d in doors) + "\n];",
        "const SLIDES = [\n" + ",\n".join(f"  {json.dumps(s)}" for s in slides) + "\n];",
        "const R = (x0,y0,x1,y1) => [[x0,y0],[x1,y0],[x1,y1],[x0,y1]];",
        "const ROOMS = [\n" + ",\n".join(f"  {{id:{json.dumps(r['id'])}, name:{json.dumps(r['name'], ensure_ascii=False)}, poly:{json.dumps(r['poly'])}, mat:{json.dumps(r['mat'])}, at:{json.dumps(r['at'])}}}" for r in rooms) + "\n];"
    ]
    arch_block = "\n\n".join(arch_lines)

    # Format furniture
    furn_lines = []
    for f in furniture:
        t, nm, cx, cy, w, d, rot, c = f
        col = f",'{c}'" if c else ""
        furn_lines.append(f"  F('{t}','{nm}',{cx},{cy},{w},{d},{rot}{col})")
    furn_block = "function defaultFurniture(){\n  return [\n" + ",\n".join(furn_lines) + "\n  ];\n}"

    # 1. Replace BOUNDS
    content = re.sub(
        r"const BOUNDS = \{x:[^,]+, y:[^,]+, w:[^,]+, h:[^}]+\};",
        "const BOUNDS = {x:-2000, y:-2000, w:19800, h:30200};",
        content
    )

    # 2. Replace OX, OY, H
    content = re.sub(
        r"const OX = \d+, OY = \d+, H = [^,]+, FOV = \d+;",
        "const OX = 7900, OY = 13100, H = 2.8, FOV = 45;",
        content
    )

    # 3. Replace architecture data (WALLS to ROOMS), keeping MATS and LIB untouched
    pattern_arch = r"const WALLS = \[[\s\S]*?const ROOMS = \[[\s\S]*?\];"
    content = re.sub(pattern_arch, arch_block, content)

    # 4. Replace defaultFurniture()
    pattern_furn = r"function defaultFurniture\(\)\{[\s\S]*?\];\}"
    content = re.sub(pattern_furn, furn_block, content)

    # 5. Enrich floor textures in TEX for deep rich contrast
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

    # 6. Ensure unique STORE key
    content = content.replace("const STORE = 'huxing-design-v1';", "const STORE = 'twin-apartment-house-3d-v4';")

    # 7. Update title
    content = content.replace("<title>户型装修设计</title>", "<title>Twin Apartment Luxury Floor Plan 3D</title>")

    # 8. Shadow camera & orbit limits
    content = content.replace(
        "Object.assign(sun.shadow.camera, {left:-11, right:11, top:11, bottom:-11, near:1, far:60});",
        "Object.assign(sun.shadow.camera, {left:-18, right:18, top:18, bottom:-18, near:1, far:90});"
    )
    content = content.replace(
        "orbit.enableDamping = true; orbit.maxPolarAngle = Math.PI*.495; orbit.minDistance = 1.5; orbit.maxDistance = 45;",
        "orbit.enableDamping = true; orbit.maxPolarAngle = Math.PI*.495; orbit.minDistance = 1.5; orbit.maxDistance = 85;"
    )

    # 9. TopWhole & walkthrough pose
    content = content.replace(
        "const topWhole = () => pose(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 19, 1e-4));",
        "const topWhole = () => pose(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 30, 1e-4));"
    )
    content = content.replace(
        "camera.position.set(wx(4200), 1.6, wz(8755)); camera.lookAt(wx(7000), 1.5, wz(8755));   // 入户门外",
        "camera.position.set(wx(7900), 1.6, wz(15200)); camera.lookAt(wx(7900), 1.5, wz(13000));   // Apartment landing"
    )

    # 10. Clean bay window lintels
    content = content.replace(
        "[[10270,800,10510,2600], 2.4], [[10270,4260,10510,5740], 2.4]",
        ""
    )

    # 11. Add 3D U-shaped Stairs and Panoramic Glass Elevator
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

    # 12. Add 2D Staircase, Elevator & Dual Unit Entrance SVG in renderOpenings()
    old_entry_svg = (
        '  // 入户标识\n'
        '  s += `<path d="M3350 8755H4350M4150 8600L4400 8755L4150 8910" fill="none" stroke="#b5653a" stroke-width="2" vector-effect="non-scaling-stroke"/>\n'
        '        <text x="3380" y="8600" font-size="200" fill="#b5653a">${tr(\'入户\',\'Entry\')}</text>`;'
    )
    assert old_entry_svg in content, "old_entry_svg not found!"
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

    content = content.replace(old_entry_svg, new_entry_svg)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Apply comprehensive Tajawal Arabic localization
    try:
        from localize_tajawal_arabic import localize_content
        from localize_all_arabic import run as run_arabic_loc
        run_arabic_loc()
    except Exception as e:
        print("Localization warning:", e)

    print("Refined generation successful!")
    print(f"Generated {len(walls)} walls, {len(wins)} windows, {len(doors)} doors, {len(slides)} sliding doors.")
    print(f"Generated {len(rooms)} rooms, {len(furniture)} furniture items.")

if __name__ == '__main__':
    generate()
