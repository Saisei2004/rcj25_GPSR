import rospy
import json
from happymimi_msgs.srv import StrTrg

# 指定したオブジェクトの数を返す関数
def obj_count_mod(target_name):
    # ROSノードの初期化（1度だけ行うように注意）
    rospy.init_node('obj_counter', anonymous=True)

    # サービスクライアントの準備
    rospy.wait_for_service("/recognition/json")  # サービスが立ち上がるまで待機
    subscriber = rospy.ServiceProxy("/recognition/json", StrTrg)
    
    try:
        # サービスを呼び出して結果を取得
        response = subscriber()
        result_dict = json.loads(response.result)  # JSON文字列を辞書に変換

        # 対象の名前が辞書にあるか確認して数を返す
        return result_dict.get(target_name, 0)
    
    except rospy.ServiceException as e:
        rospy.logerr("サービス呼び出し失敗: %s" % e)
        return -1  # エラー時は -1 を返す

# テスト実行（例として "person" の数を取得）
if __name__ == '__main__':
    count = obj_count_mod("person")
    print(f'"person" の数は: {count}')
