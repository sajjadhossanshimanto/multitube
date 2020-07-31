from fasttube import Playlist


def duration(secounds):
    h, m, s=0, 0, secounds
    if s>=60:
        m, s = divmod(s, 60)
    if m>=60:
        h, m = divmod(m, 60)
    
    return h, m, s

link=input("playlist link -> ")
videos=Playlist(link)
total_time=0
for i in videos.crawled:
    total_time+=i.lensec


p=duration(total_time)
print(p)

