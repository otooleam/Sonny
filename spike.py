import os
import discord
from discord.ext import commands

TOKEN = ''
join_emote = '\N{White Heavy Check Mark}'
battle_emote = '\N{Crossed Swords}'
leave_emote = '\N{No Entry Sign}'
delete_emote = '\N{Octagonal Sign}'

bot = commands.Bot(case_insensitive=True, command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name = 'raid')
async def raid(ctx, *, args: str):
    embed = None
    if ' ' in args:
        boss = args.rsplit(' ', 1)[0]
        time = args.rsplit(' ', 1)[1]
        if time.isnumeric() and 0<int(time)<=45:
            embed = discord.Embed(title = f'{boss} Raid', description = f'Time Remaining: {time}')
        else:
            await ctx.send('Invalid time!')
            return
    else:
        embed = discord.Embed(title = f'{args} Raid')

    embed.add_field(name = 'Host', value = f'{ctx.message.author.mention}', inline = False)
    embed.add_field(name = 'Participants', value = 'none', inline = False)
    embed.set_footer(
        text = f'{join_emote} to join. {leave_emote} to leave.\nHost: {battle_emote} to ping participants for raid start. {delete_emote} when the raid is done.')

    message = await ctx.send(embed = embed)

    await message.add_reaction(join_emote)
    await message.add_reaction(leave_emote)
    await message.add_reaction(battle_emote)
    await message.add_reaction(delete_emote)

@bot.command(name = 'raidnew')
async def raidnew(ctx, boss: str, time = -1, spaces = -1):
    embed = None
    if boss == "":  # Prevents empty boss name by doing $raid ""
        await ctx.send('Please make sure you enter a raid boss name!')
        return
    if time == -1:  # Embed with name only when time not given
        embed = discord.Embed(title = f'{boss} Raid')
    elif 0 < int(time) <= 45:
        embed = discord.Embed(title = f'{boss} Raid', description = f'Time Remaining: {time}')
    else:
        await ctx.send('Invalid time!')  # Answer with error if time is not between 0 and 45
        return
    embed.add_field(name = 'Host', value = f'{ctx.message.author.mention}', inline = False)
    embed.add_field(name = 'Participants', value = 'none', inline = False)
    if spaces != -1:
        if 0 < int(spaces):
            embed.add_field(name = 'Spaces remaining', value = f'{spaces}', inline = False)
        else:
            await ctx.send('Invalid input for spaces!')  # Answer with error if spaces is less than 1
            return  # Note: user can enter -1 as input, but it works the same as not entering anything... same for time
    embed.set_footer(
        text = f'{join_emote} to join. {leave_emote} to leave.\nHost: {battle_emote} to ping participants for raid '
               f'start. {delete_emote} when the raid is done.')

    message = await ctx.send(embed = embed)

    await message.add_reaction(join_emote)
    await message.add_reaction(leave_emote)
    await message.add_reaction(battle_emote)
    await message.add_reaction(delete_emote)


@raidnew.error  # Handles input errors
async def raidnew_error(ctx, error):
    if isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.ExpectedClosingQuoteError):
        await ctx.send("Problem interpreting input: \nUnexpected number or placement of quotation marks. Please read "
                       "usage instructions and try again!")
    elif isinstance(error, commands.BadArgument) or isinstance(error, commands.TooManyArguments) or \
            isinstance(error, commands.ArgumentParsingError) or isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Problem interpreting input: \nInvalid number or value for arguments. Please read usage "
                       "instructions and try again!")
    else:
        await ctx.send(f"Unexpected error! Please read usage instructions and try again or contact a Lead+. \nDetails: "
                       f"{error}")
    print(f'Command error: {error}')

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
        spaces = int(embed.fields[2].value) if len(embed.fields) == 3 else -1  # Only set value if field exists
        dirty = False

        await reaction.remove(user)

        if reaction.emoji == join_emote:
            if user.mention == host:
                return
            elif user.mention in participants_list:
                return
            elif spaces == 0:
                return
            else:
                if 'none' in participants_list:
                    participants_list.remove('none')
                participants_list.append(user.mention)
                if spaces != -1:
                    spaces -= 1  # Decrease number of available spaces when user joins
                dirty = True
        elif reaction.emoji == battle_emote:
            if user.mention != host:
                return
            elif 'none' in participants_list:
                return
            else:
                raiders = participants_list[:5]
                participants_list = participants_list[5:]
                await reaction.message.channel.send(
                    f'{" ".join(raiders)}: invites from {host} for a {embed.title} will be sent shortly')
                if len(participants_list) < 1:
                    participants_list.append('none')
                dirty = True
        elif reaction.emoji == leave_emote:
            if user.mention == host:
                return
            elif user.mention not in participants_list:
                return
            else:
                participants_list.remove(user.mention)
                if len(participants_list) == 0:
                    participants_list.append('none')
                if spaces != -1:
                    spaces += 1  # Increase number of available spaces when user leaves
                dirty = True
        elif reaction.emoji == delete_emote:
            if user.mention != host:
                return
            await reaction.message.delete()
        if dirty:
            embed.set_field_at(1, name = 'Participants', value = '\n'.join(participants_list), inline = False)
            if spaces != -1:
                embed.set_field_at(2, name = 'Spaces remaining', value = f'{spaces}')
            await reaction.message.edit(embed = embed)  # Update fields
        
bot.run(TOKEN)
