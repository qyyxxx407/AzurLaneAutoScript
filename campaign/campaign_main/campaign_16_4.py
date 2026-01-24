from module.map.map_base import CampaignMap
from module.map.map_grids import SelectedGrids, RoadGrids
from module.logger import logger

from .campaign_16_base_aircraft import CampaignBase
from .campaign_16_base_aircraft import Config as ConfigBase

MAP = CampaignMap('16-4')
MAP.shape = 'K8'
MAP.camera_data = ['C2', 'C6', 'F2', 'F6', 'H2', 'H7']
MAP.camera_data_spawn_point = ['C6']
MAP.camera_sight = (-2, -1, 3, 2)
MAP.map_data = """
    -- -- ++ -- -- -- ++ ME -- -- MB
    ME ++ ++ ++ -- -- ME ++ -- -- --
    -- -- ME -- -- ++ ++ ME -- -- --
    -- -- -- ME ++ -- ME -- ++ ++ --
    -- -- ME -- -- ME ++ -- ME ++ --
    -- __ -- ++ ++ -- ++ ME ME -- --
    SP -- -- ME -- -- ME ++ -- ++ ++
    SP -- -- -- ++ -- ++ ++ -- -- ++
"""
MAP.weight_data = """
    50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 40 50 50 50
    50 50 50 40 50 40 40 40 50 50 50
    50 50 50 40 40 40 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50
    50 50 50 50 50 50 50 50 50 50 50
"""
# ========== 修改点1：调整战斗阶段配置 ==========
# 原battle_2拆分为battle_2(G4)、battle_3(H6)、battle_4(H4)
# 原BOSS战battle_4调整为battle_5
MAP.spawn_data = [
    {'battle': 0, 'enemy': 5},
    {'battle': 1, 'enemy': 4},
    {'battle': 2, 'enemy': 5},  # 新增：G4战斗
    {'battle': 3, 'enemy': 5},  # 新增：H6战斗
    {'battle': 4, 'enemy': 5},  # 新增：H4战斗
    {'battle': 5, 'boss': 1},   # BOSS战顺延到battle_5
]
A1, B1, C1, D1, E1, F1, G1, H1, I1, J1, K1, \
A2, B2, C2, D2, E2, F2, G2, H2, I2, J2, K2, \
A3, B3, C3, D3, E3, F3, G3, H3, I3, J3, K3, \
A4, B4, C4, D4, E4, F4, G4, H4, I4, J4, K4, \
A5, B5, C5, D5, E5, F5, G5, H5, I5, J5, K5, \
A6, B6, C6, D6, E6, F6, G6, H6, I6, J6, K6, \
A7, B7, C7, D7, E7, F7, G7, H7, I7, J7, K7, \
A8, B8, C8, D8, E8, F8, G8, H8, I8, J8, K8, \
    = MAP.flatten()

road_main = RoadGrids([D4, F5, G4, H3])

class Config(ConfigBase):
    MAP_HAS_MAP_STORY = False
    MAP_HAS_FLEET_STEP = False
    MAP_HAS_AMBUSH = True

class Campaign(CampaignBase):
    MAP = MAP

    def battle_0(self):
        # 强制固定出战位置：D4
        self.goto(D4)
        self.clear_chosen_enemy(D4)
        return True

    def battle_1(self):
        # 强制固定出战位置：F5
        self.goto(F5)
        self.clear_chosen_enemy(F5)
        return True

    # ========== 修改点2：拆分原battle_2为三个独立方法 ==========
    def battle_2(self):
        # 第一场：强制固定出战位置G4
        self.goto(G4)
        self.clear_chosen_enemy(G4)  # 清理G4位置敌人
        # 可选：保留路障清理逻辑（按需开启）
        # if self.clear_roadblocks([road_main]):
        #     return True
        return True

    def battle_3(self):
        # 第二场：强制固定出战位置H6
        self.goto(H6)
        self.clear_chosen_enemy(H6)  # 清理H6位置敌人
        # 可选：保留路障清理逻辑（按需开启）
        # if self.clear_roadblocks([road_main]):
        #     return True
        return True

    def battle_4(self):
        # 第三场：强制固定出战位置H4
        self.goto(H4)
        self.clear_chosen_enemy(H4)  # 清理H4位置敌人
        # 核心路障清理逻辑保留在H4战斗阶段
        if self.clear_roadblocks([road_main]):
            return True
        if self.clear_potential_roadblocks([road_main]):
            return True
        if self.clear_filter_enemy(self.ENEMY_FILTER, preserve=0):
            return True
        return self.battle_default()

    # ========== 修改点3：BOSS战方法从battle_4改为battle_5 ==========
    def battle_5(self):
        # BOSS战代码完全保留，仅方法名调整
        boss = self.map.select(is_boss=True)
        if boss:
            if not self.check_accessibility(boss[0], fleet='boss'):
                return self.clear_roadblocks([road_main])
            if self.use_support_fleet:
                # at this stage the most right zone should be accessible
                self.goto(J6)
            return self.fleet_boss.clear_boss()
        if self.clear_roadblocks([road_main]):
            return True
        if self.clear_potential_roadblocks([road_main]):
            return True
        if self.clear_filter_enemy(self.ENEMY_FILTER, preserve=0):
            return True
        return self.battle_default()
