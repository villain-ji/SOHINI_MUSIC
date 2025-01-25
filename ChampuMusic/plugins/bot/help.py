import re
from math import ceil
from typing import Union

from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_command, get_string
from ChampuMusic import HELPABLE, app
from ChampuMusic.utils.database import get_lang, is_commanddelete_on
from ChampuMusic.utils.decorators.language import LanguageStart
from ChampuMusic.utils.inline.help import private_help_panel

### Command
HELP_COMMAND = get_command("HELP_COMMAND")

COLUMN_SIZE = 4
NUM_COLUMNS = 3



class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n, module_dict, prefix, chat=None, close: bool = False):
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data="{}_module({},{})".format(
                        prefix, x.__MODULE__.lower(), page_n
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data="{}_module({},{},{})".format(
                        prefix, chat, x.__MODULE__.lower(), page_n
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "❮",
                    callback_data="{}_prev({})".format(
                        prefix,
                        modulo_page - 1 if modulo_page > 0 else max_num_pages - 1,
                    ),
                ),
                EqInlineKeyboardButton(
                    "ᴄʟᴏsᴇ" if close else "Bᴀᴄᴋ",
                    callback_data="close" if close else "feature",
                ),
                EqInlineKeyboardButton(
                    "❯",
                    callback_data="{}_next({})".format(prefix, modulo_page + 1),
                ),
            )
        ]
    else:
        pairs.append(
            [
                EqInlineKeyboardButton(
                    "ᴄʟᴏsᴇ" if close else "Bᴀᴄᴋ",
                    callback_data="close" if close else "feature",
                ),
            ]
        )

    return pairs


@app.on_message(filters.command(HELP_COMMAND) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass

        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

        await update.edit_message_text(_["help_1"], reply_markup=keyboard)
    else:
        chat_id = update.chat.id
        if await is_commanddelete_on(update.chat.id):
            try:
                await update.delete()
            except:
                pass
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = InlineKeyboardMarkup(
            paginate_modules(0, HELPABLE, "help", close=True)
        )
        try:
            if update.chat.photo:
                userss_photo = await app.download_media(
                    update.chat.photo.big_file_id,
                )
            else:
                userss_photo = "assets/nodp.jpg"

            chat_photo = userss_photo if userss_photo else START_IMG_URL
        except AttributeError:
            chat_photo = "assets/nodp.jpg"

        await update.reply_photo(
            photo=chat_photo,
            caption=_["help_1"].format(config.SUPPORT_GROUP),
            reply_markup=keyboard,
        )


@app.on_message(filters.command(HELP_COMMAND) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    try:
        if message.chat.photo:
            group_photo = await app.download_media(
                message.chat.photo.big_file_id,
            )
        else:
            group_photo = "assets/nodp.png"

        chat_photo = group_photo if group_photo else "assets/nodp.png"
    except AttributeError:
        chat_photo = "assets/nodp.png"

    keyboard = private_help_panel(_)
    await message.reply_photo(
        photo=chat_photo,
        caption=_["help_2"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return keyboard


@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client, query):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back\((\d+)\)", query.data)
    create_match = re.match(r"help_create", query.data)
    language = await get_lang(query.message.chat.id)
    _ = get_string(language)
    top_text = _["help_1"]

    if mod_match:
        module = mod_match.group(1)
        prev_page_num = int(mod_match.group(2))
        text = (
            f"<b><u>𝐇ᴇʀᴇ ɪs ᴛʜᴇ ʜᴇʟᴘ ғᴏʀ {HELPABLE[module].__MODULE__}:</u></b>\n"
            + HELPABLE[module].__HELP__
        )

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="↪ 𝐁ᴀᴄᴋ", callback_data=f"help_back({prev_page_num})"
                    ),
                    InlineKeyboardButton(text="🔄 𝐂ʟᴏsᴇ", callback_data="close"),
                ],
            ]
        )

        await query.message.edit(
            text=text,
            reply_markup=key,
            disable_web_page_preview=True,
        )

    elif home_match:
        await app.send_message(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=InlineKeyboardMarkup(out),
        )
        await query.message.delete()

    elif prev_match:
        curr_page = int(prev_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        prev_page_num = int(back_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(prev_page_num, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif create_match:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

        await query.message.edit(
            text=top_text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    await client.answer_callback_query(query.id)


# ===================================

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import BANNED_USERS
from strings import helpers
from ChampuMusic import app
from ChampuMusic.utils.decorators.language import languageCB


@app.on_callback_query(filters.regex("music_callback") & ~BANNED_USERS)
@languageCB
async def music_helper_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_music(_)

    if cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.HELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.HELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.HELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.HELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.HELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.HELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.HELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.HELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.HELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.HELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.HELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.HELP_12, reply_markup=keyboard)

    elif cb == "hb13":

        await CallbackQuery.edit_message_text(helpers.HELP_13, reply_markup=keyboard)

    elif cb == "hb14":

        await CallbackQuery.edit_message_text(helpers.HELP_14, reply_markup=keyboard)

    elif cb == "hb15":

        await CallbackQuery.edit_message_text(helpers.HELP_15, reply_markup=keyboard)


@app.on_callback_query(filters.regex("management_callback") & ~BANNED_USERS)
@languageCB
async def management_callback_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_management(_)

    if cb == "extra":

        await CallbackQuery.edit_message_text(helpers.EXTRA_1, reply_markup=keyboard)

    elif cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.MHELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.MHELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.MHELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.MHELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.MHELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.MHELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.MHELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.MHELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.MHELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.MHELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.MHELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.MHELP_12, reply_markup=keyboard)


@app.on_callback_query(filters.regex("tools_callback") & ~BANNED_USERS)
@languageCB
async def tools_callback_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_tools(_)

    if cb == "ai":

        await CallbackQuery.edit_message_text(helpers.AI_1, reply_markup=keyboard)

    elif cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.THELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.THELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.THELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.THELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.THELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.THELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.THELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.THELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.THELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.THELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.THELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.THELP_12, reply_markup=keyboard)


@app.on_callback_query(filters.regex("developer"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="𝐒ʜᴜʙʜᴏ 💗", user_id=config.OWNER_ID[0]),
            InlineKeyboardButton(
                text="𝐒ᴜᴅᴏᴇʀs 👀", url=f"https://t.me/{app.username}?start=sudo"
            ),
        ],
        [
            InlineKeyboardButton(text="𝐂ʜᴀᴛ 🕊️", url=f"https://t.me/+3LYCl_fgUBgzZTQ9"),
            InlineKeyboardButton(text="𝐌ᴏᴠɪᴇs 🍿", url=f"https://t.me/+9-FI_YhCiAhmNmVl"),
        ],
        [
            InlineKeyboardButton(text="•𝐁ᴀᴄᴋ•", callback_data="about")
        ],  # Use a default label for the back button
    ]
    await callback_query.message.edit_text(
        "✦ **𝐓ʜɪs ʙᴏᴛ ɪs ᴍᴀᴅᴇ ʙʏ ᴀ sᴋɪʟʟᴇᴅ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀsʏ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀɴᴅ ᴍᴏʀᴇ ғᴜɴ.**\n\n✦ **ᴡɪᴛʜ ᴊᴜsᴛ ᴀ ғᴇᴡ ᴄʟɪᴄᴋs, ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛʀᴏʟ ᴇᴠᴇʀʏᴛʜɪɴɢ—ʟɪᴋᴇ sᴇᴛᴛɪɴɢ ᴜᴘ ᴏᴡɴᴇʀ sᴇᴛᴛɪɴɢs, ᴄʜᴇᴄᴋɪɴɢ sᴜᴅᴏᴇʀs, ᴀɴᴅ ᴇᴠᴇɴ ᴇxᴘʟᴏʀɪɴɢ ɪɴsᴛᴀɢʀᴀᴍ ᴀɴᴅ ʏᴏᴜᴛᴜʙᴇ.**\n\n✦ **ᴛʜᴇ ʙᴏᴛ ɪs ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ sᴍᴏᴏᴛʜʟʏ ᴀɴᴅ ᴇɴᴊᴏʏ ᴍᴜsɪᴄ ᴛᴏᴏ. ᴊᴜsᴛ ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴀɴᴅ sᴇᴇ ʜᴏᴡ ᴇᴀsʏ ɪᴛ ɪs!**",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex("feature"))
async def feature_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(
                text="𝐓ᴀᴘ ʜᴇʀᴇ ᴛᴏ sᴇᴇ ᴍᴀɢɪᴄ 💗",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="˹𝐌ᴜsɪᴄ˼ 🎧", callback_data="music"),
            InlineKeyboardButton(text="˹𝐌ᴧɴᴧɢᴍᴇɴᴛ˼ 🎄", callback_data="management"),
        ],
        [
            InlineKeyboardButton(text="˹ᴛᴏᴏʟs ♥️˼", callback_data="tools"),
            InlineKeyboardButton(text="˹ᴧʟʟ˼ 💥", callback_data="settings_back_helper"),
        ],
        [InlineKeyboardButton(text="𝐇ᴏᴍᴇ 👀", callback_data="go_to_start")],
    ]
    k = f"""**✨ ᴍᴇᴇᴛ {app.mention} !\n\n•❅──────✧❅✦❅✧──────❅\n🎶 ɪ’ᴍ ᴀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ | ᴍᴜsɪᴄ ʙᴏᴛ\n\n🚀 ɴᴏ ʟᴀɢ, ɴᴏ ᴀᴅs, ɴᴏ ᴘʀᴏᴍᴏᴛɪᴏɴs\n🎧 𝟸𝟺/𝟽 ᴜᴘᴛɪᴍᴇ ᴡɪᴛʜ ᴛʜᴇ ʙᴇsᴛ sᴏᴜɴᴅ ǫᴜᴀʟɪᴛʏ\n💡 ᴛᴀᴘ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs!\n\n❅──────✧❅✦❅✧──────❅\n❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ <a href=https://t.me/Chini_tomarre>𓆩 𝐒 𝐇 𝐔 𝐁 𝐇 𝐎 𓆪</a></b></blockquote>**"""
    await callback_query.message.edit_text(
        text=k, reply_markup=InlineKeyboardMarkup(keyboard)
    )


@app.on_callback_query(filters.regex("music"))
async def music_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="•𝐀ᴅᴍɪɴ•", callback_data="music_callback hb1"),
                InlineKeyboardButton(text="•𝐀ᴜᴛʜ•", callback_data="music_callback hb2"),
                InlineKeyboardButton(
                    text="•𝐁ʀᴏᴀᴅᴄᴀsᴛ•", callback_data="music_callback hb3"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="•𝐁𝐋_𝐂ʜᴀᴛ•", callback_data="music_callback hb4"
                ),
                InlineKeyboardButton(
                    text="•𝐁𝐋_𝐔sᴇʀ•", callback_data="music_callback hb5"
                ),
                InlineKeyboardButton(text="C-Pʟᴀʏ", callback_data="music_callback hb6"),
            ],
            [
                InlineKeyboardButton(text="•𝐆_𝐁ᴀɴ•", callback_data="music_callback hb7"),
                InlineKeyboardButton(text="•𝐋ᴏᴏᴘ•", callback_data="music_callback hb8"),
                InlineKeyboardButton(
                    text="•𝐌ᴀɪɴᴛᴇɴᴀɴᴄᴇ•", callback_data="music_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(text="•𝐏ɪɴɢ•", callback_data="music_callback hb10"),
                InlineKeyboardButton(text="•𝐏ʟᴀʏ•", callback_data="music_callback hb11"),
                InlineKeyboardButton(
                    text="•𝐒ʜᴜғғʟᴇ•", callback_data="music_callback hb12"
                ),
            ],
            [
                InlineKeyboardButton(text="•𝐒ᴇᴇᴋ•", callback_data="music_callback hb13"),
                InlineKeyboardButton(text="•𝐒ᴏɴɢ•", callback_data="music_callback hb14"),
                InlineKeyboardButton(text="•𝐒ᴘᴇᴇᴅ•", callback_data="music_callback hb15"),
            ],
            [InlineKeyboardButton(text="•𝐁ᴀᴄᴋ•", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        f"``**𝐂ʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.](https://t.me/+3LYCl_fgUBgzZTQ9)**\n\n**𝐀ʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /**``",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("management"))
async def management_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="•𝐄xᴛʀᴧ•", callback_data="management_callback extra"
                )
            ],
            [
                InlineKeyboardButton(
                    text="•𝐁ᴧη•", callback_data="management_callback hb1"
                ),
                InlineKeyboardButton(
                    text="•𝐊ɪᴄᴋs•", callback_data="management_callback hb2"
                ),
                InlineKeyboardButton(
                    text="•𝐌υᴛє•", callback_data="management_callback hb3"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="•𝐏ɪη•", callback_data="management_callback hb4"
                ),
                InlineKeyboardButton(
                    text="•𝐒ᴛᴧғғ•", callback_data="management_callback hb5"
                ),
                InlineKeyboardButton(
                    text="•𝐒єᴛ 𝐔ᴘ•", callback_data="management_callback hb6"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="•𝐙σϻʙɪє•", callback_data="management_callback hb7"
                ),
                InlineKeyboardButton(
                    text="•𝐆ᴧϻє•", callback_data="management_callback hb8"
                ),
                InlineKeyboardButton(
                    text="•𝐈ϻᴘσsᴛєʀ•", callback_data="management_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="•𝐒ᴧηɢ ϻᴧᴛᴧ•", callback_data="management_callback hb10"
                ),
                InlineKeyboardButton(
                    text="•𝐓ʀᴧηsʟᴧᴛє•", callback_data="management_callback hb11"
                ),
                InlineKeyboardButton(
                    text="•𝐓_𝐆ʀᴧᴘʜ•", callback_data="management_callback hb12"
                ),
            ],
            [InlineKeyboardButton(text="𝐁ᴀᴄᴋ ↪️", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        f"``**𝐂ʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.](https://t.me/+3LYCl_fgUBgzZTQ9)**\n\n**𝐀ʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /**``",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("tools"))
async def tools_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="•𝐂ʜᴧᴛɢᴘᴛ•", callback_data="tools_callback ai")],
            [
                InlineKeyboardButton(text="•𝐆σσɢʟє•", callback_data="tools_callback hb1"),
                InlineKeyboardButton(
                    text="•𝐓ᴛs_ᴠσɪᴄє•", callback_data="tools_callback hb2"
                ),
                InlineKeyboardButton(text="•𝐈ηꜰσ•", callback_data="tools_callback hb3"),
            ],
            [
                InlineKeyboardButton(text="•𝐅σηᴛ•", callback_data="tools_callback hb4"),
                InlineKeyboardButton(text="•𝐌ᴧᴛʜ•", callback_data="tools_callback hb5"),
                InlineKeyboardButton(text="•𝐓ᴧɢᴧʟʟ•", callback_data="tools_callback hb6"),
            ],
            [
                InlineKeyboardButton(text="•𝐈ϻᴧɢє•", callback_data="tools_callback hb7"),
                InlineKeyboardButton(text="•𝐇ᴧsᴛᴧɢ•", callback_data="tools_callback hb8"),
                InlineKeyboardButton(
                    text="•𝐒ᴛɪᴄᴋєʀs•", callback_data="tools_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(text="ғυη", callback_data="tools_callback hb10"),
                InlineKeyboardButton(
                    text="•𝐐υσᴛʟʏ•", callback_data="tools_callback hb11"
                ),
                InlineKeyboardButton(
                    text="•𝐓ʀ_𝐃ʜ•", callback_data="tools_callback hb12"
                ),
            ],
            [InlineKeyboardButton(text="•𝐁ᴀᴄᴋ•", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        f"``**𝐂ʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.](https://t.me/+3LYCl_fgUBgzZTQ9)**\n\n**Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /**``",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("back_to_music"))
async def feature_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(
                text="𝐓ᴀᴘ ʜᴇʀᴇ ᴛᴏ ᴀᴅᴅ ᴍᴇ 💗",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="˹𝐌ᴜsɪᴄ 🎧", callback_data="music"),
            InlineKeyboardButton(text="˹𝐌ᴧɴᴧɢᴍᴇɴᴛ˼ 🎄", callback_data="management"),
        ],
        [
            InlineKeyboardButton(text="˹𝐓ᴏᴏʟs˼ 🔧", callback_data="tools"),
            InlineKeyboardButton(text="˹𝐀ʟʟ˼ 👀", callback_data="settings_back_helper"),
        ],
        [InlineKeyboardButton(text="𝐇ᴏᴍᴇ 🔄", callback_data="go_to_start")],
    ]
    k = f"""**✨ ᴍᴇᴇᴛ {app.mention} !\n\n❅──────✧❅✦❅✧──────❅\n🎶 ɪ’ᴍ ᴀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ | ᴍᴜsɪᴄ ʙᴏᴛ\n\n🚀 ɴᴏ ʟᴀɢ, ɴᴏ ᴀᴅs, ɴᴏ ᴘʀᴏᴍᴏᴛɪᴏɴs\n🎧 𝟸𝟺/𝟽 ᴜᴘᴛɪᴍᴇ ᴡɪᴛʜ ᴛʜᴇ ʙᴇsᴛ sᴏᴜɴᴅ ǫᴜᴀʟɪᴛʏ\n💡 ᴛᴀᴘ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs!\n\n━━━━━━━━━━━━━━━\n❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ <a href=https://t.me/Chini_tomarre>𓆩 𝐒 𝐇 𝐔 𝐁 𝐇 𝐎 𓆪</a></b></blockquote>**"""
    await callback_query.message.edit_text(
        text=k,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def back_to_music(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"music",
                ),
            ]
        ]
    )
    return upl


def back_to_tools(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"tools",
                ),
            ]
        ]
    )
    return upl


def back_to_management(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"management",
                ),
            ]
        ]
    )
    return upl


@app.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="𝐒ʜᴜʙʜᴏ 💗", callback_data="developer"),
            InlineKeyboardButton(text="𝐅ᴇᴀᴛᴜʀᴇ ✨", callback_data="feature"),
        ],
        [
            InlineKeyboardButton(text="•𝐁ᴀsɪᴄ 𝐆ᴜɪᴅᴇ•", callback_data="basic_guide"),
            InlineKeyboardButton(text="•𝐃ᴏɴᴀᴛᴇ•", callback_data="donate"),
        ],
        [InlineKeyboardButton(text="•𝐁ᴀᴄᴋ•", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        f"**𝐌ᴇᴏᴡ ɪ ᴀᴍ {app.mention} **\n\n**ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴀɴᴅ ᴀᴡᴇsᴏᴍᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴀɴᴅ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴛʜᴀᴛ ɢɪᴠᴇs ʏᴏᴜ sᴘᴀᴍ-ғʀᴇᴇ ᴀɴᴅ ғᴜɴ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ғᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴘs :)**\n\n**● ɪ ᴄᴀɴ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs.**\n**● ɪ ᴄᴀɴ ɢʀᴇᴇᴛ ᴜsᴇʀs ᴡɪᴛʜ ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀɴᴅ ᴇᴠᴇɴ sᴇᴛ ᴀ ɢʀᴏᴜᴘ's ʀᴜʟᴇs.**\n**● ɪ ʜᴀᴠᴇ ᴀ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ sʏsᴛᴇᴍ.**\n**● ɪ ʜᴀᴠᴇ ᴀʟᴍᴏsᴛ ᴀʟʟ ᴀᴡᴀɪᴛᴇᴅ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢɪɴɢ ғᴇᴀᴛᴜʀᴇs ʟɪᴋᴇ ʙᴀɴ, ᴍᴜᴛᴇ, ᴡᴇʟᴄᴏᴍᴇ, ᴋɪᴄᴋ, ғᴇᴅᴇʀᴀᴛɪᴏɴ, ᴀɴᴅ ᴍᴀɴʏ ᴍᴏʀᴇ.**\n**● ɪ ʜᴀᴠᴇ ᴀ ɴᴏᴛᴇ-ᴋᴇᴇᴘɪɴɢ sʏsᴛᴇᴍ, ʙʟᴀᴄᴋʟɪsᴛs, ᴀɴᴅ ᴇᴠᴇɴ ᴘʀᴇᴅᴇᴛᴇʀᴍɪɴᴇᴅ ʀᴇᴘʟɪᴇs ᴏɴ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅs.**\n**● ɪ ᴄʜᴇᴄᴋ ғᴏʀ ᴀᴅᴍɪɴs' ᴘᴇʀᴍɪssɪᴏɴs ʙᴇғᴏʀᴇ ᴇxᴇᴄᴜᴛɪɴɢ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴀɴᴅ ᴍᴏʀᴇ sᴛᴜғғ.**\n\n**➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ʙᴏᴛ .**",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# If the back button has different meanings in various panels, you can set different callbacks
@app.on_callback_query(filters.regex("support"))
async def back_button_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(text="ᴏᴡɴᴇʀ", user_id=config.OWNER_ID[0]),
            InlineKeyboardButton(
                text="𝐀ʙᴏᴜᴛ 👀",
                url="https://t.me/about_shubho",
            ),
        ],
        [
            InlineKeyboardButton(text="𝐂ʜᴀᴛ 💗", url=f"{config.SUPPORT_GROUP}"),
            InlineKeyboardButton(text="𝐒ᴏʜɪɴɪ ♥️", url=f"{config.SUPPORT_CHANNEL}"),
        ],
        [InlineKeyboardButton(text="𝐇ᴏᴍᴇ 🔄", callback_data="go_to_start")],
    ]

    await callback_query.message.edit_text(
        "**๏ 𝐂ʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍᴇ**\n\n**ɪғ ʏᴏᴜ ғɪɴᴅ ᴀɴʏ ᴇʀʀᴏʀ ᴏʀ ʙᴜɢ ᴏɴ ʙᴏᴛ ᴏʀ ᴡᴀɴᴛ ᴛᴏ ɢɪᴠᴇ ᴀɴʏ ғᴇᴇᴅʙᴀᴄᴋ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ʏᴏᴜ ᴀʀᴇ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ  (✿◠‿◠)**",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@app.on_callback_query(filters.regex("donate"))
async def settings_back_callback(client: Client, callback_query: CallbackQuery):
    close = [[InlineKeyboardButton(text="✯ ᴄʟᴏsᴇ ✯", callback_data="close")]]
    await callback_query.message.reply_photo(
        photo="https://i.ibb.co/RcTvd4J/photo-2025-01-21-06-54-08-7462258510022049796.jpg",
        caption=f"**𝐒ᴜᴘᴘᴏʀᴛ ᴍʏ ᴄᴏᴅɪɴɢ ᴊᴏᴜʀɴᴇʏ ʙʏ ᴅᴏɴᴀᴛɪɴɢ ᴅɪʀᴇᴄᴛʟʏ ᴛᴏ ʜᴇʟᴘ ᴇɴʜᴀɴᴄᴇ ᴍʏ ʙᴏᴛ's ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴅᴇᴠᴇʟᴏᴘᴍᴇɴᴛ.**\n\n**ʏᴏᴜʀ ᴄᴏɴᴛʀɪʙᴜᴛɪᴏɴ ᴡɪʟʟ ᴅɪʀᴇᴄᴛʟʏ ғᴜɴᴅ ᴛʜᴇ ᴄʀᴇᴀᴛɪᴏɴ ᴏғ ɪɴɴᴏᴠᴀᴛɪᴠᴇ, ᴜsᴇʀ-ғʀɪᴇɴᴅʟʏ ᴛᴏᴏʟs ᴀɴᴅ ᴇxᴄɪᴛɪɴɢ ʙᴏᴛ ᴄᴀᴘᴀʙɪʟɪᴛɪᴇs.**\n\n**sɪᴍᴘʟʏ sᴄᴀɴ ᴛʜᴇ ᴄᴏᴅᴇ ᴀɴᴅ ᴍᴀᴋᴇ ᴀ ᴘᴀʏᴍᴇɴᴛ—ɴᴏ ʜᴀssʟᴇ, ᴊᴜsᴛ ᴀ ǫᴜɪᴄᴋ ᴡᴀʏ ᴛᴏ sᴜᴘᴘᴏʀᴛ ᴀɴᴅ ʜᴇʟᴘ ʙʀɪɴɢ ɴᴇᴡ ғᴇᴀᴛᴜʀᴇs ᴛᴏ ʟɪғᴇ.**\n\n**ᴇᴠᴇʀʏ ᴅᴏɴᴀᴛɪᴏɴ, ʙɪɢ ᴏʀ sᴍᴀʟʟ, ɢᴏᴇs ᴀ ʟᴏɴɢ ᴡᴀʏ ɪɴ ᴘᴜsʜɪɴɢ ᴛʜɪs ᴘʀᴏᴊᴇᴄᴛ ғᴏʀᴡᴀʀᴅ. ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ʙᴇɪɴɢ ᴀ ᴘᴀʀᴛ ᴏғ ᴛʜɪs ᴇxᴄɪᴛɪɴɢ ᴊᴏᴜʀɴᴇʏ!**",
        reply_markup=InlineKeyboardMarkup(close),
    )


@app.on_callback_query(filters.regex("basic_guide"))
async def settings_back_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [[InlineKeyboardButton(text="𝐁ᴀᴄᴋ ↪️", callback_data="about")]]
    guide_text = f"**𝐌ᴇᴏᴡ! ᴛʜɪs ɪs ᴀ ǫᴜɪᴄᴋ ᴀɴᴅ sɪᴍᴘʟᴇ ɢᴜɪᴅᴇ ᴛᴏ ᴜsɪɴɢ** {app.mention} **🎉**\n\n**1. ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 'ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʟᴀɴ' ʙᴜᴛᴛᴏɴ.**\n**2. sᴇʟᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɴᴀᴍᴇ.**\n**3. ɢʀᴀɴᴛ ᴛʜᴇ ʙᴏᴛ ᴀʟʟ ɴᴇᴄᴇssᴀʀʏ ᴘᴇʀᴍɪssɪᴏɴs ғᴏʀ sᴍᴏᴏᴛʜ ᴀɴᴅ ғᴜʟʟ ғᴜɴᴄᴛɪᴏɴᴀʟɪᴛʏ.**\n\n**ᴛᴏ ᴀᴄᴄᴇss ᴄᴏᴍᴍᴀɴᴅs, ʏᴏᴜ ᴄᴀɴ ᴄʜᴏᴏsᴇ ʙᴇᴛᴡᴇᴇɴ ᴍᴜsɪᴄ ᴏʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘʀᴇғᴇʀᴇɴᴄᴇs.**\n**ɪғ ʏᴏᴜ sᴛɪʟʟ ғᴀᴄᴇ ᴀɴʏ ɪssᴜᴇs, ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ʀᴇᴀᴄʜ ᴏᴜᴛ ғᴏʀ sᴜᴘᴘᴏʀᴛ ✨**"
    await callback_query.message.edit_text(
        text=guide_text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
