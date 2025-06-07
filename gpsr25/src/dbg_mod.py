#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#ここに関数

from ex_mod import *
from gpsr_ai import obj_it
from config import *

operator = "operator"
  
def d1():
    look_person()
def d2():
    answer_question()
def d3():
    rooms_1 = "living"#リビング”ルーム”いらない
    navigate(rooms_1)
def d4():
    person = "giving the v sign"
    find_pose(person)
def d5():
    approach_person()
def d6():
    person = "sitting"
    count_pose(person)
def d7():
    navigate(operator)
def d8():
    saved_info = "He is fun."
    give_saved_info(saved_info)
def d9():
    obj = "cup"
    # pick_object(obj)
# def d10():
    # hand_object()
def d11():
    obj = "cup"
    find_object(obj)
def d12():
    name = "jack"
    find_name(name)
def d13():
    follow_person()
def d14():
    rooms_1 = "living"
    follow_person(rooms_1)
def d15():
    rooms_2 = "living"
    guide(rooms_2)
def d16():
    greet_selfintro()
def d17():
    color = "white" 
    clothe = "shirt"
    find_color_cloth(color, clothe)
def d18():
    obj_comp = "biggest"
    obj = "cup"
    find_feature(obj_comp, obj)
def d19():
    person_info = "name"
    find_info(person_info)
def d20():
    color = "black" 
    clothe = "shirt"
    count_color_cloth(color, clothe)
def d21():
    find_person()
def d22():
    talk = "something about yourself"
    give_info(talk)
def d23():
    obj = "cup"
    count_object(obj)
def d24():
    obj_comp = "biggest"
    obj = "cup"
    find_feature(obj_comp, obj)

def execute_command():

    print("ここからデバッグ用コード")

    operator = "operator"
    saved_info = "saved_info"

    if obj == "it":
        obj = obj_it

    d2()#質問を答える
    d3()#なゔぃ
    d5()#近づく
    d7()#オペレーターへ
    d8()#保存
    d13()#ついていく
    d15()#案内
    d16()#自己紹介
    d19()#名前聞く
    d22()#教える
    
execute_command()


        