from telethon import events, TelegramClient
from telethon.tl.custom import Button
import backend
import os
from tqdm import tqdm
from time import sleep

API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = TelegramClient('youtube-downloader', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def call_tqdm(total):
    global t, tqdm_is_run

    t = tqdm(total=total, unit_scale=True, bar_format='{percentage:3.0f}%|{bar}|\n\nKecepatan {rate_fmt}', ncols=40)
    tqdm_is_run = True

yt_dlp = {}
async def main():
    @bot.on(events.NewMessage(pattern='/start'))
    async def handler(event):
        await event.respond('Selamat datang di bot <b>Youtube Working Downloader!</b>\nKirim link Untuk mulai mendownload\n\nTidak hanya youtube, bot ini mendukung semua link yang didukung oleh YT-DLP\nseperti Instagram, Facebook, dll', buttons=Button.url('Creator', 't.me/zeanetstd'))

    @bot.on(events.NewMessage(pattern='https://'))
    async def handler(event):
        global progress_list

        message = await event.respond('Mengekstrak Link...')
        yt_dlp[event.chat.username] = backend.downloadWithYtdlp(event.text)

        list_formats = yt_dlp[event.chat.username].listFormats()
        if not list_formats:
            await message.edit('Ada masalah pada module YT-DLP, Silahkan coba lagi\n\nHarap lapor jika masalah berlanjut. \nBest Regards, @zeanetstd')
            return False
        
        if list_formats['type'] == 'audio':
            async with bot.conversation(event.chat.username) as conv:

                await conv.send_message('Audio Only/Music terdeteksi')

                await conv.send_message('Mengekstrak dan memproses file...')
                yt_dlp[event.chat.username].downloadMusic()

                file = yt_dlp[event.chat.username].File()

                message = await event.respond(f'Proses selesai, mengirim file ke chat.', parse_mode='HTML')

                progress_list = []
                async def callback_progress(send_bytes, total):
                    global tqdm_is_run

                    if not tqdm_is_run:
                        call_tqdm(total)
                    progress = int((send_bytes/total) * 100)

                    if progress not in progress_list:
                        t.n = send_bytes

                        await message.edit(f'Mengirim File\n\n<code>{t}</code>', parse_mode='HTML')
                        progress_list.append(progress)

                    if progress == 100:
                        tqdm_is_run = False
                
                await conv.send_file(file, caption='Selesai!', progress_callback=callback_progress)
                os.remove(file)
        else:
            buttons = []

            formats_list = []
            for formats in list_formats['data']['formats']:
                try:
                    height = formats['height']
                    width = formats['width']

                    resolution = f'{width}x{height}'

                    if height < 144:
                        continue

                    if formats == None:
                        continue
                    
                    if resolution in formats_list:
                        continue

                    formats_list.append(resolution)
                except:
                    continue

                buttons.append([Button.inline(f'{height}p ({resolution})', f'{height}')])

            await bot.send_file(event.chat.username, list_formats['thumbnail'], caption=f'<b>Judul</b>\n{list_formats['data']['title']}\n\nPilih Resolusi :', parse_mode='HTML', buttons=buttons)


    @bot.on(events.CallbackQuery)
    async def callback_query_handler(event):
        global username, progress_list, t
    
        username = event.chat.username

        resolusi = event.data.decode('UTF-8')
        print(f'User memilih {resolusi}')
        await event.answer()
        
        await event.respond('Memproses, Tunggu sebentar...')
        yt_dlp[event.chat.username].downlodVideoFromReso(resolusi)

        file = yt_dlp[event.chat.username].File()

        message = await event.respond('Proses selesai, mengirim file ke chat.', parse_mode='HTML')

        progress_list = []
        async def callback_progress(send_bytes, total):
            global tqdm_is_run
            
            if not tqdm_is_run:
                call_tqdm(total)

            progress = int((send_bytes/total) * 100)

            if progress not in progress_list:
                t.n = send_bytes
                
                await message.edit(f'Mengirim File\n\n<code>{t}</code>', parse_mode='HTML')
                progress_list.append(progress)

            if progress == 100:
                tqdm_is_run = False
        
        try:
            await bot.send_file(username, file, caption='Selesai!', progress_callback=callback_progress)
        except:
            await bot.send_file(username, file, caption='Selesai!', progress_callback=callback_progress, force_document=True)
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
    
    @bot.on(events.NewMessage(pattern='/bar'))
    async def handler(event):
        t = tqdm(total=100, unit_scale=True, bar_format='{percentage:3.0f}%|{bar}|\n\nKecepatan {rate_fmt}', ncols=40)

        message = await event.respond(f'Memulai Bar.', parse_mode='HTML')
        angka = 0
        while angka <= 100:
            t.n = angka

            await message.edit(f'Tes Bar\n\n<code>{t}</code>', parse_mode='HTML')
            angka += 1
            sleep(0.5)

    print('Bot Running...')
    await bot.run_until_disconnected()

bot.loop.run_until_complete(main())

