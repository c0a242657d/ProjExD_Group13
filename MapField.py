import pygame
import random
import os

# --- 画面設定 ---
SCREEN_WIDTH = 800 # 画面縦
SCREEN_HEIGHT = 600 # 画面横
TILE_SIZE = 64 # タイルサイズ

COLORS = {
    0: (50, 180, 50), # 草
    1: (160, 130, 80), # 土
    2: (100, 100, 100), # 岩
    3: (200, 50, 50), # 火
    4: (0, 0, 255) # 水
}

# フィールド構成
MAP_FIELD = [
    [0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,2,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,2,0,0,0,0,0,0,4,4,4,1,1,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,3,3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,3,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,3,3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]


BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 現在のディレクトリ

def check_move(mapfield):
    """
    もしプレイヤーがx=24,y=9にいるなら次のワールドに移動する指示を返す
    引数:
        mapfield: MapFieldオブジェクト
    戻り値:
        True または None
    """
    if mapfield.player_x == 24 and mapfield.player_y == 9:
        return True
    return None

def load_image(path): # 画像読み込み
    """
    指定されたパスから画像を読み込む関数
    引数:
        path: 画像ファイルのパス
    戻り値:
        読み込んだ画像オブジェクト または None
    """
    full = os.path.join(BASE_DIR, path) # フルパス取得
    if os.path.exists(full): # ファイル存在確認
        return pygame.image.load(full).convert_alpha() # 画像読み込み
    return None # 画像なし

class MapField: # フィールド画面クラス
    def __init__(self, screen): # 初期化
        """
        __init__ の Docstring
        :param self: 説明
        :param screen: 説明
        """
        self.screen = screen # 画面情報
        self.map_data = MAP_FIELD # マップデータ

        self.player_x = 0 # プレイヤー座標
        self.player_y = 6 # プレイヤー座標

        self.move_cool = 0 # 移動クールタイム

        # プレイヤー画像読み込み
        self.tile_images = self.load_tiles() # タイル画像読み込み
        self.player_img_left = load_image("fig/map_mahou_l_1.png")
        self.player_img_right = load_image("fig/map_mahou_r_1.png")
        self.player_img_back = load_image("fig/map_mahou_b_1.png")
        self.player_img_flont = load_image("fig/map_mahou_1.png")
        self.player_img = self.player_img_flont # 初期画像

    def load_tiles(self): # タイル画像読み込み
        """
        load_tiles の Docstring
        :param self: 説明
        """
        tiles = {} # タイル画像辞書
        tiles[0] = load_image("fig/grass.png") # 草タイル
        tiles[1] = load_image("fig/load_1.png") # 土タイル
        tiles[2] = load_image("fig/stone.png") # 岩タイル
        tiles[3] = load_image("fig/flower.png") # 花タイル
        tiles[4] = load_image("fig/river_1.png") # 水タイル
        tiles[5] = load_image("fig/tree.png") # 木タイル
        return tiles # タイル画像辞書返却

    def update(self): # 更新処理
        """
        update の Docstring
        
        :param self: 説明
        """
        if self.move_cool > 0: # 移動クールタイム中
            self.move_cool -= 1 # クールタイム減少
            return

        keys = pygame.key.get_pressed() # キー取得
        dx, dy = 0, 0 # 移動量初期化
        # dx : x方向移動量
        # dy : y方向移動量

        if keys[pygame.K_LEFT]: 
            dx = -1 # 左移動
            self.player_img = self.player_img_left
        elif keys[pygame.K_RIGHT]: 
            dx = 1 # 右移動
            self.player_img = self.player_img_right
        elif keys[pygame.K_UP]: 
            dy = -1 # 上移動
            self.player_img = self.player_img_back
        elif keys[pygame.K_DOWN]: 
            dy = 1 # 下移動
            self.player_img = self.player_img_flont

        if dx or dy: # 移動がある場合
            nx = self.player_x + dx # 新しいX座標
            ny = self.player_y + dy # 新しいY座標
            #self.map_data : マップデータ参照(MAP_FIELD)
            if 0 <= ny < len(self.map_data) and 0 <= nx < len(self.map_data[0]): # 範囲内確認
                if self.map_data[ny][nx] in [0, 1]: # 移動可能タイル確認
                    self.player_x = nx # プレイヤーX座標更新
                    self.player_y = ny # プレイヤーY座標更新
                    self.move_cool = 8 # 移動クールタイム設定

        # print(self.player_x, self.player_y) # デバッグ用座標表示

    def draw(self): # 描画処理
        """
        draw の Docstring
        
        :param self: 説明
        """
        # カメラ位置計算
        map_width = len(self.map_data[0]) * TILE_SIZE # マップ幅
        map_height = len(self.map_data) * TILE_SIZE # マップ高さ

        camera_x = self.player_x * TILE_SIZE - SCREEN_WIDTH // 2 # カメラX座標
        camera_y = self.player_y * TILE_SIZE - SCREEN_HEIGHT // 2 # カメラY座標

        camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH)) # カメラX座標調整
        camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT)) # カメラY座標調整

        # マップ描画
        for y, row in enumerate(self.map_data): # マップデータ走査
            for x, tile in enumerate(row): # 各タイル走査
                px = x * TILE_SIZE - camera_x # 画面X座標
                py = y * TILE_SIZE - camera_y # 画面Y座標
                if -TILE_SIZE < px < SCREEN_WIDTH and -TILE_SIZE < py < SCREEN_HEIGHT: # 画面内確認
                    img = self.tile_images.get(tile) # タイル画像取得
                    if img: # 画像がある場合
                        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) # 画像サイズ変更
                        self.screen.blit(img, (px, py)) # 画像描画
                    else: # 画像がない場合
                        pygame.draw.rect( # 四角形描画
                            self.screen, # 画面
                            COLORS[tile],  # 色
                            (px, py, TILE_SIZE, TILE_SIZE) # 位置とサイズ
                        )

        px = self.player_x * TILE_SIZE - camera_x # プレイヤー画面X座標
        py = self.player_y * TILE_SIZE - camera_y # プレイヤー画面Y座標
        if self.player_img: # プレイヤー画像がある場合
            img = pygame.transform.scale(self.player_img, (TILE_SIZE, TILE_SIZE)) # 画像サイズ変更
            self.screen.blit(img, (px, py)) # プレイヤー描画
        else: # プレイヤー画像がない場合
            pygame.draw.rect(self.screen, (255, 0, 0), (px, py, TILE_SIZE, TILE_SIZE)) # 赤四角描画
