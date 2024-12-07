import os
import discord
import requests
import asyncio
import feedparser
import time
from discord import app_commands
from discord.ext import commands
from server import server_on

LAST_VIDEO_ID_FILE = 'last_video_id.txt'

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Twitch API Credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TWITCH_USERNAME = 'Uranutsu'

# YouTube API Key
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')

# URLs for Twitch API
OAUTH_URL = 'https://id.twitch.tv/oauth2/token'
USER_INFO_URL = 'https://api.twitch.tv/helix/users'
STREAMS_URL = 'https://api.twitch.tv/helix/streams'

# Intents for Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

# สร้าง Client สำหรับ Discord
client = discord.Client(intents=intents)

# สร้าง tree สำหรับ Slash Commands
tree = app_commands.CommandTree(client)
client = commands.Bot(command_prefix='!', intents=intents)

###################################################################################################################################

def read_last_video_id():
    if os.path.exists(LAST_VIDEO_ID_FILE):
        with open(LAST_VIDEO_ID_FILE, 'r') as f:
            return f.read().strip()
    return None

def write_last_video_id(video_id):
    with open(LAST_VIDEO_ID_FILE, 'w') as f:
        f.write(video_id)

# Cache for the last video
last_video_id = read_last_video_id()  
channel_id = os.getenv('channel_id')
discord_channel_id = 1267797519480393829

async def check_youtube(channel_id, discord_channel):
    global last_video_id
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    # Check if there is a new video
    if feed.entries:
        latest_video = feed.entries[0]
        video_id = latest_video['id']
        
        if video_id != last_video_id:  # If it's a new video
            last_video_id = video_id
            video_title = latest_video['title']
            video_url = latest_video['link']
            
            # Send the notification to Discord
            await discord_channel.send(f"Uranutsu Ch. อัพคลิปแล้ว มาดูกันเร๊วววววววว @everyone\n{video_url}")
            write_last_video_id(video_id)  # Write the new video ID to the file

# Scheduler function to run the check periodically
async def youtube_notifier(client, channel_id, discord_channel_id):
    await client.wait_until_ready()
    discord_channel = client.get_channel(discord_channel_id)
    
    while not client.is_closed():
        await check_youtube(channel_id, discord_channel)
        await asyncio.sleep(900)  # Wait 15 minutes before checking again
###################################################################################################################################

# กำหนดตัวแปร global เพื่อเก็บข้อความที่ถูกส่ง
message_sent = None

@client.event
async def on_message(message):
    global message_sent  # ใช้ global เพื่อเข้าถึงตัวแปรนี้

    if message.author == client.user:
        return

    if message.content.startswith('!rule'):
        rules = (
            "✨   กฎการอยู่ร่วมกัน    👑:\n\n"
            "⚝ พูดคุยกันอย่างสุภาพให้เกียรติซึ่งกันและกัน\n\n"
            "⚝ ไม่ซีเรียสเรื่องคำหยาบใช้คำหยาบได้ แต่ขอให้อยู่ในขอบเขตพองามและเหมาะสม\n\n"
            "⚝ ไม่ทักข้อความหานัสโดยตรงหรือแอดเฟรนนัสมาส่วนตัว แต่สามารถแท็กนัสเพื่อพูดคุยกันในช่องแชทดิสคอร์ดได้\n\n"
            "⚝ ไม่พาดพิงหรือเสียดสีเพื่อให้ผู้อื่นเสียหาย\n\n"
            "⚝ ห้ามส่งรูปภาพและข้อความลามกหรือคุกคามผู้อื่น\n\n"
            "⚝ ห้ามสแปมแชทหรือส่งข้อความซ้ำๆ รัวๆ สร้างความรำคาญให้แก่ผู้อื่น\n\n"
            "⚝ สามารถฝากคลิป / ฝากช่องของตัวเองได้ที่ห้อง <#1279197214069231656> และพิมพ์พูดคุยให้ถูกห้อง\n\n"
            "⚝ ซัพรายเดือนสามารถแท็กชวนนัสเล่นเกมได้เสมอในช่อง <#1267799728846802985> ถ้านัสไม่ติดอะไรเล่นด้วยแน่นอน\n\n"
            "⚝ ไม่อนุญาติให้โปรโมทช่องอื่น เว้นแต่ว่านัสอนุญาติแล้ว\n\n"
            "✿ หากทำผิดกฎ 2 ครั้ง จะมีการทักไปตักเตือนส่วนตัว หากมีครั้งที่ 3 จะถูกแบนออกดิสถาวรค่ะ  @everyone ✿"
        )

        # ตรวจสอบว่าข้อความถูกส่งไปแล้วหรือไม่
        if message_sent is None:
            # ส่งข้อความธรรมดาไปยังช่อง
            message_sent = await message.channel.send(rules)

            # เพิ่ม Reaction "✅" ให้กับข้อความที่ส่ง
            await message_sent.add_reaction("✅")
        else:
            await message.channel.send("ข้อความกฎถูกส่งไปแล้ว!")  # แจ้งเตือนเมื่อพยายามส่งซ้ำ

    elif message.content.startswith('!live'):
    # เรียกใช้งาน live_status_task() และ youtube_live_status_task() โดยตรง
        asyncio.create_task(live_status_task())  # เรียกใช้งาน live_status_task() ในพื้นหลัง
        asyncio.create_task(youtube_live_status_task())  # เรียกใช้งาน youtube_live_status_task() ในพื้นหลัง
    
    elif message.content.startswith('!clip'):
        discord_channel = client.get_channel(1267797519480393829)  # Channel ID for Discord notifications
        if discord_channel is None:
            await message.channel.send("ไม่สามารถค้นพบช่องที่ต้องการส่งข้อความ")
            return
        
        # เรียกใช้ฟังก์ชัน get_latest_clip() ในพื้นหลัง
        asyncio.create_task(get_latest_clip(channel_id, discord_channel))

###################################################################################################################################

# # Get Twitch OAuth Token
# def get_twitch_token():
#     params = {
#         'client_id': CLIENT_ID,
#         'client_secret': CLIENT_SECRET,
#         'grant_type': 'client_credentials'
#     }
#     response = requests.post(OAUTH_URL, params=params)
#     return response.json().get('access_token')

# # Get Twitch user ID by username
# def get_user_id(twitch_username, token):
#     headers = {
#         'Client-ID': CLIENT_ID,
#         'Authorization': f'Bearer {token}'
#     }
#     params = {'login': twitch_username}
#     response = requests.get(USER_INFO_URL, headers=headers, params=params)
#     data = response.json().get('data')
#     if data:
#         return data[0]['id'], data[0]['profile_image_url']  # คืนค่า ID และ URL ของไอคอน
#     return None, None  # คืนค่า None ถ้าไม่พบข้อมูล

##################################################################################################################################
# Function to get the latest clip from YouTube
async def get_latest_clip(channel_id, discord_channel):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)

    if feed.entries:
        latest_video = feed.entries[0]
        video_title = latest_video['title']
        video_url = latest_video['link']
        thumbnail_url = latest_video.get('media_thumbnail', [{'url': ''}])[0]['url']  # ดึง thumbnail

        # ส่งการแจ้งเตือนใน Discord
        await discord_channel.send(f'Uranutsu Ch. อัพคลิปแล้ว มาดูกันเร๊วววววววว @everyone\n{video_url}')

# Check if the user is live
# def check_live_status(user_id, token):
#     headers = {
#         'Client-ID': CLIENT_ID,
#         'Authorization': f'Bearer {token}'
#     }
#     params = {'user_id': user_id}
#     response = requests.get(STREAMS_URL, headers=headers, params=params)
#     streams = response.json().get('data')
#     if streams:
#         return streams[0]  # คืนค่าข้อมูลสตรีมถ้ามี
#     return None  # คืนค่า None ถ้าไม่มีสตรีม

# # Task to check Twitch live status periodically
# async def live_status_task():
#     await client.wait_until_ready()
#     channel = client.get_channel(1267797428849868811)  # ใส่ ID ของช่อง Discord ที่ต้องการให้บอทแจ้งเตือน
#     token = get_twitch_token()
#     user_id, icon_url = get_user_id(TWITCH_USERNAME, token)

#     global is_live 

#     while not client.is_closed():
#         stream = check_live_status(user_id, token)
#         if stream and not is_live:
#             # ถ้าผู้ใช้ไลฟ์อยู่และก่อนหน้านี้ไม่ไลฟ์
#             title = stream['title']  # ชื่อไลฟ์
#             game_name = stream['game_name']  # ชื่อเกม
#             viewer_count = stream['viewer_count']  # จำนวนคนดู
#             thumbnail_url = stream['thumbnail_url']  # URL ของตัมแมล

#             timestamp = int(time.time())
#             thumbnail_url = f"{thumbnail_url.replace('{width}x{height}', '1280x720')}?t={timestamp}"

#             embed = discord.Embed(
#                 description=f'**[{title}](https://twitch.tv/{TWITCH_USERNAME})**',
#                 color=0x9146FF  # สีม่วง
#             )

#             # เพิ่มชื่อช่องและรูปโปรไฟล์ทางซ้าย
#             embed.set_author(
#                 name=f'{TWITCH_USERNAME} is live on Twitch!',
#                 url=f'https://twitch.tv/{TWITCH_USERNAME}',
#                 icon_url=icon_url  # รูปโปรไฟล์อยู่ข้าง ๆ ชื่อ
#             )

#             # เพิ่มฟิลด์สำหรับชื่อเกมและยอดวิวในบรรทัดเดียวกัน
#             embed.add_field(name='Game', value=game_name, inline=True)  # ฟิลด์ชื่อเกม
#             embed.add_field(name='Viewers', value=viewer_count, inline=True)  # ฟิลด์จำนวนคนดู

#             # เพิ่มข้อมูลตัมแมลใน Embed
#             embed.set_image(url=thumbnail_url)  # ใช้ set_image เพื่อแสดงภาพใหญ่

#             # ส่ง Embed ไปยังช่อง
#             await channel.send(f'❥ Uranutsu กำลังสตรีมอยู่ เข้ามาพูดคุยกันได้นะคะ @everyone ʕ ᵒ ᴥ ᵒʔ', embed=embed)
#             is_live = True  # เปลี่ยนสถานะเป็นไลฟ์
#         elif not stream and is_live:
#             # ถ้าผู้ใช้ไม่ได้ไลฟ์และก่อนหน้านี้ไลฟ์
#             is_live = False  # เปลี่ยนสถานะเป็นไม่ไลฟ์

#         await asyncio.sleep(900)  # รอ 60 วินาที

# Get Twitch OAuth Token
def get_twitch_token():
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(OAUTH_URL, params=params)
    return response.json().get('access_token')

# Get Twitch user ID by username
def get_user_id(twitch_username, token):
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    params = {'login': twitch_username}
    response = requests.get(USER_INFO_URL, headers=headers, params=params)
    data = response.json().get('data')
    if data:
        return data[0]['id'], data[0]['profile_image_url']  # คืนค่า ID และ URL ของไอคอน
    return None, None  # คืนค่า None ถ้าไม่พบข้อมูล

# Check if the user is live
def check_live_status(user_id, token):
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    params = {'user_id': user_id}
    response = requests.get(STREAMS_URL, headers=headers, params=params)
    streams = response.json().get('data')
    if streams:
        return streams[0]  # คืนค่าข้อมูลสตรีมถ้ามี
    return None  # คืนค่า None ถ้าไม่มีสตรีม

# ฟังก์ชันสำหรับสร้าง URL ของตัมเนล
def generate_thumbnail_url(base_url):
    timestamp = int(time.time())  # รับ timestamp ใหม่ทุกครั้ง
    return f"{base_url.replace('{width}x{height}', '1280x720')}?t={timestamp}"

# Task to check Twitch live status periodically
async def live_status_task():
    await client.wait_until_ready()
    channel = client.get_channel(1267797428849868811)  # ใส่ ID ของช่อง Discord ที่ต้องการให้บอทแจ้งเตือน
    token = get_twitch_token()
    user_id, icon_url = get_user_id(TWITCH_USERNAME, token)

    global is_live 

    while not client.is_closed():
        stream = check_live_status(user_id, token)
        if stream and not is_live:
            # ถ้าผู้ใช้ไลฟ์อยู่และก่อนหน้านี้ไม่ไลฟ์
            title = stream['title']  # ชื่อไลฟ์
            game_name = stream['game_name']  # ชื่อเกม
            viewer_count = stream['viewer_count']  # จำนวนคนดู
            thumbnail_url = stream['thumbnail_url']  # URL ของตัมแมล

            # สร้าง URL สำหรับตัมเนล
            thumbnail_url = generate_thumbnail_url(thumbnail_url)

            embed = discord.Embed(
                description=f'**[{title}](https://twitch.tv/{TWITCH_USERNAME})**',
                color=0x9146FF  # สีม่วง
            )

            # เพิ่มชื่อช่องและรูปโปรไฟล์ทางซ้าย
            embed.set_author(
                name=f'{TWITCH_USERNAME} is live on Twitch!',
                url=f'https://twitch.tv/{TWITCH_USERNAME}',
                icon_url=icon_url  # รูปโปรไฟล์อยู่ข้าง ๆ ชื่อ
            )

            # เพิ่มฟิลด์สำหรับชื่อเกมและยอดวิวในบรรทัดเดียวกัน
            embed.add_field(name='Game', value=game_name, inline=True)  # ฟิลด์ชื่อเกม
            embed.add_field(name='Viewers', value=viewer_count, inline=True)  # ฟิลด์จำนวนคนดู

            # เพิ่มข้อมูลตัมแมลใน Embed
            embed.set_image(url=thumbnail_url)  # ใช้ set_image เพื่อแสดงภาพใหญ่

            # ส่ง Embed ไปยังช่อง
            await channel.send(f'❥ Uranutsu กำลังสตรีมอยู่ เข้ามาพูดคุยกันได้นะคะ @everyone ʕ ᵒ ᴥ ᵒʔ', embed=embed)
            is_live = True  # เปลี่ยนสถานะเป็นไลฟ์
        elif not stream and is_live:
            # ถ้าผู้ใช้ไม่ได้ไลฟ์และก่อนหน้านี้ไลฟ์
            is_live = False  # เปลี่ยนสถานะเป็นไม่ไลฟ์

        await asyncio.sleep(900)  # รอ 15 นาที (900 วินาที)


###################################################################################################################################

# Function to check if the YouTube channel is live and get video details
def get_youtube_live_video(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        video_id = data['items'][0]['id']['videoId']
        title = data['items'][0]['snippet']['title']
        thumbnail_url = data['items'][0]['snippet']['thumbnails']['high']['url']

        # ดึงข้อมูลเพิ่มเติมเกี่ยวกับวิดีโอ
        video_details_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=liveStreamingDetails,snippet&key={YOUTUBE_API_KEY}'
        video_details_response = requests.get(video_details_url)
        video_details = video_details_response.json()

        # ดึงชื่อเกมและยอดวิว
        if 'items' in video_details and len(video_details['items']) > 0:
            live_details = video_details['items'][0].get('liveStreamingDetails', {})
            game_name = live_details.get('gameTitle', '-')  # ใช้ "-" หากไม่มีชื่อเกม
            viewer_count = live_details.get('concurrentViewers', '0')  # ยอดวิว
        else:
            game_name = '-'
            viewer_count = '0'

        return video_id, title, thumbnail_url, game_name, viewer_count
    
    return None, None, None, None, None  # ถ้าไม่มีข้อมูล


# Function to get YouTube channel details (profile image, channel name)
def get_youtube_channel_details(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        channel_name = data['items'][0]['snippet']['title']
        profile_image_url = data['items'][0]['snippet']['thumbnails']['high']['url']
        return channel_name, profile_image_url

    return None, None  # คืนค่า None ถ้าไม่พบข้อมูล

# Task to check live status periodically for YouTube
async def youtube_live_status_task():
    await client.wait_until_ready()
    channel = client.get_channel(1267797519480393829)  # ใส่ ID ของช่อง Discord ที่ต้องการให้บอทแจ้งเตือน

    is_live = False  # สถานะเริ่มต้น: ไม่ไลฟ์

    while not client.is_closed():
        video_id, title, thumbnail_url, game_name, viewer_count = get_youtube_live_video(YOUTUBE_CHANNEL_ID)
        channel_name, profile_image_url = get_youtube_channel_details(YOUTUBE_CHANNEL_ID)

        if video_id and not is_live:
            # ถ้าผู้ใช้ไลฟ์อยู่และก่อนหน้านี้ไม่ไลฟ์
            embed = discord.Embed(description=f'**[{title}](https://www.youtube.com/watch?v={video_id})**', color=0xFF0000)

            # เพิ่มชื่อช่องและรูปโปรไฟล์ทางซ้าย
            embed.set_author(name=f'{channel_name} is live on YouTube!', url=f'https://www.youtube.com/channel/{YOUTUBE_CHANNEL_ID}', icon_url=profile_image_url)

            # เพิ่มฟิลด์สำหรับชื่อเกมและยอดวิว
            embed.add_field(name="Game", value=game_name, inline=True)
            embed.add_field(name="Viewers", value=viewer_count, inline=True)

            # เพิ่มภาพ thumbnail
            embed.set_image(url=thumbnail_url)

            # ส่ง Embed ไปยังช่อง
            await channel.send(f'❥ Uranutsu กำลังสตรีมอยู่ เข้ามาพูดคุยกันได้นะคะ @everyone ʕ ᵒ ᴥ ᵒʔ', embed=embed)
            is_live = True  # เปลี่ยนสถานะเป็นไลฟ์
        elif not video_id and is_live:
            is_live = False  # เปลี่ยนสถานะเป็นไม่ไลฟ์
            print(f'{channel_name} is not live.')

        await asyncio.sleep(900)  # ตรวจสอบทุกๆ 60 วินาที

###################################################################################################################################


# เริ่มต้นการทำงานของบอท
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.tree.sync()
    # client.loop.create_task(live_status_task())  # เริ่มการตรวจสอบสถานะ Twitch
    # check new clip
    # discord_channel = client.get_channel(discord_channel_id)
    # await check_youtube(channel_id, discord_channel)  # เรียกฟังก์ชันทันทีเพื่อส่งคลิปล่าสุด
    # client.loop.create_task(youtube_notifier(client, channel_id, discord_channel_id)) # ตรวจสอบการอัพคลิปลง youtube
    # client.loop.create_task(youtube_live_status_task())  # เริ่มการตรวจสอบสถานะ YouTube


###################################################################################################################################
# ยินดีต้อนรับคนเข้าดิส
@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='🎊-ยินดีต้อนรับ')  # เปลี่ยนชื่อช่องตามที่ต้องการ
    if channel:
        embed = discord.Embed(
            title="❥ ยินดีต้อนรับเข้าสู่โลกของยูเรนัสสึนะคะ ★\n"
            "• • • • • • •• • • • • • •• • • • • • •• • • • • • •• • • • • •• • •",
            color=0xffc0cb  # สีชมพูอ่อนสำหรับแถบข้าง ๆ
        )
        embed.add_field(
            name="",
            value=f"𝐻𝑜𝓁𝓁𝒶ッ {member.mention} ʕ ˵• ₒ •˵ ʔ\n"
                  "✩✩ อ่านกฎได้ที่ : <#1267797773034721443>\n"
                  "กดซัพช่องTwitchรายเดือน69บาทเพื่อใช้อิโมจิในไลฟ์และมองเห็นห้องเฉพาะสำหรับซัพ\n"
                  "**สำคัญเชื่อมDiscordกับTwitchเพื่อรับยศซัพอัตโนมัตินะคะ**\n"
                  "เล่นเกมให้สนุกอย่าให้เกมเล่นเรานะจ๊ะ ♛\n"
                  "•—————----------—•°•✿•°•——-----------————•",
            inline=False
        )
        

        # ใส่รูป GIF ที่ด้านบนขวา
        embed.set_thumbnail(url="https://media1.tenor.com/m/obO4Phs6lLMAAAAC/6555.gif")  # แทนที่ด้วย URL ของ GIF ที่อยู่ด้านบนขวา

        # ใส่รูป GIF ที่ด้านล่างของข้อความ
        embed.set_image(url="https://media.tenor.com/Psq0TSQb_b0AAAAi/welcome-anime.gif")  # แทนที่ด้วย URL ของ GIF ที่อยู่ด้านล่าง

        # ส่ง Embed ไปที่ช่อง
        await channel.send(embed=embed)

###################################################################################################################################
server_on()

client.run(DISCORD_TOKEN)  # รัน Discord bot
