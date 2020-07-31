from fasttube import Playlist
from fasttube import YouTube
import pyperclip


playlist_url=input("playlist url -> ")

qu_list = [1080, 720, 480, 360, 240, 144]
print("All available quality.")
for i in range(6):
    print(f"{i}. {qu_list[i]}")
qu = qu_list[int(input("Chose quality number -> "))]

videos=Playlist(playlist_url)
total_video=len(videos)

total_url=""
for vid_info in videos.crawled:
    index=vid_info.index
    video_streams=YouTube(vid_info.url)

    video_streams.title=f"{index}. {video_streams.title}.mp4"#this is important to rename title before filtering as
    total_url+=video_streams.filter(qu)["url"]+"\n"# filter will dress up the url
    # and dressed up stream can not be changed

    print(f"{index}/{total_video}", end="\r")

pyperclip.copy(total_url)
print("All links copied to clipboard.")
print("go IDM -> Task -> Add batch download from clipboard")

