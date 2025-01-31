import yt_dlp
import json
import os
import subprocess

output_ytdlp = 'output-ytdlp'
output_video_info = 'output-video-info'
cookie = os.environ.get('COOKIE')

class downloadWithYtdlp:
    if not os.path.exists(output_video_info):
        os.mkdir(output_video_info)
    if not os.path.exists(output_ytdlp):
        os.mkdir(output_ytdlp)

    def __init__(self, url, dataVideo = None):
        self.url = url
        
        #self.infoVideo = dataVideo
        #self.dataVideo = json.loads(dataVideo)

    def listFormats(self):
        ydl_opts = {
            'cookiefile': cookie
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                dataVideo = ydl.extract_info(self.url, download=False)
                dataVideoSanitize = ydl.sanitize_info(dataVideo)
                self.title = dataVideoSanitize['title'].replace('/', '-')
                type_file = 'audio' if dataVideoSanitize['resolution'] == 'audio only' else 'video'
                self.extension = 'mp4' if type_file == 'video' else 'mp3'

                try:
                    thumbnail = dataVideoSanitize['thumbnails'][0]['url']
                except:
                    thumbnail = False

                with open(f'{output_video_info}/{self.title}.json', 'w') as file:
                    json.dump(dataVideoSanitize, file, indent=4)
                self.file_info = f'{output_video_info}/{self.title}.json'
                #file = open('yt_dl.json', 'w')
                #json.dump(dataVideoSanitize, file, indent=4)
                #file.close()

                print('Data Berhasil ditulis di file')
                return {'thumbnail': thumbnail, 'type': type_file,'data': {'title':dataVideoSanitize['title'], 'formats': dataVideoSanitize['formats']}}
        except Exception as e:
            print(e)
            return False

    def downlodVideoFromReso(self, reso):
        ydl_opts = {
            'cookiefile': cookie,
            'format': f'bv*[height<={reso}]+ba/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_ytdlp}/{self.title}.%(ext)s'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.download_with_info_file(self.file_info)

        print(f'Berhasil Mendownload file {self.title} ke {output_ytdlp}')

        os.remove(self.file_info)

    def downloadMusic(self):
        ydl_opts = {
            'format': f'ba/best',
            'outtmpl': f'{output_ytdlp}/{self.title}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download_with_info_file(self.file_info)

        print(f'Berhasil Mendownload file {self.title} ke {output_ytdlp}')

        os.remove(self.file_info)
        

    def File(self):
        file = f'{output_ytdlp}/{self.title}.{self.extension}'
        return file