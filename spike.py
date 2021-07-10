import os
import discord
from discord.ext import commands

TOKEN = ''
join_emote = '\N{White Heavy Check Mark}'
battle_emote = '\N{Crossed Swords}'
leave_emote = '\N{No Entry Sign}'
delete_emote = '\N{Octagonal Sign}'

bot = commands.Bot(case_insensitive=True, command_prefix='!')
active_raids = []
posting_channels = {
        "legendary" : 861773666169520211
    }
hosting_categories = {
        "legendary" : [861773935700213800]
    }

class Raid:
    def __init__(self, boss, host, time_remaining):
        self.boss = boss
        self.host = host
        self.time_reminaing = None
        
        self.participants_list = []
        self.geotag = None
        self.weather = None
        self.max_invites = None

        self.annoucement = None
        self.channel = None
        self.message = None

    def get_posting_embed(self):
        embed = discord.Embed(title = f'{self.boss} Raid', description=f'Host: {self.host.mention}')
        embed.add_field(name = 'Number of Participants', value = len(self.participants_list))
        if self.weather:
            embed.add_field(name='Weather', value = self.weather)
        if self.geotag:
            embed.add_field(name='Geotag', value = self.geotag)
        if self.max_invites:
            embed.add_field(name='Available Spots', value = int(self.max_invites)-len(self.participants_list))
        embed.set_footer(text=f'press {join_emote} to join this raid')
        return embed

    def get_embed(self):
        embed = discord.Embed(title = f'{self.boss} Raid', description=f'Host: {self.host.mention}')
        if self.participants_list:
            embed.add_field(name = 'Participants', value = '\n'.join([p.mention for p in self.participants_list]))
        if self.weather:
            embed.add_field(name='Weather', value = self.weather)
        if self.geotag:
            embed.add_field(name='Geotag', value = self.geotag)
        if self.max_invites:
            embed.add_field(name='Max Participants', value = self.max_invites)
        embed.set_footer(text=f'press {leave_emote} to leave this raid')
        return embed
    
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name = 'raid')
async def raid(ctx, raid_boss, time_remaining = None):
    if ctx.channel.id == 861773666169520211: #legendary category
        new_raid = Raid(raid_boss, ctx.message.author, time_remaining)
        active_raids.append(new_raid)
        await ctx.message.delete()
        new_raid.announcement = await ctx.send(embed=new_raid.get_posting_embed())
        await new_raid.announcement.add_reaction(join_emote)
        category = discord.utils.get(ctx.guild.categories, id=hosting_categories['legendary'][-1])
        if len(category.channels) >= 50:
            category = await ctx.guild.create_category(f"legendary raids {len(hosting_categories['legendary'] + 1)}")
            hosting_categories['legendary'].append(category.id)
        new_raid.channel = await ctx.guild.create_text_channel(f'{new_raid.boss}-{new_raid.host.nick or new_raid.host.name}',
                                                           category=category)
        new_raid.message = await new_raid.channel.send(embed=new_raid.get_embed())
        await new_raid.message.add_reaction(leave_emote)
        await new_raid.message.add_reaction(battle_emote)

@bot.command(name='finish')
async def finish_raid(ctx):
    await ctx.message.delete()
    if ctx.channel.id == 861773666169520211:
        return
    raid = next(x for x in active_raids if x.channel == ctx.channel)
    if ctx.message.author != raid.host:
        return
    active_raids.remove(raid)
    await raid.announcement.delete()
    await raid.channel.delete()

@bot.command(name='remove')
async def remove_mia_raider(ctx, user_mention):
    await ctx.message.delete()
    print(user_mention)
    if ctx.channel.id == 861773666169520211:
        return
    raid = next(x for x in active_raids if x.channel == ctx.channel)
    print(raid.participants_list)
    if ctx.message.author != raid.host:
        return
    absentee = next(r for r in raid.participants_list if r.mention == user_mention)
    raid.participants_list.remove(absentee)
    await raid.message.edit(embed=raid.get_embed())
    await raid.announcement.edit(embed=raid.get_posting_embed())

    dm = await absentee.create_dm()
    await dm.send(f'You have been removed from the {raid.boss} raid hosted by {new_raid.host.nick or new_raid.host.name}')

@bot.command(name='weather')
async def set_weather(ctx, *weather):
    await ctx.message.delete()
    if ctx.channel.id == 861773666169520211:
        return
    raid = next(x for x in active_raids if x.channel == ctx.channel)
    if ctx.message.author != raid.host:
        return
    raid.weather = ' '.join(weather)
    await raid.message.edit(embed=raid.get_embed())
    await raid.announcement.edit(embed=raid.get_posting_embed())

@bot.command(name='geotag')
async def set_max_invites(ctx, *geotag):
    await ctx.message.delete()
    if ctx.channel.id == 861773666169520211:
        return
    raid = next(x for x in active_raids if x.channel == ctx.channel)
    if ctx.message.author != raid.host:
        return
    raid.geotag = ' '.join(geotag)
    await raid.message.edit(embed=raid.get_embed())
    await raid.announcement.edit(embed=raid.get_posting_embed())

@bot.command(name='invites')
async def set_weather(ctx, max_invites):
    await ctx.message.delete()
    if ctx.channel.id == 861773666169520211:
        return
    raid = next(x for x in active_raids if x.channel == ctx.channel)
    if ctx.message.author != raid.host:
        return
    raid.max_invites = ' '.join(max_invites)
    await raid.message.edit(embed=raid.get_embed())
    await raid.announcement.edit(embed=raid.get_posting_embed())

@bot.command(name='time')
async def set_time_remaining(ctx, time_remaining):
    await ctx.message.delete()
    if ctx.channel.id == 861773666169520211:
        return
    raid = next(x for x in active_raids if x.channel == ctx.channel)
    if ctx.message.author != raid.host:
        return
    raid.time_remaining = ' '.join(time_remaining)
    await raid.message.edit(embed=raid.get_embed())
    await raid.announcement.edit(embed=raid.get_posting_embed())

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    elif reaction.message.author != bot.user:
        return
    elif len(reaction.message.embeds) < 1:
        return
    else:
        await reaction.remove(user)
        raid = next(x for x in active_raids if x.message == reaction.message or x.announcement == reaction.message)
        dirty = False
        if reaction.emoji == join_emote:
            if user == raid.host:
                return
            raid.participants_list.append(user)
            dirty = True
        elif reaction.emoji == leave_emote:
            if user == raid.host:
                return
            if user in raid.participants_list:
                raid.participants_list.remove(user)
                dirty = True
        elif reaction.emoji == battle_emote:
            if user != raid.host:
                return
            if not raid.participants_list:
                return
            raiders = raid.participants_list[:int(raid.max_invites) or 5]
            print(raiders)
        if dirty:
            await raid.message.edit(embed=raid.get_embed())
            await raid.announcement.edit(embed=raid.get_posting_embed())
bot.run(TOKEN)


        
