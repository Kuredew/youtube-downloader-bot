from telethon import events, TelegramClient
from telethon.tl.custom import Button
import backend
import os

API_ID = '29025157'
API_HASH = '1b24dd470c853bf2d5f411b7fb215644'
BOT_TOKEN = '7582144074:AAGln6na087oFIJzytqZrhEdqatv-wm3-rI'
BOT_TOKEN_TEST = '7229088612:AAEaAJOoJ2Mo0SfivrQq6ZjVOR34CjsRfnM'

bot = TelegramClient('youtube-downloader-test', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


yt_dlp = {}
async def main():
    @bot.on(events.NewMessage(pattern='/start'))
    async def handler(event):
        await event.respond('Selamat datang di bot Youtube Working Downloader!\nKirim link Untuk mulai mendownload\n\nBot ini mendukung semua link yang didukung oleh YT-DLP', buttons=Button.url('Creator', 't.me/zeanetstd'))

    @bot.on(events.NewMessage(pattern='https://'))
    async def handler(event):
        await event.respond('Mengekstrak Link...')
        yt_dlp[event.chat.username] = backend.downloadWithYtdlp(event.text)

        list_formats = yt_dlp[event.chat.username].listFormats()
        if not list_formats:
            await event.respond('Terjadi masalah saat mengekstrak link, silahkan coba lagi')
            return False
        
        if list_formats['type'] == 'audio':
            async with bot.conversation(event.chat.username) as conv:
                global message

                await conv.send_message('Audio Only/Music terdeteksi')

                await conv.send_message('Mengekstrak dan mendownload file...')
                yt_dlp[event.chat.username].downloadMusic()

                file = yt_dlp[event.chat.username].File()

                message = await event.respond(f'Proses selesai, mengirim file ke chat. (<code>{0}%</code>)', parse_mode='HTML')

                async def callback_progress(send_bytes, total):
                    global message

                    progress = int((send_bytes/total) * 100)
                    #await event.respond('0')
                    await message.edit(f'Proses selesai, mengirim file ke chat. (<code>{progress}%</code>)', parse_mode='HTML')
                await conv.send_file(file, caption='Selesai!', progress_callback=callback_progress)
                os.remove(file)
        else:
            buttons = []
            for formats in list_formats['data']['formats']:
                resolusi = formats['height']
                if resolusi == None:
                    continue

                buttons.append(Button.inline(f'{resolusi}p', f'{resolusi}'))

            await bot.send_file(event.chat.username, list_formats['thumbnail'], caption=f'<b>Judul</b>\n{list_formats['data']['title']}\n\nPilih Resolusi :', parse_mode='HTML', buttons=buttons)

    @bot.on(events.CallbackQuery)
    async def callback_query_handler(event):
        global message
        resolusi = event.data.decode('UTF-8')
        print(f'User memilih {resolusi}')
        await event.answer()
        
        await event.respond('Memproses, Tunggu sebentar...')
        yt_dlp[event.chat.username].downlodVideoFromReso(resolusi)

        file = yt_dlp[event.chat.username].File()

        message = await event.respond('Proses selesai, mengirim file ke chat. (<code>0%</code>)', parse_mode='HTML')

        async def callback_progress(send_bytes, total):
            global message

            progress = int((send_bytes/total) * 100)
            #await event.respond('0')
            await message.edit(f'Proses selesai, mengirim file ke chat. (<code>{progress}%</code>)', parse_mode='HTML')
        
        await bot.send_file(event.chat.username, file, caption='Selesai!', progress_callback=callback_progress)
        os.remove(file)

    @bot.on(events.NewMessage(pattern='/tes-kirim'))
    async def handler(event):
        global edit
        edit = False
        async def callback_progress(send_bytes, total):
            global edit, message

            progress = int((send_bytes/total) * 100)
            #await event.respond('0')
            if not edit:
                message = await event.respond(f'Tunggu sebentar (<code>{progress}%</code>)', parse_mode='HTML')
                edit = True
            else:
                await message.edit(f'Tunggu sebentar (<code>{progress}%</code>)', parse_mode='HTML')

        await bot.send_file(event.chat.username, 'output-ytdlp/Video by zeanlost-DCRRpz3sOFh.mp4', caption='Selesai!', progress_callback=callback_progress)
        print('[Selesai]')
        edit = False
    
    print('Bot Running...')
    await bot.run_until_disconnected()

bot.loop.run_until_complete(main())

