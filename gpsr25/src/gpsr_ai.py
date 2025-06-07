import random
import re
import itertools
from difflib import get_close_matches
import sys

import warnings
obj_it = None
from utils import *
from config import *
from cmd_gen import *
from ex_mod import *

import re
from collections import Counter

from difflib import SequenceMatcher

segment_counter1 = Counter()
segment_counter2 = Counter()
segment_counter3 = Counter()
segment_counter4 = Counter()

# 全体のセグメントリスト
output_text_list = []
special_words = ["it"]

    # CommandGeneratorのインスタンスを作成します
cmd_gen = CommandGenerator(
    person_names,
    location_names,
    placement_location_names,
    room_names,
    object_names,
    object_categories_plural,
    object_categories_singular
)

import sys
import re
from collections import Counter

# 各セグメントのカウンター
segment_counter1 = Counter()
segment_counter2 = Counter()
segment_counter3 = Counter()
segment_counter4 = Counter()

# 全体のセグメントリスト
output_text_list = []

special_words = ["it"]

unk_to_re_lists = {
    "objects_unk": result_objects,
    "rooms_unk": result_rooms,
    "nema_unk": result_names,
    "placemen_unk": result_placemen,
    "person_unk": result_person,
    "talk_unk": result_talk,
    "person_info_unk": result_person_info,
    "object_comp_unk": result_object_comp,
    "color_list_unk": result_color_list,
    "clothe_list_unk": result_clothe_list,
}

now_room = None
find_fin = None
saved_info = "saved_info"

def execute_command(command, obj=None, name=None, placemen=None, person=None, talk=None, 
                    person_info=None, obj_comp=None, color=None, clothe=None, 
                    rooms_1=None, rooms_2=None, color_map=None):
    
    global now_room
    global saved_info
    global find_fin
    
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
    saved_info = "saved_info"

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
        approach_person()
        answer_question()
    
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
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,rooms_1)
        approach_person()
        answer_question()
        now_room = rooms_1

    
    elif command == "countPrsInRoom":
        print(command_color + f"{rooms_1}にいる{person}を数えてオペレーターに伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を数える
        移動する
        '''
        
        navigate(rooms_1)
        saved_info = count_pose(person)
        navigate(operator)
        give_saved_info(saved_info)
        now_room = rooms_1
    
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
        now_room = rooms_1
    
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
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,rooms_1)
        hand_object()
        now_room = rooms_1

    
    elif command == "findObj":
        print(command_color + f"{obj}を見つける" + RESET)
        print(YELLOW + f"")
        '''
        あるものを探す
        '''
        if obj == None:
            obj = input_text
        find_fin = find_object(obj,now_room)
        print("これが見たかった！！")
    
    elif command == "findObjInRoom":
        print(command_color + f"{rooms_1}で{obj}を見つける" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるものを探す
        '''
        # navigate(rooms_1)
        if obj == None:
            obj = input_text
        find_fin = find_object(obj,rooms_1)
        now_room = rooms_1
    
    elif command == "findPrs":
        print(command_color + f"{person}をその場で探す" + RESET)
        print(YELLOW + f"")
        '''
        あるポーズの人を探す
        '''
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,None)
    
    elif command == "findPrsInRoom":
        print(command_color + f"{person}を{rooms_1}で探す" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を探す
        '''
        navigate(rooms_1)
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,rooms_1)
        now_room = rooms_1
    
    elif command == "followPrs":
        print(command_color + f"{name}についていく" + RESET)
        print(YELLOW + f"")
        '''
        目の前の人を見る
        名前を聞いて人を特定する
        人追従
        '''
        look_person()
        if name != "them":
            find_name(name)
        follow_person()
        now_name = name
    
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
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,rooms_1)        
        approach_person()
        follow_person()
        now_room = rooms_1
    
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
        if name != "them":
            find_name(name)
        follow_person()
        now_room = rooms_1
        now_name = name
    
    elif command == "followPrsToRoom":
        print(command_color + f"{rooms_1}まで{person}についていく" + RESET)
        print(YELLOW + f"")
        '''
        あるポーズの人を探す
        人追従
        '''
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,None)

        follow_person(rooms_1)
        now_room = rooms_1
        
    
    elif command == "goToLoc":
        print(command_color + f"{rooms_1}に行く" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        '''
        navigate(rooms_1)
        now_room = rooms_1
    
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
        now_room = rooms_1
    
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
        if name != "them":
            find_name(name)
        approach_person()
        greet_selfintro()
        now_room = rooms_1
        now_name = name

    
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
        now_room = rooms_2
    
    elif command == "guideNameFromBeacToBeac":
        print(command_color + f"{name}を{rooms_1}から{rooms_2}に案内する" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        名前確認
        移動する（案内）
        '''
        navigate(rooms_1)
        print(name)
        if name == "them":
            pass
        elif name in person_list:
            find_pose(name,None)
        elif name != "them":
            find_name(name)
        guide(rooms_2)
        now_room = rooms_2
        now_name = name
    
    elif command == "guidePrsToBeacon":
        print(command_color + f"{name}を{rooms_1}に案内する" + RESET)
        print(YELLOW + f"")
        '''
        名前確認
        移動する（案内）
        '''
        print(type(name),name)
        if name == "them":
            pass
        elif name in person:
            find_pose(name)
        elif name != "them":
            find_name(name)
        guide(rooms_1)
        now_room = rooms_1
        now_name = name
    
    elif command == "meetName":
        print(command_color + f"その場で{name}に会う" + RESET)
        print(YELLOW + f"")
        '''
        名前確認
        挨拶
        '''
        if name != "them":
            find_name(name)
        greet_selfintro()
        now_name = name
    
    elif command == "meetNameAtLoc":
        print(command_color + f"{rooms_1}で{name}に会う" + RESET)
        print(YELLOW + f"")
        '''
        移動
        名前確認
        挨拶
        '''
        navigate(rooms_1)
        if name != "them":
            find_name(name)
        greet_selfintro()
        now_room = rooms_1
        now_name = name
    
    elif command == "meetPrsAtBea":
        print(command_color + f"{rooms_1}で{name}に会う" + RESET)
        print(YELLOW + f"")
        '''
        移動
        名前確認
        挨拶
        '''
        navigate(rooms_1)
        if name != "them":
            find_name(name)
        greet_selfintro()
        now_room = rooms_1
        now_name = name
    
    elif command == "placeObjOnPlcmt":
        print(command_color + f"{obj}を{placemen}の上に置く" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        家具の上に置く
        '''
        navigate(placemen)
        put_object(placemen)
    
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
        if find_fin == True:
            print("把持済みです")
        else:
            pick_object(obj)
    
    elif command == "talkInfo":
        print(command_color + f"{talk}を伝える" + RESET)
        print(YELLOW + f"")
        '''
        情報を伝える
        '''
        approach_person()
        if talk == None:
            give_saved_info(saved_info)
        else:
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
        saved_info = find_feature(obj_comp,obj)
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
        saved_info = find_feature(obj_comp,obj)
        navigate(operator)
        give_saved_info(saved_info)
    
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
        approach_person()
        saved_info = find_info(person_info)      
        navigate(operator)
        give_saved_info(saved_info)
        now_room = rooms_1

    
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
        saved_info = find_info(person_info)
        navigate(rooms_2)
        find_person()
        approach_person()
        give_saved_info(saved_info)
        now_room = rooms_2
    
    elif command == "guidePrsFromBeacToBeac":
        print(command_color + f"{person}を{rooms_1}から{rooms_2}に案内する" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を見つける
        移動（案内）
        '''
        navigate(rooms_1)
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,rooms_1)
        guide(rooms_2)
        now_room = rooms_2
    
    elif command == "talkInfoToGestPrsInRoom":
        print(command_color + f"{rooms_1}にいる{person}に、{talk}を伝える" + RESET)
        print(YELLOW + f"")
        '''
        移動する
        あるポーズの人を見つける
        ある情報を伝える
        '''
        navigate(rooms_1)
        if person == "them":
            pass
        elif person in names:
            find_name(person)
        elif person in person_list:
            find_pose(person,rooms_1)
        give_info(talk)
        now_room = rooms_1
    
    else:
        print(command_color + f"未定義のコマンド: {command}" + RESET)
        
    print(RESET)


def replace_text(text):
    # オブジェクト名を "OBJ" に置き換え
    # if input_text == None:
    #     return "" , []
    for obj in objects_OBJ:
        text = re.sub(rf"\b{obj}\b", "OBJ", text)

    for plcmt in placemen:
        text = re.sub(rf"\b{plcmt}\b", "PLCMT", text)

    for tell in talk:
        text = re.sub(rf"\b{tell}\b", "INFO", text)

    # personリストの各項目を正確に"PRS"に置き換え
    for prs in person:
        text = re.sub(rf"\b{re.escape(prs)}\b", "PRS", text)

    for prsinfo in person_info:
        text = re.sub(rf"\b{prsinfo}\b", "PRSINFO", text)
    
    # 部屋名を "ROOM" に置き換え
    for room in rooms:
        text = re.sub(rf"\b{re.escape(room)}\b", "ROOM", text)
    
    # 名前を "NAME" に置き換え
    for name in names:
        text = re.sub(rf"\b{name}\b", "PRS", text)
    
    # 動詞をカテゴリー + "Verb" に置き換え
    for verb_category, verb_list in verbs.items():
        for verb in verb_list:
            text = re.sub(rf"\b{verb}\b", verb_category, text)

    text = re.sub(r"\bfrom\b", "FROM", text)
    text = re.sub(r"\bin\b", "IN", text)
    text = re.sub(r"\bto\b", "TO", text)
    text = re.sub(r"\bon\b", "ON", text)
    text = re.sub(r"\bthem\b", "PRS", text)
    text = re.sub(r"\bme\b", "ME", text)
    text = re.sub(r"\bat\b", "AT", text)
    text = re.sub(r"\bquestion\b", "QUESTION", text)    
    text = re.sub(r"\bquiz\b", "QUESTION", text)  
    text = re.sub(r"\bwhat is\b \w+ \w+", "PROP", text)
    text = re.sub(r".*\bhow many \b\w+", "COUNT", text)
    text = re.sub(r"\bwearing\b \w+ \w+", "CLOTHPRS", text)
    text = re.sub(r"\bthere\b", "OBJ", text)
    text = re.sub(r"\bwearing\b", "CLOTHPRS", text)
    text = re.sub(r"\bsitting person\b", "PRS", text)
    text = re.sub(r"_\s", "", text)
    text = re.sub(r"\?", "", text)

    

    # 最終的な変換を実行（大文字変換）
    for category, replacement in final_replacements.items():
        text = text.replace(category, replacement)

    # "and" または "then" で分割して別項目として保存
    split_text = re.split(r"\b(?:and|then)\b", text)
    split_text = [segment.strip() for segment in split_text if segment.strip()]  # 空の要素を削除

    # 各セグメントから小文字を削除し、再度空白を1つに統一
    split_text = [re.sub(r"[a-z]", "", segment).strip() for segment in split_text]
    split_text = [re.sub(r"\s+", " ", segment) for segment in split_text]  # 最後に再度、余分な空白を削除
    
    # 各セグメントから出現順に動詞を抽出
    verbs_found = []
    for segment in split_text:
        segment_verbs = []
        for match in re.finditer(r"\b(" + "|".join(final_replacements.values()) + r")\b", segment):
            segment_verbs.append(match.group())
        verbs_found.append(segment_verbs)

    return split_text, verbs_found


def filter_text(segment):
    segment = re.sub(r"[^A-Z\s]", "", segment)  # 大文字と空白以外を削除
    segment = re.sub(r"\s{2,}", " ", segment)    # 連続する空白を1つに統一
    return segment.strip()


def match_segment_with_manual_mapping(segment, threshold=0.6):
    # 空白を除去したフィルタリング済みセグメントを用意
    #print("セグメント",segment)

    #強制的な処理
    if segment == "TALK TO PRS IN ROOM":
        return "greetNameInRm"

    filtered_segment = filter_text(segment)


    # 最も類似度の高いキーを見つける
    best_match = None
    highest_score = 0

    for key in manual_mapping.keys():
        # 類似度スコアを計算
        score = SequenceMatcher(None, filtered_segment, key).ratio()
        
        # 最も高いスコアでかつしきい値を超える場合に更新
        if score > highest_score and score >= threshold:
            highest_score = score
            best_match = key

    # 最も近いマッチが見つかった場合、そのマッピングを返す
    if best_match:
        #print("あああ",manual_mapping[best_match])
        return manual_mapping[best_match]
    else:
        return "No match found"

# def extract_in_order_with_duplicates(text, words_list, word_type):
#     """
#     text: 検索対象の文字列
#     words_list: 検索する単語または文章のリスト
#     word_type: 現在のリストの種類（"rooms", "objects", など）
#     """
#     found_words = []
#     for word in words_list:
#         if word in text:
#             found_words.append(word)

#     # rooms と objects は最後の要素を3回追加する特別処理
#     if word_type in ["rooms", "objects"] and found_words:
#         last_word = found_words[-1]
#         found_words.extend([last_word] * 3)

#     return found_words



def extract_in_order_with_duplicates(text, words_list, word_type):
    """
    text: 検索対象の文字列
    words_list: 検索する単語のリスト
    word_type: 現在のリストの種類（"rooms", "objects", etc.）
    """
    found_words = []
    for word in words_list:
        if word_type == "person":
            # re.escape の結果を一時変数に格納して操作
            escaped_word = re.escape(word)
            # エスケープされた空白を正規表現の \s+ に置き換え
            escaped_word = escaped_word.replace(r"\ ", r"\s+")
            # パターンを作成
            pattern = r'\b' + escaped_word + r'\b'
        else:
            # 通常の完全一致を正規表現で検索
            pattern = r'\b' + re.escape(word) + r'\b'

        # パターンに一致する単語を検索
        matches = re.findall(pattern, text)
        
        # 重複ありにする場合（"rooms" または "objects"）
        if word_type in ["rooms", "objects"]:
            found_words.extend(matches)  # 重複をそのまま追加
        else:
            # 重複を排除して追加
            for match in matches:
                if match not in found_words:
                    found_words.append(match)
    
    # 最後の要素を処理（rooms または objects のみ）
    if word_type in ["rooms", "objects"] and found_words:
        last_word = found_words[-1]  # 最後の要素を取得
        found_words.extend([last_word] * 3)  # 最後の要素を3回追加

    # テキスト中の登場順に並び替え（空白を含む単語対応）
    ordered_words = []
    for word in words_list:
        # 空白を含む単語も認識できる正規表現を作成
        pattern = re.escape(word).replace(r"\ ", r"\s+")
        matches = re.finditer(pattern, text)
        for match in matches:
            if word not in ordered_words:
                ordered_words.append(word)

    found_words = ordered_words

    return found_words


def extract_words_in_order(input_text, category_list):
    """
    入力テキストからカテゴリに一致する単語を、順番を保持して抽出する関数
    """
    found_words = []
    for word in category_list:
        pattern = rf'\b{re.escape(word)}\b'
        matches = re.findall(pattern, input_text)
        found_words.extend(matches)
    return found_words


def replace_unk(description):
    # 置き換えた単語を格納する変数
    replaced_object = None
    replaced_name = None
    replaced_placemen = None
    replaced_person = None
    replaced_talk = None
    replaced_person_info = None
    replaced_object_comp = None
    replaced_color_list = None
    replaced_clothe_list = None

    # "objects_unk" を置き換え
    while "objects_unk" in description:
        print(result_objects)
        if result_objects:
            replaced_object = result_objects.pop(0)
            description = description.replace("objects_unk", replaced_object, 1)
        else:
            print("Warning: No more replacements available for 'objects_unk'",description)
            sys.exit()
            break

    # "nema_unk" を置き換え
    while "nema_unk" in description:
        if result_names:
            replaced_name = result_names.pop(0)
            description = description.replace("nema_unk", replaced_name, 1)
        elif result_person:
            replaced_name = result_person.pop(0)
            description = description.replace("nema_unk", replaced_name, 1)
        else:
            print("Warning: No more replacements available for 'nema_unk'")
            sys.exit()

    # "placemen_unk" を置き換え
    while "placemen_unk" in description:
        if result_placemen:
            replaced_placemen = result_placemen.pop(0)
            description = description.replace("placemen_unk", replaced_placemen, 1)
        else:
            print("Warning: No more replacements available for 'placemen_unk'")
            sys.exit()

    # "person_unk" を置き換え
    while "person_unk" in description:
        if result_person:
            replaced_person = result_person.pop(0)
            description = description.replace("person_unk", replaced_person, 1)
        elif result_names:
            replaced_person = result_names.pop(0)
            description = description.replace("person_unk", replaced_person, 1)
        else:
            print("Warning: No more replacements available for 'person_unk'")
            sys.exit()

    # "talk_unk" を置き換え
    while "talk_unk" in description:
        if result_talk:
            replaced_talk = result_talk.pop(0)
            description = description.replace("talk_unk", replaced_talk, 1)
        else:
            print("Warning: No more replacements available for 'talk_unk'")
            sys.exit()

    # "person_info_unk" を置き換え
    while "person_info_unk" in description:
        if result_person_info:
            replaced_person_info = result_person_info.pop(0)
            description = description.replace("person_info_unk", replaced_person_info, 1)
        else:
            print("Warning: No more replacements available for 'person_info_unk'")
            sys.exit()

    # "object_comp_unk" を置き換え
    while "object_comp_unk" in description:
        if result_object_comp:
            replaced_object_comp = result_object_comp.pop(0)
            description = description.replace("object_comp_unk", replaced_object_comp, 1)
        else:
            print("Warning: No more replacements available for 'object_comp_unk'")
            sys.exit()

    # "color_list_unk" を置き換え
    while "color_list_unk" in description:
        if result_color_list:
            replaced_color_list = result_color_list.pop(0)
            description = description.replace("color_list_unk", replaced_color_list, 1)
        else:
            print("Warning: No more replacements available for 'color_list_unk'")
            sys.exit()

    # "clothe_list_unk" を置き換え
    while "clothe_list_unk" in description:
        if result_clothe_list:
            replaced_clothe_list = result_clothe_list.pop(0)
            description = description.replace("clothe_list_unk", replaced_clothe_list, 1)
        else:
            print("Warning: No more replacements available for 'clothe_list_unk'")
            sys.exit()

    # エラーチェック
    # if "_unk" in description:
    #     print("Error: '_unk' が含まれています。プログラムを終了します。")
    #     sys.exit(1) 

    if "No" in description:
        print("ついかされてねーぜ")
        global saved_live
        saved_live = False
        # raise Exception("reading.....")
        sys.exit(1) 
        raise Exception("reading.....")
        
        

    # 置き換えた変数を辞書で返す
    return description, replaced_object, replaced_name, replaced_placemen, replaced_person, replaced_talk, replaced_person_info, replaced_object_comp, replaced_color_list, replaced_clothe_list


def find_matching_rooms(input_text: str, rooms: list) -> list:
    """
    input_text 内に含まれる room の名前を、出現順に抽出する。

    Parameters:
        input_text (str): 検索対象の文字列。
        rooms (list of str): 検索する部屋名のリスト。

    Returns:
        list: input_text 内で見つかった部屋名のリスト（出現順）。
    """
    if not rooms:
        return []  # rooms が None または空の場合、空リストを返す
    
    rooms = [room for room in rooms if isinstance(room, str) and room]  # 非文字列および空文字列を除外
    if not rooms:
        return []  # すべての要素が無効だった場合、空リストを返す
    
    found_rooms = []
    try:
        pattern = r'\b(?:' + '|'.join(re.escape(room) for room in sorted(rooms, key=len, reverse=True)) + r')\b'
    except TypeError:
        return []  # rooms に不正な値が含まれる場合は空リストを返す
    
    for match in re.finditer(pattern, input_text, re.IGNORECASE):
        found_rooms.append(match.group())
    
    return found_rooms

def replace_rooms_unk(input_text: str, found_rooms: list) -> tuple:
    """
    input_text 内の "rooms_unk" の数だけ、found_rooms の先頭から単語を抜き出し、
    "rooms_1", "rooms_2", ... の変数として返す。

    Parameters:
        input_text (str): 処理する文字列
        found_rooms (list): 置き換え用の単語が格納されたリスト

    Returns:
        tuple: (rooms_1, rooms_2, ..., 更新後の found_rooms リスト)
    """
    count = input_text.count("rooms_unk")  # "rooms_unk" の出現回数をカウント
    
    # "rooms_unk" が存在しない場合、None, None, found_rooms を返す
    if count == 0:
        return None, None, found_rooms
    
    # 取り出す単語の数が足りない場合、Noneを補完
    extracted_rooms = [found_rooms.pop(0) if found_rooms else None for _ in range(count)]
    
    # 更新後の found_rooms リスト
    updated_rooms = found_rooms[:]
    
    # タプルとして返す（rooms_1, rooms_2, ..., updated_rooms）
    return (*extracted_rooms, updated_rooms)

def extract_rooms(input_text: str, found_rooms: list):
    # "rooms_unk" の出現回数を数える（最大2個）
    count = min(len(re.findall(r"rooms_unk", input_text)), 2)
    # print("かうんと",count)

    # found_roomsの先頭からcount個の要素を取得（なければNone）
    rooms_1 = found_rooms.pop(0) if count >= 1 and found_rooms else None
    rooms_2 = found_rooms.pop(0) if count == 2 and found_rooms else None

    # 更新されたリストを取得
    updated_rooms_lst = found_rooms[:]

    return rooms_1, rooms_2, updated_rooms_lst


import os
import sys

'''
やばくない
↑
🟣本番使わなそうだから放置だ。                     1
🔵触るな！！完成だ！！                           14
🟡MAPでたら急いで作れ。ただしほぼ完成だ。           2
⚪デバッグ次第                                  4
🔴できてない！！やばい！！                        1
↓
やばい
'''
# from ask_name_new import run_ask_name_with_params
# print("test")
dbg = 0
if dbg == 1:
    print("test")
    time.sleep(3)

    print("😁😁😁😁😁名前探しデバッグ😁😁😁😁⚪")
    name = "Jack"
    angle = [0,90,180]
    find_name(name,angle)
    input_com = input("次のデバッグ行きますか？:")
    if input_com == "no":
        print("^Cを押せ")
        time.sleep(3)
    sys.exit()

    # print("😁😁😁😁😁コップ数えデバッグ😁😁😁😁⚪")
    # obj = "bottlerosr"
    # saved_info = count_object(obj)
    # give_saved_info(saved_info)
    # input_com = input("次のデバッグ行きますか？:")
    # if input_com == "no":
    #     print("^Cを押せ")
    #     time.sleep(3)
    # sys.exit()

    # print("😁😁😁😁😁部屋中モノ探しデバッグ😁😁😁⚪🟡")
    # now_room = "living room"
    # obj = "cup"
    # find_object(obj, now_room)
    # input_com = input("次のデバッグ行きますか？:")
    # if input_com == "no":
    #     print("^Cを押せ")
    #     time.sleep(3)

    # print("😁😁😁😁😁モノつかみデバッグ😁😁😁😁⚪")
    # obj = "red cup"
    # pick_object(obj)
    # sys.exit()
    # input_com = input("次のデバッグ行きますか？:")
    # if input_com == "no":
    #     print("^Cを押せ")
    #     time.sleep(3)

    # print("😁😁😁😁😁物体配置デバッグ😁😁😁😁⚪")
    # put_pl = "table"
    # put_object(put_pl)
    # sys.exit()

    '''
    print("😁😁😁😁😁もの特徴デバッグ😁😁😁😁🔴")
    obj_comp = "tall"
    saved_info = find_feature(obj_comp,obj)
    give_saved_info(saved_info)
    '''

    input_com = input("input: ")
    import time 
    for i in range(3):
        time.sleep(1)
elif dbg == 2:
    print("test2")
    num = int(input("実行したい関数の番号を入力してください（0～20）: "))

    if num == 0:#ok?
        print("🔧 実行: find_person()")
        find_person()

    elif num == 1:#ok
        print("🔧 実行: find_pose(person)")
        person = input("ポーズ名: ")
        find_pose(person,None)

    elif num == 2:#ok
        print("🔧 実行: count_pose(person)")
        person = input("ポーズ名: ")
        saved_info = count_pose(person)

    elif num == 3:#ok
        print("🔧 実行: find_color_cloth(color, clothe)")
        color = input("色: ")
        clothe = input("服: ")
        find_color_cloth(color, clothe)

    elif num == 4:#ok
        print("🔧 実行: count_color_cloth(color, clothe)")
        color = input("色: ")
        clothe = input("服: ")
        saved_info = count_color_cloth(color, clothe)

    elif num == 5:#進む距離治ればOK
        print("🔧 実行: find_name(name, angle)")
        name = input("名前: ")
        find_name(name)

    elif num == 6:#おそらくok？　名前のやつできればOK
        print("🔧 実行: find_info(person_info)")
        person_info = input("人物情報: ")
        saved_info = find_info(person_info)

    elif num == 7:#okだけど、v8次第　首の角度
        print("🔧 実行: count_object(obj)")
        obj = input("物体名: ")
        saved_info = count_object(obj)

    elif num == 8:#これ動きはしたけど、今の環境ではちょっと
        print("🔧 実行: find_object(obj, now_room)")
        obj = input("物体名: ")
        now_room = input("現在の部屋名: ")
        find_object(obj, now_room)

    elif num == 9:#okじゃないけどok　GPTでやるかな
        print("🔧 実行: find_feature(obj_comp, obj)")
        obj_comp = input("比較対象を入力してください: ")
        obj = input("物体名を入力してください: ")
        saved_info = find_feature(obj_comp, obj)

    elif num == 10:#ok
        print("🔧 実行: greet_selfintro()")
        greet_selfintro()

    elif num == 11:#ok
        print("🔧 実行: give_info(talk)")
        talk = input("話す内容: ")
        give_info(talk)

    elif num == 12:#ok
        print("🔧 実行: answer_question()")
        answer_question()

    elif num == 13:#ok
        print("🔧 実行: give_saved_info(saved_info)")
        saved_info = input("保存された情報を入力してください: ")
        give_saved_info(saved_info)

    elif num == 14:#ok
        print("🔧 実行: navigate(rooms)")
        rooms = input("移動先: ").split(',')
        navigate(rooms)

    elif num == 15:#ok
        print("🔧 実行: approach_person()")
        approach_person()

    elif num == 16:#ok
        print("🔧 実行: follow_person(rooms)")
        # rooms_input = input("追従先（空欄で全体）: ")
        # rooms = rooms_input.split(',') if rooms_input else None
        follow_person(rooms)

    elif num == 17:#ok
        print("🔧 実行: guide(rooms)")
        rooms = input("案内する部屋名: ").split(',')
        guide(rooms)

    elif num == 18:#ok
        print("🔧 実行: pick_object(obj)")
        obj = input("持ち上げる物体名: ")
        pick_object(obj)

    elif num == 19:#ok
        print("🔧 実行: hand_object()")
        hand_object()

    elif num == 20:#ok
        print("🔧 実行: put_object(put_pl)")
        put_pl = input("置く場所: ")
        put_object(put_pl)

    else:
        print("⚠ 無効な番号です。0～20の範囲で入力してください。")

    give_saved_info(saved_info)
    print(saved_info)
    sys.exit()

elif dbg == 3:
    tts_pub2("Hello my name is mmimimimimimimimimimimimimimimimi")
    rospy.sleep(5)
    sys.exit()
# #     find_name_dbg("jack")
# #     sys.exit()
#     pick_object("red cup")
# print("これがひょうじされたら異常！！！！")
# sys.exit()

        


count = 0

# コマンド生成とカウント
for _ in range(3):
    print(count)
    
    # input_text = cmd_gen.generate_command_start()
    # input_text = "tell me how many people in the living room are wearing black jackets"#1
    #まあまあ
    # input_text = "greet the person wearing a black jackets in the kitchen and answer a quiz"
    #人探索ができないうーん
    # input_text = "look for a person raising their right arm in the office and answer a question"
    #全くできないわけではないが人探索が
    # input_text = "go to the living room then find the person crossing one's arms and tell where RoboCup is held this year"
    #できた
    # input_text = "tell something about yourself to the person giving the v sign in the bathroom"
    #できた
    # input_text = "give me a cup from the table"

    '''
    input_text = input_com()
#

    

    output_text, verbs_found = replace_text(input_text)

    # 入力の出力（テスト用）
    print("in :",input_text)

    #print("out :",output_text)

    # `output_text_list` に `output_text` を追加
    output_text_list.append(output_text)

    for segment in output_text:
        mapped_command = match_segment_with_manual_mapping(segment)
        #(f"{segment.upper()} → {mapped_command}")


    result_objects = extract_in_order_with_duplicates(input_text, objects, special_words)
    result_rooms = extract_in_order_with_duplicates(input_text, rooms, special_words)
    result_names = extract_in_order_with_duplicates(input_text, names, special_words)
    result_placemen = extract_in_order_with_duplicates(input_text, placemen, special_words)
    result_person = extract_in_order_with_duplicates(input_text, person, special_words)
    result_talk = extract_in_order_with_duplicates(input_text, talk, special_words)
    result_person_info = extract_in_order_with_duplicates(input_text, person_info, special_words)

    result_object_comp = extract_in_order_with_duplicates(input_text, object_comp, special_words)
    result_color_list = extract_in_order_with_duplicates(input_text, color_list, special_words)
    result_clothe_list = extract_in_order_with_duplicates(input_text, clothe_list, special_words)

    # 最後の要素を3つに増やす処理
    if result_objects: 
        last_elementOJ = result_objects[-1]  
        result_objects.extend([last_elementOJ] * 2)

    if result_rooms: 
        last_element = result_rooms[-1]  
        result_rooms.extend([last_element] * 2)

    output_text, verbs_found = replace_text(input_text)
    seg_num = 0
    '''
    input_text = input_com()
    input_text = input_text.replace("?", "")


    result_objects = objects.copy()
    result_rooms = rooms.copy()
    result_names = names.copy()
    result_placemen = placemen.copy()
    result_person = person.copy()
    result_talk = talk.copy()
    result_person_info = person_info.copy()
    result_object_comp = object_comp.copy()
    result_color_list = color_list.copy()
    result_clothe_list = clothe_list.copy()

    # 🔵 まずここでストックを作る
    result_objects = extract_in_order_with_duplicates(input_text, objects, special_words)
    result_rooms = extract_in_order_with_duplicates(input_text, rooms, special_words)
    result_names = extract_in_order_with_duplicates(input_text, names, special_words)
    result_placemen = extract_in_order_with_duplicates(input_text, placemen, special_words)
    result_person = extract_in_order_with_duplicates(input_text, person, special_words)
    result_talk = extract_in_order_with_duplicates(input_text, talk, special_words)
    print("result_talk:", result_talk)

    result_person_info = extract_in_order_with_duplicates(input_text, person_info, special_words)
    result_object_comp = extract_in_order_with_duplicates(input_text, object_comp, special_words)
    result_color_list = extract_in_order_with_duplicates(input_text, color_list, special_words)
    result_clothe_list = extract_in_order_with_duplicates(input_text, clothe_list, special_words)

    # 最後の要素を3つに増やす処理
    if result_objects: 
        last_elementOJ = result_objects[-1]  
        result_objects.extend([last_elementOJ] * 2)

    if result_rooms: 
        last_element = result_rooms[-1]  
        result_rooms.extend([last_element] * 2)

    # 🔵 ストックを作ったあとで初めて replace_text を呼ぶ
    output_text, verbs_found = replace_text(input_text)
    seg_num = 0
    # 入力の出力（テスト用）
    print("in :", input_text)

    # `output_text_list` に `output_text` を追加
    output_text_list.append(output_text)
    for segment in output_text:
        mapped_command = match_segment_with_manual_mapping(segment)
        description = next((desc for cmd, desc in command_descriptions if cmd == mapped_command), "No description found")
        # print(f"{segment} → {description}")

        user_message = f''' Compare the given English sentence (input_text) with the incomplete Japanese sentence (description). Identify missing parts in description marked as _unk and extract the corresponding words or consecutive word pairs from input_text.
                            Requirements:
                            The number of extracted elements must exactly match the number of _unk in description.
                            Extracted words must appear exactly as they are in input_text, without modifications.
                            If an _unk corresponds to multiple consecutive words, treat them as a single entry.
                            Maintain the order of appearance from input_text.
                            Output only a Python list containing the extracted words—no additional text or explanations.

                            input_text = {input_text}  
                            description = {description}"
                            '''


        updated_description, obj, name, placemen, person, talk, person_info, obj_comp, color, clothe = replace_unk(description)

        found_rooms = find_matching_rooms(input_text, rooms)

        rooms_1, rooms_2, updated_rooms_lst = extract_rooms(description, found_rooms)

        counts = {var: description.count(var) for var in unk_variables}
        # for var, count in counts.items():
        #     print(f"{var}: {count}")
        for key, count in counts.items():
            if key in unk_to_re_lists:
                del unk_to_re_lists[key][:count]



        execute_command(mapped_command,obj, name, placemen, person, talk, person_info, obj_comp, color, clothe,rooms_1, rooms_2)

        obj_it = obj

    print("\n--- 完了 ---")
    
    seg_num += 1
    count = int(os.environ.get("RESTART_COUNT", "0"))
    if count < 100:
        os.environ["RESTART_COUNT"] = str(count + 1)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        print("これ以上は再実行しません。")

#navigate to the bedroom then find a phone stand and fetch it and bring it to the person crossing one's arms in the study room