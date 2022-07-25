import json
import random
import math
from datetime import date


def distance(locate1, locate2):
    return math.sqrt(math.pow(locate1["Px"] - locate2["Px"], 2) + math.pow(locate1["Py"] - locate2["Py"], 2)) * 100


def checkAround(main_locate, sub_locate1, sub_locate2, dist):
    major_axis = math.sqrt(math.pow(dist, 2) + math.pow(distance(sub_locate1, sub_locate2), 2))
    if (distance(main_locate, sub_locate1) < dist or distance(main_locate, sub_locate2) < dist or (
            distance(main_locate, sub_locate1) + distance(main_locate, sub_locate2) < major_axis)):
        return True
    else:
        return False


def choosebetween(chooselist, sub_locate1, sub_locate2):
    chedlist = []
    distan = 0.1
    looptimes = 0
    while len(chedlist) == 0 and looptimes < 10:
        for i in range(len(chooselist)):
            if (checkAround(chooselist[i], sub_locate1, sub_locate2, distan)):
                chedlist.append(i)
        distan += 5
        looptimes += 1
    if (looptimes == 10 and len(chedlist) == 0):
        return "null"
    return chooselist.pop(chedlist[random.randrange(0, len(chedlist))])


def chooserandom(traverlist, pointer, times, activity, restaurant, scenic):
    for i in range(random.randrange(1, times + 1)):
        flag = True
        while flag:
            nowtype = random.randrange(0, 4)
            if nowtype == 0:
                insertlocate = choosebetween(activity, traverlist[pointer - 1], traverlist[pointer])
            elif nowtype == 2 or nowtype == 1:
                insertlocate = choosebetween(scenic, traverlist[pointer - 1], traverlist[pointer])
            elif nowtype == 3:
                insertlocate = choosebetween(restaurant, traverlist[pointer - 1], traverlist[pointer])
            if insertlocate != "null":
                flag = False
        traverlist.insert(pointer, insertlocate)
        pointer += 1
    return pointer


def chooserday(traverlist, activity, restaurant, scenic, hotel):
    start_hotel = traverlist[-1]
    end_hotel = hotel[random.randrange(0, len(hotel))]
    
    chedrestaurant = []
    for i in range(2):
        chedrestaurant.append(choosebetween(restaurant, start_hotel, end_hotel))
    
    if (distance(start_hotel, chedrestaurant[0]) > distance(start_hotel, chedrestaurant[1])):
        temp = chedrestaurant[0]
        chedrestaurant[0] = chedrestaurant[1]
        chedrestaurant[1] = temp
    
    traverlist.append(chedrestaurant[0])
    traverlist.append(chedrestaurant[1])
    traverlist.append(end_hotel)
    
    pointer = len(traverlist) - 3
    pointer = chooserandom(traverlist, pointer, 2, activity, restaurant, scenic)
    pointer += 1
    pointer = chooserandom(traverlist, pointer, 4, activity, restaurant, scenic)
    pointer += 1
    pointer = chooserandom(traverlist, pointer, 3, activity, restaurant, scenic)


def chooser(region, day):
    with open("travelScheduling/activity_C_f.json", encoding="utf-8-sig") as f:
        j = json.load(f)
        activity = j["XML_Head"]["Infos"]["Info"]
    with open("travelScheduling/hotel_C_f.json", encoding="utf-8-sig") as f:
        j = json.load(f)
        hotel = j["XML_Head"]["Infos"]["Info"]
    with open("travelScheduling/restaurant_C_f.json", encoding="utf-8-sig") as f:
        j = json.load(f)
        restaurant = j["XML_Head"]["Infos"]["Info"]
    with open("travelScheduling/scenic_spot_C_f.json", encoding="utf-8-sig") as f:
        j = json.load(f)
        scenic = j["XML_Head"]["Infos"]["Info"]
    
    region_activity = []
    region_hotel = []
    region_restaurant = []
    region_scenic = []
    
    for i in hotel:
        if i["Region"] == region:
            region_hotel.append(i)
    
    today = date.today()
    for i in activity:
        if i["Region"] == region and (date.fromisoformat(i["End"][0:10]) > today):
            # "End": "2022-08-31T00:00:00+08:00"
            region_activity.append(i)
    
    for i in scenic:
        if i["Region"] == region:
            region_scenic.append(i)
    
    for i in restaurant:
        if i["Region"] == region:
            region_restaurant.append(i)
    
    random.seed()
    start_hotel = region_hotel[random.randrange(0, len(region_hotel))]
    traverlist = [[start_hotel]]
    
    for i in range(day):
        chooserday(traverlist[i], region_activity, region_restaurant, region_scenic, region_hotel)
        traverlist.append([traverlist[i][-1]])
    traverlist.pop()
    traverlist[0].pop(0)
    traverlist[-1].pop()
    
    return traverlist
