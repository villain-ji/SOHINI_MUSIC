from pyrogram.types import InlineKeyboardButton

import config
from config import SUPPORT_GROUP
from ChampuMusic import app


def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_9"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_3"], url=f"{SUPPORT_GROUP}"),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text=_["S_B_3"], url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text=_["S_B_4"], url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_1"], callback_data="settings_back_helper"
            )
        ],
    ]
    return buttons


def alive_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_9"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_3"], url=f"{SUPPORT_GROUP}"),
        ],
    ]
    return buttons

def music_start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="𝐓ᴀᴘ ʜᴇʀᴇ ᴛᴏ sᴇᴇ ᴍᴀɢɪᴄ 💗",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="˹𝐀ʙᴏᴜᴛ 🌛", callback_data="about"),
            InlineKeyboardButton(text="˹𝐂ʜᴀᴛ 🎄", callback_data="support"),
        ],
        [
            InlineKeyboardButton(text="𝐒ᴜʙsᴄʀɪʙᴇ ᴛᴏ sᴏʜɪɴɪ 💗", url=f"https://t.me/Want_To_Know_Me"),
        ]
        [InlineKeyboardButton(text="𝐀ʙɪʟɪᴛɪᴇs 👀", callback_data="feature")],
    ]
    return buttons
