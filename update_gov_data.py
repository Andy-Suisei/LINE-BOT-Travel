import urllib.request

urllib.request.urlretrieve("https://gis.taiwan.net.tw/XMLReleaseALL_public/scenic_spot_C_f.json",
                           "travelScheduling/scenic_spot_C_f.json")
urllib.request.urlretrieve("https://gis.taiwan.net.tw/XMLReleaseALL_public/restaurant_C_f.json",
                           "travelScheduling/restaurant_C_f.json")
urllib.request.urlretrieve("https://gis.taiwan.net.tw/XMLReleaseALL_public/hotel_C_f.json",
                           "travelScheduling/hotel_C_f.json")
urllib.request.urlretrieve("https://gis.taiwan.net.tw/XMLReleaseALL_public/activity_C_f.json",
                           "travelScheduling/activity_C_f.json")
