#ここに変数tell me what is the biggest potato chip on the shelf

from utils import *

objects = [
    # # "noodle", "noodles", "potato_chip", "potato_chips", "cookie", "cookies", "cracker", "crackers", 
    # # "coffee", "coffees", "bag", "bags", "dice", "light_bulb", "light_bulbs", "block", "blocks", 
    # # "table_clock", "table_clocks", "freezer_bag", "freezer_bags", "lunch_box", "lunch_boxes", 
    # # "cup", "cups", "detergent", "detergents", "it", "person", "people", "persons", "peoples","objects","object","bottle","bottles",
    # "dice", "light bulb", "glue gun", "block", "detergent", "cup", "lunch box", "bowl", "bottle", "noodles", "cookies", "potato chips", "gummy",
    "phon stand","cup","cups",
    "cookie", "noodle", "potato chip", "caramel corn", "detergent", "sponge", "lunch box", "dice", "glue gun", "light bulb", "phone stand",
    "cookies", "noodles", "potato chips", "caramel corn", "detergents", "sponges", "lunch boxes", "dice", "glue guns", "light bulbs", "phone stands"
    ,"objects","object","food items","kitchen items","task items",

]
objects_not_it = [
    # "dice", "light bulb", "glue gun", "block", "detergent", "cup", "lunch box", "bowl", "bottle", "noodles", "cookies", "potato chips", "gummy"
    "cookie", "noodle", "potato chip", "caramel corn", "detergent", "sponge", "lunch box", "dice", "glue gun", "light bulb", "phone stand",
    "cookies", "noodles", "potato chips", "caramel corn", "detergents", "sponges", "lunch boxes", "dice", "glue guns", "light bulbs", "phone stands",
    "food items","kitchen items","task items",
]
#meet jack at the right tray then lacate them in the study room

objects_OBJ = [
    # "noodle", "noodles", "potato_chip", "potato_chips", "cookie", "cookies", "cracker", "crackers", 
    # "coffee", "coffees", "bag", "bags", "dice", "light_bulb", "light_bulbs", "block", "blocks", 
    # "table_clock", "table_clocks", "freezer_bag", "freezer_bags", "lunch_box", "lunch_boxes", "bottle","bottles",
    # "cup", "cups", "detergent", "detergents", "it","objects","object",
    "cookie", "noodle", "potato chip", "caramel corn", "detergent", "sponge", "lunch box", "dice", "glue gun", "light bulb", "phone stand",
    "cookies", "noodles", "potato chips", "caramel corn", "detergents", "sponges", "lunch boxes", "dice", "glue guns", "light bulbs", "phone stands",
    "objects","object", "food items","kitchen items","task items",
]

rooms = ["dining room", "living room", "bedroom", "study room",
         "counter", "left tray", "right tray", "pen holder", "container", "left Kachaka shelf", "right Kachaka shelf", "low table", "tall table", "trash bin", "left chair", "right chair", "left Kachaka station", "right Kachaka station", "shelf", "bed", "dining table", "couch", "entrance", "exit"] #roomついてるかついてないか
# names = [
#     "jack", "aaron", "angel", "adam", "vanessa", "chris", "william", "max", "hunter", "olivia", #"them",
#     "yoshimura", "angel", "wataru",  # re@dy tamkachallenger
#     "basil", "moo deng", "cheesecake",  # skuba
#     "andrew", "sophia", "leo",  # sobits
#     "jack", "mike", "william",  # kit happy robot
#     "lisa", "leo", "tom"  # er@sers
#     ,"chikako"
# ]
names = ["yoshimura", "angel", "basil", "chikako", "andrew", "sophia", "jack", "mike", "leo", "tom"]

placemen = ["counter","low table","tall table","shelf","dining table",]#"bedroom"]
person = ["raising their right arm", "sitting", "standing", "squatting", "looking back", 
           "crossing one's arms", "pointing to the left", "giving the v sign","people","them"]
person_list = ["raising their right arm", "sitting", "standing", "squatting", "looking back", 
           "crossing one's arms", "pointing to the left", "giving the v sign","people","them"]
# talk = ["something about yourself", "what day today is", "what day tomorrow is",
#         "where RoboCup is held this year", "what the result of 3 plus 5 is", "your team's name",
#         "where you come from", "what the weather is like today", "what the time is"]
talk = [
    "go to the living room, count how many people are there, and report it to me",
    "go to the dining table, check what objects are on it, and tell me what you found",
    "go to the person in the kitchen, ask them what their favorite food is, and come back to tell me",
    "go to the person in the living room and tell them what color your body is",
    "move to the person in the living room and tell them your name",
    "what do thai people usually ride when catching insects",
    "will you marry me",
    "can i trust you",
    "why do robots move in a jerky way",
    "did you see my screwdriver",
    "what color is the japanese flag",
    "which room has no walls, no doors, and no windows",
    "how many legs does a chair usually have",
    "what is the largest planet in our solar system",
    "what do bees make",
    "what is the current world population",
    "what is the most spoken language in the world?",
    "what is the most spoken language in the world",
    "what is the correct spelling of robot",
    "what is the brightest star in the solar system",
    "what is the probability of getting a total of 7 when rolling two dice",
    "would you like something to drink",
    "do you have a favorite color, if i may ask",
    "is there a time you need to be heading home today",
    "are there any foods you prefer to avoid",
    "is the room temperature comfortable for you",
    "something about yourself", "what day today is", "what day tomorrow is",
        "where RoboCup is held this year", "what the result of 3 plus 5 is", "your team's name",
        "where you come from", "what the weather is like today", "what the time is"
]

person_info = ["name", "shirt color", "age", "height"]
object_comp = ["biggest", "largest", "smallest", "heaviest", "lightest", "thinnest"]
color_list = ["blue", "yellow", "black", "white", "red", "orange", "gray"]
clothe_list = ["t shirt", "shirt", "blouse", "sweater", "coat", "jacket","t shirts", "shirts", "blouses", "sweaters", "coats", "jackets"]


# 動詞の置き換え辞書
verbs = {
    "takeVerb": ["take", "get", "grasp", "fetch"],
    "placeVerb": ["put", "place"],
    "deliverVerb": ["bring", "give", "deliver"],
    "bringVerb": ["bring", "give"],
    "goVerb": ["go", "navigate"],
    "findVerb": ["find", "locate", "look for"],
    "talkVerb": ["tell", "say"],
    "answerVerb": ["answer"],
    "meetVerb": ["meet"],
    "tellVerb": ["tell"],
    "greetVerb": ["greet", "salute", "say hello to", "introduce yourself to"],
    "rememberVerb": ["meet", "contact", "get to know", "get acquainted with"],
    "countVerb": ["tell me how many"],
    "describeVerb": ["tell me how", "describe"],
    "offerVerb": ["offer"],
    "followVerb": ["follow"],
    "guideVerb": ["guide", "escort", "take", "lead"],
    "accompanyVerb": ["accompany"]
}

# カテゴリごとの最終変換マップ（大文字変換）
final_replacements = {
    "takeVerb": "TAKE",
    "placeVerb": "PLACE",
    "deliverVerb": "DELIVER",
    "goVerb": "GO",
    "findVerb": "FIND",
    "talkVerb": "TALK",
    "answerVerb": "ANSWER",
    "meetVerb": "MEET",
    "tellVerb": "TELL",
    "greetVerb": "GREET",
    "rememberVerb": "REMEMBER",
    "countVerb": "COUNT",
    "describeVerb": "DESCRIBE",
    "offerVerb": "OFFER",
    "followVerb": "FOLLOW",
    "guideVerb": "GUIDE",
    "accompanyVerb": "ACCOMPANY"
}

manual_mapping = {
    "ANSWERQUESTION": "answerQuestion",
    "ANSWERQUESTIONPRSINROOM": "answerToGestPrsInRoom",
    "COUNTINROOM": "countPrsInRoom",
    "COUNTINROOMCLOTHPRS": "countClothPrsInRoom",
    "COUNTOBJONPLCMT": "countObjOnPlcmt",
    "DELIVERMEFROMPLCMT": "bringMeObjFromPlcmt",
    "DELIVERMEOBJFROMPLCMT": "bringMeObjFromPlcmt",
    "DELIVEROBJTOME": "deliverObjToMe",
    "DELIVEROBJTOPRSINROOM": "deliverObjToPrsInRoom",
    "FIND": "findObj",
    "FINDINROOM": "findObjInRoom",
    "FINDOBJ": "findObj",
    "FINDOBJINROOM": "findObjInRoom",
    "FINDPRS": "findPrs",
    "FINDPRSINROOM": "findPrsInRoom",
    "FOLLOWPRS": "followPrs",
    "FOLLOWPRSATROOM": "followPrsAtLoc",
    "FOLLOWPRSFROMROOMTOROOM": "followNameFromBeacToRoom",
    "FOLLOWPRSINROOM": "followPrsAtLoc",
    "FOLLOWPRSTOROOM": "followPrsToRoom",
    "GOTOROOM": "goToLoc",
    "GREETCLOTHPRSINROOM": "greetClothDscInRm",
    "GREETPRSINROOM": "greetNameInRm",
    "GUIDECLOTHPRSFROMROOMTOROOM": "guideClothPrsFromBeacToBeac",
    "GUIDEPRSFROMROOMTOROOM": "guideNameFromBeacToBeac",
    "GUIDEPRSTOROOM": "guidePrsToBeacon",
    "MEETPRS": "meetName",
    "MEETPRSATROOM": "meetNameAtLoc",
    "MEETPRSINROOM": "meetPrsAtBea",
    "PLACEOBJONPLCMT": "placeObjOnPlcmt",
    "TAKECLOTHPRSFROMROOMTOROOM": "guideClothPrsFromBeacToBeac",
    "TAKEFROMPLCMT": "takeObjFromPlcmt",
    "TAKEOBJ": "takeObj",
    "TAKEOBJFROMPLCMT": "takeObjFromPlcmt",
    "TAKEPRSFROMROOMTOROOM": "guidePrsFromBeacToBeac",
    "TAKEPRSTOROOM": "guidePrsToBeacon",
    "TALKINFO": "talkInfo",
    "TALKINFOTOPRSINROOM": "talkInfoToGestPrsInRoom",
    "TALKMEPROPOBJONPLCMT": "tellCatPropOnPlcmt",
    "TALKMEPROPONPLCMT": "tellObjPropOnPlcmt",
    "TALKMEPRSINFOATROOM": "tellPrsInfoInLoc",
    "TALKMEPRSINFOINROOM": "tellPrsInfoInLoc",
    "TALKPRSINFOATROOMTOATROOM": "tellPrsInfoAtLocToPrsAtLoc",
    "TALKTOCLOTHPRSINROOM": "greetClothDscInRm",
    "TALKTOPRSINROOM": "greetNameInRm",
    "TAKEPRSFROMROOMTOROOM": "guideNameFromBeacToBeac",
    "TALK INFO TO PRS IN ROOM": "talkInfoToGestPrsInRoom",
}

names_1 = "nema_unk"            # 名前に関する情報
person_1 = "person_unk"           # 人に関する情報
person_info_1 = "person_info_unk"       # 人の追加情報
rooms_1 = "rooms_unk"            # 部屋の名前1
rooms_2 = "rooms_unk"            # 部屋の名前2
objects_1 = "objects_unk"          # オブジェクト（物）の名前
placemen_1 = "placemen_unk"         # 物が置かれる場所
color_list_1 = "color_list_unk"       # 色に関する情報
clothe_list_1 = "clothe_list_unk"      # 衣服に関する情報
talk_1 = "talk_unk"             # 会話や話題
object_comp_1 = "object_comp_unk"      # オブジェクトの特徴

unk_variables = [
    "nema_unk", 
    "person_unk", 
    "person_info_unk", 
    "rooms_unk", 
    "objects_unk", 
    "placemen_unk", 
    "color_list_unk", 
    "clothe_list_unk", 
    "talk_unk", 
    "object_comp_unk"
]

command_descriptions = [#消すな
    ("answerQuestion", f"目の前の人の質問に答える"),
    ("answerToGestPrsInRoom", f"{rooms_1}にいる{person_1}の人の質問に答える"),
    ("countPrsInRoom", f"{rooms_1}にいる{person_1}を数えてオペレーターに伝える"),
    ("countClothPrsInRoom", f"{rooms_1}にいる{color_list_1}色の{clothe_list_1}を着ている人の数をオペレーターに伝える"),
    ("countObjOnPlcmt", f"{placemen_1}の上にある{objects_1}の数をオペレーターに伝える"),
    ("bringMeObjFromPlcmt", f"{placemen_1}にある{objects_1}をオペレーターにもっていく"),
    ("deliverObjToMe", f"{objects_1}をオペレーターに持っていく"),
    ("deliverObjToPrsInRoom", f"{rooms_1}にいる{person_1}にそれを持っていく"),
    ("findObj", f"{objects_1}を見つける"),
    ("findObjInRoom", f"{rooms_1}で{objects_1}を見つける"),
    ("findPrs", f"{person_1}をその場で探す"),
    ("findPrsInRoom", f"{person_1}を{rooms_1}で探す"),
    ("followPrs", f"{names_1}についていく"),
    ("followPrsAtLoc", f"{rooms_1}の{person_1}についていく"),
    ("followNameFromBeacToRoom", f"{names_1}を{rooms_1}から{rooms_2}についていく"),
    ("followPrsToRoom", f"{rooms_1}まで{person_1}についていく"),
    ("goToLoc", f"{rooms_1}に行く"),
    ("greetClothDscInRm", f"{rooms_1}にいる{color_list_1}色の{clothe_list_1}を着ている人にhelloと言う"),
    ("greetNameInRm", f"{rooms_1}にいる{names_1}にhelloを言う"),
    ("guideClothPrsFromBeacToBeac", f"{color_list_1}色の{clothe_list_1}を着ている人を{rooms_1}から{rooms_2}についていく"),
    ("guideNameFromBeacToBeac", f"{names_1}を{rooms_1}から{rooms_2}に案内する"),
    ("guidePrsToBeacon", f"{names_1}を{rooms_1}に案内する"),
    ("meetName", f"その場で{names_1}に会う"),
    ("meetNameAtLoc", f"{rooms_1}で{names_1}に会う"),
    ("meetPrsAtBea", f"{rooms_1}で{names_1}に会う"),
    ("placeObjOnPlcmt", f"{objects_1}を{placemen_1}の上に置く"),
    ("takeObjFromPlcmt", f"{objects_1}を{placemen_1}からとる"),
    ("takeObj", f"{objects_1}をとる"),
    ("talkInfo", f"{talk_1}を伝える"),
    ("tellCatPropOnPlcmt", f"オペレーターに{placemen_1}の上の{object_comp_1}の{objects_1}がどれか伝える"),
    ("tellObjPropOnPlcmt", f"オペレーターに{placemen_1}の上の{object_comp_1}の{objects_1}がどれか伝える"),
    ("tellPrsInfoInLoc", f"オペレーターに{rooms_1}にいる人の{person_info_1}を伝える"),
    ("tellPrsInfoAtLocToPrsAtLoc", f"{rooms_1}にいる人の{person_info_1}を{rooms_2}にいる人に伝える"),
    ("guidePrsFromBeacToBeac" , f"{person_1}を{rooms_1}から{rooms_2}に案内する"),
    ("talkInfoToGestPrsInRoom" , f"{rooms_1}にいる{person_1}、{talk_1}を伝える")
    
]


#視覚に基づく認識
# look_person = "目の前の人を見る"
# find_person = "人を探す"
# find_pose = "あるポーズの人を見つける"
# count_pose = "あるポーズの人を数える"
# find_color_cloth = "ある色のある服を着ている人を探す"
# count_object = "ある物の数を数える"
# find_object = "あるものを探す"
# find_feature = "ある特徴のものを探して特定する"
# identify_person = "あるひとの身体的特徴を特定する"

# #対話・コミュニケーション
# answer_question = "質問に答える"
# ask_name = "名前を聞く"
# greet_selfintro = "挨拶と自己紹介をする"
# give_info = "指定された情報を伝える"

# #行動・移動
# # navigate = "ナビゲーション"
# approach_person = "指定された人に近づく"
# follow_person = "目の前の人についていく"

# #操作・物体の取り扱い
# pick_object = "指定されたものを持つ"
# hand_object = "持っているものを渡す"


result_objects = []
result_rooms = []
result_names = []
result_placemen = []
result_person = []
result_talk = []
result_person_info = []
result_object_comp = []
result_color_list = []
result_clothe_list = []

