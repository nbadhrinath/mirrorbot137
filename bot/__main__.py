import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from sys import executable

from telegram import ParseMode
from telegram.ext import CommandHandler
from telegraph import Telegraph
from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, alive, web, OWNER_ID, AUTHORIZED_CHATS, telegraph_token
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, delete, speedtest, leech_settings, usage


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>╭────【 🌟 BOT STATISTICS 🌟 】</b>\n' \
            f'<b>│</b>\n' \
            f'<b>├  ⏰ Bot Uptime : {currentTime}</b>\n' \
            f'<b>├  🗄 Total Disk Space : {total}</b>\n' \
            f'<b>├  🗂 Total Used Space : {used}</b>\n' \
            f'<b>├  📂 Total Free Space : {free}</b>\n' \
            f'<b>├  📑 Data Usage 📑:</b>\n' \
            f'<b>├  📤 Total Upload : {sent}</b>\n' \
            f'<b>├  📥 Total Download : {recv}</b>\n' \
            f'<b>├  🖥️ CPU : {cpuUsage}%</b>\n' \
            f'<b>├  🚀 RAM : {memory}%</b>\n' \
            f'<b>└  🗄 DISK : {disk}%</b>'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("⚜️Repo⚜️", "https://github.com/rahulkhatri137/mirrorbot137")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
🔶This bot is designed by @rahulkhatri137 to mirror your links to Google Drive!🔶
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(
            'Oops! not a Authorized user⛔ \nPlease deploy your own <b>RK137 mirrorbot</b>.',
            context.bot,
            update,
            reply_markup,
        )


def restart(update, context):
    restart_message = sendMessage("✴️Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    web.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Start mirroring the link to Google Drive.
<br><br>
<b>/{BotCommands.TarMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.LeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram, Use <b>/{BotCommands.LeechSetCommand}</b> for leech settings
<br><br>
<b>/{BotCommands.TarLeechCommand}</b> [download_url][magnet_link]:  Start leeching to Telegram and upload it as (.tar)
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram and upload it as (.zip)
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram and if downloaded file is any archive, extracts it to Telegram
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl. Use this without link for more help
<br><br>
<b>/{BotCommands.TarWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and zip before uploading
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> [youtube-dl supported link]: Leech through youtube-dl 
<br><br>
<b>/{BotCommands.LeechTarWatchCommand}</b> [youtube-dl supported link]: Leech through youtube-dl and tar before uploading 
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> [youtube-dl supported link]: Leech through youtube-dl and zip before uploading 
<br><br>
<b>/{BotCommands.LeechSetCommand}</b>: Leech Settings 
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Cancel all running tasks
<br><br>
<b>/{BotCommands.ListCommand}</b> [search term]: Searches the search term in the Google Drive, If found replies with the link
<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show Stats of the machine the bot is hosted on
<br><br>
<b>/{BotCommands.PingCommand}</b>: Check how long it takes to Ping the Bot
<br><br>
<b>/{BotCommands.AuthorizeCommand}</b>: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)
<br><br>
<b>/{BotCommands.UnAuthorizeCommand}</b>: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)
<br><br>
<b>/{BotCommands.AuthorizedUsersCommand}</b>: Show authorized users (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.AddSudoCommand}</b>: Add sudo user (Only Owner)
<br><br>
<b>/{BotCommands.RmSudoCommand}</b>: Remove sudo users (Only Owner)
<br><br>
<b>/{BotCommands.RestartCommand}</b>: Restart the bot
<br><br>
<b>/{BotCommands.LogCommand}</b>: Get a log file of the bot. Handy for getting crash reports
<br><br>
<b>/{BotCommands.SpeedCommand}</b>: Check Internet Speed of the Host
<br><br>
<b>/{BotCommands.UsageCommand}</b>: To see Heroku Dyno Stats (Owner & Sudo only).
'''
help = Telegraph(access_token=telegraph_token).create_page(
        title='RK137 Mirrorbot Help',
        author_name='RK137 Mirrorbot',
        author_url='https://github.com/rahulkhatri137/mirrorbot137',
        html_content=help_string_telegraph,
    )["path"]

help_string = f'''
*Check all commands for more...*
/{BotCommands.HelpCommand}: To get this message
/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to google drive
/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link] : starts mirroring and if downloaded file is any archive , extracts it to google drive
/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: start mirroring and upload the archived (.tar) version of the download
/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.
/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading
/{BotCommands.CancelMirror} : Reply to the message by which the download was initiated and that download will be cancelled
/{BotCommands.StatusCommand}: Shows a status of all the downloads
/{BotCommands.ListCommand} [search term]: Searches the search term in the Google drive, if found replies with the link
/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on
/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by owner of the bot)
/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports
/{BotCommands.SpeedCommand}: Check Internet Speed of the Host
/{BotCommands.RestartCommand}: Restart the bot
/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot
/{BotCommands.UsageCommand}: To see Heroku Dyno Stats (Owner & Sudo only)
/{BotCommands.LeechWatchCommand} [youtube-dl supported link]: Leech through youtube-dl 
/{BotCommands.LeechCommand} [download_url][magnet_link]: Start leeching to Telegram, Use /{BotCommands.LeechSetCommand} for leech settings
'''

def bot_help(update, context):
    button = button_build.ButtonMaker()
    button.buildbutton("All Commands", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

'''
botcmds = [
        (f'{BotCommands.HelpCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.TarMirrorCommand}','Start mirroring and upload as .tar'),
        (f'{BotCommands.ZipMirrorCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract files'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeleteCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchCommand}','Mirror Youtube-dl support link'),
        (f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as .tar'),
        (f'{BotCommands.ZipWatchCommand}','Mirror Youtube playlist link as .zip'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsCommand}','Bot Usage Stats'),
        (f'{BotCommands.PingCommand}','Ping the Bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.LogCommand}','Get the Bot Log [owner/sudo only]'),
        (f'{BotCommands.UsageCommand}','To see Heroku Dyno Stats (Owner only)')
        (f'{BotCommands.LeechCommand}','Start leeching to Telegram')
    ]
'''

def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("♻️Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
    # bot.set_my_commands(botcmds)
    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
