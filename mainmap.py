import pygame
import sys
import random
import os

# =====================
# 基本設定
# =====================
SCREEN_WIDTH = 800 #画面幅
SCREEN_HEIGHT = 600 #画面高
TILE_SIZE = 64 # タイルサイズ 
FPS = 60 # フレームレート

# =====================
# 色（画像が無い時の代用）
# =====================
COLORS = {
    0: (50, 180, 50),    # 草
    1: (160, 130, 80),   # 土
    2: (100, 100, 100),  # 岩
    3: (200, 50, 50),    # 家
    4: (0, 0, 255)       # 水
}

# =====================
# マップ定義（DQ方式）
# =====================
MAP_VILLAGE = [ 
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,4,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================
# ゲーム本体
# =====================
class Game:
    def __init__(self): # 初期化
        pygame.init() # pygame初期化
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # 画面設定
        pygame.display.set_caption("ドラクエ風タイルRPG") # タイトル設定
        self.clock = pygame.time.Clock() # クロック設定

        self.map_data = MAP_VILLAGE # マップデータ

        # プレイヤー（マス座標）
        self.player_x = 1 # 初期X座標
        self.player_y = 1 # 初期Y座標

        # 移動制御（押しっぱなし用）
        self.MOVE_INTERVAL_FIRST = 6   # 押し始め（遅い）
        self.MOVE_INTERVAL_REPEAT = 6   # 押しっぱなし（速い）
        self.move_cooltime = 0
        self.moving = False

        # 画像ロード
        self.tile_images = self.load_tiles() # タイル画像
        self.player_image = self.load_image("fig/map_yuusha_1.png") # プレイヤー画像

    # ---------------------
    # 画像ロード共通
    # ---------------------
    def load_image(self, relative_path):
        path = os.path.join(BASE_DIR, relative_path)
        if not os.path.exists(path):
            print("画像が見つかりません:", path)
            return None
        print("画像読み込み成功:", path)
        return pygame.image.load(path).convert_alpha()
    

    def load_tiles(self): # タイル画像ロード
        tiles = {} # タイル辞書
        tiles[0] = self.load_image("tiles/grass.png") # 草
        tiles[1] = self.load_image("tiles/soil.png") # 土
        tiles[2] = self.load_image("tiles/rock.png") # 岩
        tiles[3] = self.load_image("tiles/house.png") # 家
        tiles[4] = self.load_image("tiles/water.png") # 水
        return tiles # タイル辞書返す

    # ---------------------
    # メインループ
    # ---------------------
    def run(self): # メインループ
        while True: # 無限ループ
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    # ---------------------
    # 入力処理（DQ風）
    # ---------------------
    def handle_events(self): # 入力処理
        for event in pygame.event.get(): # イベント取得
            if event.type == pygame.QUIT: # 終了イベント
                pygame.quit() # pygame終了
                sys.exit() # プログラム終了
    # ---------------------
    # 更新処理（押しっぱなし移動）
    # ---------------------
    def update(self):
        if self.move_cooltime > 0:
            self.move_cooltime -= 1
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        if dx != 0 or dy != 0:
            moved = self.move_player(dx, dy)
            if moved:
                if not self.moving:
                    self.move_cooltime = self.MOVE_INTERVAL_FIRST
                    self.moving = True
                else:
                    self.move_cooltime = self.MOVE_INTERVAL_REPEAT
        else:
            self.moving = False

    # ---------------------
    # プレイヤー移動
    # ---------------------
    def move_player(self, dx, dy): # プレイヤー移動処理
        nx = self.player_x + dx # 新X座標
        ny = self.player_y + dy # 新Y座標

        if 0 <= ny < len(self.map_data) and 0 <= nx < len(self.map_data[0]): # 範囲内チェック
            tile = self.map_data[ny][nx] # タイルID取得

            # 通行可能タイル
            if tile in [0, 1]: # 草・土のみ通行可能
                self.player_x = nx # 移動確定
                self.player_y = ny # 移動確定

                # ランダムエンカウント（例）
                if tile == 0 and random.randint(0, 100) < 5: # 草タイルで5%の確率
                    print("敵が現れた！（仮）") # エンカウントメッセージ
                return True # 移動成功
        return False # 移動失敗

    # ---------------------
    # 描画
    # ---------------------
    def draw(self): # 描画処理
        self.screen.fill((0, 0, 0)) # 画面クリア

        # マップ描画
        for y, row in enumerate(self.map_data): # 行ループ
            for x, tile_id in enumerate(row): # 列ループ
                px = x * TILE_SIZE # 画面X座標
                py = y * TILE_SIZE # 画面Y座標

                img = self.tile_images.get(tile_id) # タイル画像取得
                if img: # 画像がある場合
                    self.screen.blit(img, (px, py)) # 画像描画
                else: # 画像が無い場合
                    pygame.draw.rect( # タイル描画
                        self.screen, # 画面
                        COLORS[tile_id], # 色
                        (px, py, TILE_SIZE, TILE_SIZE) # 四角形
                    )

        # プレイヤー描画
        px = self.player_x * TILE_SIZE # 画面X座標
        py = self.player_y * TILE_SIZE # 画面Y座標

        if self.player_image:
            img = pygame.transform.scale(
                self.player_image,
                (TILE_SIZE, TILE_SIZE)
                )
            self.screen.blit(img, (px, py))
        else: # 画像が無い場合
            pygame.draw.rect( # プレイヤー描画
                self.screen, # 画面
                (255, 0, 0), # 赤色
                (px, py, TILE_SIZE, TILE_SIZE) # 四角形
            )

        pygame.display.flip() # 画面更新

# =====================
# 起動
# =====================
if __name__ == "__main__":
    Game().run()
