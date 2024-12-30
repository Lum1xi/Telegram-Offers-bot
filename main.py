from config import *
from ReplyKeyboardMarkupButton import *
from aiogram import Bot, Dispatcher, types, F
import sqlite3
import asyncio

bot = Bot(token=TOKEN)
dp = Dispatcher()


connection = sqlite3.connect('user.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    username TEXT NOT NULL,
    id INTEGER PRIMARY KEY,
    offer INTEGER NOT NULL,
    idea INTEGER NOT NULL,
    process TEXT NOT NULL)
    ''')

connection.commit()

connection2 = sqlite3.connect('accept_offer.db')

connection2.commit()


# Work with callback
@dp.callback_query(F.data.startswith("Accept_"))
async def accept(callback_query: types.CallbackQuery):
    try:
        data = callback_query.data.split("_")
        if len(data) < 3:
            await bot.send_message(callback_query.from_user.id, "Невірний формат даних")
            return

        userid = data[1]
        messagetype = data[2]
        # Отримуємо дані `offer` та `idea` одним запитом
        cursor.execute("SELECT offer, idea FROM Users WHERE id = ?", (userid,))
        result = cursor.fetchone()

        # Перевіряємо, чи існує користувач у базі даних
        if not result:
            await bot.send_message(callback_query.from_user.id, "Користувача не знайдено")
            return

        offer, idea = result
        # Обробка натискання кнопки
        if messagetype == 1:
            if idea == 1:  # Якщо ідея нова
                await bot.send_message(userid, "Ваш запит приняли", reply_markup=user)
                await bot.send_message(callback_query.from_user.id, "Вашу відповідь було надіслано користувачу")

                cursor.execute('UPDATE Users SET idea = ? WHERE id = ?', (0, userid))
                connection.commit()
            else:  # Якщо заявку вже оброблено
                await bot.send_message(callback_query.from_user.id, "Заявку уже було оброблено", reply_markup=user)
        else:
            if offer == 1:  # Якщо ідея нова
                await bot.send_message(userid, "Вашу заявку підтримали", reply_markup=user)
                await bot.send_message(callback_query.from_user.id, "Вашу відповідь було надіслано користувачу")
                cursor.execute('UPDATE Users SET offer = ? WHERE id = ?', (0, userid))
                connection.commit()
            else:  # Якщо заявку вже оброблено
                await bot.send_message(callback_query.from_user.id, "Заявку уже було оброблено", reply_markup=user)
        # Важливо: відповідаємо на callback_query
        await callback_query.answer()  # Це дозволить кнопці зникнути після натискання

    except Exception as e:
        # Лог помилки для налагодження
        print(f"Виникла помилка: {e}")
        await bot.send_message(callback_query.from_user.id, "Сталася помилка під час обробки запиту")


def message_test(message):
    message_to_reply = message.split(" ")
    if message_to_reply[0] == "Вам":
        # print(message_to_reply[0] == "Вам")
        return True
    else:
        return False


@dp.callback_query(F.data.startswith("Cancel_"))
async def cancel(callback_query: types.CallbackQuery):
    try:
        data = callback_query.data.split("_")
        if len(data) < 3:
            await bot.send_message(callback_query.from_user.id, "Невірний формат даних")
            return

        userid = data[1]
        messagetype = data[2]

        # Отримуємо дані `offer` та `idea` одним запитом
        cursor.execute("SELECT offer, idea FROM Users WHERE id = ?", (userid,))
        result = cursor.fetchone()

        # Перевіряємо, чи існує користувач у базі даних
        if not result:
            await bot.send_message(callback_query.from_user.id, "Користувача не знайдено")
            return

        offer, idea = result

        # Обробка натискання кнопки
        if messagetype == 1:
            if idea == 1:  # Якщо ідея нова
                await bot.send_message(userid, "Ваш запит відхиленно", reply_markup=user)
                await bot.send_message(callback_query.from_user.id, "Вашу відповідь було надіслано користувачу")
                cursor.execute('UPDATE Users SET idea = ? WHERE id = ?', (0, userid))
                connection.commit()
            else:  # Якщо заявку вже оброблено
                await bot.send_message(callback_query.from_user.id, "Заявку уже було оброблено", reply_markup=user)
        else:
            if offer == 1:  # Якщо ідея нова
                await bot.send_message(userid, "Вашу заявку відхиленно", reply_markup=user)

                await bot.send_message(callback_query.from_user.id, "Вашу відповідь було надіслано користувачу")
                cursor.execute('UPDATE Users SET offer = ? WHERE id = ?', (0, userid))
                connection.commit()
            else:  # Якщо заявку вже оброблено
                await bot.send_message(callback_query.from_user.id, "Заявку уже було оброблено", reply_markup=user)

        # Важливо: відповідаємо на callback_query
        await callback_query.answer()  # Це дозволить кнопці зникнути після натискання
    except Exception as e:
        # Лог помилки для налагодження
        print(f"Виникла помилка: {e}")
        await bot.send_message(callback_query.from_user.id, "Сталася помилка під час обробки запиту")


# Bot Start Message and add Markup
@dp.message()
async def start_command(message: types.Message) -> None:
    userid = message.from_user.id
    if message.text == '/start':
        if userid in admins:
            await bot.send_message(userid, welcomMessage, )
            try:
                cursor.execute('INSERT INTO Users (username, id, offer, idea, process) VALUES (?, ?, ?, ?, ?)',
                               (message.from_user.username, message.from_user.id, 0, 0, 0,))
                connection.commit()
            except:
                # print("Admin Already Exists")
                pass
        else:
            try:
                cursor.execute('INSERT INTO Users (username, id, offer, idea, process) VALUES (?, ?, ?, ?, ?)',
                               (message.from_user.username, message.from_user.id, 0, 0, 0,))
                connection.commit()
            except:
                # print("User Already Exists")
                pass
            await bot.send_message(userid, welcomMessage, reply_markup=user)
    elif message.reply_to_message is not None and message.from_user.id not in admins and message_test(
            message.reply_to_message.text) is False:
        await give_messsage(message, False)
    elif message.reply_to_message and message.from_user.id in admins:
        await give_messsage(message, True)
    elif message.reply_to_message and message.from_user.id not in admins and message_test(
            message.reply_to_message.text):
        await give_messsage(message, False)
    else:
        await message_handler(message)


async def send_message_to_admin(userid, usertag, messagetype, message):  # 1 = idea 2=offer
    if messagetype == 1:
        for i in admins:
            if i != userid:
                await bot.send_message(i, f"Надійшло нове Питання\n\n{message} \n\nВід Користувача @{usertag}",
                                       reply_markup=addbutton(userid, usertag, messagetype))
    elif messagetype == 2:
        for i in admins:
            if i != userid:
                await bot.send_message(i, f"Надійшла нова Пропозиція\n\n{message}\n\nВід Користувача @{usertag}",
                                       reply_markup=addbutton(userid, usertag, messagetype))


@dp.message()
async def message_handler(message: types.Message) -> None:
    userid = message.from_user.id
    if message.text == '💭 Հարց ուղղել' and userid not in admins:
        await message.reply("Գրեք ձեր հարցը և մենք հետադարձ կապ կհաստատենք ձեզ հետ հնարավորինս սեղմ ժամկետում։")
    elif message.text == '✉️ Առաջարկ' and userid not in admins:
        await message.reply(
            "Ներկայացրեք ձեր առաջարկը օգտագործելով հետևյալ կետերը․ \n\n• առաջարկի հակիրճ նկարագիր \n\n• դիտարկվող ժամկետ \n• անհրաժեշտ ռեսուրսներ \n• նպատակ")
    elif userid in admins:
        await message.reply("դուք ադմինիստրատոր եք, չեք կարող հարցումներ ուղարկել")


async def setup_data(message, message_type):
    userid = message.from_user.id
    usertag = message.from_user.username
    messagetosend = message.text

    try:
        cursor.execute("SELECT offer,idea FROM Users WHERE id = ?", (userid,))
        result = cursor.fetchone()
        offer, idea = result
        if message_type == 1:
            if idea != 1:
                cursor.execute('UPDATE Users SET idea = ? WHERE username = ?', (1, usertag))
                connection.commit()

                await bot.send_message(message.from_user.id,
                                       f"Ձեր նամակը \n\n{message.text} \n\nուղարկված է, մենք շուտով կպատասխանենք ձեզ:",
                                       reply_markup=user)
                await send_message_to_admin(userid, usertag, message_type, messagetosend)
            else:
                await bot.send_message(message.from_user.id, "Ви уже відправили ваш запит зачикайте", reply_markup=user)
        else:
            if offer != 1:
                cursor.execute('UPDATE Users SET offer = ? WHERE username = ?', (1, usertag))
                connection.commit()
                await bot.send_message(message.from_user.id,
                                       f"Ձեր նամակը \n\n{message.text} \n\nուղարկված է, մենք շուտով կպատասխանենք ձեզ:",
                                       reply_markup=user)
                await send_message_to_admin(userid, usertag, message_type, messagetosend)
            else:
                await bot.send_message(message.from_user.id, "Ви уже відправили вашу пропозицію", reply_markup=user)
    except Exception as e:
        print(f"Error: {e}")
        pass
    pass


@dp.message()
async def give_messsage(message: types.Message, admin_message=False) -> None:
    if not admin_message:
        message_to_reply = message.reply_to_message
        firs_word = message_to_reply.text.split(' ')
        firs_word = firs_word[0]
        if firs_word == "Գրեք":
            await setup_data(message, 1)
        elif firs_word == "Ներկայացրեք":
            await setup_data(message, 2)
        elif firs_word == "Вам":
            cursor.execute("SELECT process,id FROM Users WHERE process = ?", (message.from_user.id,))
            process, id = cursor.fetchone()
            if int(process) == message.from_user.id:
                await bot.send_message(id,
                                       f"Вам надійшла відповідь \n\n{message.text}"
                                       )
                await bot.send_message(message.from_user.id,
                                       "Адміністратору Була відправленна ваша відповідь",
                                       reply_markup=user)
            elif int(process) != message.from_user.id:
                await bot.send_message(message.from_user.id,
                                       "Ваше питання було закрито",
                                       reply_markup=user)
        else:
            await bot.send_message(message.from_user.id,
                                   "Եթե ​​դա առաջարկ/գաղափար էր, պատճենեք այն և կտտացրեք ստորև գտնվող կոճակներին՝ ուղարկելուց առաջ",
                                   reply_markup=user)
    else:
        message_to_reply = message.reply_to_message

        first_line = message_to_reply.text
        first_line = first_line.split('\n')
        first_line = first_line[0]

        lastWord = message_to_reply.text.split(' ')
        lastWord = lastWord[-1]

        if lastWord[0] == "@":
            lastWord = lastWord.split("@")[1]

        cursor.execute("SELECT id,offer,idea,process FROM Users WHERE username = ?", (lastWord,))
        id, offer, idea, process = cursor.fetchone()
        try:
            if process is not None and process is not message.from_user.id:
                if first_line == "Надійшла нова Пропозиція" and process != 0:
                    if offer != 1:
                        await bot.send_message(message.from_user.id, "Пропозицію було уже розгялененно")
                    elif offer != 0:
                        cursor.execute('UPDATE Users SET process = ? WHERE id = ?', (id, message.from_user.id))
                        connection.commit()

                        await bot.send_message(message.from_user.id,
                                               f"Ваше повідомлення було відправленно користувачу @{lastWord}")
                        try:
                            await bot.send_message(id, f"Вам надійшло повідомлення \n\n{message.text}")
                        except Exception as e:
                            print(f"Error {e}")
                elif first_line == "Надійшло нове Питання" and process != 0:
                    if idea != 1:
                        await bot.send_message(message.from_user.id, "Пропозицію було уже розгялененно")
                    elif idea != 0:
                        cursor.execute('UPDATE Users SET process = ? WHERE id = ?', (id, message.from_user.id))
                        await bot.send_message(message.from_user.id,
                                               f"Ваше повідомлення було відправленно користувачу @{lastWord}")
                        try:
                            await bot.send_message(id, f"Вам надійшло повідомлення \n\n{message.text}")
                        except Exception as e:
                            print(f"Error {e}")
                else:
                    print(first_line)
            elif offer != 0:
                await bot.send_message(message.from_user.id, "Цею пропозицією уже заняті ")
            elif idea != 0:
                await bot.send_message(message.from_user.id, "Цим Питанням уже заняті ")
        except Exception as e:
            print(f"Error: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
