import os
import discord
from discord.ext import commands

TOKEN = ''
join_emote = '\N{White Heavy Check Mark}'
battle_emote = '\N{Crossed Swords}'
leave_emote = '\N{No Entry Sign}'

bot = commands.Bot(case_insensitive=True, command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='raid')
async def raid(ctx, *args):
    embed = None
    if len(args) > 1:
        embed=discord.Embed(title=f'{" ".join(args[:-1])} Raid', description=f'Time Remaining: {args[-1]}')
    else:
        embed=discord.Embed(title=f'{args[0]} Raid')
        
    embed.add_field(name='Host', value=f'{ctx.message.author.mention}', inline=False)
    embed.add_field(name='Participants', value='none', inline=False)
    embed.set_footer(text=f'{join_emote} to join. {leave_emote} to leave.\nHost: {battle_emote} to ping participants for raid start')

    message = await ctx.send(embed = embed)

    await message.add_reaction(join_emote)
    await message.add_reaction(battle_emote)
    await message.add_reaction(leave_emote)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    elif reaction.message.author != bot.user:
        return
    elif len(reaction.message.embeds) < 1:
        return
    else:
        embed = reaction.message.embeds[0]
        host = embed.fields[0].value
        participants_list = embed.fields[1].value.split()
        dirty = false

        await reaction.remove(user)

        if reaction.emoji == join_emote:
            if user.mention == host:
                return
            elif user.mention in participants_list:
                return
            else:
                if 'none' in participants_list:
                    participants_list.remove('none')
                participants_list.append(user.mention)
                dirty = true
        elif reaction.emoji == battle_emote:
            if user.mention != host:
                return
            elif 'none' in participants_list:
                return
            else:
                raiders = participants_list[:5]
                participants_list = participants_list[5:]
                await reaction.message.channel.send(f'{" ".join(raiders)}: invites from {host} for a {embed.title} will be sent shortly')
                if len(participants_list) < 1:
                    participants_list.append('none')
                dirty = true
        elif reaction.emoji == leave_emote:
            if user.mention == host:
                return
            elif user.mention not in participants_list:
                return
            else:
                participants_list.remove(user.mention)
                if len(participants_list) == 0:
                    participants_list.append('none')
                dirt = true
        if dirty:
            embed.set_field_at(1, name='Participants', value='\n'.join(participants_list), inline=False)
            await reaction.message.edit(embed = embed)
        
bot.run(TOKEN)
