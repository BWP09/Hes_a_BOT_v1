import discord, yaml, datetime, os, atexit, asyncio, random
from dateutil import tz
import colorama as col
from discord.utils import get

#= By Brandon Payne or BWP09 =#
#= Github repo for this (terrible) project: https://github.com/BWP09/Hes_a_BOT =#

## PLANS ##
# 1. Add a queue for playing files
# 2. Add blacklisting for roles

def update_yaml(yaml_file, key, value):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    data[key] = value
    with open(yaml_file, "w") as f:
        yaml.dump(data, f)

def append_yaml(yaml_file, key, value):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    data[key].append(value)
    with open(yaml_file, "w") as f:
        yaml.dump(data, f)

def remove_yaml(yaml_file, key, value):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    data_new = data[key]
    data[key] = data_new.remove(value)
    with open(yaml_file, "w") as f:
        yaml.dump(data, f)

def update_blacklist():
    global blacklist_UPDATED
    with open("data/config/blacklist.yml", "r") as file:
        blacklist_UPDATED = yaml.safe_load(file)

def update_config():
    global TOKEN, PREFIX, ADMIN_NAME, ADMIN_ID, EMBED_COLOR, PLAYING_STATUS, VERSION, COLOR, BOT_ID, MEGASPAM_MAX, PURGE_MAX
    global bl_server, bl_channel, bl_response_server, bl_response_channel, bl_user, snipe_message, kid_counter

    with open("data/config/config.yml", "r") as file:
        config = yaml.safe_load(file)

    with open("data/config/token.yml", "r") as file:
        token = yaml.safe_load(file)

    with open("data/config/data.yml", "r") as file:
        data = yaml.safe_load(file)

    with open("data/config/blacklist.yml", "r") as file:
        blacklist = yaml.safe_load(file)

    TOKEN = token["token"]
    BOT_ID = config["bot"]["id"]
    PREFIX = config["bot"]["prefix"]
    ADMIN_NAME = config["bot"]["admin"]["admin_name"]
    ADMIN_ID = config["bot"]["admin"]["admin_id"]
    EMBED_COLOR = config["bot"]["color"]
    PLAYING_STATUS = config["bot"]["playing_status"]
    VERSION = config["bot"]["version"]
    COLOR = config["bot"]["color"]
    MEGASPAM_MAX = int(config["bot"]["megaspam_max"])
    PURGE_MAX = int(config["bot"]["purge_max"])

    bl_server = blacklist["server"]
    bl_channel = blacklist["channel"]
    bl_response_server = blacklist["response_server"]
    bl_response_channel = blacklist["response_channel"]
    bl_user = blacklist["user"]

    snipe_message = data["snipe_message"]
    kid_counter = data["kid_counter"]

def get_date_time(type):
    match type:
        case 0: return datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        case 1: return datetime.datetime.now().strftime("%m-%d-%Y")
        case 2: return datetime.datetime.now().strftime("%m/%d/%Y")
        case 3: return datetime.datetime.now().strftime("%H:%M:%S")

def convert_utc_time(input_time: str):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = datetime.datetime.strptime(input_time.split(".")[0], '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo = from_zone)
    local_time = utc.astimezone(to_zone).replace(tzinfo=None)
    new_time = datetime.datetime.strptime(str(local_time), "%Y-%m-%d %H:%M:%S")

    return new_time.strftime('%m-%d-%Y %H:%M:%S')

def log(file_name, text):
    with open(f"data/logs/{file_name}.log", "a", encoding = "utf-8") as file:
        file.write(f"{text}\n")

def file_append(file_name, text):
    with open(file_name, "a", encoding = "utf-8") as file:
        file.write(text)

def file_write(file_name, text):
    with open(file_name, "r+", encoding = "utf-8") as file:
        file.seek(0)
        file.truncate()
        file.write(text)

def file_read(file_name):
    with open(file_name, "r", encoding = "utf-8") as file:
        return file.read()

def error_handler(error):
    print(f"{col.Fore.YELLOW}>[Error Handler]: {error}")

    if error == "list index out of range": text = "Syntax error"
    elif error.count("invalid literal for int() with base 10") > 0: text = "Syntax error"
    elif error == "invalid command syntax": text = "Syntax error"
    elif error == "too many megaspam messages": text = f"Amount of messages is too high, the max is {MEGASPAM_MAX} messages"
    elif error == "too many spam messages": text = f"Amount of messages is too high, the amount of characters times the number of messages must be fewer than 2000"
    elif error == "too many purge messages": text = f"Amount of messages is too high, the max is {PURGE_MAX} messages"
    elif error == "Not connected to voice channel": text = "Not connected to voice channel"
    elif error == "Audio not paused": text = "Audio Error"
    elif error == "Audio not playing": text = "Audio Error"
    elif error == "'NoneType' object has no attribute 'id'": text = "Role error"

    else: text = "Unknown Error"

    return f"[Error Handler]: **{text}**\n(try `{PREFIX} help`)\n```{error}```"

def exit_handler():
    print(f"{col.Fore.YELLOW}>[Exit Handler]: Closing bot.")
    log(f"LOG-{get_date_time(1)}", f">[Exit Handler]: Closing bot.")
    print(f"{col.Style.RESET_ALL}Closed")

def syntax_embed(command_name):
    return discord.Embed(title = f"Syntax Help: {command_name}", description = file_read(f"data/config/syntax_help/{command_name}.txt"), color=COLOR)

update_config()
atexit.register(exit_handler)
client = discord.Client()
os.system("color")

@client.event
async def on_ready():
    update_config()
    print(f"{col.Style.RESET_ALL}Logged in as:")
    print("{0.user}".format(client) + f" (v{VERSION})")
    await client.change_presence(status = discord.Status.online)
    await client.change_presence(activity = discord.Game(PLAYING_STATUS))

@client.event
async def on_message_edit(before, after):
    update_config()

    before_message = str(before.content)
    after_message = str(after.content)

    username = str(before.author).split("#")[0]
    channel = str(before.channel)
    server = str(before.guild)

    log(f"LOG-{get_date_time(1)}", f"[MESSAGE EDIT]: [{get_date_time(0)}]: [{server}: {channel}]: {username}:\n OLD: {before_message}\n NEW: {after}\n")
    print(f"{col.Fore.RED}[MESSAGE EDIT]: {col.Fore.LIGHTMAGENTA_EX}[{get_date_time(0)}]: {col.Fore.GREEN}[{server}: {col.Fore.LIGHTGREEN_EX}{channel}{col.Fore.GREEN}]: {col.Fore.CYAN}{username}:\n{col.Fore.LIGHTBLUE_EX} OLD: {before_message}\n NEW: {col.Fore.LIGHTBLUE_EX}\033[4m{after_message}\033[0m")

@client.event
async def on_message_delete(message):
    update_config()

    user_message = str(message.content)

    username = str(message.author).split("#")[0]
    channel = str(message.channel)
    server = str(message.guild)

    update_yaml("data/config/data.yml", "snipe_message", f"[{get_date_time(0)}]: [{server}: {channel}]: {username}: {user_message}")
    log(f"LOG-{get_date_time(1)}", f"[MESSAGE DELETE]: [{get_date_time(0)}]: [{server}: {channel}]: {username}: {user_message}")
    log(f"SNIPE-{get_date_time(1)}", f"[{get_date_time(0)}]: [{server}: {channel}]: {username}: {user_message}")
    print(f"{col.Fore.RED}[MESSAGE DELETE]: {col.Fore.LIGHTMAGENTA_EX}[{get_date_time(0)}]: {col.Fore.GREEN}[{server}: {col.Fore.LIGHTGREEN_EX}{channel}{col.Fore.GREEN}]: {col.Fore.CYAN}{username}: {col.Fore.LIGHTBLUE_EX}\033[4m{user_message}\033[0m")

@client.event
async def on_message(message):
    update_config()

    user_message = str(message.content)

    username = str(message.author).split("#")[0]
    author = str(message.author)
    author_id = int(message.author.id)
    channel = str(message.channel)
    channel_id = int(message.channel.id)
    server = str(message.guild)

    try: server_id = int(message.guild.id)
    except: server_id = 0

    # try: url = message.attachments[0].url
    # except: url = 0

    if message.reference != None:
        ref_message = await message.channel.fetch_message(message.reference.message_id) #ref_message.content

        ref_content = str(ref_message.content)
        ref_username = str(ref_message.author).split("#")[0]
        ref_author = str(ref_message.author)
        ref_author_id = int(ref_message.author.id)
        ref_message_time = convert_utc_time(str(ref_message.created_at))

        log(f"LOG-{get_date_time(1)}", f"= [{ref_message_time}]: [{server}: {channel}]: {ref_username}: {ref_content}\n^ [{get_date_time(0)}]: [{server}: {channel}]: {username}: {user_message}")
        print(f"{col.Fore.YELLOW}= {col.Fore.LIGHTMAGENTA_EX}[{ref_message_time}]: {col.Fore.GREEN}[{server}: {col.Fore.LIGHTGREEN_EX}{channel}{col.Fore.GREEN}]: {col.Fore.CYAN}{ref_username}: {col.Fore.LIGHTBLUE_EX}{ref_content}\n{col.Fore.YELLOW}^ {col.Fore.LIGHTMAGENTA_EX}[{get_date_time(0)}]: {col.Fore.GREEN}[{server}: {col.Fore.LIGHTGREEN_EX}{channel}{col.Fore.GREEN}]: {col.Fore.CYAN}{username}: {col.Fore.LIGHTBLUE_EX}{user_message}")

    else:
        log(f"LOG-{get_date_time(1)}", f"[{get_date_time(0)}]: [{server}: {channel}]: {username}: {user_message}")
        print(f"{col.Fore.LIGHTMAGENTA_EX}[{get_date_time(0)}]: {col.Fore.GREEN}[{server}: {col.Fore.LIGHTGREEN_EX}{channel}{col.Fore.GREEN}]: {col.Fore.CYAN}{username}: {col.Fore.LIGHTBLUE_EX}{user_message}")


    if author_id == BOT_ID: return


    elif user_message.lower().startswith(f"{PREFIX} blacklist"):
        try:
            args = user_message.lower().split(" | ")[1]
            arg1 = args.split(" / ")[0]
            arg2 = args.split(" / ")[1]
            if arg1 == "add":
                if arg2.startswith("user:"):
                    bl_user_id = int(arg2.split("user: ")[1])
                    append_yaml("data/config/blacklist.yml", "user", bl_user_id)

                elif arg2.startswith("server:"):
                    bl_server_id = int(arg2.split("server: ")[1])
                    append_yaml("data/config/blacklist.yml", "server", bl_server_id)

                elif arg2.startswith("channel:"):
                    bl_channel_id = int(arg2.split("channel: ")[1])
                    append_yaml("data/config/blacklist.yml", "channel", bl_channel_id)

                elif arg2.startswith("response_server:"):
                    bl_response_server_id = int(arg2.split("response_server: ")[1])
                    append_yaml("data/config/blacklist.yml", "response_server", bl_response_server_id)

                elif arg2.startswith("response_channel:"):
                    bl_response_channel_id = int(arg2.split("response_channel: ")[1])
                    append_yaml("data/config/blacklist.yml", "response_channel", bl_response_channel_id)

                await message.add_reaction("☑️")

            if arg1 == "remove":
                if arg2.startswith("user:"):
                    bl_user_id = int(arg2.split("user: ")[1])
                    remove_yaml("data/config/blacklist.yml", "user", bl_user_id)
                    update_blacklist()
                    if blacklist_UPDATED["user"] == None:
                        update_yaml("data/config/blacklist.yml", "user", [""])

                elif arg2.startswith("server:"):
                    bl_server_id = int(arg2.split("server: ")[1])
                    remove_yaml("data/config/blacklist.yml", "server", bl_server_id)
                    update_blacklist()
                    if blacklist_UPDATED["server"] == None:
                        update_yaml("data/config/blacklist.yml", "server", [""])

                elif arg2.startswith("channel:"):
                    bl_channel_id = int(arg2.split("channel: ")[1])
                    remove_yaml("data/config/blacklist.yml", "channel", bl_channel_id)
                    update_blacklist()
                    if blacklist_UPDATED["channel"] == None:
                        update_yaml("data/config/blacklist.yml", "channel", [""])

                elif arg2.startswith("response_server:"):
                    bl_response_server_id = int(arg2.split("response_server: ")[1])
                    remove_yaml("data/config/blacklist.yml", "response_server", bl_response_server_id)
                    update_blacklist()
                    if blacklist_UPDATED["response_server"] == None:
                        update_yaml("data/config/blacklist.yml", "response_server", [""])

                elif arg2.startswith("response_channel:"):
                    bl_response_channel_id = int(arg2.split("response_channel: ")[1])
                    remove_yaml("data/config/blacklist.yml", "response_channel", bl_response_channel_id)
                    update_blacklist()
                    if blacklist_UPDATED["response_channel"] == None:
                        update_yaml("data/config/blacklist.yml", "response_channel", [""])

                await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif server_id in bl_server: return
    elif channel_id in bl_channel: return
    elif author_id in bl_user: return


    elif user_message.lower().count("(!)") > 0: return


    elif user_message.lower().startswith("d!<"):
        message_id = int(user_message.lower().removeprefix("d!<").removesuffix(">"))
        delete_message = await message.channel.fetch_message(message_id)
        await message.add_reaction("☑️")
        await delete_message.delete()
        await asyncio.sleep(1)
        await message.delete()


    elif user_message.lower().startswith(f"{PREFIX} purge") or user_message.lower().startswith("p!<"): # ADD ALTERNATIVE TO THIS COMMAND WITH SIMPLER SYNTAX
        try:
            case = 0
            amount = 0

            if user_message.lower().startswith(f"{PREFIX} purge"):
                amount = int(user_message.lower().split(" | ")[1])
                case = 1

            elif user_message.lower().startswith("p!<"):
                amount = int(user_message.lower().removeprefix("p!<").removesuffix(">"))

            if amount > PURGE_MAX:
                raise Exception("too many purge messages")

            else:
                print(f"{col.Fore.RED}[purge] {col.Style.RESET_ALL}purging {amount} messages")
                await message.add_reaction("☑️")
                await asyncio.sleep(1)

                async for delete_message in message.channel.history(limit = amount + 1):
                    await delete_message.delete()

                if case == 1:
                    await message.channel.send(f"Purge Complete :smiling_imp:\nDeleted {amount} messages")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} stop"):
        if author_id == ADMIN_ID:
            try:
                if message.guild.voice_client: await message.guild.voice_client.disconnect()
            except: pass

            await client.change_presence(activity = discord.Game("I am offline"))
            await message.add_reaction("☑️")
            await client.close()
        else:
            await message.channel.send("hehe no no!")
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} help"):
        embed_var = discord.Embed(title = "Help Command", description = file_read("data/config/help_file.txt"), color = COLOR)
        await message.channel.send(embed = embed_var, reference = message)
        await message.add_reaction("☑️")


    elif user_message.lower().startswith(f"{PREFIX} *help*"):
        embed_var = discord.Embed(title = "*Help* Command", description = file_read("data/config/help_file_secrete.txt"), color = COLOR)
        await message.channel.send(embed = embed_var, reference = message)
        await message.add_reaction("☑️")


    elif user_message.lower().startswith(f"{PREFIX} syntax"):
        try:
            command_name = user_message.lower().split(" | ")[1]
            description_embed = ""

            match command_name:
                case "blacklist": description_embed = syntax_embed(command_name)
                case "help": description_embed = syntax_embed(command_name)
                case "id": description_embed = syntax_embed(command_name)
                case "join": description_embed = syntax_embed(command_name)
                case "leave": description_embed = syntax_embed(command_name)
                case "megaspam": description_embed = syntax_embed(command_name)
                case "purge": description_embed = syntax_embed(command_name)
                case "role": description_embed = syntax_embed(command_name)
                case "snipe": description_embed = syntax_embed(command_name)
                case "spam": description_embed = syntax_embed(command_name)
                case "status": description_embed = syntax_embed(command_name)
                case "stop": description_embed = syntax_embed(command_name)
                case "syntax": description_embed = syntax_embed(command_name)
                case "test": description_embed = syntax_embed(command_name)
                case "vc": description_embed = syntax_embed(command_name)

                case _: raise Exception("invalid command syntax")

            await message.channel.send(embed = description_embed, reference = message)

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} test"):
        await message.channel.send(f"Running v{VERSION}", reference = message)
        await message.add_reaction("☑️")


    elif user_message.lower().startswith(f"{PREFIX} id"):
        try:
            args = user_message.lower().split(" | ")[1]

            if args == "server": await message.channel.send(f"Current server's ID: {server_id}", reference = message)
            elif args == "channel": await message.channel.send(f"Current channel's ID: {channel_id}", reference = message)
            elif args.startswith("user: "): 
                user_id = args.split("@")[1].removesuffix(">")
                await message.channel.send(f"User's ID: {user_id}", reference = message)

            else: raise Exception("invalid command syntax")

            await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} status"): # REFACTOR THIS JUST LIKE HOW THE SYNTAX CMD WORKS
        try:
            args = user_message.split(" | ")[1]
            if args.startswith("msg:"):
                msg_args = args.split("msg: ")[1]
                status_message = msg_args.split(" / ")[0]
                status_activity = msg_args.lower().split(" / ")[1]

                match status_activity:
                    case "online":  await client.change_presence(activity = discord.Game(str(status_message)), status = discord.Status.online)
                    case "offline": await client.change_presence(activity = discord.Game(str(status_message)), status = discord.Status.invisible)
                    case "idle":    await client.change_presence(activity = discord.Game(str(status_message)), status = discord.Status.idle)
                    case "dnd":     await client.change_presence(activity = discord.Game(str(status_message)), status = discord.Status.dnd)

                    case _: raise Exception("invalid command syntax")

            else:
                match args:
                    case "online":  await client.change_presence(status = discord.Status.online)
                    case "offline": await client.change_presence(status = discord.Status.invisible)
                    case "idle":    await client.change_presence(status = discord.Status.idle)
                    case "dnd":     await client.change_presence(status = discord.Status.dnd)

                    case _: raise Exception("invalid command syntax")

            await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} spam"):
        try:
            spam_message = ""
            args = user_message.split(" | ")[1]
            text = args.split(" / ")[1]
            amount = args.split(" / ")[0]
            print(f"{col.Fore.RED}[spam] {col.Style.RESET_ALL}spamming: {text}, {amount} times")

            if (len(text) + 1) * int(amount) >= 2000:
                raise Exception("too many spam messages")

            for _ in range(int(amount)):
                spam_message += f"{text}\n"

            await message.channel.send(spam_message)
            await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} megaspam"):
        try:
            args = user_message.split(" | ")[1]
            text = args.split(" / ")[1]
            amount = int(args.split(" / ")[0])

            if amount > MEGASPAM_MAX:
                raise Exception("too many megaspam messages")

            else:
                print(f"{col.Fore.RED}[megaspam] {col.Style.RESET_ALL}spamming: {text}, {amount} times")
                await message.add_reaction("☑️")

                for i in range(amount):
                    print(f"{col.Fore.RED}[megaspam] {col.Style.RESET_ALL}on message: {i + 1} of {amount}")
                    await message.channel.send(text)

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} role"):
        try:
            args = user_message.lower().split(" | ")[1]
            arg = args.split(" / ")[0]
            role_name = args.split(" / ")[1]
            if arg == "add":
                member = message.author
                role = get(member.guild.roles, name = role_name)
                await member.add_roles(role)

            if arg == "remove":
                member = message.author
                role = get(member.guild.roles, name = role_name)
                await member.remove_roles(role)

            await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    # elif user_message.lower().startswith(f"{PREFIX} k*dcounter"):
    #     embed_var = discord.Embed(title = "K*d counter", description = f"The k*d counter is at {kid_counter}", color = COLOR, reference = message)
    #     await message.channel.send(embed = embed_var, reference = message)
    #     await message.add_reaction("☑️")


    elif user_message.lower().startswith(f"{PREFIX} snipe"):
        await message.channel.send(f"[Last deleted message]: {snipe_message}")
        await message.add_reaction("☑️")


    elif user_message.lower().startswith(f"{PREFIX} join"):
        if message.author.voice:
            channel = message.author.voice.channel
            await channel.connect()
            await message.channel.send("sure")

        else:
            await message.channel.send("i dont wanna vc by myself")


    elif message.content.startswith(f"{PREFIX} leave"):
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send("fine")

        else:
            await message.channel.send("im not even in a vc")


    elif user_message.lower().startswith(f"{PREFIX} vc"):
        try:
            args_main = user_message.lower().split(" | ")[1]
            if args_main.startswith("play"):
                file_name = args_main.split(" / ")[1]
                if message.guild.voice_client:
                    vc = message.guild.voice_client
                    vc.play(discord.FFmpegPCMAudio(executable = "C:/Program Files (extracted)/ffmpeg-n5.0-latest-win64-gpl-5.0/bin/ffmpeg.exe", source = "C:/Users/BWP09/Desktop/Misc/Code/Python/Discord/Bots/Hes_a_BOT_v1/data/vc_files/" + file_name))

                else: raise Exception("Not connected to voice channel")

            elif args_main.startswith("stop"):
                if message.guild.voice_client:
                    vc = message.guild.voice_client
                    vc.stop()

                else: raise Exception("Not connected to voice channel")

            elif args_main.startswith("pause"):
                if message.guild.voice_client:
                    vc = message.guild.voice_client
                    if vc.is_playing():
                        vc.pause()

                    else: raise Exception("Audio not playing")
                else: raise Exception("Not connected to voice channel")

            elif args_main.startswith("resume"):
                if message.guild.voice_client:
                    vc = message.guild.voice_client
                    if vc.is_paused:
                        vc.resume()

                    else: raise Exception("Audio not paused")
                else: raise Exception("Not connected to voice channel")

            elif args_main.startswith("list"):
                names = "Files:\n"
                files = os.listdir("data/vc_files/")
                for file in files:
                    names += file + "\n"
                await message.channel.send(names, reference = message)

            else: raise Exception("invalid command syntax")

            await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif user_message.lower().startswith(f"{PREFIX} invite"):
        try:
            invite_link = await message.channel.create_invite()
            await message.channel.send(invite_link, reference = message)
            await message.add_reaction("☑️")

        except Exception as e:
            await message.channel.send(error_handler(str(e)), reference = message)
            await message.add_reaction("❌")


    elif server_id in bl_response_server: return
    elif channel_id in bl_response_channel: return
    elif author_id == BOT_ID: return


    # elif user_message.lower().count("kid") > 0:
    #     await message.channel.send("dont you mean \"k*d\"?", reference = message)
    #     update_yaml("data/config/data.yml", "kid_counter", kid_counter + 1)

    elif user_message.lower() == "sammy":
        await message.channel.send("is HOT AF")

    elif user_message.lower().count("jack") > 0:
        await message.channel.send("did someone say jack....\n", file = discord.File("data/images/jackhigh.png"), reference = message)

    elif user_message.lower() == "keegan":
        await message.channel.send("hehe")

    elif user_message.lower().count("hassan") > 0:
        await message.channel.send("kidnapped your family + L + ratio + bozo", file = discord.File("data/images/hassan_bozo.jpg"))

    elif user_message.lower() == "brandon":
        await message.channel.send("SOURCE ENGINE")

    elif user_message.lower() == "rodrigo":
        await message.channel.send("is gay", reference = message)

    elif user_message.lower().count("gay") > 0:
        await message.channel.send("Rodrigo is so gay lol its true. One time he dm'ed hesa and said: \"I am so gay\"\nIts true")

    elif user_message.lower() == "yeah":
        await message.channel.send("yeah")

    elif user_message.lower() == "ok" or user_message.lower() == "okay":
        await message.channel.send("ok then bud")

    elif user_message.lower() == "oh":
        await message.channel.send("bawls")

    elif user_message.lower() == "big sad":
        await message.channel.send(":cry:")

    elif user_message.lower() == "mega sad":
        await message.channel.send(":cry: :cry: :cry: :cry: :cry:")

    elif user_message.lower() == "chunky sad":
        await message.channel.send(":cry:\nhttps://i1.sndcdn.com/artworks-G7nQ5blTKxfiVCc0-YuOnUQ-t500x500.jpg")

    elif user_message.lower() == "no":
        await message.channel.send("how about yes")

    elif user_message.lower().count("dm me") > 0:
        await message.channel.send("ok", reference = message)
        await message.author.send("you are now DM-ed!")

    elif user_message.lower().count("dumb") > 0:
        await message.channel.send("you're dumb")

    elif user_message.lower().count("half life 3") > 0:
        await message.channel.send("if only..... :disappointed_relieved:")

    elif user_message.lower().count("valorant") > 0:
        await message.channel.send("hold on i gotta pee")

    elif user_message.lower().count("jk") > 0:
        await message.channel.send("i dont think so :thinking:")

    elif user_message.lower() == "please":
        await message.channel.send("with a cherry on top...", reference = message)

    elif user_message.lower().count("shut up") > 0:
        await message.channel.send("i dont shut up, i grow up, and when i look at you i throw up", reference = message)

    elif user_message.lower().count("jesus") > 0: return

    elif user_message.lower().count("sus") > 0 and user_message.lower().count("jesus") == 0:
        rand_int = random.randint(0, 1)
        match rand_int:
            case 0: await message.channel.send("why so sussy son?", reference = message)
            case 1: await message.channel.send("sussy bussy busty baka", reference = message)

    elif user_message.lower() == "why":
        rand_int = random.randint(0, 1)
        match rand_int:
            case 0: await message.channel.send("because yes", reference = message)
            case 1: await message.channel.send("why not?", reference = message)

    elif user_message.lower() == "yes":
        rand_int = random.randint(0, 2)
        match rand_int:
            case 0: await message.channel.send("sure")
            case 1: await message.channel.send("ok")
            case 2: await message.channel.send("fur sure...")

    elif user_message.lower().count("kys") > 0:
        rand_int = random.randint(0, 1)
        match rand_int:
            case 0: await message.channel.send("no u", reference = message)
            case 1: await message.channel.send("maybe later...", reference = message)

    elif user_message.lower().count("lol") > 0:
        rand_int = random.randint(0, 1)
        match rand_int:
            case 0: await message.channel.send("omg so lol", reference = message)
            case 1: await message.channel.send("lol", reference = message)

    elif user_message.lower().count("amogus") > 0:
        rand_int = random.randint(0, 2)
        match rand_int:
            case 0: await message.channel.send("sus")
            case 1: await message.channel.send("sus sus")
            case 2: await message.channel.send("sussy")

    elif user_message.lower().count("bottom") > 0: return

    elif user_message.lower().count("bot ") > 0:
        await message.channel.send("Im not a bot.... thats so mean :cry:", reference = message)

    elif user_message.lower().endswith("bot"):
        await message.channel.send("Im not a bot.... thats so mean :cry:", reference = message)

client.run(TOKEN)