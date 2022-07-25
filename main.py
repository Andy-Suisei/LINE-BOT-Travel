import ast
import re

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, PostbackEvent, FollowEvent
)

from line_flexmessage import *
from locatechooser import *
from sql_util import *

app = Flask(__name__)

line_bot_api = LineBotApi(
    'RKGHBK/EWiNcZA7l9NiWHjsuR84dCGIgb8mRwecl/OdFmxXnABc0+lvYBEMdc/BL4JbM0tY2Yvym1S8SZfHXjWGhY5sgrLpD+X9tJt6mwzdYE96zk4Sbf3uOi8RFqZ0LbQ5aKGoPA/HIM+lW04pgQgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b6c536ac8f1f17c4886bcf9060e8252f')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    
    # get request body as text
    
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_event(event):
    uid = event.source.user_id
    if event.message.text == '@設定旅遊資料':
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='區域選擇表',
                contents=region_select_all
            )
        )
    elif event.message.text == '@開始排程':
    
        day = sql_get_user_select_day(uid)
        region = sql_get_user_select_region(uid)
        try:
            traver_list = chooser(region, day)
        except ValueError:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='很抱歉 你尚未設定相關資料喔 改快先設定資料吧')
            )
            return
    
        hotel = []
        food = []
        play = []
        activity = []
        name_list = []
        
        for day_go in traver_list:
            h_t, f_t, p_t, n_t, a_t = [], [], [], [], []
            for attraction in day_go:
                if "'" in attraction['Name']:
                    attraction['Name'].replace("'", "”")
                if attraction['Id'][1] != '2':
                    n_t.append(attraction['Name'])
                if attraction['Id'][1] == '1':
    
                    p_t.append(attraction['Name'])
                elif attraction['Id'][1] == '2':
                    a_t.append(attraction['Name'])
                elif attraction['Id'][1] == '3':
                    f_t.append(attraction['Name'])
                elif attraction['Id'][1] == '4':
                    h_t.append(attraction['Name'])
            hotel.append(h_t)
            food.append(f_t)
            play.append(p_t)
            activity.append(a_t)
            name_list.append(n_t)
    
        sql_schedule_list = list_to_list_str(name_list)
        sql_hotel_list = list_to_list_str(hotel)
        sql_food_list = list_to_list_str(food)
        sql_play_list = list_to_list_str(play)
        sql_activity_list = list_to_list_str(activity)
        sql_set_user_schedule_classification(uid, sql_schedule_list, sql_hotel_list, sql_food_list,
                                             sql_play_list, sql_activity_list)
    
        schedule_flex = {
            "type": "carousel",
            "contents": [
            ]
        }
    
        for day in range(day):
            template = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"第{num_to_tw[day + 1]}天行程",
                            "weight": "bold",
                            "size": "xxl"
                        },
                        {
                            "type": "text",
                            "text": "住宿",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "吃東西",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "景點&活動",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "點我查看Google路線圖",
                                "data": f"google_map_{day}"
                            }
                        }
                    ]
                }
            }
            for h in hotel[day]:
                template['body']['contents'][2]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{h}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for f in food[day]:
                template['body']['contents'][4]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{f}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for p in play[day]:
                template['body']['contents'][6]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{p}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for a in activity[day]:
                template['body']['contents'][6]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{a}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            schedule_flex['contents'].append(template)
    
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='行程結果',
                contents=schedule_flex
            )
        )
    elif event.message.text == '@查詢上次排程結果':
        schedule, hotel, food, play, activity = sql_get_user_schedule_classification(uid)

        if schedule == '':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='很抱歉 你尚未有歷史排程喔 改快先去排程吧')
            )
            return

        hotel = ast.literal_eval(hotel)
        food = ast.literal_eval(food)
        play = ast.literal_eval(play)
        activity = ast.literal_eval(activity)
        
        schedule_flex = {
            "type": "carousel",
            "contents": [
            ]
        }
        
        for day in range(len(food)):
            template = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"第{num_to_tw[day + 1]}天行程",
                            "weight": "bold",
                            "size": "xxl"
                        },
                        {
                            "type": "text",
                            "text": "住宿",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "吃東西",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "景點&活動",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "點我查看Google路線圖",
                                "data": f"google_map_{day}"
                            }
                        }
                    ]
                }
            }
            for h in hotel[day]:
                template['body']['contents'][2]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{h}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for f in food[day]:
                template['body']['contents'][4]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{f}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for p in play[day]:
                template['body']['contents'][6]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{p}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for a in activity[day]:
                template['body']['contents'][6]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{a}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            schedule_flex['contents'].append(template)

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='行程結果',
                contents=schedule_flex
            )
        )

    elif event.message.text == '@修改刪除行程':
        schedule, hotel, food, play, activity = sql_get_user_schedule_classification(uid)

        if schedule == '':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='很抱歉 你尚未有歷史排程喔 改快先去排程吧')
            )
            return

        hotel = ast.literal_eval(hotel)
        food = ast.literal_eval(food)
        play = ast.literal_eval(play)
        activity = ast.literal_eval(activity)
        schedule_flex = {
            "type": "carousel",
            "contents": [
            ]
        }

        for day in range(len(food)):
            template = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"第{num_to_tw[day + 1]}天行程",
                            "weight": "bold",
                            "size": "xxl"
                        },
                        {
                            "type": "text",
                            "text": "#點選想要刪除的行程",
                            "margin": "sm",
                            "size": "md",
                            "color": "#7B7B7B"
                        },
                        {
                            "type": "text",
                            "text": "住宿",
                            "size": "xl",
                            "align": "center",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "吃東西",
                            "size": "xl",
                            "align": "center",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "景點&活動",
                            "size": "xl",
                            "align": "center",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        }
                    ]
                }
            }
            for i, h in enumerate(hotel[day]):
                template['body']['contents'][3]['contents'].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": f"{h}",
                            "data": f"delete_h_{day}_{i}"
                        }
                    }
                )
            for i, f in enumerate(food[day]):
                template['body']['contents'][5]['contents'].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": f"{f}",
                            "data": f"delete_f_{day}_{i}"
                        }
                    }
                )
            for i, p in enumerate(play[day]):
                template['body']['contents'][7]['contents'].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": f"{p}",
                            "data": f"delete_p_{day}_{i}"
                        }
                    }
                )
            for i, a in enumerate(activity[day]):
                template['body']['contents'][7]['contents'].append(
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": f"{a}",
                            "data": f"delete_a_{day}_{i}"
                        }
                    }
                )
            schedule_flex['contents'].append(template)

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='行程結果',
                contents=schedule_flex
            )
        )


@handler.add(PostbackEvent)
def postback_event(event):
    uid = event.source.user_id
    # 收到選擇區域
    if re.compile(r'area_*').match(event.postback.data):
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text=f'{event.postback.data[-2:]}縣市表',
                contents=region_select[event.postback.data[-2:]]
            )
        )
    
    # 收到選擇縣市
    elif re.compile(r'select_*').match(event.postback.data):
        sql_set_user_select_region(uid, event.postback.data[-3:])
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='日期選擇表',
                contents=play_day_select
            )
        )
    
    # 收到選擇遊玩天數
    elif re.compile(r'\d天').match(event.postback.data):
        sql_set_user_select_day(uid, int(event.postback.data[0]))
        day = sql_get_user_select_day(uid)
        region = sql_get_user_select_region(uid)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f'設定完成！目前設定遊玩縣市:{region}'
                     f'天數：{day}')
        )
    
    elif re.compile(r'google_map_\d').match(event.postback.data):
        schedule = sql_get_user_schedule_classification(uid)[0]
        day = int(event.postback.data[11])
        schedule = ast.literal_eval(schedule)

        def to_url(s: list):
            result = []
            for i in s:
                result.append(i)
                result.append('%7C')
            result = ''.join(result)
            return result.replace(' ', '')

        g_map = f"https://www.google.com/maps/dir/?api=1&origin={schedule[day][0].replace(' ', '')}" \
                f"&waypoints={to_url(schedule[day][1:-1])}" \
                f"&destination={schedule[day][-1].replace(' ', '')}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'Google路線圖：{g_map}')
        )
    
    elif re.compile(r'delete_*').match(event.postback.data):
        # delete_{f}_{day}_{index}
        category = event.postback.data[7]
        days = int(event.postback.data[9])
        index = int(event.postback.data[11])
        schedule, hotel, food, play, activity = sql_get_user_schedule_classification(uid)

        schedule = ast.literal_eval(schedule)
        hotel = ast.literal_eval(hotel)
        food = ast.literal_eval(food)
        play = ast.literal_eval(play)
        activity = ast.literal_eval(activity)
        delete = ''
        if category == 'h':
            delete = hotel[days].pop(index)
            sql_hotel = list_to_list_str(hotel)
            sql_set_hotel(uid, sql_hotel)
        elif category == 'f':
            delete = food[days].pop(index)
            sql_food = list_to_list_str(food)
            sql_set_food(uid, sql_food)
        elif category == 'p':
            delete = play[days].pop(index)
            sql_play = list_to_list_str(play)
            sql_set_play(uid, sql_play)
        elif category == 'a':
            delete = activity[days].pop(index)
            sql_activity = list_to_list_str(activity)
            sql_set_activity(uid, sql_activity)

        print(delete)
        print(schedule)
        if delete in schedule[days]:
            schedule[days].remove(delete)
            sql_schedule = list_to_list_str(schedule)
            sql_set_schedule(uid, sql_schedule)

        schedule_flex = {
            "type": "carousel",
            "contents": [
            ]
        }

        for day in range(len(food)):
            template = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"第{num_to_tw[day + 1]}天行程",
                            "weight": "bold",
                            "size": "xxl"
                        },
                        {
                            "type": "text",
                            "text": "住宿",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "吃東西",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        },
                        {
                            "type": "text",
                            "text": "景點&活動",
                            "size": "xl",
                            "color": "#FF0000",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "點我查看Google路線圖",
                                "data": f"google_map_{day}"
                            }
                        }
                    ]
                }
            }
            for h in hotel[day]:
                template['body']['contents'][2]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{h}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for f in food[day]:
                template['body']['contents'][4]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{f}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for p in play[day]:
                template['body']['contents'][6]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{p}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            for a in activity[day]:
                template['body']['contents'][6]['contents'].append(
                    {
                        "type": "text",
                        "text": f"{a}",
                        "size": "md",
                        "margin": "xs",
                        "align": "start",
                        "wrap": True
                    }
                )
            if day == days:
                template['body']['contents'].insert(1, {
                    "type": "text",
                    "text": f"#已刪除{delete}",
                    "margin": "sm",
                    "size": "md",
                    "color": "#7B7B7B"
                })

            schedule_flex['contents'].append(template)

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text='行程結果',
                contents=schedule_flex
            )
        )


@handler.add(FollowEvent)
def follow_event(event):
    uid = event.source.user_id
    sql_init_user(uid)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='歡迎加入好友！')
    )


if __name__ == "__main__":
    app.run()
