def navigate(rooms):#🟡
    print(f"{rooms}に移動")
    # tts_pub(f"Moving to {rooms}.")
    if rooms == "bedroom":
        rooms = "bedroom"

    elif rooms == "kitchen":
        rooms = "kitchen"

    elif rooms == "dining room":
        rooms = "dining_room"

    elif rooms == "study room":
        rooms = "study_room"

    elif rooms == "shelf":#家具
        rooms = "st_shelf"

    elif rooms == "":
        rooms = "cml_start"
    elif rooms == "":
        rooms = "trash"
    elif rooms == "counter":#家具
        rooms = "counter_a"
    elif rooms == "":
        rooms = "counter_b"
    elif rooms == "":
        rooms = "li_shelf_a"
    elif rooms == "":
        rooms = "li_shelf_b"
    elif rooms == "low table":#家具
        rooms = "low_table"
    elif rooms == "dining table":#家具
        rooms = "dining_table"
    elif rooms == "":
        rooms = "operator"
    elif rooms == "":
        rooms = "exit"
    elif rooms == "":
        rooms = "entrance_a"
    elif rooms == "":
        rooms = "entrance_b"

    return rooms

print(type(navigate("dining table")))