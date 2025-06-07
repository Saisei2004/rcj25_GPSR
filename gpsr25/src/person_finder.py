#使いません

import json

# ----------------------------------------
# 複数引数バージョンのパーサー
# ----------------------------------------
def person_finder(*args):
    if len(args) == 4:
        angle, action, target_type, target_value = args
        return {
            "angle": angle,
            "action": action,
            "target_type": target_type,
            "target_value": target_value
        }
    elif len(args) == 3:
        angle, action, target_value = args
        return {
            "angle": angle,
            "action": action,
            "target_type": None,
            "target_value": target_value
        }
    elif len(args) == 2:
        angle, action = args
        return {
            "angle": angle,
            "action": action,
            "target_type": None,
            "target_value": None
        }
    else:
        return {"error": "引数の数が不正です"}

# ----------------------------------------
# 条件ごとの処理（今はprintだけ）
# ----------------------------------------
def handle_logic(parsed):
    if "error" in parsed:
        print(parsed["error"])
        return

    angle = parsed["angle"]
    action = parsed["action"]
    t_type = parsed["target_type"]
    t_value = parsed["target_value"]

    if action == "find" and t_type == "pose":
        print(f"[処理] {angle}度内でポーズ「{t_value}」の人を探す")

    elif action == "count" and t_type == "pose":
        print(f"[処理] {angle}度内でポーズ「{t_value}」の人の数を数える")

    elif action == "find" and t_type == "clothe":
        print(f"[処理] {angle}度内で「{t_value[0]}の{t_value[1]}」を着ている人を探す")

    elif action == "count" and t_type == "clothe":
        print(f"[処理] {angle}度内で「{t_value[0]}の{t_value[1]}」を着ている人の数を数える")

    elif action == "find" and t_type is None:
        print(f"[処理] {angle}度内で誰でもいいから人を探す")

    elif action == "count" and t_type is None:
        print(f"[処理] {angle}度内にいる人の数を数える")

    elif action == "name":
        print(f"[処理] {angle}度内で名前「{t_value}」の人を探す")

    else:
        print("[未対応] このコマンド形式は未対応です")

# ----------------------------------------
# 実行テスト（引数で渡すパターン）
# ----------------------------------------
if __name__ == "__main__":
    # test_args = [
    #     (90, 'find', 'pose', 'sitting'),
    #     (60, 'count', 'clothe', ['red', 'shirt']),
    #     (30, 'find'),
    #     (100, 'count'),
    #     (45, 'name', 'Jack')
    # ]

    # for args in test_args:
    #     print(f"\n📥 コマンド: {args}")
    #     parsed = parse_command_args(*args)
    #     handle_logic(parsed)
    
    parsed = person_finder(60, 'count', 'clothe', ['red', 'shirt'])
    handle_logic(parsed)
