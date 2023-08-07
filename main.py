import json
import discord
import re

from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from discord.ext import commands


# get discord token
with open('token.json') as json_file:
    discoData = json.load(json_file)

discordToken = discoData['discord_Token']


# get watson token
with open('watsonTokens.json') as json_file2:
    watsonData = json.load(json_file2)

authenticator = IAMAuthenticator(watsonData['apikey'])
tone_analyzer = ToneAnalyzerV3(
    version='2020-03-06',
    authenticator=authenticator
)

# get crab matrix
with open('crabMatrix.json') as json_file3:
    matrixData = json.load(json_file3)

tone_analyzer.set_service_url(watsonData['url'])

# start the bot
bot = commands.Bot(command_prefix='!')

# set of crab emojis
crab_list = re.compile("\U0001F980|:crab:|<a:crabrave:818140071681064960>|<a:CrabRave:817413906237751333>")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    emoji = discord.utils.get(bot.emojis)
    print(emoji)


@bot.event
async def on_reaction_add(reaction, user):
    print('{0} {1}'.format(reaction.message.id, user.id))

    # ignore self
    if user == bot.user:
        return

    if reaction.emoji == '\U0001F980':
        await reaction.message.add_reaction('\U0001F980')


@bot.event
async def on_message(message):

    # ignore self
    if message.author == bot.user:
        return

    if message.content[0] != '!':
        if message.content.find('crab') != -1 or message.content.find('Crab') != -1:
            # gifsend = discord.Embed()
            # gifsend.set_image(url='https://media1.tenor.com/images/7d7a56efbd12e0485f62bcfe986c08b4/tenor.gif')
            # await message.channel.send('I HAVE BEEN SUMMONED', embed=gifsend)
            await message.add_reaction('\U0001F980')



        crab_search = crab_list.search(message.content)
        if crab_search is not None:
            await message.channel.send('<a:crabrave:818140071681064960>')

    else:
        await bot.process_commands(message)


@bot.command(name='crabrave', help='What it says on the tin', aliases=['cr', 'cangrejo'])
async def crab_rave(ctx):
    gifsend = discord.Embed()
    gifsend.set_image(url='https://upload.wikimedia.org/wikipedia/en/7/70/Crab_Rave_Noiseporn_gif.gif?1615132198601')
    await ctx.send("CRAB TIME", embed=gifsend)

@bot.command(name='crabdance', help='What it says on the tin', aliases=['cd'])
async def crab_dance(ctx):
    gifsend = discord.Embed()
    gifsend.set_image(url='https://media1.tenor.com/images/7d7a56efbd12e0485f62bcfe986c08b4/tenor.gif')
    await ctx.send('I will dance the dance of my people.', embed=gifsend)

@bot.command(name='crabknife', help='What it says on the tin', aliases=['ck'])
async def crab_knife(ctx):
    gifsend = discord.Embed()
    gifsend.set_image(url='https://media.giphy.com/media/uA8WItRYSRkfm/giphy.gif')
    await ctx.send('Mess with the crabbo, get the stabbo', embed=gifsend)

@bot.command(name='crabwisdom', help='Access in the infinite wisdom of the Crab Cloud', aliases=['cw'])
async def crab_wisdom(ctx):
    text = ctx.message.content.replace('!cw ', '')
    print(text)

    tone_analysis = tone_analyzer.tone(
        {'text': text},
        content_type='application/json',
        sentences=False
    ).get_result()
    print(json.dumps(tone_analysis, indent=2))

    doc_tone = tone_analysis['document_tone']['tones']
    primarytTone = [None, 0.0]
    secondaryTone = [None, 0.0]

    for tone in doc_tone:
        if tone['score'] > primarytTone[1]:
            # cpy > secondary
            secondaryTone[1] = primarytTone[1]
            secondaryTone[0] = primarytTone[0]
            # new primary
            primarytTone[1] = tone['score']
            primarytTone[0] = tone['tone_id']
        elif tone['score'] > secondaryTone[1]:
            secondaryTone[1] = tone['score']
            secondaryTone[0] = tone['tone_id']

    if secondaryTone[0] is None:
        secondaryTone[1] = primarytTone[1]
        secondaryTone[0] = primarytTone[0]

    print(primarytTone)
    print(secondaryTone)

    # if url.find('tenor') != -1:
    #     gifsend = discord.Embed()
    #     gifsend.set_image(url=url)
    #     await ctx.send(f"I impart the wisdom of the Crab of {primarytTone[0]} {secondaryTone[0]}", embed=gifsend)
    # else:
    if primarytTone[0] is not None:
        url = matrixData[primarytTone[0]][secondaryTone[0]]
        print(url)
        await ctx.send(f"I impart the wisdom of the Crab of {primarytTone[0]} {secondaryTone[0]} {url}")
    else:
        gifsend = discord.Embed()
        gifsend.set_image(url="https://aquariumbreeder.com/wp-content/uploads/2019/08/logo-Red-Clawed-Crabs-.jpg")
        await ctx.send(f"Tell me more so that I may answer your statement more wisely.", embed=gifsend)

bot.run(discordToken)
