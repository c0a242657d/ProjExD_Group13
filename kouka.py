import pygame
import sys
import random
import os
import MapField

# --- 資料の必須要件: 実行ディレクトリをファイルのある場所に固定 ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 設定 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)       
BLUE = (0, 0, 255)      
YELLOW = (255, 215, 0)  
CYAN = (0, 255, 255)    
FLASH_COLOR = (255, 255, 255) 
GOLD = (255, 223, 0)    

# 状態定数
STATE_MAP = "MAP"
STATE_BATTLE = "BATTLE"
STATE_ENDING = "ENDING"
STATE_GAME_OVER = "GAME_OVER"

# マップID
MAP_VILLAGE = 0
MAP_FIELD = 1
MAP_CAMPUS = 2

class Game:
    def __init__(self):
        # Pygameの初期化
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG 工科クエスト")
        self.clock = pygame.time.Clock()

        # フォント設定
        try:
            self.font = pygame.font.SysFont("meiryo", 32)
            self.small_font = pygame.font.SysFont("meiryo", 24)
            self.msg_font = pygame.font.SysFont("meiryo", 20)
        except:
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
            self.msg_font = pygame.font.Font(None, 20)

        # --- 背景画像の読み込み ---
        # 1. 最初の村
        try:
            self.bg_village_original = pygame.image.load("fig/2.png")
            self.bg_village = pygame.transform.scale(self.bg_village_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            print("エラー: 画像が見つかりません。figフォルダに 2.png を入れてください。")
            self.bg_village = None

        # 2. キャンパス
        try:
            self.bg_campus_original = pygame.image.load("fig/gray-dot3.jpg")
            self.bg_campus = pygame.transform.scale(self.bg_campus_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            print("エラー: 画像が見つかりません。figフォルダに gray-dot3.jpg を入れてください。")
            self.bg_campus = None

        # --- 敵画像の読み込み ---
        self.enemy_images = []
        self.boss_image = None
        try:
            # 雑魚敵用 (1と2)
            img1 = pygame.image.load("fig/enemy_1.png").convert_alpha()
            img1 = pygame.transform.scale(img1, (100, 100)) # 雑魚敵サイズ
            
            img2 = pygame.image.load("fig/enemy_2.png").convert_alpha()
            img2 = pygame.transform.scale(img2, (100, 100)) # 雑魚敵サイズ
            
            self.enemy_images = [img1, img2]

            # ボス用 (3)
            img3 = pygame.image.load("fig/enemy_3.png").convert_alpha()
            self.boss_image = pygame.transform.scale(img3, (200, 200)) # ボスサイズ
            
        except FileNotFoundError:
            print("警告: 敵画像(fig/enemy_*.png)が見つかりません。四角で表示します。")

        # --- プレイヤー画像の読み込み ---
        self.player_size = 64
        try:
            # MapFieldで使用している魔法使いの画像を読み込む
            self.img_front = pygame.image.load("fig/map_mahou_1.png").convert_alpha()
            self.img_back = pygame.image.load("fig/map_mahou_b_1.png").convert_alpha()
            self.img_left = pygame.image.load("fig/map_mahou_l_1.png").convert_alpha()
            self.img_right = pygame.image.load("fig/map_mahou_r_1.png").convert_alpha()
            
            # サイズ調整
            self.img_front = pygame.transform.scale(self.img_front, (self.player_size, self.player_size))
            self.img_back = pygame.transform.scale(self.img_back, (self.player_size, self.player_size))
            self.img_left = pygame.transform.scale(self.img_left, (self.player_size, self.player_size))
            self.img_right = pygame.transform.scale(self.img_right, (self.player_size, self.player_size))
            
            self.player_img = self.img_front 
        except FileNotFoundError:
            print("警告: キャラクター画像が見つかりません。")
            self.player_img = None

        # プレイヤー初期設定
        self.player_pos = [400, 200]
        self.speed = 5
        
        # ステータス初期値
        self.player_level = 1
        self.player_exp = 0
        self.player_next_exp = 100
        self.player_max_hp = 100
        self.player_hp = 100
        self.player_max_mp = 100
        self.player_mp = 100
            
        # ゲーム進行管理フラグ
        self.state = STATE_MAP
        self.current_map = MAP_VILLAGE
        self.is_boss_battle = False
        
        # 戦闘用変数
        self.enemy_hp = 0
        self.battle_message = ""
        self.heals_left = 0
        self.items = {"potion": 3, "atk": 1, "def": 1}
        self.atk_buff_turns = 0
        self.def_buff_turns = 0
        self.atk_multiplier = 1.0
        self.def_multiplier = 1.0
        self.message_log = []
        self.max_messages = 4
        self.enemies = []
        self.battle_logs = []

        # MapFieldの初期化
        self.map_field = MapField.MapField(self.screen)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_BATTLE:
                    if event.key == pygame.K_SPACE:
                        # 攻撃
                        base_damage = random.randint(30, 60)
                        damage = int(base_damage * self.atk_multiplier)
                        self.enemy_hp -= damage
                        self.add_message(f"こうかとんの攻撃！ {damage} のダメージ！")
                        if self.enemy_hp > 0:
                            self.enemy_counterattack()
                        else:
                            self.add_message("敵を倒した！")
                            self.end_battle(win=True)

                    elif event.key == pygame.K_h: # 回復
                        if self.heals_left > 0:
                            heal = random.randint(200, 400)
                            old_hp = self.player_hp
                            self.player_hp = min(self.player_max_hp, self.player_hp + heal)
                            self.heals_left -= 1
                            self.add_message(f"回復した！ +{self.player_hp - old_hp} HP")
                            if self.enemy_hp > 0: self.enemy_counterattack()
                        else:
                            self.add_message("回復回数がありません！")

                    # アイテム使用キー (1, 2, 3)
                    elif event.key == pygame.K_1:
                        if self.items["potion"] > 0:
                            self.items["potion"] -= 1
                            self.player_hp = min(self.player_max_hp, self.player_hp + 150)
                            self.add_message("回復薬を使用！")
                            if self.enemy_hp > 0: self.enemy_counterattack()
                    elif event.key == pygame.K_2:
                        if self.items["atk"] > 0:
                            self.items["atk"] -= 1; self.atk_buff_turns = 3; self.atk_multiplier = 1.5
                            self.add_message("攻撃力アップ！")
                            if self.enemy_hp > 0: self.enemy_counterattack()
                    elif event.key == pygame.K_3:
                        if self.items["def"] > 0:
                            self.items["def"] -= 1; self.def_buff_turns = 3; self.def_multiplier = 0.5
                            self.add_message("防御力アップ！")
                            if self.enemy_hp > 0: self.enemy_counterattack()

                elif self.state in [STATE_ENDING, STATE_GAME_OVER]:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if self.state == STATE_GAME_OVER and event.key == pygame.K_r:
                        self.restart()

    def update(self):
        # --- 戦闘中の更新 ---
        if self.state == STATE_BATTLE:
            for enemy in self.enemies:
                if enemy.get("flash_timer", 0) > 0:
                    enemy["flash_timer"] -= 1

        # --- マップ移動中の更新 ---
        if self.state == STATE_MAP:
            # フィールドマップ (MapField) の場合
            if self.current_map == MAP_FIELD:
                self.map_field.update()
                
                # 右端(x >= 24)に行けばどこでも次のマップへ遷移
                if self.map_field.player_x >= 24:
                     self.current_map = MAP_CAMPUS
                     self.player_pos[0] = 10
                
                # ランダムエンカウント
                if getattr(self.map_field, "move_cool", 0) == 8:
                    self.check_random_encounter()

            # 村 (MAP_VILLAGE) または キャンパス (MAP_CAMPUS) の場合
            else:
                keys = pygame.key.get_pressed()
                moved = False
                
                # 移動方向に応じて画像を変更
                if keys[pygame.K_LEFT]:  
                    self.player_pos[0] -= self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_left
                if keys[pygame.K_RIGHT]: 
                    self.player_pos[0] += self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_right
                if keys[pygame.K_UP]:    
                    self.player_pos[1] -= self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_back
                if keys[pygame.K_DOWN]:  
                    self.player_pos[1] += self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_front
                
                # マップ端の遷移判定
                self.check_map_transition()
                
                # キャンパス奥でのボス戦判定
                if self.current_map == MAP_CAMPUS and self.player_pos[0] > 700:
                    self.start_battle(is_boss=True)

    def draw(self):
        self.screen.fill(BLACK) # 画面クリア

        # --- マップ画面の描画 ---
        if self.state == STATE_MAP:
            # 村マップ
            if self.current_map == MAP_VILLAGE:
                if self.bg_village:
                    self.screen.blit(self.bg_village, (0, 0))
                else:
                    pygame.draw.rect(self.screen, (100, 200, 100), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # キャラクター描画
                if self.player_img:
                    self.screen.blit(self.player_img, self.player_pos)
                else:
                    pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))

            # フィールドマップ (MapFieldが描画を担当)
            elif self.current_map == MAP_FIELD:
                self.map_field.draw() 

            # キャンパスマップ
            elif self.current_map == MAP_CAMPUS:
                if self.bg_campus:
                    self.screen.blit(self.bg_campus, (0, 0))
                else:
                    pygame.draw.rect(self.screen, GRAY, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # キャラクター描画
                if self.player_img:
                    self.screen.blit(self.player_img, self.player_pos)
                else:
                    pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))

            # ステータス表示
            status_str = f"Lv:{self.player_level}  HP:{self.player_hp}/{self.player_max_hp}"
            status = self.font.render(status_str, True, BLACK)
            self.screen.blit(status, (550, 20))

        # --- 戦闘画面の描画 ---
        elif self.state == STATE_BATTLE:
            for enemy in self.enemies:
                # 画像があれば表示
                if enemy.get("img"):
                    # ダメージ点滅（簡易的に画像を非表示にする）
                    if enemy.get("flash_timer", 0) > 0 and (enemy["flash_timer"] // 2) % 2 == 0:
                        pass # 点滅中は描画しない
                    else:
                        self.screen.blit(enemy["img"], enemy["rect"])
                else:
                    # 画像がない場合は四角形
                    draw_color = FLASH_COLOR if enemy.get("flash_timer", 0) > 0 else enemy["color"]
                    pygame.draw.rect(self.screen, draw_color, enemy["rect"])
                
                # HPバー描画
                hp_rate = max(0, enemy["hp"] / enemy["max_hp"])
                pygame.draw.rect(self.screen, RED, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width, 5))
                pygame.draw.rect(self.screen, GREEN, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width * hp_rate, 5))

            pygame.draw.rect(self.screen, BLACK, (0, 350, SCREEN_WIDTH, 250))
            pygame.draw.rect(self.screen, WHITE, (0, 350, SCREEN_WIDTH, 250), 2)
            
            y = 420
            for log in self.message_log:
                self.screen.blit(self.msg_font.render(log, True, WHITE), (50, y))
                y += 25
            
            info = f"HP: {self.player_hp}  MP: {self.player_mp}  回復残: {self.heals_left}"
            self.screen.blit(self.font.render(info, True, WHITE), (400, 420))
            cmd = "[SPACE]攻撃 [H]回復 [1]薬 [2]攻 [3]防"
            self.screen.blit(self.font.render(cmd, True, YELLOW), (50, 360))

        # --- エンディング・ゲームオーバー ---
        elif self.state == STATE_ENDING:
            self.screen.fill(WHITE)
            self.screen.blit(self.font.render("MISSION COMPLETE!", True, BLACK), (280, 250))
        
        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            self.screen.blit(self.font.render("GAME OVER... (R to Retry)", True, RED), (250, 250))

        pygame.display.flip()

    # --- ヘルパーメソッド ---
    def check_map_transition(self):
        if self.player_pos[0] > SCREEN_WIDTH:
            if self.current_map < MAP_CAMPUS:
                self.current_map += 1; self.player_pos[0] = 10
            else: self.player_pos[0] = SCREEN_WIDTH - self.player_size
        elif self.player_pos[0] < 0:
            if self.current_map > MAP_VILLAGE:
                self.current_map -= 1; self.player_pos[0] = SCREEN_WIDTH - 10
            else: self.player_pos[0] = 0
        if self.player_pos[1] < 0: self.player_pos[1] = 0
        if self.player_pos[1] > SCREEN_HEIGHT - self.player_size: self.player_pos[1] = SCREEN_HEIGHT - self.player_size

    def check_random_encounter(self):
        if random.randint(0, 100) < 1: self.start_battle(is_boss=False)

    def start_battle(self, is_boss):
        self.state = STATE_BATTLE
        self.is_boss_battle = is_boss
        self.heals_left = 5 if is_boss else 3
        self.message_log = []
        self.enemies = []
        
        if is_boss:
            self.enemy_hp = 200
            self.add_message("ボスが現れた！")
            self.enemies.append({
                "name": "BOSS", 
                "hp": 1000, 
                "max_hp": 1000, 
                "color": YELLOW, 
                "rect": pygame.Rect(300, 50, 200, 200),
                "img": self.boss_image 
            })
        else:
            self.enemy_hp = 100
            self.add_message("敵が現れた！")
            num = random.randint(1, 2)
            for i in range(num):
                img = random.choice(self.enemy_images) if self.enemy_images else None
                self.enemies.append({
                    "name": f"Enemy{i}", 
                    "hp": 50, 
                    "max_hp": 50, 
                    "color": BLUE, 
                    "rect": pygame.Rect(150 + i*200, 100, 100, 100),
                    "img": img
                })

    def end_battle(self, win):
        self.state = STATE_ENDING if (win and self.is_boss_battle) else STATE_MAP
        if not win: self.game_over()

    def game_over(self): self.state = STATE_GAME_OVER
    
    def restart(self):
        self.state = STATE_MAP; self.current_map = MAP_VILLAGE
        self.player_hp = self.player_max_hp; self.player_pos = [400, 200]

    def add_message(self, text):
        self.message_log.append(text)
        if len(self.message_log) > self.max_messages: self.message_log.pop(0)

    def enemy_counterattack(self):
        dmg = random.randint(10, 30)
        dmg = int(dmg * self.def_multiplier)
        self.player_hp -= dmg
        self.add_message(f"敵の反撃！ {dmg} ダメージ")
        if self.player_hp <= 0: self.game_over()
        if self.atk_buff_turns > 0: self.atk_buff_turns -= 1; 
        if self.atk_buff_turns == 0: self.atk_multiplier = 1.0
        if self.def_buff_turns > 0: self.def_buff_turns -= 1; 
        if self.def_buff_turns == 0: self.def_multiplier = 1.0
    
    def gain_exp(self, amount):
        self.player_exp += amount
        while self.player_exp >= self.player_next_exp:
            self.player_level += 1; self.player_exp -= self.player_next_exp
            self.player_next_exp = int(self.player_next_exp * 1.5)
            self.player_max_hp += 20; self.player_hp = self.player_max_hp

if __name__ == "__main__":
    Game().run()