import os
import pygame
import sys
import random


os.chdir(os.path.dirname(os.path.abspath(__file__)))
import MapField

# --- 資料の必須要件: 実行ディレクトリをファイルのある場所に固定 ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCREEN_WIDTH = 800  # 設定
SCREEN_HEIGHT = 600
FPS = 60


WHITE = (255, 255, 255)  # 色定義
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)  # こうかとん
BLUE = (0, 0, 255)  # 雑魚敵
YELLOW = (255, 215, 0)  # ボス
CYAN = (0, 255, 255)  # MP
FLASH_COLOR = (255, 255, 255)  # ダメージ時の閃光
GOLD = (255, 223, 0)  # レベルアップ用

GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)       
BLUE = (0, 0, 255)      
YELLOW = (255, 215, 0)  
CYAN = (0, 255, 255)    
FLASH_COLOR = (255, 255, 255) 
GOLD = (255, 223, 0)    

STATE_MAP = "MAP"  # 状態定数
STATE_BATTLE = "BATTLE"
STATE_ENDING = "ENDING"
STATE_GAME_OVER = "GAME_OVER"
STATE_TRANSITION = "TRANSITION"  # 戦闘画面遷移。担当田代


MAP_VILLAGE = 0  # マップID
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
        
        
        self.enemies = []  # 戦闘用変数
        self.battle_logs = []

        self.transition_step = 0  # 遷移演出　担当田代
        self.transition_speed = 32
        self.next_is_boss = False

    def get_japanese_font(self, size):
        font_names = ["meiryo", "msgothic", "yugothic", "hiraginosans", "notosanscjkjp"]
        available_fonts = pygame.font.get_fonts()
        for name in font_names:
            if name in available_fonts:
                return pygame.font.SysFont(name, size)
        return pygame.font.Font(None, size)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
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
        if self.state == STATE_BATTLE:  # 敵のアニメーション処理
            enemies_to_remove = []
            
            for enemy in self.enemies:
                if enemy.get("flash_timer", 0) > 0:  # 1. ダメージ演出
                    enemy["flash_timer"] -= 1
                if enemy["hp"] <= 0:  # 2. 死亡演出
                    if "death_timer" not in enemy:
                        enemy["death_timer"] = 60 
                        self.battle_logs.append(f"{enemy['name']}をやっつけた！")
                    enemy["death_timer"] -= 1
                    if enemy["death_timer"] <= 0:  # タイマー0で消滅（経験値獲得）
                        self.gain_exp(enemy["xp"])   # 経験値処理へ
                        enemies_to_remove.append(enemy)

            for enemy in enemies_to_remove:  # リスト消滅実行
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
            if len(self.enemies) == 0:
                self.end_battle(win=True)

        if self.state == STATE_MAP:  # 移動画面処理
            keys = pygame.key.get_pressed()
            moved = False
            
            if keys[pygame.K_LEFT]:
                self.player_pos[0] -= self.speed
                moved = True
            if keys[pygame.K_RIGHT]:
                self.player_pos[0] += self.speed
                moved = True
            if keys[pygame.K_UP]:
                self.player_pos[1] -= self.speed
                moved = True
            if keys[pygame.K_DOWN]:
                self.player_pos[1] += self.speed
                moved = True

            self.check_map_transition()
            if moved and self.current_map == MAP_FIELD:
                self.check_random_encounter()
            
            if self.current_map == MAP_CAMPUS and self.player_pos[0] > 700:
                self.start_transition_to_battle(is_boss=True)

        if self.state == STATE_TRANSITION:  # 遷移演出
            self.update_transition()

    
    def gain_exp(self, amount):  # 重要：経験値とレベルアップ処理
        self.player_exp += amount
        self.battle_logs.append(f"{amount} Expを獲得！")
        
        while self.player_exp >= self.player_next_exp:  # レベルアップ判定
            self.player_level += 1
            self.player_exp -= self.player_next_exp # 現在のExpを消費して次のレベルへ
            self.player_next_exp = int(self.player_next_exp * 1.5) # 必要経験値増加
            
            # ステータス上昇
            self.player_max_hp += 20
            self.player_max_mp += 10
            
            # 全回復（ボーナス）
            self.player_hp = self.player_max_hp
            self.player_mp = self.player_max_mp
            
            self.battle_logs.append(f"レベルアップ！ Lv{self.player_level} になった！")
            self.battle_logs.append("最大HPとMPが増え、全回復した！")

    def start_transition_to_battle(self, is_boss):  # 遷移演出処理　担当田代
        self.state = STATE_TRANSITION
        self.transition_step = 0
        self.transition_wait_timer = 0
        self.next_is_boss = is_boss

    def update_transition(self):  # 遷移演出　担当田代
        if self.transition_step < SCREEN_WIDTH + 100:  # 画面より大きくなるまで広げる
            self.transition_step += self.transition_speed
        else:  # 画面が真っ暗になったらタイマーを作動させる
            self.transition_wait_timer += 1
            if self.transition_wait_timer > 60:  # 60フレーム（約1秒）待ったら戦闘開始
                self.start_battle(self.next_is_boss)
        
    def check_map_transition(self):  # 画面端でのマップ切り替え
        if self.player_pos[0] > SCREEN_WIDTH:
            if self.current_map < MAP_CAMPUS:
                self.current_map += 1
                self.player_pos[0] = 10
            else:
                self.player_pos[0] = SCREEN_WIDTH - self.player_size
        elif self.player_pos[0] < 0:
            if self.current_map > MAP_VILLAGE:
                self.current_map -= 1; self.player_pos[0] = SCREEN_WIDTH - 10
            else: self.player_pos[0] = 0
        if self.player_pos[1] < 0: self.player_pos[1] = 0
        if self.player_pos[1] > SCREEN_HEIGHT - self.player_size: self.player_pos[1] = SCREEN_HEIGHT - self.player_size

    def check_random_encounter(self):
        if random.randint(0, 100) < 1:
            self.start_transition_to_battle(is_boss=False)

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
            num_enemies = random.randint(1, 3)
            for i in range(num_enemies):
                x_pos = 150 + i * 180
                self.enemies.append({
                    "name": f"課題{i+1}",
                    "hp": 50, "max_hp": 50, "atk": 10, "xp": 40, # 雑魚は40Exp
                    "color": BLUE, "rect": pygame.Rect(x_pos, 100, 100, 100),
                    "flash_timer": 0
                })
    
    def execute_turn(self, action_type):
        self.battle_logs = [] 
        valid_targets = [e for e in self.enemies if e["hp"] > 0]

        if not valid_targets and len(self.enemies) == 0:
            return

        # --- プレイヤー行動 ---
        # レベルに応じた威力補正
        level_bonus = (self.player_level - 1) * 2

        if action_type == "HOIMI":
            if self.player_mp >= 10:
                self.player_mp -= 10
                base_heal = random.randint(30, 50)
                heal_amount = base_heal + level_bonus # レベルで回復量も増える
                
                old_hp = self.player_hp
                self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
                recovered = self.player_hp - old_hp
                self.battle_logs.append(f"ホイミ！ HPが{recovered}回復！")
            else:
                self.battle_logs.append("MPが足りない！")

        elif action_type == "MAGIC":
            if self.player_mp >= 30:
                if valid_targets:
                    target = valid_targets[0]
                    self.player_mp -= 30
                    
                    base_dmg = random.randint(50, 80)
                    damage = base_dmg + (level_bonus * 2) # 魔法はレベル恩恵大
                    
                    if random.randint(0, 100) < 10:
                        damage = int(damage * 1.5)
                        self.battle_logs.append("会心の一撃！！")
                    
                    target["hp"] -= damage
                    target["flash_timer"] = 10 
                    self.battle_logs.append(f"魔法攻撃！{target['name']}に{damage}ダメ！")
            else:
                self.battle_logs.append("MPが足りない！")

        elif action_type == "ATTACK":
            if valid_targets:
                target = valid_targets[0]
                base_dmg = random.randint(20, 30)
                damage = base_dmg + level_bonus

                if random.randint(0, 100) < 15:
                    damage = damage * 2
                    self.battle_logs.append("会心の一撃！！")

                target["hp"] -= damage
                target["flash_timer"] = 10 
                self.battle_logs.append(f"攻撃！ {target['name']}に{damage}ダメ！")

        # --- 敵の反撃 ---
        surviving_enemies = [e for e in self.enemies if e["hp"] > 0]
        total_dmg = 0
        for enemy in surviving_enemies:
            hit_chance = random.randint(0, 100)
            if hit_chance < 20: 
                self.battle_logs.append(f"{enemy['name']}の攻撃ミス！")
            else:
                dmg = random.randint(enemy["atk"] - 3, enemy["atk"] + 3)
                total_dmg += dmg
        
        if total_dmg > 0:
            self.player_hp -= total_dmg
            self.battle_logs.append(f"敵の攻撃！ 計{total_dmg}のダメージ！")

        if self.player_hp <= 0:
            self.player_hp = 0
            self.end_battle(win=False)

    def end_battle(self, win):
        if win:
            if self.is_boss_battle:
                self.state = STATE_ENDING
            else:
                self.state = STATE_MAP
        else:
            self.state = STATE_GAME_OVER

    def draw_map_elements(self):
        color = GREEN
        if self.current_map == MAP_VILLAGE: color = (100, 200, 100)
        elif self.current_map == MAP_CAMPUS: color = GRAY
        pygame.draw.rect(self.screen, color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))
        
        # マップ画面のステータス表示
        status_str = f"Lv:{self.player_level}  HP:{self.player_hp}/{self.player_max_hp}"
        status = self.font.render(status_str, True, BLACK)
        self.screen.blit(status, (550, 20))

    def draw(self):
        #self.screen.fill(BLACK)  各状態で背景を描く
        if self.state == STATE_MAP:
            self.screen.fill(BLACK)
            self.draw_map_elements()

        elif self.state == STATE_BATTLE:
            self.screen.fill(BLACK)
            for enemy in self.enemies:
                if "death_timer" in enemy:
                    if (enemy["death_timer"] // 5) % 2 == 0:
                        pygame.draw.rect(self.screen, (100, 0, 0), enemy["rect"])
                else:
                    draw_color = enemy["color"]
                    if enemy.get("flash_timer", 0) > 0:
                        draw_color = FLASH_COLOR
                    pygame.draw.rect(self.screen, draw_color, enemy["rect"])
                    
                    if enemy["hp"] > 0:
                        hp_rate = max(0, enemy["hp"] / enemy["max_hp"])
                        pygame.draw.rect(self.screen, RED, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width, 5))
                        pygame.draw.rect(self.screen, GREEN, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width * hp_rate, 5))

            # UI描画
            ui_y_start = 350
            ui_height = SCREEN_HEIGHT - ui_y_start
            pygame.draw.rect(self.screen, BLACK, (0, ui_y_start, SCREEN_WIDTH, ui_height))
            pygame.draw.rect(self.screen, WHITE, (0, ui_y_start, SCREEN_WIDTH, ui_height), 2)

            # ステータス表示（Lv, Exp追加）
            hp_color = WHITE if self.player_hp > 30 else RED
            
            # LvとExp
            lv_text = f"Lv: {self.player_level}"
            exp_text = f"Exp: {self.player_exp}/{self.player_next_exp}"
            self.screen.blit(self.font.render(lv_text, True, GOLD), (30, ui_y_start + 15))
            self.screen.blit(self.small_font.render(exp_text, True, WHITE), (120, ui_y_start + 20))

            # HPとMP
            hp_text = f"HP: {self.player_hp}/{self.player_max_hp}"
            mp_text = f"MP: {self.player_mp}/{self.player_max_mp}"
            self.screen.blit(self.font.render(hp_text, True, hp_color), (300, ui_y_start + 15))
            self.screen.blit(self.font.render(mp_text, True, CYAN), (550, ui_y_start + 15))

            # コマンド
            cmd_text = "[A]たたかう  [M]まほう(30)  [H]ホイミ(10)"
            self.screen.blit(self.font.render(cmd_text, True, YELLOW), (30, ui_y_start + 60))

            # 区切り線
            line_y = ui_y_start + 100
            pygame.draw.line(self.screen, WHITE, (0, line_y), (SCREEN_WIDTH, line_y), 1)

            # ログ
            display_logs = self.battle_logs[-5:] 
            for i, log in enumerate(display_logs):
                log_color = WHITE
                if "会心" in log: log_color = YELLOW
                if "やっつけた" in log: log_color = (255, 100, 100)
                if "レベルアップ" in log: log_color = GOLD # レベルアップは金色
                
                txt = self.small_font.render(log, True, log_color)
                self.screen.blit(txt, (30, line_y + 10 + i * 28))

        elif self.state == STATE_TRANSITION:
            self.draw_map_elements()  # 中央から広がる黒い矩形を描く
            rect_w = self.transition_step
            rect_h = int(self.transition_step * (SCREEN_HEIGHT / SCREEN_WIDTH))
            
            # 中央座標
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            # Rect作成（中央から広げる計算）
            black_rect = pygame.Rect(
                center_x - rect_w // 2,
                center_y - rect_h // 2,
                rect_w,
                rect_h
            )
            pygame.draw.rect(self.screen, BLACK, black_rect)

        elif self.state == STATE_ENDING:
            self.screen.fill(WHITE)
            msg = self.font.render("MISSION COMPLETE!", True, BLACK)
            self.screen.blit(msg, (200, 300))

        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            msg = self.font.render("GAME OVER...", True, RED)
            self.screen.blit(msg, (300, 300))

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()