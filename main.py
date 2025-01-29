from telethon import events, TelegramClient
from telethon.tl.custom import Button
import backend

API_ID = '29025157'
API_HASH = '1b24dd470c853bf2d5f411b7fb215644'
BOT_TOKEN = '7582144074:AAGln6na087oFIJzytqZrhEdqatv-wm3-rI'

bot = TelegramClient('youtube-downloader', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

yt_dlp = {}
async def main():
    @bot.on(events.NewMessage)
    async def handler(event):
        await event.respond('Mengekstrak Link...')
        yt_dlp[event.chat.username] = backend.downloadWithYtdlp(event.text)

        list_formats = yt_dlp[event.chat.username].listFormats()
        if not list_formats:
            await event.respond('Terjadi masalah saat mengekstrak link, silahkan coba lagi')
            return False
        
        if list_formats['type'] == 'audio only':
            async with bot.conversation(event.chat.username) as conv:
                await conv.send_message('Audio Only/Music terdeteksi')

                await conv.send_message('Mengekstrak dan mendownload file...')
                yt_dlp[event.chat.username].downloadMusic()

                file = yt_dlp[event.chat.username].File()

                await event.respond('Proses selesai, mengirim file ke chat..')
                await conv.send_file(file, caption='Done!')
        else:
            buttons = []
            for formats in list_formats['data']['formats']:
                resolusi = formats['height']

                buttons.append(Button.inline(f'{resolusi}p', f'{resolusi}'))

            await event.respond(f'<b>Judul</b>\n{list_formats['data']['title']}\n\nPilih Resolusi :', parse_mode='HTML', buttons=buttons)

    @bot.on(events.CallbackQuery)
    async def inline_query_handler(event):
        resolusi = event.data.decode('UTF-8')
        print(f'User memilih {resolusi}')
        await event.answer()
        
        await event.respond('Memproses, Tunggu sebentar...')
        yt_dlp[event.chat.username].downlodVideoFromReso(resolusi)

        file = yt_dlp[event.chat.username].File()

        await event.respond('Proses selesai, mengirim file ke chat..')
        await bot.send_file(event.chat.username, file, caption='Done!')

    @bot.on(events.NewMessage(pattern='/tes-kirim'))
    async def handler(event):
        await bot.send_file(event.chat.username, 'output-ytdlp/Video by zeanlost-DCRRpz3sOFh.mp4', caption='Done!')
    
    print('Bot Running...')
    await bot.run_until_disconnected()

bot.loop.run_until_complete(main())

