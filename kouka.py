import pygame
import sys
import random
import os

import MapField

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 設定 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60


# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)   # 草原
GRAY = (169, 169, 169)  # キャンパス床
RED = (255, 0, 0)       # こうかとん
BLUE = (0, 0, 255)      # 雑魚敵
YELLOW = (255, 215, 0)  # ボス


# 状態定数
STATE_MAP = "MAP"
STATE_BATTLE = "BATTLE"
STATE_ENDING = "ENDING"


# マップID
MAP_VILLAGE = 0
MAP_FIELD = 1
MAP_CAMPUS = 2


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG こうく")
        self.clock = pygame.time.Clock()
       
        # 日本語フォントの設定（OSに合わせて読み込む）
        self.font = self.get_japanese_font(32)


        # プレイヤー初期状態
        self.player_pos = [50, 300]
        self.player_size = 40
        self.speed = 5
       
        # ゲーム進行管理
        self.state = STATE_MAP
        self.current_map = MAP_VILLAGE
        self.is_boss_battle = False
       
        # 戦闘用変数
        self.enemy_hp = 0
        self.battle_message = ""
        self.battle_sub_message = ""

        self.map_field = MapField.MapField(self.screen) # フィールド画面クラス C0A24265


    def get_japanese_font(self, size):
        """OS標準の日本語フォントを優先的に探して返す"""
        # Windows, Mac, Linuxで一般的な日本語フォント名
        font_names = ["meiryo", "msgothic", "yugothic", "hiraginosans", "notosanscjkjp", "takaoexgothic"]
        available_fonts = pygame.font.get_fonts()
       
        selected_font = None
        for name in font_names:
            if name in available_fonts:
                selected_font = name
                break
       
        if selected_font:
            return pygame.font.SysFont(selected_font, size)
        else:
            # 見つからない場合はデフォルト（日本語が表示できない可能性あり）
            print("警告: 日本語フォントが見つかりませんでした。")
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
           
            # 戦闘中・エンディング中の操作
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_BATTLE:
                    if event.key == pygame.K_SPACE:
                        # 攻撃処理
                        damage = random.randint(30, 60)
                        self.enemy_hp -= damage
                        self.battle_message = f"こうかとんの攻撃！ {damage} のダメージ！"
                        if self.enemy_hp <= 0:
                            self.end_battle()
                elif self.state == STATE_ENDING:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


    def update(self):
        if self.state == STATE_MAP:
            keys = pygame.key.get_pressed()
            moved = False

            if self.current_map == MAP_FIELD: # フィールドマップ時 C0A24265
                prev_x, prev_y = self.map_field.player_x, self.map_field.player_y # 移動前座標保存 C0A24265
                self.map_field.update() # フィールド画面更新 C0A24265
                if (prev_x, prev_y) != (self.map_field.player_x, self.map_field.player_y): # 座標が変化したら C0A24265
                    moved = True # 移動フラグ立て C0A24265
                if MapField.check_move(self.map_field): # マップ移動判定 C0A24265
                    self.current_map = MAP_CAMPUS
            else:
                # 移動処理
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


            # マップ遷移判定とエンカウント
            self.check_map_transition()
            if moved and self.current_map == MAP_FIELD:
                self.check_random_encounter()

           
            # ボスイベント判定（キャンパス奥地）
            if self.current_map == MAP_CAMPUS and self.player_pos[0] > 700:
                self.start_battle(is_boss=True)


    def check_map_transition(self):
        # 画面端でのマップ切り替え
        if self.player_pos[0] > SCREEN_WIDTH:
            if self.current_map < MAP_CAMPUS:
                self.current_map += 1
                self.player_pos[0] = 10 # 次のマップの左端へ
            else:
                self.player_pos[0] = SCREEN_WIDTH - self.player_size # 行き止まり


        elif self.player_pos[0] < 0:
            if self.current_map > MAP_VILLAGE:
                self.current_map -= 1
                self.player_pos[0] = SCREEN_WIDTH - 10 # 前のマップの右端へ
            else:
                self.player_pos[0] = 0 # 行き止まり


    # --- 重要：遷移関数 ---
    def check_random_encounter(self):
        # 1%の確率で戦闘開始（移動中常に呼ばれる）
        if random.randint(0, 100) < 1: # 遭遇率調整
            self.start_battle(is_boss=False)


    def start_battle(self, is_boss):
        self.state = STATE_BATTLE
        self.is_boss_battle = is_boss
        self.battle_sub_message = "スペースキーで攻撃！"
        if is_boss:
            self.enemy_hp = 500
            self.battle_message = "「単位を奪う悪の組織」が現れた！"
        else:
            self.enemy_hp = 100
            self.battle_message = "「未提出の課題」が現れた！"


    def end_battle(self):
        if self.is_boss_battle:
            self.state = STATE_ENDING
        else:
            self.state = STATE_MAP
            self.battle_message = ""
            # 戦闘終了後、再エンカウント防止のために少し座標をずらすなどの処理を入れるとより良い
            pygame.time.wait(500) # 少しウェイトを入れる


    def draw(self):
        self.screen.fill(BLACK)


        if self.state == STATE_MAP:
            # 背景描画
            color = GREEN
            loc_text = ""
            if self.current_map == MAP_VILLAGE:
                color = (100, 200, 100)
                loc_text = "最初の村（右へ進もう）"
            elif self.current_map == MAP_FIELD:
                # color = GREEN
                # loc_text = "外の散策エリア（敵が出ます）"
                pass # フィールド画面は testsub.MapField クラスで描画 C0A24265
            elif self.current_map == MAP_CAMPUS:
                color = GRAY
                loc_text = "八王子キャンパス（奥にボスがいます）"
           
            pygame.draw.rect(self.screen, color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            if self.current_map == MAP_FIELD: # フィールドマップ時 C0A24265
                self.map_field.draw() # フィールド画面描画 C0A24265
            
            if self.current_map != MAP_FIELD: # フィールドマップ以外はこうかとん描画 C0A24265
                # プレイヤー（こうかとん）
                pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))
           
            # ガイド表示
            text = self.font.render(loc_text, True, BLACK)
            self.screen.blit(text, (20, 20))


        elif self.state == STATE_BATTLE:
            # 戦闘画面
            # 敵の描画
            enemy_color = BLUE if not self.is_boss_battle else YELLOW
            pygame.draw.rect(self.screen, enemy_color, (300, 100, 200, 200))
           
            # メッセージ枠
            pygame.draw.rect(self.screen, BLACK, (0, 400, SCREEN_WIDTH, 200))
            pygame.draw.rect(self.screen, WHITE, (0, 400, SCREEN_WIDTH, 200), 2)


            msg = self.font.render(self.battle_message, True, WHITE)
            self.screen.blit(msg, (50, 420))
           
            hp_msg = self.font.render(f"敵HP: {self.enemy_hp}", True, WHITE)
            self.screen.blit(hp_msg, (50, 470))
           
            sub_msg = self.font.render(self.battle_sub_message, True, WHITE)
            self.screen.blit(sub_msg, (50, 520))


        elif self.state == STATE_ENDING:
            # エンディング（白暗転）
            self.screen.fill(WHITE)
            end_text1 = self.font.render("単位は守られた！", True, BLACK)
            end_text2 = self.font.render("Thank you for playing.", True, BLACK)
           
            self.screen.blit(end_text1, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(end_text2, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 30))


        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()

