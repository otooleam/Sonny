import os
import discord
from discord.ext import commands

TOKEN = ''
join_emote = '\N{White Heavy Check Mark}'
battle_emote = '\N{Crossed Swords}'

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='raid')
async def raid(ctx, raid_boss, time_remaining):
    print('raid command recieved')
    
    embed=discord.Embed(title=f'{raid_boss} Raid', description=f'Time Remaining: {time_remaining}')
    embed.add_field(name='Host', value=f'{ctx.message.author.nick}', inline=False)

    message = await ctx.send(embed = embed)

    await message.add_reaction(join_emote)
    await message.add_reaction(battle_emote)

@bot.event
async def on_reaction_add(reaction, user):
    if (user == bot.user):
        return
    elif reaction.emoji == join_emote:
        embed = reaction.message.embeds[0]
        
        if any(field.name == 'Participants' for field in embed.fields):
            embed.set_field_at(1, 'Participants', embed.fields[1].value += '\n{user.nick}', False)
        else:
            embed.add_field(name='Participants', value=f'{user.nick}', inline=False)
        
        await reaction.message.edit(embed = embed)
    elif reaction.emoji == battle_emote:
        embed = reaction.message.embeds[0]
        
        await reaction.message.edit(embed = embed)

bot.run(TOKEN)
