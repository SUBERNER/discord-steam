import discord
import requests
from dotenv import load_dotenv
import os
import re


# loads variables from .env file
load_dotenv()
DISCORD = os.getenv("DISCORD")  # discord bot key
STEAM = os.getenv("STEAM")  # web API key

# helps categorize servers and what parts will be needed in the bots methods based on what server the user is apart of
# all IDs used for identifying parts of the server
# each will one from each server for each language
class Server:
    def __init__(self, server_id, role_id, channel_id):
        self.server_id = server_id  # the server being used for research
        self.role_id = role_id  # the role given to users when they want to participate
        self.channel_id = channel_id  # the channel that will be sent data about who is participating


usa_server = Server(1148628177183326378, 1340454432428523560, 1341261059540910211)
msu_server = Server(1349433403132608523, 1349433403132608524, 1349433403673415697)
roma_server = Server(1349433409654620233, 1349433409654620234, 1349433413404459044)
sweden_server = Server(1349433857681784905, 1349433857681784906, 1349433858126516372)
servers = [usa_server, msu_server, roma_server, sweden_server]

# determines what server user is a part of
# returns the server that will be used for its roles and
# WILL NOT WORK PROPERLY IF USER IS A PART OF MULTIPLE SERVERS,
# MOST LIKELY WILL DEFAULT USER TO ENGLISH SERVER
def get_server(servers: list[Server], memeber: discord.Member):
    for server in servers:
        guild = client.get_guild(server.server_id)
        if guild and guild.get_member(memeber.id):  # returns the guild not the server id
            return server

    return None  # returns none to let bot know user is not part of a server

# sets language to better communicate with users
# THIS WILL NOT REMOVE EXISTING INSTANCES OF USERS, WE WILL JUST SEARCH FOR THE LATEST INSTANCE IN GET_LANGUAGE
def set_language(user_id, language):
    try:
        with open("language.txt", "a") as f:  # adds discord id and language selected
            f.write(f"{user_id} {language}\n")
    except Exception as e:
        print(e)


# determines what language to use with a user
def get_language(user_id):
    with open("language.txt", "r") as f:  # finds what language user has selected
        data = f.read()
        found = re.findall(fr'{user_id}.*', data)  # only the last on is important, as its most recent
        if len(found) == 0:  # default to english
            return "None"
        if "Italiano" in found[-1]:  # if a user has selected Italiano in the past
            return "Italiano"
        elif "English" in found[-1]:  # if a user has selected Italian in the past
            return "English"
        else:  # default to english
            return "None"


def get_steam(steam_id):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"

    params = {"key": STEAM, "steamids": steam_id}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        players = data.get("response", {}).get("players", [])

        if players:
            player = players[0]  # Get the first player
            return [player.get("steamid"), player.get("personaname"), player.get("profileurl")]

        else:
            return None

# used for selecting your language for the bot
# noinspection PyUnresolvedReferences
class LanguageSelectView(discord.ui.View):
    def __init__(self, member, server, role):
        super().__init__(timeout=None)
        self.member = member  # Stores the member messaging the bot
        self.server = server  # Stores the member messaging the bot
        self.role = role  # Stores the role that will be given to user

        # fancy displays of user data
        # explains what the experiment is and what participants will do
        self.english_embed = discord.Embed(
            title=f"TO PARTICIPATE IN THE EXPERIMENT YOU WILL NEED TO DO THE FOLLOWING:",
            description=f"**WARNING: HIGHLY RECOMMENDED YOU CREATE A NEW ACCOUNT FOR THIS EXPERIMENT (*SCHOOL EMAIL IS ACCEPTABLE*), THERE ARE CHANCES YOUR ACCOUNT COULD BE BANNED AND GAME REPLAYS WILL BE PUBLIC FOR RESEARCHERS, RESULTS IN OTHER RESEARCHES BEING ABLE TO SEE YOUR ACCOUNT**\n"
                        f"To take part in the experiment you will need to provide the *SteamID of a newly created or spare Steam Account*, The links below will help you [create a new Steam Account](https://store.steampowered.com/join) and [find your SteamID](https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC).\nOnce you have your SteamID, enter your SteamID in the textbox below without adding any spaces or extra characters.\n"
                        f"If your SteamID was valid and confirmed, you will given the **{self.role.name}** role allowing you to participate in the experiment session.",
            color=discord.Color.orange()
        )
        self.italiano_embed = discord.Embed(
            title=f"PER PARTECIPARE ALL’ESPERIMENTO, FAI QUANTO SEGUE:",
            description=f"**ATTENZIONE: LA CREAZIONE DI UN NUOVO ACCOUNT PER QUESTO ESPERIMENTO E’ FORTEMENTE RACCOMANDATA (*LA EMAIL DELLA SCUOLA È ACCETTATA*). E’ POSSIBILE CHE IL TUO ACCOUNT POSSA ESSERE BANNATO E CHE I GAME REPLAY POSSANO ESSERE RESI PUBBLICI PER RICERCHE, CON LA CONSEGUENZA CHE ALTRI RICERCATORI POTREBBERO VEDERE IL TUO ACCOUNT**\n"
                        f"Per prendere parte all’esperimento, dovrai fornire lo *SteamID di un nuovo account o di un account Steam di riserva*. I link di seguito ti aiuteranno a [creare un nuovo account Steam] (https://store.steampowered.com/join) ed a [trovare il tuo SteamID]( https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC).\n Una volta ottenuto il tuo SteamID, inseriscilo nella casella di testo sottostante senza inserire spazi o ulteriori caratteri.\n"
                        f"Se il tuo SteamID è valido e confermato, ti verrà assegnato il ruolo **{self.role.name}** che ti consentirà di partecipare alla sessione dell'esperimento.",
            color=discord.Color.orange()
        )

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.member  # Ensures only the member can interact

    @discord.ui.button(label="English 🇬🇧", style=discord.ButtonStyle.primary)
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You selected **English**!\n", embed=self.english_embed)

        print(f'\n{self.member.name} selected English')
        set_language(self.member.id, "English")  # sets language for future messages for discord user

    @discord.ui.button(label="Italiano 🇮🇹", style=discord.ButtonStyle.primary)
    async def italian_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Hai selezionato **Italiano**!", embed=self.italiano_embed)

        print(f'\n{self.member.name} selected Italiano')
        set_language(self.member.id, "Italiano")  # sets language for future messages for discord user


# used to make sure user put in the correct data
# noinspection PyUnresolvedReferences
class ProfileSelectView(discord.ui.View):
    def __init__(self, member, message, role, channel, server):
        super().__init__(timeout=None)
        self.member = member  # Stores the member messaging the bot
        self.message = message  # Store the message content
        self.role = role  # Stores the role that will be given to user
        self.channel = channel  # Stores then chanel where the data will be sent
        self.server = server  # Stores then server where the data will be sent

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.member  # Ensures only the member can interact

    # once a button is hit, it will send the data and let the server know they are participating
    @discord.ui.button(label="YES", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # lets them know they have been given the role and sets them up to be able to participate
        # checks if the account already exists in the .txt file
        print(f'\n{self.member.name} selected YES')
        if get_language(self.member.id) == "Italiano":
            await interaction.response.send_message(f"Ora puoi partecipare!")

        elif get_language(self.member.id) == "English":
            await interaction.response.send_message(f"you are now able to participate!")

        else:
            view = LanguageSelectView(self.member, self.server, self.role)
            await interaction.response.send_message(f"*select a language* / *seleziona la lingua*", view=view)
            return  # ends if language was not selected

        with open("accounts.txt", "r") as fr:  # checks if SteamID is a duplicate
            accounts = fr.read()
            if re.search(fr'(?<!<@)\b{re.escape(self.message.content)}\b(?!>)', accounts) is not None:
                print(f"steam account already entered")
                if get_language(self.member.id) == "Italiano":
                    await self.member.send(f"Qualcuno è stato già inserito, prova ancora!")
                elif get_language(self.member.id) == "English":
                    await self.member.send(f"someone has already been entered, try again!")
                return  # stops if account already exists

            # continues if no account was found
            # give user their role to partisipate in the event
            await self.member.add_roles(self.role)
            print(f"Assigned role {self.role.name} to {self.member.name}")
            if get_language(self.member.id) == "Italiano":
                await self.member.send(f"Il ruolo **{self.role.name}** è stato assegnato a {self.message.author.mention}!\n Ora puoi partecipare alle sessioni sperimentali!")
            elif get_language(self.member.id) == "English":
                await self.member.send(f"{self.message.author.mention} has been assigned the **{self.role.name}** role!\n You are now able to participate in the experimental sessions!")

            # adds user steam account into the .txt file
            # sends data to account-channel
            print(f"{self.server.name} {self.message.author.mention}: {get_steam(self.message.content)[0]} {get_steam(self.message.content)[1]} {get_steam(self.message.content)[2]}")
            await self.channel.send(f"{self.server.name} {self.message.author.mention}: {get_steam(self.message.content)[0]} {get_steam(self.message.content)[1]} {get_steam(self.message.content)[2]}")  # displays users steam account to a channel.Including discord mention id,steam id,steam name,and steam link
            with open("accounts.txt", "a") as fa:  # adds SteamID to list, making sure there are no duplicat accounts
                fa.write(f"{self.server.name} {self.message.author.mention}: {get_steam(self.message.content)[0]} {get_steam(self.message.content)[1]} {get_steam(self.message.content)[2]}\n")

    # does not add an account to .txt file and ask them to retry
    @discord.ui.button(label="NO", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f'\n{self.member.name} selected NO')
        if get_language(self.member.id) == "Italiano":
            await interaction.response.send_message(f"Se ancora vuoi partecipare, prova di nuovo!")

        elif get_language(self.member.id) == "English":
            await interaction.response.send_message(f"If you still want to participate, try again!")

        else:
            view = LanguageSelectView(self.member, self.message, self.role)
            await interaction.response.send_message(f"*select a language* / *seleziona la lingua*", view=view)


class Client(discord.Client):
    async def on_member_join(self, member):

        # determines what server user is a part of
        user_server = get_server(servers, member)
        if not user_server:
            print(f"\nCould not find server with {member.name}")
            return  # no valid server was found

        server = self.get_guild(user_server.server_id)
        role = server.get_role(user_server.role_id)
        print(f"\n{member.name} joined {server.name}")
        if member:
            if get_language(member.id) == "None":  # only outputs if a user has never selected a language
                # lets user select language
                view = LanguageSelectView(member, server, role)
                await member.send(f"**TO PARTICIPATE IN THE EXPERIMENTAL YOU WILL NEED TO DO THE FOLLOWING:\nPER PARTECIPARE ALL’ESPERIMENTO, FAI QUANTO SEGUE:**")
                await member.send(f"*select a language* / *seleziona la lingua*", view=view)

            else:  # user has already attempted the process before
                # check if member has already sent in a steamID, automatically giving them the participating role
                with open("accounts.txt", "r") as f:  # checks if user has already been mentioned
                    if member.mention in f.read():
                        print(f"{member.name} already provided a SteamID")

                        # outputs and gives a role if user has already provided a steamID
                        if get_language(member.id) == "Italiano":
                            await member.send(f"A {member.mention} è stato assegnato il ruolo **{role.name}** perché ha già fornito uno SteamID.")

                        else:  # defaults to english
                            await member.send(f"{member.mention} has been assigned the **{role.name}** role due to already provided a SteamID.")

                        await member.add_roles(role)  # receives user role to participate

    async def on_message(self, message):

        # determines what server user is a part of
        user_server = get_server(servers, message.author)
        if not user_server:
            print(f"\nCould not find server with {message.author}")
            return  # no valid server was found

        server = self.get_guild(user_server.server_id)
        role = server.get_role(user_server.role_id)
        channel = self.get_channel(user_server.channel_id)
        if message.author == self.user:
            return  # ignore bot's own messages

        print(f'\nMessage from {message.author}: {message.content}')

        # check if message is a DM
        if isinstance(message.channel, discord.DMChannel):
            if server:  # get user from server
                member = server.get_member(message.author.id)
                if member:
                    steam_player = get_steam(message.content)
                    if steam_player is None:  # if it failed to find a user
                        print(f"{member.name} sent an invalid steam account")
                        if get_language(member.id) == "Italiano":
                            await member.send(f"{message.author.mention} ha inviato un account Steam non valido, prova ancora!")
                        elif get_language(member.id) == "English":
                            await member.send(f"{message.author.mention} has sent an invalid Steam account, try again!")
                        else:
                            view = LanguageSelectView(member, message, role)
                            await member.send(f"*select a language* / *seleziona la lingua*", view=view)
                        return  # stops form sending a message to an account channel

                    else:  # if user was found
                        print(f"{member.name} sent a valid steam account")
                        if get_language(member.id) == "Italiano":
                            await member.send(f"{message.author.mention} ha inviato un account Steam valido!")
                        elif get_language(member.id) == "English":
                            await member.send(f"{message.author.mention} has sent a valid Steam account!")
                        else:
                            view = LanguageSelectView(member, server, role)
                            await member.send(f"*select a language* / *seleziona la lingua*", view=view)
                            return  # ends if user does have not selected a language

                        # fancy displays of user data
                        english_embed = discord.Embed(
                            title="Is this your Steam Account?",
                            description=f"**Steam ID:** `{steam_player[0]}`\n"
                                        f"**Username:** `{steam_player[1]}`\n"
                                        f"[**Profile Link**]({steam_player[2]})",
                            color=discord.Color.orange()
                        )
                        italiano_embed = discord.Embed(
                            title="Questo è il tuo Account Steam?",
                            description=f"**Steam ID:** `{steam_player[0]}`\n"
                                        f"**Username:** `{steam_player[1]}`\n"
                                        f"[**Link al profilo**]({steam_player[2]})",
                            color=discord.Color.orange()
                        )

                        print(f"{member.name} was promoted ProfileSelectView")
                        # asks if user put in the correct information
                        view = ProfileSelectView(member, message, role, channel, server)  # ask if this is the correct account
                        if get_language(member.id) == "Italiano":
                            await member.send(embed=italiano_embed, view=view)

                        elif get_language(member.id) == "English":
                            await member.send(embed=english_embed, view=view)

                        else:
                            view = LanguageSelectView(member, server, role)
                            await member.send(f"*select a language* / *seleziona la lingua*", view=view)
                            return  # ends if user does have not selected a language


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # role assignment
intents.dm_messages = True  # DM handling

client = Client(intents=intents)
client.run(DISCORD)
