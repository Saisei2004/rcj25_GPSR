#これつかってないらしいわ
#gpsr_aiみたいなやつ使ってね
from ex_mod import *
from gpsr_ai import obj_it
from config import *

def execute_command(command, obj=None, name=None, placemen=None, person=None, talk=None, 
                    person_info=None, obj_comp=None, color=None, clothe=None, 
                    rooms_1=None, rooms_2=None, color_map=None):
    
    # ANSIエスケープコードの定義
    RESET = "\033[0m"       # 色リセット
    RED = "\033[31m"        # 赤
    GREEN = "\033[32m"      # 緑
    YELLOW = "\033[33m"     # 黄
    BLUE = "\033[34m"       # 青
    CYAN = "\033[36m"       # シアン（明るい青）

    # デフォルトの色を赤にする
    default_color = RED

    operator = "operator"
    # saved_info = "saved_info"

    if obj == "it":
        obj = obj_it
    
    # ユーザーが指定したカラーマッピングがあれば、それを適用
    if color_map is None:
        color_map = {}  # デフォルトで空の辞書
    
    # `color_map` に指定されたコマンドごとの色を取得（なければデフォルトの赤）
    command_color = color_map.get(command, default_color)
    
    if command == "answerQuestion":
        print(command_color + "目の前の人の質問に答える" + RESET)
        print(YELLOW + f"")
        
        '''
        目の前を見る
        質問に答える
        '''
        #目の前を見る

        look_person()
        answer_question(talk)
    
    elif command == "answerToGestPrsInRoom":
        print(command_color + f"{rooms_1}にいる{person}の人の質問に答える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人の場所を特定
        近づく
        質問に答える
        '''
        navigate(rooms_1)
        find_pose(person)
        approach_person()
        answer_question(talk)

    
    elif command == "countPrsInRoom":
        print(command_color + f"{rooms_1}にいる{person}を数えてオペレーターに伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を数える
        移動する
        '''
        navigate(rooms_1)
        count_pose(person)
        navigate(operator)
    
    elif command == "countClothPrsInRoom":
        print(command_color + f"{rooms_1}にいる{color}色の{clothe}を着ている人の数をオペレーターに伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        ある色のある服を着ている人を数える
        移動する
        保存した情報を伝える
        '''
        navigate(rooms_1)
        saved_info = count_color_cloth(color,clothe)
        navigate(operator)
        # saved_info = "aaaaaaaaaaaaaaaaaa"
        give_saved_info(saved_info)
    
    elif command == "countObjOnPlcmt":
        print(command_color + f"{placemen}の上にある{obj}の数をオペレーターに伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるのものの数を数える
        保存した情報をオペレーターに伝える
        '''
        navigate(placemen)
        saved_info = count_object(obj)
        navigate(operator)
        give_saved_info(saved_info)
    
    elif command == "bringMeObjFromPlcmt":
        print(command_color + f"{placemen}にある{obj}をオペレーターにもっていく" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるものを掴む
        移動する
        渡す
        '''
        navigate(placemen)
        pick_object(obj)
        navigate(operator)
        hand_object()

    
    elif command == "deliverObjToMe":
        print(command_color + f"{obj}をオペレーターに持っていく" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        渡す
        '''
        navigate(operator)
        hand_object()
    
    elif command == "deliverObjToPrsInRoom":
        print(command_color + f"{rooms_1}にいる{person}にそれを持っていく" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズをしている人を探す
        渡す
        '''
        navigate(rooms_1)
        find_pose(person)
        hand_object()

    
    elif command == "findObj":
        print(command_color + f"{obj}を見つける" + RESET)
        print(YELLOW + f"")
        '''
        あるものを探す
        '''
        find_object(obj)
    
    elif command == "findObjInRoom":
        print(command_color + f"{rooms_1}で{obj}を見つける" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるものを探す
        '''
        navigate(rooms_1)
        find_object(obj)
    
    elif command == "findPrs":
        print(command_color + f"{person}をその場で探す" + RESET)
        print(YELLOW + f"")
        '''
        あるポーズの人を探す
        '''
        find_pose(person)
    
    elif command == "findPrsInRoom":
        print(command_color + f"{person}を{rooms_1}で探す" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を探す
        '''
        navigate(rooms_1)
        find_pose(person)
    
    elif command == "followPrs":
        print(command_color + f"{name}についていく" + RESET)
        print(YELLOW + f"")
        '''
        目の前の人を見る
        名前を聞いて人を特定する
        人追従
        '''
        look_person()
        find_name(name)
        follow_person()
    
    elif command == "followPrsAtLoc":
        print(command_color + f"{rooms_1}の{person}についていく" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        人を探す
        人に近づく
        人追従
        '''
        navigate(rooms_1)
        find_person()
        approach_person()
        follow_person()
    
    elif command == "followNameFromBeacToRoom":
        print(command_color + f"{name}を{rooms_1}から{rooms_2}についていく" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        目の前の人を見る
        名前を聞く
        人追従
        '''
        navigate(rooms_1)
        look_person()
        find_name(name)
        follow_person()
    
    elif command == "followPrsToRoom":
        print(command_color + f"{rooms_1}まで{person}についていく" + RESET)
        print(YELLOW + f"")
        '''
        あるポーズの人を探す
        人追従
        '''
        find_pose(person)
        follow_person(rooms_1)
    
    elif command == "goToLoc":
        print(command_color + f"{rooms_1}に行く" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        '''
        navigate(rooms_1)
    
    elif command == "greetClothDscInRm":
        print(command_color + f"{rooms_1}にいる{color}色の{clothe}を着ている人にhelloと言う" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        ある色のある服を着ている人を探す
        近づく
        挨拶する
        '''
        navigate(rooms_1)
        find_color_cloth(color,clothe)
        approach_person()
        greet_selfintro()
    
    elif command == "greetNameInRm":
        print(command_color + f"{rooms_1}にいる{name}にhelloを言う" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        名前確認
        近づく
        挨拶
        '''
        navigate(rooms_1)
        find_name(name)
        approach_person()
        greet_selfintro()

    
    elif command == "guideClothPrsFromBeacToBeac":
        print(command_color + f"{color}色の{clothe}を着ている人を{rooms_1}から{rooms_2}についていく" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        ある色のある服の人を探す
        ついていく
        '''
        navigate(rooms_1)
        find_color_cloth(color,clothe)
        follow_person(rooms_2)
    
    elif command == "guideNameFromBeacToBeac":
        print(command_color + f"{name}を{rooms_1}から{rooms_2}に案内する" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        名前確認
        移動する（案内）
        '''
        navigate(rooms_1)
        find_name(name)
        guide(rooms_2)
    
    elif command == "guidePrsToBeacon":
        print(command_color + f"{name}を{rooms_1}に案内する" + RESET)
        print(YELLOW + f"")
        '''
        名前確認
        移動する（案内）
        '''
        find_name(name)
        guide(rooms_1)
    
    elif command == "meetName":
        print(command_color + f"その場で{name}に会う" + RESET)
        print(YELLOW + f"")
        '''
        名前確認
        挨拶
        '''
        find_name(name)
        greet_selfintro()
    
    elif command == "meetNameAtLoc":
        print(command_color + f"{rooms_1}で{name}に会う" + RESET)
        print(YELLOW + f"")
        '''
        移動
        名前確認
        挨拶
        '''
        navigate(rooms_1)
        find_name(name)
        greet_selfintro()
    
    elif command == "meetPrsAtBea":
        print(command_color + f"{rooms_1}で{name}に会う" + RESET)
        print(YELLOW + f"")
        '''
        移動
        名前確認
        挨拶
        '''
        navigate(rooms_1)
        find_name(name)
        greet_selfintro()
    
    elif command == "placeObjOnPlcmt":
        print(command_color + f"{obj}を{placemen}の上に置く" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        家具の上に置く
        '''
        navigate(placemen)
        put_object()
    
    elif command == "takeObjFromPlcmt":
        print(command_color + f"{obj}を{placemen}からとる" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるのもを取る
        '''
        navigate(placemen)
        pick_object(obj)
    
    elif command == "takeObj":
        print(command_color + f"{obj}をとる" + RESET)
        print(YELLOW + f"")
        '''
        あるものを取る
        '''
        pick_object(obj)
    
    elif command == "talkInfo":
        print(command_color + f"{talk}を伝える" + RESET)
        print(YELLOW + f"")
        '''
        情報を伝える
        '''
        give_info(talk)

    
    elif command == "tellCatPropOnPlcmt":
        print(command_color + f"オペレーターに{placemen}の上の{obj_comp}の{obj}がどれか伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        ある特徴のあるもののソートを特定する
        移動する
        保存した情報を伝える
        '''
        navigate(placemen)
        find_feature(obj_comp,obj)
        navigate(operator)
        give_saved_info(saved_info)
    
    elif command == "tellObjPropOnPlcmt":
        print(command_color + f"オペレーターに{placemen}の上の{obj_comp}の{obj}がどれか伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        ある特徴のあるもののソートを特定する
        移動する
        保存した情報を伝える
        '''
        navigate(placemen)
        find_feature(obj_comp,obj)
        navigate(operator)
        give_saved_info()
    
    elif command == "tellPrsInfoInLoc":
        print(command_color + f"オペレーターに{rooms_1}にいる人の{person_info}を伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        人を見つける
        近づく
        目の前の人のある情報を取得する
        移動する
        保存した情報を伝える
        '''
        navigate(rooms_1)
        find_person()
        find_info(person_info)
        approach_person()
        navigate(operator)
        give_saved_info(saved_info)

    
    elif command == "tellPrsInfoAtLocToPrsAtLoc":
        print(command_color + f"{rooms_1}にいる人の{person_info}を{rooms_2}にいる人に伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        人を見つける
        近づく
        目の前の人のある情報を取得する
        移動する
        人を見つける
        近づく
        保存した情報を伝える
        '''
        navigate(rooms_1)
        find_person()
        approach_person()
        find_info(person_info)
        navigate(rooms_2)
        find_person()
        approach_person()
        give_saved_info(saved_info)
    
    elif command == "guidePrsFromBeacToBeac":
        print(command_color + f"{person}を{rooms_1}から{rooms_2}に案内する" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を見つける
        移動（案内）
        '''
        navigate(rooms_1)
        find_pose(person)
        guide(rooms_2)
    
    elif command == "talkInfoToGestPrsInRoom":
        print(command_color + f"{rooms_1}にいる{person}に、{talk}を伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を見つける
        ある情報を伝える
        '''
        navigate(rooms_1)
        find_pose(person)
        give_info(talk)
    
    else:
        print(command_color + f"未定義のコマンド: {command}" + RESET)
        
    print(RESET)

# def remove_brackets(s):
#     start = s.find('[') + 1  # '[' の次の位置を取得
#     end = s.rfind(']')  # ']' の位置を取得
#     return s[start:end] if start > 0 and end > start else s 


# def force_to_list(data):
#     """
#     Converts the input into a list.
    
#     - If the input is a tuple, it converts it into a list.
#     - If the input is a string, it wraps it in a list.
#     - If the input is already a list, it returns it unchanged.
#     - For any other type, it returns a single-element list containing the input.
#     """
#     if isinstance(data, list):
#         return data
#     elif isinstance(data, tuple):
#         return list(data)
#     elif isinstance(data, str):
#         return [data]
#     else:
#         return [data]
    
