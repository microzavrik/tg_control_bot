import subprocess
import psutil
import pyautogui

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import os

import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

API_TOKEN = 'YOUR_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

admins = set() 
admins.add(5934596933)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.id in admins:
        keyboard_markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton("🟥 Turn off PC", callback_data='turn_off_pc'),
            InlineKeyboardButton("🧭 Restart PC", callback_data='restart_pc'),
            InlineKeyboardButton("🔊 Change volume", callback_data='change_volume'),
            InlineKeyboardButton("🖼 Take a screenshot", callback_data='take_screenshot'),
            InlineKeyboardButton("💤 Sleep PC", callback_data='sleep_pc'),
            InlineKeyboardButton("🗃 View Directory", callback_data='view_directory'),
            InlineKeyboardButton("🗑 Delete File", callback_data='delete_file')
        ]
        
        keyboard_markup.add(*buttons)
        
        await message.answer(text=f"🔹 Welcome, {message.from_user.username}! Here are the available actions:", reply_markup=keyboard_markup)
    else:
        await message.answer(text="You are not authorized to access this bot.")

@dp.callback_query_handler(lambda query: query.data == 'view_directory')
async def callback_view_directory(query: types.CallbackQuery):
    await query.answer()
    await query.message.answer("🔸 Use /view_directory <check_directory>")

@dp.message_handler(lambda message: message.text.startswith("/view_directory "))
async def handle_view_directory(message: types.Message):
    directory_path = message.text.split(" ", 1)[1]
    
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        await message.answer("The specified path is not a valid directory.")
        return
    
    files_list = os.listdir(directory_path)
    if not files_list:
        await message.answer("❌ No files found in the specified directory.")
    else:
        files_str = "\n".join(files_list)
        await message.answer(f"📁 Files in directory '{directory_path}':\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n{files_str}")

@dp.callback_query_handler(lambda query: query.data == 'delete_file')
async def callback_delete_file(query: types.CallbackQuery):
    await query.answer()
    await query.message.answer("🔸 Use /delete_file <path_to_delete_file>")

@dp.message_handler(lambda message: message.text.startswith("/delete_file "))
async def handle_delete_file(message: types.Message):
    file_path = message.text.split(" ", 1)[1]
    
    if not os.path.exists(file_path):
        await message.answer("The specified file does not exist.")
        return
    
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            await message.answer(f"✅ File '{file_path}' has been deleted.")
        else:
            await message.answer("❌ The specified path is not a file.")
    except Exception as e:
        await message.answer(f"An error occurred while trying to delete the file: {str(e)}")

        

@dp.callback_query_handler(lambda query: query.data == 'turn_off_pc')
async def callback_turn_off_pc(query: types.CallbackQuery):
    await handle_shutdown_restart(query.message, action="turn off pc")
    
@dp.callback_query_handler(lambda query: query.data == 'restart_pc')
async def callback_restart_pc(query: types.CallbackQuery):
    await handle_shutdown_restart(query.message, action="restart pc")

async def handle_shutdown_restart(message: types.Message, action: str):
    if action == "turn off pc":
        subprocess.call("shutdown /p /f", shell=True)
        await message.answer("Initiating turn off action on the PC.")
    elif action == "restart pc":
        subprocess.call("shutdown /r /f", shell=True)
        await message.answer("Initiating restart action on the PC.")

def set_volume(volume_percentage):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(volume_percentage, None)

@dp.callback_query_handler(lambda query: query.data == 'change_volume')
async def change_volume_callback(query: types.CallbackQuery):
    await handle_change_volume(query.message)

async def handle_change_volume(message: types.Message):
    await message.answer("Please enter the volume percentage you want to set (0-100):")

@dp.message_handler(lambda message: message.text.isdigit())
async def handle_volume_input(message: types.Message):
    volume_percentage = min(1, max(0, int(message.text)) / 100)  
    set_volume(volume_percentage)
    
    await message.answer(f"The volume is set to {volume_percentage * 100}%.")

@dp.message_handler(lambda message: message.text == "Take a screenshot")
async def handle_take_screenshot(message: types.Message):
    screenshot_path = "screenshot.png"
    pyautogui.screenshot(screenshot_path)
    
    with open(screenshot_path, "rb") as photo:
        await bot.send_photo(message.from_user.id, photo)
    
    await message.answer("Screenshot taken and sent to you.")

@dp.callback_query_handler(lambda query: query.data == 'sleep_pc')
async def sleep_pc_callback(query: types.CallbackQuery):
    await handle_sleep_pc(query.message)

async def handle_sleep_pc(message: types.Message):
    subprocess.call("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    await message.answer("Putting the PC to sleep.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)