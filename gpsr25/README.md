# GPSR25 RoboCup@Home OPL ソフトウェア全体仕様


## 目的（Purpose）

本リポジトリは、RoboCup@Home OPL（Open Platform League）GPSR（General Purpose Service Robot）競技向けに開発したロボットの自律動作プログラム群を管理・公開するものです。（ただ、チームとして非公開のものはお見せすることができません。それらは省いてあります。）


---

## 概要（Overview）

本システムは、GPSR競技でロボットが**自然言語の指示**を受けて自律的に認識・計画・行動することを目標に、  
音声認識、自然言語処理、物体・人物認識、ナビゲーション、アクションプランニングなど複数の機能モジュールで構成しています。  
主要部分は**ROS Noetic**、Python3をベースとし、ノード間連携によって高度なサービスロボット制御を実現します。

---

## 競技の内容（About the Competition）

**GPSR（General Purpose Service Robot）**は、  
審判からロボットに与えられる様々な自然言語コマンド（例：「テーブルの上からカップを持ってきて」や「Aさんを案内して」など）を理解し、  
自律的な移動・物体把持・人物認識・情報伝達などを複合的に行う能力を競う競技です。

---

# 各主要モジュールの説明

# GPSR25 主要モジュール早見表

| ファイル名                    | 主な役割・機能                      | 主な入出力・サービス／トピック                                                                              | 主なコマンド・関数                                          |
| :----------------------- | :--------------------------- | :------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| gpsr\_ai.py              | 自然言語コマンド解析・アクションプランニング       | 受信: 英語コマンド（str）<br>送信: ex\_mod呼び出し                                                           | execute\_command, replace\_text など                 |
| ex\_mod.py               | ロボットの実行動作（移動・認識・把持・対話）を担当    | 多数のROSサービス（tts, grasp, navigation等）                                                          | navi, pick\_object, find\_person など                |
| ask\_name\_new\.py       | 人物を名前で特定する対話ノード              | /get\_distance, /piper/tts, /whisper\_stt                                                    | ask\_name, run\_ask\_name\_with\_params            |
| ask\_person\_dis.py      | 前方人物までの距離計測・返却               | sub: /scan, srv: /get\_distance                                                              | （/get\_distanceサービス）                               |
| chaser.py                | 人物追従モジュール                    | sub: /follow\_me/distance\_angle\_data, pub: /chacer\_sign, /mimic1/tts/topic, srv: /yes\_no | start\_chase, stop\_chase, tts\_pub2               |
| chaser\_setup\_node.py   | 追従モジュールの起動・停止制御              | 関数呼び出し（chaser\_setup）                                                                        | chaser\_setup                                      |
| cmd\_gen.py              | 英語コマンド自動生成ジェネレータ             | なし（標準出力／リスト返却のみ）                                                                             | generate\_command\_start など                        |
| config.py                | コマンド解析・生成用の各種辞書・単語リスト        | importのみ（他ノードから参照）                                                                           | -                                                  |
| delay.py                 | launch用の人工ディレイ               | 起動時: durationパラメータ                                                                           | main                                               |
| find\_obj.py             | 指定物体の方向へカメラ首振り・注視            | pub: /servo/head, /target\_object, srv: /face\_object                                        | look\_at\_target\_object, initialize\_publishers   |
| obj\_count\_mod.py       | 物体認識結果から個数をカウント              | srv: /recognition/json                                                                       | obj\_count\_mod                                    |
| simple\_base\_control.py | 台車のシンプルな直進・回転・停止制御           | pub: /cmd\_vel, sub: /amcl\_pose                                                             | rotateAngle, translateDist                         |
| gpsr-mono8.py            | カメラ画像＋任意プロンプトでOpenAI応答取得     | sub: /camera/color/image\_raw, srv: /shelf\_object\_feature, OpenAI API                      | handle\_service, encode\_image など                  |
| gpsr-super7.py           | 人物特徴探索/人数カウント/角度リスト化/年齢服色推定等 | sub: /camera/color/image\_raw, pub: /servo/head, srv: /multi\_person\_scan, OpenAI API       | run\_scan, scan\_and\_analyze, estimate\_height など |

---
((gpsr_aiと、ex_modの2つを見れば全体像はつかめます。))

# gpsr_ai.py

[メインノードのソースコード（gpsr_ai.py）はこちら](src/gpsr_ai.py)

## 説明
英語の自然言語コマンドを受け取り、ロジックベースで行動計画（アクションプランニング）を立て、  
アクション名＋パラメータに分解して後続ノードに渡すノードです。  
ROS環境に依存せず、複数アクションや複雑な指示も一連の処理として扱えます。

## 処理の流れ
1. 英語コマンド文（例: "Bring me a cup from the table."）を入力
2. コマンド文から対象（物体・部屋・人など）を抽出
3. アクション名＋パラメータに変換
4. ex_mod.py等にアクション実行を委譲（例: navigate、pick_object、hand_objectなど）
5. 実行状況や結果を標準出力に表示

## Communication

| Communication | Name             | Type           | Request                                                        | Result                                  |
|:--------------|:-----------------|:---------------|:---------------------------------------------------------------|:----------------------------------------|
| Function      | execute_command  | Function       | string型: command_name<br>dict型: params                       | なし（後続ノードへ指示）                |
| Function      | replace_text     | Function       | string型: command_text                                         | list型: パターン化コマンド              |
| Function      | extract_in_order_with_duplicates | Function | string型: command_text<br>list型: words_list<br>string型: type | list型: 抽出語リスト                    |

## コマンド一覧

| コマンド名                      | 説明                                            | 主なパラメータ                    |
|:--------------------------------|:------------------------------------------------|:----------------------------------|
| bringMeObjFromPlcmt             | 家具の上の物体を持ってきて渡す                   | obj, placemen                     |
| deliverObjToPrsInRoom           | 部屋にいる人に物を持っていく                     | obj, rooms_1, person              |
| findObjInRoom                   | 部屋内で物体を探索                               | obj, rooms_1                      |
| followNameFromBeacToRoom        | 部屋から別の部屋へ特定の人についていく           | name, rooms_1, rooms_2            |
| countObjOnPlcmt                 | 家具の上の物体数を数える                         | obj, placemen                     |
| greetNameInRm                   | 部屋にいる名前指定の人に挨拶                     | name, rooms_1                     |
| guideNameFromBeacToBeac         | 名前指定の人を2地点間案内                        | name, rooms_1, rooms_2            |
| tellPrsInfoInLoc                | 部屋の人物情報を伝える                           | rooms_1, person_info              |
| takeObj                         | その場で物体を取る                               | obj                               |
| guidePrsToLoc                   | 人を指定の場所まで案内する                       | person, rooms_1                   |
| guideNameToLoc                  | 名前指定の人を指定場所まで案内                   | name, rooms_1                     |
| putObjOnPlcmt                   | 物体を指定家具や場所に置く                       | obj, placemen                     |
| findNameInRm                    | 部屋内で特定の人物（名前）を探索                 | name, rooms_1                     |
| countPrsInRm                    | 部屋内の人物数を数える                           | rooms_1                           |
| tellObjInfoOnPlcmt              | 家具の上の物体情報を伝える                       | obj, placemen, obj_comp           |
| countColorObjOnPlcmt            | 家具の上にある特定の色の物体を数える             | color, obj, placemen              |
| countColorPrsInRm               | 部屋にいる特定色の服の人物数を数える             | color, rooms_1                    |
| findObjByFeat                   | 特徴指定で物体を探索                             | obj_comp, obj                     |
| findNameByColorInRm             | 部屋内で色指定で人物を探索                       | color, rooms_1                    |
| greet                           | オペレーターに挨拶                               | なし                              |
| freeTalk                        | オペレーターと自由に会話                         | talk                              |
| giveInfo                        | 指定情報を伝える                                 | talk                              |
| askYesNo                        | Yes/Noで答える質問を投げる                       | talk                              |
| freeAsk                         | オペレーターに自由質問                           | talk                              |
| answerQuestion                  | 質問に答える                                     | talk                              |
| getConfig                       | 設定情報を取得                                   | config_name                       |
| naviFront                       | 正面へ自律移動                                   | なし                              |
| approachPerson                  | 指定人物に接近                                   | person                            |
| followPerson                    | 指定人物を追従                                   | person                            |
| handObject                      | 物体を手渡し                                     | なし                              |
| pickObject                      | 物体を把持                                       | obj                               |
| putObject                       | 物体を置く                                       | obj, placemen                     |
| navigate                        | 指定場所へ自律移動                               | rooms_1, placemen                 |
| findPerson                      | 人物探索                                         | person                            |
| findFeature                     | 特徴を持つ物体/人物を探索                        | obj_comp, obj, person_info        |
| countObject                     | 物体数を数える                                   | obj, rooms_1, placemen            |
| countPose                       | 指定姿勢の人数を数える                           | person, rooms_1                   |
| imageInfo                       | 画像から情報を取得                               | 画像ファイル名等                  |
| guestIntro                      | 来客紹介                                         | guest_name                        |
| enterRoom                       | 部屋への進入                                     | rooms_1                           |
| lookPerson                      | 人を見つめる                                     | person                            |
| findColorCloth                  | 色付きの服を着た人物を探索                       | color, clothe, rooms_1            |
| countColorCloth                 | 色付きの服の人数をカウント                       | color, clothe, rooms_1            |
| putObjectOnPlcmt                | 物体を指定場所に置く                             | obj, placemen                     |
| giveSavedInfo                   | 保存済み情報を伝達                               | info_key                          |


## 入力と出力例

**入力例**  
英語コマンド:  
`"Go to the bedroom, find a phone stand, fetch it, and bring it to the person crossing one's arms in the study room."`

---

**出力例**

### 1. コマンド分解  
- コマンド名リスト:  
    1. `navigateToLoc`  
    2. `findObjInRoom`  
    3. `pick_object`  
    4. `navigateToLoc`  
    5. `findPrsInRoom`  
    6. `hand_object`

- パラメータ:
    - `rooms_1 = "bedroom"`
    - `obj = "phone stand"`
    - `rooms_2 = "study room"`
    - `person = "crossing one's arms"`

---

### 2. 関数呼び出しシーケンス（詳細フロー）

1. `navigate("bedroom")`
2. `find_object("phone stand", "bedroom")`
3. `pick_object("phone stand")`
4. `navigate("study room")`
5. `find_pose("crossing one's arms", "study room")`
6. `hand_object()`

---

### 3. 標準出力例（実行時ログ）

```plaintext
[Action] 🚶‍♂️ Navigating to bedroom...
[Status] Arrived at: bedroom

[Action] 🔎 Searching for object: phone stand in bedroom...
[Status] Found object: phone stand

[Action] 🤖 Picking up object: phone stand...
[Status] Successfully picked up: phone stand

[Action] 🚶‍♂️ Navigating to study room...
[Status] Arrived at: study room

[Action] 👀 Searching for person: crossing one's arms in study room...
[Status] Person identified: crossing one's arms

[Action] 🤝 Handing object: phone stand to crossing one's arms
[Status] Task completed. All actions succeeded!

```
---
# ex_mod.py
- [ex_mod.pyソースコード](src/ex_mod.py)
## 説明  
gpsr_ai.pyから送られるアクション名＋パラメータをもとに、  
ロボットの実際の行動（移動・把持・探索・人物認識・対話など）を実行するノードです。  
各アクションは、ROSサービス・トピック・サブルーチンでハードウェア・各種センサ・音声入出力を統括します。

## 処理の流れ
1. gpsr_ai.pyなどからアクション名＋パラメータを受け取る
2. 対応する関数（例：navigate、pick_object、find_objectなど）を実行
3. 必要に応じてROSサービス/トピックを介してセンサ・アクチュエータ・TTS等を呼び出し
4. 実行結果を標準出力・音声などでフィードバック

## Communication

| Communication | Name                    | Type           | Request                                                         | Result                              |
|:--------------|:------------------------|:---------------|:----------------------------------------------------------------|:------------------------------------|
| Service       | /piper/tts              | piperTTS       | string型: text                                                  | 合成音声出力（TTS）                 |
| Service       | /execute_grasp          | GraspItemWithTarget | string型: target_object                                    | bool型: success                     |
| Service       | /multi_person_scan      | Str2Str        | string型: mode, prompt, angle                                   | string型: output（人数, 角度リスト等）|
| Service       | /servo/set_joint_angles | SetJointAngles | list型: shoulder, elbow, wrist                                  | なし                                |
| Service       | /servo/arm              | StrTrg         | string型: pose ("give"等)                                       | なし                                |
| Service       | /recognition/yolo_info  | SetStr         | string型: obj名                                                 | string型: 検出結果                  |
| Service       | /target_check           | StrInt         | string型: obj名                                                 | int型: 数                           |
| Service       | /shelf_object_feature   | Str2Str        | string型: prompt                                                | string型: 特徴説明                  |
| Service       | /whisper_stt            | SetStr         | string型: 音声認識プロンプト                                     | string型: 認識結果                  |
| Service       | /yes_no                 | YesNo          | なし（直前の質問に対するYes/No音声認識）                         | bool型: yes/no                      |
| Publisher     | /servo/head             | Float64        | float型: 角度                                                   | なし                                |
| Publisher     | /servo/endeffector      | Bool           | bool型: True/False（ハンド開閉）                                | なし                                |
| Publisher     | /clip_sign              | String         | string型: 特徴抽出コマンド                                      | なし                                |
| Publisher     | /chacer_sign            | String         | string型: "start"/"stop"（追従指示）                            | なし                                |

## コマンド一覧（関数名）

| コマンド名           | 概要                             | 主なパラメータ           |
|:---------------------|:---------------------------------|:-------------------------|
| grasp_launch         | grasping_itemsモジュール起動     | なし                     |
| kill_grasp_launch    | grasping_itemsモジュール停止     | なし                     |
| tts_pub2             | 非同期TTS出力                    | string型: text           |
| navi                 | 指定部屋へ移動                   | string型: navi_room      |
| find_person          | 人物探索                         | なし                     |
| find_pose            | 指定ポーズの人物探索             | string型: person, room   |
| count_pose           | 指定ポーズの人数カウント         | string型: person         |
| find_color_cloth     | 指定色の服を着た人物探索         | string型: color, clothe  |
| count_color_cloth    | 指定色の服人数カウント           | string型: color, clothe  |
| find_name            | 名前で人物特定                   | string型: name           |
| find_info            | 人物特徴情報取得                 | string型: person_info    |
| count_object         | 物体数カウント                   | string型: obj            |
| find_object          | 物体探索・把持                   | string型: obj, now_room  |
| find_feature         | 物体の特徴探索                   | string型: obj_comp, obj  |
| greet_selfintro      | 自己紹介・挨拶                   | なし                     |
| give_info            | 任意情報の発話                   | string型: talk           |
| answer_question      | 質問応答                         | なし                     |
| give_saved_info      | 保存済み情報の発話               | string型: saved_info     |
| navigate             | 指定部屋へ移動                   | string型: rooms          |
| approach_person      | 前方人物に接近                   | なし                     |
| follow_person        | 人物追従                         | string型: rooms（省略可）|
| guide                | 案内（指定部屋まで誘導）         | string型: rooms          |
| pick_object          | 物体を持つ                       | string型: obj            |
| hand_object          | 物体を手渡し                     | なし                     |
| put_object           | 物体を置く                       | string型: put_pl         |
| place_object         | アーム角度・ハンド開閉で物体設置 | list型: joint_angles     |

## 入力と出力例

**入力例1:**
- アクション: `navigate`
- パラメータ: `"dining room"`

**出力例1:**
- TTS: "Moving to dining room."
- 実際の移動動作、進行状況ログ（標準出力）

**入力例2:**
- アクション: `pick_object`
- パラメータ: `"cup"`

**出力例2:**
- TTS: "Picking up cup."
- grasping_itemsサービス呼び出し
- 成功時: "✅ 把持成功しました！"（標準出力）
- 失敗時: "❌ 把持失敗しました。"（標準出力）

**入力例3:**
- アクション: `find_person`
- パラメータ: なし

**出力例3:**
- TTS: "Searching for a person."
- 人物方向へ回転し探索、検出できれば追従など次アクションへ
- 標準出力に探索状況・結果

---

# ask_name_new.py
- [ask_name_new.pyソースコード](src/ask_name_new.py)
## 説明  
部屋内の複数人物の中から、順番に名前を尋ねて特定の人物（指定名）を同定するノードです。  
指定方向(angle_list)ごとに台車を回転させ、人がいる方向で「Are you ○○?」と音声で質問し、  
yes/noの返答で本人かどうか判定します。

## 処理の流れ
1. 角度リスト(angle_list)に従い順番に台車を回転
2. 距離サービス(get_distance)で人物までの距離を取得
3. その位置まで前進
4. 「Are you ○○?」と質問し、音声認識(whisper_stt)で返答取得
5. yesなら同定・終了、noなら後退して次の方向へ
6. 全方向調査して該当者がいなければ終了

## 【呼び出している Service / Publisher 一覧】

| 通信種別     | 名称             | 型       | 内容（用途）               |
|:-------------|:-----------------|:---------|:---------------------------|
| Service      | /get_distance    | Distance | 人物までの距離取得         |
| Service      | /piper/tts       | piperTTS | 音声合成で質問を出す       |
| Service      | /whisper_stt     | SetStr   | yes/noの音声認識           |
| Publisher    | /mimic1/tts/topic| String   | 音声出力（質問や案内）     |

## 【他ノードから呼び出せる Service / Publisher 一覧】

| 通信種別     | 名称                        | 型          | 内容（用途）                            |
|:-------------|:----------------------------|:------------|:----------------------------------------|
| Service      | /run_ask_name_with_params   | 独自         | 指定angle_list/want_nameで呼び出し可    |
| なし         | -                           | -           | 通常はクラス・関数のインスタンス経由    |

## コマンド一覧

| 関数名                 | 概要                                       | 主なパラメータ           |
|:----------------------|:--------------------------------------------|:------------------------|
| ask_name              | 指定人物名がいるか順番に聞いて判定する       | なし（インスタンス変数に依存） |
| run_ask_name_with_params | 外部からパラメータ指定で呼び出し           | angle_list, want_name   |

## 入力と出力例

**入力例**  
- angle_list: `[30, 50, 80, 90]`  
- want_name: `["Olivia"]`

**出力例**  
- 実際の質問発話: `"Are you Olivia? Please answer yes or no."`（順番に発話）
- ユーザーの「yes」音声認識で `"FIN"` を返す  
- 見つからなければ `"NOT_FOUND"` を返す  
- 標準出力で調査経過と最終結果を表示

---

# ask_person_dis.py
- [ask_person_dis.pyソースコード](src/ask_person_dis.py)
## 説明  
LaserScanデータ（/scan）から、前方人物までの直線距離を計算し、  
サービス（/get_distance）経由で外部ノードへ返すノード。

## 処理の流れ
1. /scanトピックからLaserScanデータを受信
2. 各点を(x, y)座標に変換し、xが-0.1～+0.1＆y>0の正面点だけ抽出
3. その中で最もy（前方距離）が小さい点＝最近点を記録
4. /get_distanceサービスリクエストが来たら、記録した距離を返す

## 【呼び出している Service / Publisher 一覧】

| 通信種別 | 名称    | 型           | 内容（用途）         |
|:---------|:--------|:-------------|:---------------------|
| Subscriber | /scan | LaserScan    | レーザースキャンの購読|

## 【呼び出される Service / Publisher 一覧】

| 通信種別 | 名称          | 型              | 内容（用途）                |
|:---------|:--------------|:----------------|:----------------------------|
| Service  | /get_distance | Distance        | 距離取得要求（result: float）|

## コマンド一覧  
このノードは明確なコマンド関数は持たず、内部でLaserScanデータを常時処理し、  
外部からのサービスリクエスト（/get_distance）に応じて結果を返します。

## 入力と出力例

**入力例**  
- /scanトピック（LaserScanメッセージ）がパブリッシュされる  
- サービスリクエスト: `/get_distance`（リクエスト型：空 or ダミー）

**出力例**  
- サービスレスポンス: `DistanceResponse(result=0.85)`（前方最近点までの距離m）  
- 標準出力:  Returning distance: 0.85 
取得できない場合は `DistanceResponse(result=inf)` を返す

---

# chaser.py
- [chaser.pyソースコード](src/chaser.py)
## 説明  
前方の人物を検出・追従し、ユーザーに到着確認（Yes/No音声認識）後に停止する「人物追従」ノードです。  
台車移動・TTS音声出力・サービス連携で自律的に人の後ろを付いていきます。

## 処理の流れ
1. `/follow_me/distance_angle_data`のPointメッセージで人物位置・距離を取得
2. "start"を合図に追従開始。随時距離を監視し人物についていく
3. 一定距離内＆一定時間経過後、TTS音声で到着確認
4. `/yes_no`サービスで「Is this the location?」へのユーザー返答を判定
5. Yesなら停止合図と微後退、chaser_setup_nodeで追従モジュールを停止

## 【呼び出している Service / Publisher 一覧】

| 通信種別     | 名称                        | 型              | 内容（用途）                       |
|:-------------|:----------------------------|:----------------|:-----------------------------------|
| Subscriber   | /follow_me/distance_angle_data | Point         | 人物までの距離・角度情報取得       |
| Publisher    | /chacer_sign                | String          | 追従開始・停止（"start"/"stop"）   |
| Publisher    | /mimic1/tts/topic           | String          | 音声ガイダンス・案内TTS出力        |
| Service      | /yes_no                     | YesNo           | Yes/No音声認識（到着確認）         |
| Service      | /servo/arm                  | StrTrg          | アーム制御（物体手渡し等）         |
| Service      | /piper/tts                  | piperTTS        | 合成音声出力（TTS）                |
| 関数呼び出し | chaser_setup_node.chaser_setup | Function      | 追従モジュールの起動・停止         |
| その他       | base_control.BaseControl     | Class           | 移動制御（translateDist等）        |

## 【呼び出される Service / Publisher 一覧】

| 通信種別     | 名称    | 型      | 内容（用途）    |
|:-------------|:--------|:--------|:---------------|
| なし         | -       | -       | -              |

（本ノード自体は外部からサービス等で直接呼び出されず、main内から直接起動）

## コマンド一覧

| 関数名           | 概要                         | 主なパラメータ   |
|:-----------------|:----------------------------|:----------------|
| start_chase      | 追従開始、人物追従ロジック   | なし            |
| stop_chase       | 追従停止、モジュール停止等   | なし            |
| tts_pub2         | 合成音声TTS出力（非同期）    | text            |

## 入力と出力例

**入力例**  
- /follow_me/distance_angle_data（Point型）が人物の移動に応じて随時発行される

**出力例**  
- `/chacer_sign`トピックに"start"や"stop"をパブリッシュ  
- `/mimic1/tts/topic`や`/piper/tts`に「I am now following you.」などの案内音声
- `/yes_no`サービスでYesを受けたら自動停止  
- 標準出力に「追従開始」「到着確認」など進捗ログ

---

# chaser_setup_node.py
- [chaser_setup_node.pyソースコード](src/chaser_setup_node.py)
## 説明  
人物追従モジュール（chacer24.launch）を動的に起動・停止するためのノード。  
外部から "start" で追従モジュールをlaunch、"stop" で安全に停止する。

## 処理の流れ
1. chaser.pyや他ノードから、"start" または "stop" シグナルを受ける
2. "start" の場合、roslaunchを用いて chacer24.launch を起動
3. "stop" の場合、launchオブジェクトをshutdownして終了
4. どちらでもない場合はエラーメッセージ

## 【呼び出している Service / Publisher 一覧】

| 通信種別   | 名称                   | 型                    | 内容（用途）                    |
|:-----------|:----------------------|:----------------------|:--------------------------------|
| Function   | roslaunch.rlutil      | function              | UUID生成等                      |
| Function   | roslaunch.parent.ROSLaunchParent | class        | launchファイルの起動・管理       |

## 【呼び出される Service / Publisher 一覧】

| 通信種別   | 名称         | 型          | 内容（用途）                 |
|:-----------|:-------------|:------------|:-----------------------------|
| Function   | chaser_setup | function    | "start"/"stop"で呼び出し可   |

## コマンド一覧

| 関数名       | 概要                              | 主なパラメータ         |
|:-------------|:----------------------------------|:----------------------|
| chaser_setup | 追従モジュールの起動・停止         | signal（"start"/"stop"）|

## 入力と出力例

**入力例**  
- `chaser_setup("start")`  
- `chaser_setup("stop")`

**出力例**  
- start: chacer24.launchファイルが起動される（人物追従モジュール稼働開始）
- stop: chacer24.launchが安全にシャットダウン、「Launch stopped」と表示
- その他: 「Error」「Launch not running」など標準出力にエラーメッセージ

---

# cmd_gen.py
- [cmd_gen.pyソースコード](src/cmd_gen.py)
## 説明  
GPSR競技向けの英語自然言語コマンドを自動生成するノード。  
組み合わせ辞書とテンプレート文から大量の自然なコマンド文を作り出し、デバッグやシミュレーション、コマンド網羅テストに利用します。

## 処理の流れ
1. 人名・部屋名・物体名等のリストや動詞辞書を初期化
2. コマンドテンプレート（all_cmdやperson_cmd_list, object_cmd_list）からランダムに選択
3. テンプレート内のプレースホルダーをランダムな値で埋めて自然言語文を生成
4. 生成コマンド文のリストを表示・返却

## 【呼び出している Service / Publisher 一覧】

| 通信種別 | 名称    | 型           | 内容（用途）         |
|:---------|:--------|:-------------|:---------------------|
| ―        | ―       | ―            | 外部通信なし         |

## 【呼び出される Service / Publisher 一覧】

| 通信種別 | 名称    | 型           | 内容（用途）         |
|:---------|:--------|:-------------|:---------------------|
| ―        | ―       | ―            | 外部通信なし         |

## コマンド一覧（生成できるコマンド種別）

| コマンド名                     | 概要（生成内容）                    |
|:-------------------------------|:-------------------------------------|
| goToLoc                        | 部屋や場所に移動                     |
| findPrsInRoom                  | 部屋内で人物探索                     |
| meetPrsAtBeac                  | 指定場所で人物と会う                 |
| countPrsInRoom                 | 部屋内の人物数を数える               |
| tellPrsInfoInLoc               | 部屋の人物情報を伝える               |
| talkInfoToGestPrsInRoom        | 部屋内の人物に話しかける             |
| answerToGestPrsInRoom          | 部屋内の人物の質問に答える           |
| followNameFromBeacToRoom       | 人物について別の部屋に行く           |
| guideNameFromBeacToBeac        | 名前指定の人物を案内                 |
| guidePrsFromBeacToBeac         | 特定条件の人物を案内                 |
| guideClothPrsFromBeacToBeac    | 特定の服装の人物を案内               |
| greetClothDscInRm              | 服装特徴指定の人物に挨拶             |
| greetNameInRm                  | 名前指定の人物に挨拶                 |
| meetNameAtLocThenFindInRm      | 指定場所で会ってから部屋内で探索     |
| countClothPrsInRoom            | 特定の服装人数をカウント             |
| tellPrsInfoAtLocToPrsAtLoc     | 場所ごとの人物情報を伝える           |
| followPrsAtLoc                 | 指定場所の人物を追従                 |
| takeObjFromPlcmt               | 家具の上から物体を取る               |
| findObjInRoom                  | 部屋内で物体探索                     |
| countObjOnPlcmt                | 家具の上の物体数を数える             |
| tellObjPropOnPlcmt             | 家具の上の特徴的な物体情報           |
| bringMeObjFromPlcmt            | 家具の上の物体を持ってくる           |
| tellCatPropOnPlcmt             | 家具の上の特定カテゴリ物体を伝える   |

## 入力と出力例

**入力例**  
- 直接実行時は引数なし（Pythonスクリプト実行）

**出力例**  
- コマンド文（例）:  
1.Go to the dining room then find a person raising 
2.their right arm and follow them.
3.Bring me a bottle from the shelf.
4.Guide Sophia from the desk to the living room.
- 全コマンド種が網羅されるまでリストで出力

---

# config.py
- [config.pyソースコード](src/config.py)
## 説明

GPSR競技で使う物体名・部屋名・人物名・場所名・動詞・コマンド名・特徴リストなど、
自然言語コマンドの解析・生成・アクションプランニング時に参照する**単語辞書・カテゴリ辞書**を一元管理するPythonモジュールです。

## 処理の流れ

1. 物体名・部屋名・人物名・特徴語等をリスト/辞書として定義
2. 他のノードやスクリプトからimportされ、コマンド生成や解析などで各種単語・変数の照合、置換、説明生成、パターン認識などに利用される

## 【呼び出している Service / Publisher 一覧】

| 通信種別 | 名称 | 型  | 内容（用途） |
| :--- | :- | :- | :----- |
| ―    | ―  | ―  | 外部通信なし |

## 【呼び出される Service / Publisher 一覧】

| 通信種別 | 名称 | 型  | 内容（用途） |
| :--- | :- | :- | :----- |
| ―    | ―  | ―  | 外部通信なし |

## データ構成（主な変数・リスト例）

| 変数名                   | 内容例・用途                              |
| :-------------------- | :---------------------------------- |
| objects               | 物体名リスト（cup, cookie, potato chip など） |
| rooms                 | 部屋・家具名リスト（dining room, shelf など）    |
| names                 | 人名リスト（jack, sophia, tom など）         |
| placemen              | 物の設置場所リスト（counter, shelf, table など） |
| person                | 人の状態・ポーズ（raising their right arm等）  |
| talk                  | 雑談や質問・課題文リスト                        |
| person\_info          | 人物の追加情報（name, shirt color など）       |
| object\_comp          | 物体特徴語（biggest, largest, heaviest等）  |
| color\_list           | 色名リスト                               |
| clothe\_list          | 衣服名リスト（shirt, coat等・複数形も）           |
| verbs                 | 動詞カテゴリごとの置き換え辞書                     |
| final\_replacements   | 動詞カテゴリの最終コマンド名変換マップ                 |
| manual\_mapping       | 英語コマンド→内部コマンド名への手動マッピング             |
| command\_descriptions | コマンド名ごとの日本語説明リスト                    |

## 入力と出力例

**入力例**
他ノードから

```python
from config import objects, rooms, names, verbs
```

**出力例**
例えば `objects` を参照

```python
print(objects)
# => ['phon stand', 'cup', 'cups', 'cookie', ...]
```

`verbs["takeVerb"]`

```python
# => ["take", "get", "grasp", "fetch"]
```

`command_descriptions`

```python
# => [("bringMeObjFromPlcmt", "{placemen_1}にある{objects_1}をオペレーターにもっていく"), ...]
```

---

# delay.py
- [delay.pyソースコード](src/delay.py)
## 説明

launchファイル実行時に、機体側ノードの同時起動によるエラーや競合を防ぐため、指定秒数だけ人工的にディレイ（遅延）を発生させるROSノードです。

## 処理の流れ

1. ノード起動時に`~duration`パラメータで待機時間（秒）を取得（デフォルト1.0秒）
2. 指定時間`sleep`する
3. 待機完了後、自動でノードをshutdownして終了

## 【呼び出している Service / Publisher 一覧】

| 通信種別 | 名称 | 型  | 内容（用途） |
| :--- | :- | :- | :----- |
| ―    | ―  | ―  | 外部通信なし |

## 【呼び出される Service / Publisher 一覧】

| 通信種別 | 名称 | 型  | 内容（用途） |
| :--- | :- | :- | :----- |
| ―    | ―  | ―  | 外部通信なし |

## コマンド一覧

| 関数名  | 概要            | 主なパラメータ             |
| :--- | :------------ | :------------------ |
| main | 遅延開始〜shutdown | duration（float, 秒数） |

## 入力と出力例

**入力例**

* launchファイル等で `rosrun delay.py _duration:=2.5` などの形で起動

**出力例**

* 標準出力（roslog）：

  ```
  [INFO] [xxx]: Delay node sleeping for 2.5 seconds...
  [INFO] [xxx]: Delay node done. Shutting down.
  ```
* 指定秒数経過後にノード自動終了

---

# find\_obj.py
- [find_obj.pyソースコード](src/find_obj.py)
## 説明

YOLOやOpenCVを利用して、カメラ画像から指定された物体を検出し、その方向へロボットの頭部（カメラ）を回転させて注視させるノードです。
物体の把持は行わず、“見つめる・方向を向く”ことに特化しています。

## 処理の流れ

1. initialize\_publishers()でパブリッシャを初期化（外部から呼び出し）
2. look\_at\_target\_object(object\_name)で注視対象を受信
3. /target\_objectトピックに物体名をパブリッシュ
4. /servo/headトピックに角度（-20度）をパブリッシュし頭を向ける
5. /face\_objectサービスを呼び出して、実際に物体方向を注視（Trigger型）
6. 成否をGraspItemWithTargetResponse型で返す

## 【呼び出している Service / Publisher 一覧】

| 通信種別      | 名称              | 型       | 内容（用途）         |
| :-------- | :-------------- | :------ | :------------- |
| Publisher | /servo/head     | Float64 | カメラ頭部の角度指示     |
| Publisher | /target\_object | String  | 注視対象物体名のパブリッシュ |
| Service   | /face\_object   | Trigger | 注視動作のトリガー呼び出し  |

## 【呼び出される Service / Publisher 一覧】

| 通信種別     | 名称                       | 型        | 内容（用途）                 |
| :------- | :----------------------- | :------- | :--------------------- |
| Function | initialize\_publishers   | function | パブリッシャ初期化（他ノードから呼び出し）  |
| Function | look\_at\_target\_object | function | 物体名指定で注視動作（他ノードから呼び出し） |

## コマンド一覧

| 関数名                      | 概要         | 主なパラメータ           |
| :----------------------- | :--------- | :---------------- |
| initialize\_publishers   | パブリッシャ初期化  | なし                |
| look\_at\_target\_object | 物体名指定で注視動作 | object\_name（str） |

## 入力と出力例

**入力例**

* initialize\_publishers()を実行
* look\_at\_target\_object("bottle")

**出力例**

* /target\_objectに"bottle"をpublish
* /servo/headに-20.0をpublish（頭部を下げる）
* /face\_objectサービス呼び出しで注視動作
* 結果：GraspItemWithTargetResponse(success=True, message="把持なしで注視動作に成功しました")

---

# obj\_count\_mod.py
- [obj_count_mod.pyソースコード](src/obj_count_mod.py)
## 説明

物体認識結果（JSON形式）から、指定したオブジェクトの個数を返すためのユーティリティノード／関数です。
YOLOや画像認識で検出された物体一覧から、欲しい名前のもの（例: "person"や"cup"）の個数をプログラムから簡単に取得できます。

## 処理の流れ

1. ROSノードを初期化
2. /recognition/jsonサービス（StrTrg型）を呼び出し、物体検出結果（JSON文字列）を取得
3. 結果を辞書に変換し、target\_nameの数を返す
4. 指定名が無ければ0、サービスエラー時は-1を返す

## 【呼び出している Service / Publisher 一覧】

| 通信種別    | 名称                | 型      | 内容（用途）        |
| :------ | :---------------- | :----- | :------------ |
| Service | /recognition/json | StrTrg | 物体認識結果JSONの取得 |

## 【呼び出される Service / Publisher 一覧】

| 通信種別     | 名称              | 型        | 内容（用途）          |
| :------- | :-------------- | :------- | :-------------- |
| Function | obj\_count\_mod | function | 他ノード・他関数から呼び出し可 |

## コマンド一覧

| 関数名             | 概要            | 主なパラメータ           |
| :-------------- | :------------ | :---------------- |
| obj\_count\_mod | 指定オブジェクトの個数取得 | target\_name（str） |

## 入力と出力例

**入力例**

* obj\_count\_mod("person")

**出力例**

* /recognition/jsonサービスを呼び出し
* （検出結果例：{"cup": 2, "person": 3, ...}）
* 戻り値: 3  # "person"の個数
* サービスエラー時は -1

---

# simple\_base\_control.py
- [simple_base_control.pyソースコード](src/simple_base_control.py)
## 説明

台車の基本的な前進・後退・回転のみを行う、シンプルなベースコントロール用ノード／クラスです。
AMCL等を使った自己位置推定から現在位置を購読しつつ、/cmd\_velにTwist型で速度指令を出すのみの構成です。
（PID制御や高度な軌道生成は未使用。初期開発や一時運用用）

## 処理の流れ

1. クラスSimpleBaseControlをインスタンス化
2. rotateAngle(angle\_deg, angular\_speed)でその場旋回
3. translateDist(distance, linear\_speed)で直進・後退
4. 終了時は自動で停止信号を複数回送信

## 【呼び出している Service / Publisher 一覧】

| 通信種別       | 名称          | 型                         | 内容（用途）         |
| :--------- | :---------- | :------------------------ | :------------- |
| Publisher  | /cmd\_vel   | Twist                     | 台車の速度指令（直進・回転） |
| Subscriber | /amcl\_pose | PoseWithCovarianceStamped | 現在位置購読         |

## 【呼び出される Service / Publisher 一覧】

| 通信種別           | 名称                | 型              | 内容（用途）            |
| :------------- | :---------------- | :------------- | :---------------- |
| Class/Function | SimpleBaseControl | class/function | 他ノードやスクリプトから呼び出し可 |

## コマンド一覧

| 関数名           | 概要          | 主なパラメータ                    |
| :------------ | :---------- | :------------------------- |
| rotateAngle   | 指定角度だけ回転    | angle\_deg, angular\_speed |
| translateDist | 指定距離だけ直進/後退 | distance, linear\_speed    |

## 入力と出力例

**入力例**

* rotateAngle(90)
* translateDist(1.0)

**出力例**

* /cmd\_velに指定値のTwistメッセージをpublish（回転/直進）
* /amcl\_poseを購読してself.current\_poseを更新
* 動作終了時に複数回停止信号（Twist()）をpublish

---

# gpsr-mono8.py
- [gpsr-mono8.pyソースコード](mod/gpsr-mono8.py)
## 説明

カメラ画像（/camera/color/image\_raw）を直接OpenAI API（gpt-4-turbo）に送り、ユーザー指定のプロンプトに対して画像全体を元に応答を得るサービスノードです。
バウンディングボックス等で切り出さず“画面全体”を解析に使うのが特徴です。

## 処理の流れ

1. 画像トピック（/camera/color/image\_raw）を購読し、常に最新画像を保持
2. /shelf\_object\_featureサービス呼び出し時に画像を保存＆base64エンコード
3. 入力された任意プロンプト＋画像全体をOpenAI API（gpt-4-turbo）に送信
4. 返答テキストをサービスレスポンスで返却

## 【呼び出している Service / Publisher 一覧】

| 通信種別       | 名称                       | 型                | 内容（用途）          |
| :--------- | :----------------------- | :--------------- | :-------------- |
| Subscriber | /camera/color/image\_raw | Image            | カメラ画像の購読        |
| Service    | /shelf\_object\_feature  | Str2Str          | サービス呼び出しでAI応答取得 |
| 外部API      | OpenAI API               | chat.completions | 画像と質問で応答取得      |

## 【呼び出される Service / Publisher 一覧】

| 通信種別    | 名称                      | 型       | 内容（用途）          |
| :------ | :---------------------- | :------ | :-------------- |
| Service | /shelf\_object\_feature | Str2Str | 任意プロンプト＋画像全体で応答 |

## コマンド一覧

| 関数名                      | 概要              | 主なパラメータ         |
| :----------------------- | :-------------- | :-------------- |
| handle\_service          | サービス受付〜AI応答返却   | req（input: str） |
| prepare\_save\_directory | 画像保存ディレクトリ作成    | なし              |
| encode\_image            | 画像ファイルをbase64変換 | path（str）       |
| image\_callback          | 画像トピック購読        | msg（Image型）     |
| run                      | ノードスピン          | なし              |

## 入力と出力例

**入力例**

* rosservice call /shelf\_object\_feature "input: 'What is the most heaviest object?'"

**出力例**

* 最新カメラ画像全体＋プロンプトをOpenAIに送信
* 返答: "The heaviest object is the laptop." など
* 画像が未受信やAPIエラー時はエラーメッセージ返却

---

# gpsr-mono8.py
- [gpsr-super7.pyソースコード](mod/gpsr-super7.py)
## 説明

カメラ画像（/camera/color/image\_raw）を直接OpenAI API（gpt-4-turbo）に送り、ユーザー指定のプロンプトに対して画像全体を元に応答を得るサービスノードです。
バウンディングボックス等で切り出さず“画面全体”を解析に使うのが特徴です。

## 処理の流れ

1. 画像トピック（/camera/color/image\_raw）を購読し、常に最新画像を保持
2. /shelf\_object\_featureサービス呼び出し時に画像を保存＆base64エンコード
3. 入力された任意プロンプト＋画像全体をOpenAI API（gpt-4-turbo）に送信
4. 返答テキストをサービスレスポンスで返却

## 【呼び出している Service / Publisher 一覧】

| 通信種別       | 名称                       | 型                | 内容（用途）          |
| :--------- | :----------------------- | :--------------- | :-------------- |
| Subscriber | /camera/color/image\_raw | Image            | カメラ画像の購読        |
| Service    | /shelf\_object\_feature  | Str2Str          | サービス呼び出しでAI応答取得 |
| 外部API      | OpenAI API               | chat.completions | 画像と質問で応答取得      |

## 【呼び出される Service / Publisher 一覧】

| 通信種別    | 名称                      | 型       | 内容（用途）          |
| :------ | :---------------------- | :------ | :-------------- |
| Service | /shelf\_object\_feature | Str2Str | 任意プロンプト＋画像全体で応答 |

## コマンド一覧

| 関数名                      | 概要              | 主なパラメータ         |
| :----------------------- | :-------------- | :-------------- |
| handle\_service          | サービス受付〜AI応答返却   | req（input: str） |
| prepare\_save\_directory | 画像保存ディレクトリ作成    | なし              |
| encode\_image            | 画像ファイルをbase64変換 | path（str）       |
| image\_callback          | 画像トピック購読        | msg（Image型）     |
| run                      | ノードスピン          | なし              |

## 入力と出力例

**入力例**

* rosservice call /shelf\_object\_feature "input: 'What is the most heaviest object?'"

**出力例**

* 最新カメラ画像全体＋プロンプトをOpenAIに送信
* 返答: "The heaviest object is the laptop." など
* 画像が未受信やAPIエラー時はエラーメッセージ返却
