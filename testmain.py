import pygame as pg
import os
import sys

import MapField

os.chdir(os.path.dirname(os.path.abspath(__file__))) # カレントディレクトリをこのファイルの場所に変更

class MainGame:
    def __init__(self):
        pg.init()

        # 画面作成
        self.screen = pg.display.set_mode((MapField.SCREEN_WIDTH, MapField.SCREEN_HEIGHT)) # 画面サイズ
        pg.display.set_caption("Map Test Main") # 画面タイトル

        self.clock = pg.time.Clock() # クロック設定

        # フィールド生成（testsub.pyのクラスをそのまま使う）
        self.map_field = MapField.MapField(self.screen) # フィールド画面クラス

        # 状態管理
        self.running = True # メインループ制御フラグ

    def run(self): # メインループ
        while self.running: # メインループ
            self.handle_events() # イベント処理
            result = self.map_field.update() # フィールド更新処理

            # エンカウント検知
            if result == "ENCOUNTER": # エンカウント発生時
                print("エンカウント発生！（ここでバトル画面に切替可能）") # デバッグ用表示

            self.draw() # 画面描画処理
            self.clock.tick(60) # フレームレート設定

        pg.quit() # Pygame終了
        sys.exit() # プログラム終了

    def handle_events(self): # イベント処理
        for event in pg.event.get(): # イベントループ
            if event.type == pg.QUIT: # 終了イベント
                self.running = False # メインループ終了

    def draw(self): # 画面描画処理
        self.screen.fill((0, 0, 0)) # 画面クリア
        self.map_field.draw() # フィールド画面描画
        pg.display.flip() # 画面更新


if __name__ == "__main__":
    MainGame().run() # メインゲーム実行