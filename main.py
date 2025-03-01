import discord
import requests
from dotenv import load_dotenv
import os
import re


# loads variables from .env file
load_dotenv()
DISCORD = os.getenv("DISCORD")  # discord bot key
STEAM = os.getenv("STEAM")  # web API key

# all IDs used for identifying parts of the server
SERVER_ID = 1148628177183326378
ROLE_ID = 1340454432428523560
CHANNEL_ID = 1341261059540910211


# checks if the steam account user sent is a real account
def check_steam(steam_id):
    find = ["An error was encountered while processing your request:<br><br>", "<h3>Failed loading profile data, please try again later.</h3><br><br>"]  # YES, I do know how bad this is, will fix later
    url = f"https://steamcommunity.com/profiles/{steam_id}/"  # or use /profiles/{steam_id} if you have the numerical ID
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if find[0] in response.text and find[0] in response.text:
            return False  # could not find account
        else:
            return True  # found account
    except Exception as e:
        print(e)


# get name of the steam account user sent is a real account
def get_steam(steam_id):
    url = f"https://steamcommunity.com/profiles/{steam_id}/"  # or use /profiles/{steam_id} if you have the numerical ID
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        steam_name = re.search(r"<title>Steam Community :: .*</title>", response.text)[0]  # gets steam name
        # clears unneeded data out of it
        steam_name = steam_name.replace("<title>Steam Community :: ", " ")
        steam_name = steam_name.replace("</title>", " ")

        return steam_name
    except Exception as e:
        print(e)


class Client(discord.Client):
    async def on_ready(self):
        try:
            print(f'Logged on as {self.user}!')
        except Exception as e:
            print(e)

    async def on_member_join(self, member):
        try:
            server = self.get_guild(SERVER_ID)
            role = server.get_role(ROLE_ID)
            channel = self.get_channel(CHANNEL_ID)
            print(f"{member.name} joined {server.name}")
            if member:
                # check if member has already sent in a steamID, automatically giving them the participating role
                with open("accounts.txt", "r") as f:  # checks if user has already been mentioned
                    if member.mention in f.read():
                        print(member.mention)
                        print(f"{member.name} already provided a SteamID")
                        await member.send(f"{member.mention} has been assigned the **{role.name}** role due to already provided a SteamID.")
                        await member.add_roles(role)
                        return

                # used to notify players how to participate
                await member.send(f"welcome {member.mention} to **{server.name}**\nTO PARTICIPATE IN THE EXPERIMENTAL YOU WILL NEED TO DO THE FOLLOWING:")
                await member.send("**WARNING: HIGHLY RECOMMENDED YOU CREATE A NEW ACCOUNT FOR THIS EXPERIMENT, THERE ARE CHANCES YOUR ACCOUNT COULD BE BANNED AND GAME REPLAYS WILL BE PUBLIC FOR RESEARCHERS, RESULTS IN OTHER RESEARCHES BEING ABLE TO SEE YOUR ACCOUNT!**")
                await member.send(f"To take part in the experiment you will need to provide the *SteamID of a newly created or spare Steam Account*, The link below will help you [create a new Steam Account](https://store.steampowered.com/join) and [find your SteamID](https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC).\nOnce you have your SteamID, enter your SteamID in the textbox below without adding any spaces or extra characters.\nYou will then be notified if the SteamID entered was valid or invalid. If the SteamID was invalid, make sure there are only numbers in the message sent and that you entered the SteamID correctly. If your SteamID was valid, you will given the **{role.name}** role allowing you to participate in the experiment session.")
                await member.send(f'**DO NOT SEND AN ACCOUNT FOR SOMEONE ELSE!!!**')
        except Exception as e:
            print(e)

    async def on_message(self, message):
        try:
            if message.author == self.user:
                return  # ignore bots own messages

            print(f'\nMessage from {message.author}: {message.content}')

            # check if message is a DM
            if isinstance(message.channel, discord.DMChannel):
                server = self.get_guild(SERVER_ID)
                role = server.get_role(ROLE_ID)
                if server:
                    member = server.get_member(message.author.id)
                    if member:
                        if check_steam(message.content):  # checks if user sent a valid steam account id
                            print(f"{member.name} sent a valid steam account")
                            await message.channel.send(f"{message.author.mention} has sent a valid steam account!")
                        else:
                            print(f"{member.name} sent an invalid steam account")
                            await message.channel.send(f"{message.author.mention} has sent an invalid steam account, try again!")
                            return  # stops form sending message to account channel

                        with open("accounts.txt", "r") as f:  # checks if SteamID is a duplicate
                            accounts = f.read()
                            if re.search(fr'(?<!<@)\b{re.escape(message.content)}\b(?!>)', accounts) is not None:
                                print(f"{member.name} steam account already entered")
                                await message.channel.send(f"{message.content} has already been entered, try again!")
                                return  # stops form sending message to account channel

                        await message.channel.send(f"{message.content} {get_steam(message.content)} *if this is not your account, try again!*")

                        if role and role not in member.roles:
                            await member.add_roles(role)
                            print(f"Assigned role {role.name} to {member.name}")
                            await message.channel.send(f"{message.author.mention} has been assigned the **{role.name}** role!\n You are now able to participate in the experimental sessions!")
                        else:
                            await message.channel.send(f"{message.author.mention} has already been assigned the **{role.name}** role.")
                            print(f"Already Assigned role {role.name} to {member.name}")

            # sends data to account-channel
            channel = client.get_channel(CHANNEL_ID)
            await channel.send(f"{message.author.mention}: {message.content}{get_steam(message.content)}")  # displays users steam account to channel
            with open("accounts.txt", "a") as f:  # adds SteamID to list, making sure there are no duplicat accounts
                f.write(f"{message.author.mention} {message.content}{get_steam(message.content)}\n")
        except Exception as e:
            print(e)


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # role assignment
intents.dm_messages = True  # DM handling

client = Client(intents=intents)
client.run(DISCORD)
