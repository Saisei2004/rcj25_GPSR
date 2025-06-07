# -*- coding: utf-8 -*-
import sys
import re
import difflib
import time

# 移動制御用のダミークラス
class BaseControl:
    def rotateAngle(self, angle, speed=0, wait=1):
        print(f"🔄 {angle}度 回転します")
        time.sleep(wait)

    def translateDist(self, distance, speed=0.5):
        print(f"🚶 {distance}m 移動します")
        time.sleep(1)

# 仮のTTS：端末に出力
def dummy_tts(message):
    print(f"💬 ロボット: {message}")

# 仮のSTT：端末から入力
def dummy_stt():
    text = input("🎤 人間（話してください）: ")
    return text

# 仮の距離取得サービス
def dummy_get_distance():
    try:
        value = float(input("📏 移動すべき距離（例: 1.0）: "))
        return value
    except ValueError:
        print("❌ 入力が無効です。0を返します")
        return 0.0

class AskName:
    def __init__(self, angle_list=None, want_name=['Jack']):
        self.bc = BaseControl()
        self.angle_list = angle_list if angle_list else [30, 50, 80, 90]
        self.want_name = want_name
        self.num = len(self.angle_list)
        self.now_num = 1
        self.list_num = 0
        self.now_angle = 90
        self.name_list = ["Jack", "Aaron", "Angel", "Adam", "Vanessa", "Chris", "William", "Max", "Hunter", "Olivia", "them"]
        self.answer_list = ["yes", "no"]

    def ask_name(self):
        print(self.angle_list)
        for angle in self.angle_list:
            print(f"➡️ 現在の角度: {self.now_angle}, 次の角度: {angle}")
            rot_angle = angle - self.now_angle
            self.bc.rotateAngle(rot_angle)
            self.now_angle = angle

            distance_to_move = dummy_get_distance()
            if distance_to_move < 0:
                distance_to_move = 0
            self.bc.translateDist(distance_to_move)

            while True:
                dummy_tts("What your name?")
                sentence = dummy_stt()

                name_tx_list = [w for w in re.split("[. !?,]", sentence.strip()) if w]
                print("🔍 分解結果:", name_tx_list)

                if name_tx_list:
                    name = name_tx_list[-1]
                    name = difflib.get_close_matches(name, self.name_list, n=1, cutoff=0.3)
                    print("🎯 候補:", name)

                    if name:
                        dummy_tts(f"Are you {name[0]}?")
                        dummy_tts("please answer yes or no.")
                        answer = dummy_stt()
                        answer_words = [w for w in re.split("[. !?,]", answer.strip()) if w]
                        if answer_words:
                            answer = answer_words[-1]
                            answer = difflib.get_close_matches(answer, self.answer_list, n=1, cutoff=0.3)
                            print("🤔 回答:", answer)

                            if answer == ['yes']:
                                print("✅ 名前の受取に成功")
                                break
                            else:
                                print("❌ 名前の受取に失敗。再試行します。")
                                continue
                        else:
                            print("❌ 聞き取り失敗。再試行します。")
                            continue
                    else:
                        print("❌ 候補が見つかりませんでした。再試行します。")
                        continue
                else:
                    print("❌ 聞き取り失敗。再試行します。")
                    continue

            print(f"📋 受け取った名前: {name}")
            print(f"🎯 ターゲット名: {self.want_name}")
            if name[0] in self.want_name:
                print(f"✅ 名前の一致を確認。角度: {angle}")
                self.bc.translateDist(-distance_to_move)
                return "FIN"
            else:
                print("❌ 一致しませんでした。")
                self.bc.translateDist(-distance_to_move)
                continue

        return "NOT_FOUND"

# 他のスクリプトから使えるように関数定義
def run_ask_name_with_params(angle_list, want_name):
    print("🌟", angle_list, "の方向の中から", want_name, "を探す🌟")
    client = AskName(angle_list=angle_list, want_name=want_name)
    result = client.ask_name()
    return result

# スクリプトとして動かすとき
if __name__ == "__main__":
    result = run_ask_name_with_params([30, 60, 90], ["Olivia"])
    print(f"🎉 結果: {result}")
