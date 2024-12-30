from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def addbutton(userid,usertag,message_type):
    admin_panel = [
            [
                types.InlineKeyboardButton(text="✅Ընդունել",callback_data=f"Accept_{userid}_{message_type}"),
                types.InlineKeyboardButton(text="❌Չեղարկել",callback_data=f"Cancel_{userid}_{message_type}")
            ],
            [types.InlineKeyboardButton(text="📃Կապնվել անձնական նամակով", url=f"https://t.me/{usertag}")]
        ]


    return types.InlineKeyboardMarkup(inline_keyboard=admin_panel)

user =\
    [
        [KeyboardButton(text="💭 Հարց ուղղել"), KeyboardButton(text="✉️ Առաջարկ")],
    ]

user = ReplyKeyboardMarkup(keyboard=user)