import pygame
import sys
import random

# --- 設定 ---
# 画面サイズとフレームレート（1秒間の描画回数）
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色定義 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)       # プレイヤー（こうかとん）の色
BLUE = (0, 0, 255)      # 通常の敵（課題）の色
YELLOW = (255, 215, 0)  # ボスの色 / 会心の一撃の文字色
CYAN = (0, 255, 255)    # MP表示用
FLASH_COLOR = (255, 255, 255) # ダメージを受けた時の点滅色
GOLD = (255, 223, 0)    # レベルアップ時の文字色

# ゲームの状態定数（シーン管理用）
STATE_MAP = "MAP"           # マップ移動中
STATE_BATTLE = "BATTLE"     # 戦闘中
STATE_ENDING = "ENDING"     # クリア画面
STATE_GAME_OVER = "GAME_OVER" # ゲームオーバー画面

# マップID（場所の識別用）
MAP_VILLAGE = 0 # 最初の村（安全地帯）
MAP_FIELD = 1   # フィールド（敵が出現）
MAP_CAMPUS = 2  # キャンパス（ボスが出現）

class Game:
    def __init__(self):
        # Pygameの初期化とウィンドウ設定
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG こうく - Smart MP Check")
        self.clock = pygame.time.Clock()
        
        # フォントの読み込み（日本語対応のため自作メソッドを使用）
        self.font = self.get_japanese_font(32)
        self.small_font = self.get_japanese_font(24)

        # プレイヤーの初期座標とサイズ
        self.player_pos = [50, 300]
        self.player_size = 40
        self.speed = 5 # 移動速度
        
        # プレイヤーのステータス初期値
        self.player_level = 1
        self.player_exp = 0
        self.player_next_exp = 100 # 次のレベルまでの必要経験値
        
        self.player_max_hp = 100
        self.player_hp = 100
        self.player_max_mp = 100
        self.player_mp = 100
        
        # ゲーム進行管理フラグ
        self.state = STATE_MAP     # 初期状態はマップ
        self.current_map = MAP_VILLAGE # 初期マップ
        self.is_boss_battle = False
        
        # 戦闘用変数（敵リスト、ログ保存用）
        self.enemies = []
        self.battle_logs = []

    def get_japanese_font(self, size):
        """
        OSにインストールされているフォントから日本語対応のものを探して返す
        Windows/Mac/Linux環境での文字化けを防ぐための処理
        """
        font_names = ["meiryo", "msgothic", "yugothic", "hiraginosans", "notosanscjkjp"]
        available_fonts = pygame.font.get_fonts()
        for name in font_names:
            if name in available_fonts:
                return pygame.font.SysFont(name, size)
        return pygame.font.Font(None, size) # 見つからなければデフォルト（日本語非対応）

    def run(self):
        """
        ゲームのメインループ
        イベント処理 -> 更新処理 -> 描画処理 を繰り返す
        """
        while True:
            self.handle_events() # キー入力などの受付
            self.update()        # ゲームロジックの計算
            self.draw()          # 画面への描画
            self.clock.tick(FPS) # フレームレート調整

    def handle_events(self):
        """
        ユーザーからの入力を処理する
        """
        for event in pygame.event.get():
            # 閉じるボタンが押された場合
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # キーが押された瞬間の処理
            if event.type == pygame.KEYDOWN:
                # 戦闘中のコマンド入力
                if self.state == STATE_BATTLE:
                    if event.key == pygame.K_a:      # Aキー：攻撃
                        self.execute_turn("ATTACK")
                    elif event.key == pygame.K_m:    # Mキー：魔法
                        self.execute_turn("MAGIC")
                    elif event.key == pygame.K_h:    # Hキー：回復（ホイミ）
                        self.execute_turn("HOIMI")
                
                # エンディングまたはゲームオーバー時の終了操作
                elif self.state == STATE_ENDING or self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def update(self):
        """
        ゲームの状態ごとの更新処理を行う
        """
        # --- 戦闘中の更新 ---
        if self.state == STATE_BATTLE:
            enemies_to_remove = []
            for enemy in self.enemies:
                # ダメージ時の点滅タイマーを減らす
                if enemy.get("flash_timer", 0) > 0:
                    enemy["flash_timer"] -= 1

                # 敵のHPが0以下になった場合の処理
                if enemy["hp"] <= 0:
                    # 死亡タイマーがセットされていなければセット（消滅エフェクト用）
                    if "death_timer" not in enemy:
                        enemy["death_timer"] = 60 
                        self.battle_logs.append(f"{enemy['name']}をやっつけた！")

                    # 死亡タイマーを進める
                    enemy["death_timer"] -= 1
                    # タイマーが0になったら経験値を獲得して削除リストへ
                    if enemy["death_timer"] <= 0:
                        self.gain_exp(enemy["xp"])
                        enemies_to_remove.append(enemy)

            # 倒された敵をリストから実際に削除
            for enemy in enemies_to_remove:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
            
            # 全ての敵がいなくなったら勝利
            if len(self.enemies) == 0:
                self.end_battle(win=True)

        # --- マップ移動中の更新 ---
        if self.state == STATE_MAP:
            keys = pygame.key.get_pressed()
            moved = False
            
            # 矢印キーによる移動処理
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

            # 画面端でのマップ切り替え判定
            self.check_map_transition()
            
            # フィールド（MAP_FIELD）を移動中ならランダムエンカウント判定
            if moved and self.current_map == MAP_FIELD:
                self.check_random_encounter()
            
            # キャンパス（MAP_CAMPUS）の奥まで進んだらボス戦開始
            if self.current_map == MAP_CAMPUS and self.player_pos[0] > 700:
                self.start_battle(is_boss=True)

    def gain_exp(self, amount):
        """
        経験値獲得とレベルアップ処理
        """
        self.player_exp += amount
        self.battle_logs.append(f"{amount} Expを獲得！")
        # 次のレベルに必要な経験値を超えている間、レベルアップを繰り返す
        while self.player_exp >= self.player_next_exp:
            self.player_level += 1
            self.player_exp -= self.player_next_exp
            self.player_next_exp = int(self.player_next_exp * 1.5) # 必要経験値増加
            
            # ステータス上昇と全回復
            self.player_max_hp += 20
            self.player_max_mp += 10
            self.player_hp = self.player_max_hp
            self.player_mp = self.player_max_mp
            
            self.battle_logs.append(f"レベルアップ！ Lv{self.player_level} になった！")
            self.battle_logs.append("最大HPとMPが増え、全回復した！")

    def check_map_transition(self):
        """
        画面端に到達した際のマップ切り替え処理
        """
        # 右端へ行った場合：次のマップへ
        if self.player_pos[0] > SCREEN_WIDTH:
            if self.current_map < MAP_CAMPUS:
                self.current_map += 1
                self.player_pos[0] = 10 # 左端へワープ
            else:
                self.player_pos[0] = SCREEN_WIDTH - self.player_size # 行き止まり
        
        # 左端へ行った場合：前のマップへ
        elif self.player_pos[0] < 0:
            if self.current_map > MAP_VILLAGE:
                self.current_map -= 1
                self.player_pos[0] = SCREEN_WIDTH - 10 # 右端へワープ
            else:
                self.player_pos[0] = 0 # 行き止まり

    def check_random_encounter(self):
        """
        ランダムエンカウントの判定（約1%の確率で戦闘開始）
        """
        if random.randint(0, 100) < 1:
            self.start_battle(is_boss=False)

    def start_battle(self, is_boss):
        """
        戦闘の初期化処理
        敵の生成（ボス or 雑魚）とステータスのリセット
        """
        self.state = STATE_BATTLE
        self.is_boss_battle = is_boss
        self.enemies = []
        self.battle_logs = ["敵が現れた！"]

        if is_boss:
            # ボスデータ
            self.enemies.append({
                "name": "悪の組織",
                "hp": 1000, "max_hp": 1000, "atk": 40, "xp": 5000,
                "color": YELLOW, "rect": pygame.Rect(300, 50, 200, 200),
                "flash_timer": 0
            })
        else:
            # 雑魚敵（1〜3体ランダム生成）
            num_enemies = random.randint(1, 3)
            for i in range(num_enemies):
                x_pos = 150 + i * 180
                self.enemies.append({
                    "name": f"課題{i+1}",
                    "hp": 50, "max_hp": 50, "atk": 10, "xp": 40,
                    "color": BLUE, "rect": pygame.Rect(x_pos, 100, 100, 100),
                    "flash_timer": 0
                })

    def execute_turn(self, action_type):
        """
        1ターンの処理を実行（プレイヤー行動 -> 敵行動）
        MP不足時は行動をキャンセルする
        """
        # 1. 事前MPチェック
        # 足りない場合はログを出して即return（ターンを消費しない）
        if action_type == "HOIMI":
            if self.player_mp < 10:
                self.battle_logs = ["MPが足りない！ 他のコマンドを選んでください。"]
                return # ここで終了！敵のターンには行かない
        
        elif action_type == "MAGIC":
            if self.player_mp < 30:
                self.battle_logs = ["MPが足りない！ 他のコマンドを選んでください。"]
                return # ここで終了！
        
        # 2. ここまで来たら行動成功確定なのでログをクリアして処理開始
        self.battle_logs = []
        valid_targets = [e for e in self.enemies if e["hp"] > 0] # 生存している敵
        if not valid_targets and len(self.enemies) == 0:
            return

        level_bonus = (self.player_level - 1) * 2 # レベルによる補正値

        # --- プレイヤー行動の分岐 ---
        if action_type == "HOIMI":
            # MP消費と回復計算
            self.player_mp -= 10
            base_heal = random.randint(30, 50)
            heal_amount = base_heal + level_bonus
            old_hp = self.player_hp
            self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
            recovered = self.player_hp - old_hp
            self.battle_logs.append(f"ホイミ！ HPが{recovered}回復！")

        elif action_type == "MAGIC":
            if valid_targets:
                target = valid_targets[0] # 先頭の敵を狙う
                self.player_mp -= 30
                
                base_dmg = random.randint(50, 80)
                damage = base_dmg + (level_bonus * 2)
                
                # 10%で会心の一撃
                if random.randint(0, 100) < 10:
                    damage = int(damage * 1.5)
                    self.battle_logs.append("会心の一撃！！")
                
                target["hp"] -= damage
                target["flash_timer"] = 10 # 被ダメージ演出ON
                self.battle_logs.append(f"魔法攻撃！{target['name']}に{damage}ダメ！")

        elif action_type == "ATTACK":
            if valid_targets:
                target = valid_targets[0]
                base_dmg = random.randint(20, 30)
                damage = base_dmg + level_bonus

                # 15%で会心の一撃
                if random.randint(0, 100) < 15:
                    damage = damage * 2
                    self.battle_logs.append("会心の一撃！！")

                target["hp"] -= damage
                target["flash_timer"] = 10 
                self.battle_logs.append(f"攻撃！ {target['name']}に{damage}ダメ！")

        # --- 敵の反撃ターン ---
        surviving_enemies = [e for e in self.enemies if e["hp"] > 0]
        total_dmg = 0
        for enemy in surviving_enemies:
            hit_chance = random.randint(0, 100)
            if hit_chance < 20: 
                # 20%で攻撃をミスする
                self.battle_logs.append(f"{enemy['name']}の攻撃ミス！")
            else:
                # ダメージ計算
                dmg = random.randint(enemy["atk"] - 3, enemy["atk"] + 3)
                total_dmg += dmg
        
        # ダメージがあればHPを減らす
        if total_dmg > 0:
            self.player_hp -= total_dmg
            self.battle_logs.append(f"敵の攻撃！ 計{total_dmg}のダメージ！")

        # プレイヤーの敗北判定
        if self.player_hp <= 0:
            self.player_hp = 0
            self.end_battle(win=False)

    def end_battle(self, win):
        """
        戦闘終了処理
        勝利時：ボスならエンディング、雑魚ならマップに戻る
        敗北時：ゲームオーバー
        """
        if win:
            if self.is_boss_battle:
                self.state = STATE_ENDING
            else:
                self.state = STATE_MAP
        else:
            self.state = STATE_GAME_OVER

    def draw(self):
        """
        画面描画処理（1フレームごとに呼ばれる）
        """
        self.screen.fill(BLACK) # 背景をリセット

        # --- マップ画面の描画 ---
        if self.state == STATE_MAP:
            color = GREEN
            # マップによって背景色を変える
            if self.current_map == MAP_VILLAGE: color = (100, 200, 100)
            elif self.current_map == MAP_CAMPUS: color = GRAY
            pygame.draw.rect(self.screen, color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # プレイヤーの描画
            pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))
            
            # 簡易ステータス表示
            status_str = f"Lv:{self.player_level}  HP:{self.player_hp}/{self.player_max_hp}"
            status = self.font.render(status_str, True, BLACK)
            self.screen.blit(status, (550, 20))

        # --- 戦闘画面の描画 ---
        elif self.state == STATE_BATTLE:
            # 敵の描画ループ
            for enemy in self.enemies:
                if "death_timer" in enemy:
                    # 倒した敵は点滅させながら消す
                    if (enemy["death_timer"] // 5) % 2 == 0:
                        pygame.draw.rect(self.screen, (100, 0, 0), enemy["rect"])
                else:
                    # 通常描画（ダメージ時は白く光る）
                    draw_color = enemy["color"]
                    if enemy.get("flash_timer", 0) > 0:
                        draw_color = FLASH_COLOR
                    pygame.draw.rect(self.screen, draw_color, enemy["rect"])
                    
                    # 敵HPバーの描画（赤背景の上に緑バーを重ねる）
                    if enemy["hp"] > 0:
                        hp_rate = max(0, enemy["hp"] / enemy["max_hp"])
                        pygame.draw.rect(self.screen, RED, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width, 5))
                        pygame.draw.rect(self.screen, GREEN, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width * hp_rate, 5))

            # UIエリア（画面下部）の描画
            ui_y_start = 350
            ui_height = SCREEN_HEIGHT - ui_y_start
            pygame.draw.rect(self.screen, BLACK, (0, ui_y_start, SCREEN_WIDTH, ui_height))
            pygame.draw.rect(self.screen, WHITE, (0, ui_y_start, SCREEN_WIDTH, ui_height), 2) # 枠線

            # HPが30以下のときは文字を赤くする（ピンチ演出）
            hp_color = WHITE if self.player_hp > 30 else RED
            
            # ステータス情報の描画
            lv_text = f"Lv: {self.player_level}"
            exp_text = f"Exp: {self.player_exp}/{self.player_next_exp}"
            self.screen.blit(self.font.render(lv_text, True, GOLD), (30, ui_y_start + 15))
            self.screen.blit(self.small_font.render(exp_text, True, WHITE), (120, ui_y_start + 20))

            hp_text = f"HP: {self.player_hp}/{self.player_max_hp}"
            mp_text = f"MP: {self.player_mp}/{self.player_max_mp}"
            self.screen.blit(self.font.render(hp_text, True, hp_color), (300, ui_y_start + 15))
            self.screen.blit(self.font.render(mp_text, True, CYAN), (550, ui_y_start + 15))

            # コマンド説明
            cmd_text = "[A]たたかう  [M]まほう(30)  [H]ホイミ(10)"
            self.screen.blit(self.font.render(cmd_text, True, YELLOW), (30, ui_y_start + 60))

            # ログ表示エリアの区切り線
            line_y = ui_y_start + 100
            pygame.draw.line(self.screen, WHITE, (0, line_y), (SCREEN_WIDTH, line_y), 1)

            # バトルログの表示（最新5行のみ）
            display_logs = self.battle_logs[-5:] 
            for i, log in enumerate(display_logs):
                # ログの内容によって色を変える
                log_color = WHITE
                if "会心" in log: log_color = YELLOW
                if "やっつけた" in log: log_color = (255, 100, 100)
                if "レベルアップ" in log: log_color = GOLD
                if "足りない" in log: log_color = (255, 100, 255) # 警告色

                txt = self.small_font.render(log, True, log_color)
                self.screen.blit(txt, (30, line_y + 10 + i * 28))

        # --- エンディング画面 ---
        elif self.state == STATE_ENDING:
            self.screen.fill(WHITE)
            msg = self.font.render("MISSION COMPLETE!", True, BLACK)
            self.screen.blit(msg, (200, 300))

        # --- ゲームオーバー画面 ---
        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            msg = self.font.render("GAME OVER...", True, RED)
            self.screen.blit(msg, (300, 300))

        # 画面更新を確定
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()