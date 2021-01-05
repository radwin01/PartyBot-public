import discord
import os
import operator
import math
import random
import asyncio
import pymongo
from discord.ext import commands


bot = commands.Bot(command_prefix="-")
myclient = pymongo.MongoClient("sorry cant give you this either :p")
mydb = myclient.test
mycol = mydb["discord_users"]


@bot.event
async def on_ready():
    print("Who is ready to party?")
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count += 1
    print("I am currently in " + str(guild_count) + " server(s)")


@bot.command(brief="Register your name to be apart of the leaderboard!")
async def reg(ctx):
    author_name = ctx.author.name
    author_id = ctx.author.id
    server_id = ctx.guild.name
    if (mycol.count_documents({"disc_id": author_id, "server": server_id}) == 0):
        mycol.insert_one({"disc_id": author_id, "name": author_name,
                          "server": server_id, "score": 0})
        await ctx.channel.send("You are successfully registered! Play some games to earn points!")
    else:
        await ctx.channel.send("??? You have already been registered!")


@bot.command(brief="Rock paper scissors. 'R' = rock, 'P' = paper, 'S' = scissors")
async def rps(ctx, arg):
    options = {'R': 'S', 'P': 'R', 'S': 'P'}
    options_full = ["Rock", "Paper", "Scissors"]
    pick = random.choice(list(options))
    pick_idx = list(options).index(pick)
    if arg not in list(options):
        await ctx.channel.send("invalid option!")
    else:
        arg_idx = list(options).index(arg)
        if (options.get(pick) == arg):
            mycol.find_one_and_update({"disc_id": ctx.author.id, "server": ctx.guild.name}, {
                                      "$inc": {"score": -10}})
            await ctx.channel.send("I picked " + options_full[pick_idx] + ", while you picked " + options_full[arg_idx] + ". " + options_full[pick_idx] + " beats " + options_full[arg_idx] + ": L for you! You lose 10 points, GGWP!")
        elif (pick == arg):
            await ctx.channel.send("I picked " + options_full[pick_idx] + ", while you picked " + options_full[arg_idx] + ": It's a tie! No points lost/won.")
        else:
            mycol.find_one_and_update({"disc_id": ctx.author.id, "server": ctx.guild.name}, {
                                      "$inc": {"score": 20}})
            await ctx.channel.send("I picked " + options_full[pick_idx] + ", while you picked " + options_full[arg_idx] + ". " + options_full[arg_idx] + " beats " + options_full[pick_idx] + ": W for you! You win 20 points, GJ!")


@bot.command(brief="Find who is closest to a randomized integer (1-100 inclusive)")
async def rng(ctx, arg):
    number = random.randint(1, 100)
    pick = random.randint(1, 100)
    if (not(arg.isdigit()) or int(arg) < 1 or int(arg) > 100):
        await ctx.channel.send("ummmm wat... Please enter an integer between 1 to 100!")
    else:
        if (abs(number - pick) < abs(number - int(arg))):
            mycol.find_one_and_update({"disc_id": ctx.author.id, "server": ctx.guild.name}, {
                                      "$inc": {"score": -10}})
            await ctx.channel.send("The number was " + str(number) + ". I picked " + str(pick) + ", while you picked " + str(arg) + ": I was closer, so L for you! You lose 10 points, GGWP!")
        elif (abs(number - pick) == abs(number - int(arg))):
            await ctx.channel.send("The number was " + str(number) + ". I picked " + str(pick) + ", while you picked " + str(arg) + ": It's a tie! No points lost/won.")
        else:
            mycol.find_one_and_update({"disc_id": ctx.author.id, "server": ctx.guild.name}, {
                                      "$inc": {"score": 15}})
            await ctx.channel.send("The number was " + str(number) + ". I picked " + str(pick) + ", while you picked " + str(arg) + ": You were closer, so W for you! You win 15 points, GJ!")


# helper
def endcond(total: int) -> bool:
	return (total == 19 or total == 18 or total == 17)

@bot.event
async def on_message(message):
    if message.content.startswith('-21'):
        legal = [1, 2, 3]
        channel = message.channel
        # print(str(message.author.id) + ", " + str(message.guild))
        intro = "Let's play a game of 21! You and I will take turns picking either 1, 2, or 3.\nIf you are the person to land on 21 OR you take too long to reply (over 7 seconds), you lose! Let's go:"
        await channel.send(intro)
        pick = random.randint(1, 2) # decides who goes first: 1 for PB, 2 for user
        total = 0
        end = 0
        if (pick == 1):
            await channel.send("I will start first.")
            while (total < 20):
                if (not endcond(total)):
                    comp_choice = random.randint(1, 3)
                    total += comp_choice
                    await channel.send("I pick " + str(comp_choice) + ". The total is currently at " + str(total))
                    await channel.send("Your turn! Pick either a 1, 2, or 3.")
                    try:
                        user_choice = await bot.wait_for('message', check=lambda message: message.content.isdigit() and int(message.content) in legal
                                                 and message.channel == channel, timeout=7)
                        if (user_choice):
                            total += int(user_choice.content)
                            await channel.send("You picked " + str(user_choice.content) + ". The total is currently at " + str(total))
                            if (total >= 20): break
                        else:
                            break
                    except asyncio.TimeoutError:
                        mycol.find_one_and_update(
                            {"disc_id": message.author.id, "server": str(message.guild)}, {"$inc": {"score": -50}})
                        await channel.send("You scrub! Since you took too long to answer, I must cancel this game.\n" +
                                    "You lose 50 points for wasting my time!")
                        break
                else:
                    comp_choice = 21 - total - 1
                    total += comp_choice
                    end = 1
                    mycol.find_one_and_update(
                        {"disc_id": message.author.id, "server": str(message.guild)}, {"$inc": {"score": -50}})
                    await channel.send("I pick " + str(comp_choice) + ".\nxd, u lose noob! goodbye to 50 of your points!")
        else:
            await channel.send("You will start first.")
            while (total < 20):
                await channel.send("Your turn! Pick either a 1, 2, or 3.")
                try:
                    user_choice = await bot.wait_for('message', check=lambda message: message.content.isdigit() and int(message.content) in legal
                                                 and message.channel == channel, timeout=7)
                    if (user_choice):
                        total += int(user_choice.content)
                        await channel.send("You picked " + str(user_choice.content) + ". The total is currently at " + str(total))
                        if (total >= 20): break
                    else:
                        break
                except asyncio.TimeoutError:
                    mycol.find_one_and_update(
                        {"disc_id": message.author.id, "server": str(message.guild)}, {"$inc": {"score": -50}})
                    await channel.send("You scrub! Since you took too long to answer, I must cancel this game.\n" +
                                   "You lose 50 points for wasting my time!")
                    break
                if (not endcond(total)):
                    comp_choice = random.randint(1, 3)
                    total += comp_choice
                    await channel.send("I pick " + str(comp_choice) + ". The total is currently at " + str(total))
                elif (endcond):
                    comp_choice = 21 - total - 1
                    total += comp_choice 
                    end = 1
                    mycol.find_one_and_update(
                        {"disc_id": message.author.id, "server": str(message.guild)}, {"$inc": {"score": -50}})
                    await channel.send("I pick " + str(comp_choice) + ".\nxd, u lose noob! goodbye to 50 of your points!")

        if (total == 20 and end != 1): 
            mycol.find_one_and_update(
               {"disc_id": message.author.id, "server": str(message.guild)}, {"$inc": {"score": 100}})
            await channel.send("sadge... I pick 1.\nYou won! Take ya (100) points and go 😔")
        elif (total > 20 and end != 1):
            mycol.find_one_and_update(
               {"disc_id": message.author.id, "server": str(message.guild)}, {"$inc": {"score": -50}})
            await channel.send("Xd, did you just kill yourself? lol ok")
    await bot.process_commands(message)


@bot.command(brief="Displays the current leaderboard")
async def ldbd(ctx):
    server_users = mycol.find({"server": ctx.guild.name})
    ret = ">>> Here are the current stats: \n"
    user_profiles = {user.get("name"): user.get("score")
                     for user in server_users}
    sorted_users = sorted(user_profiles.items(),
                          key=operator.itemgetter(1), reverse=True)
    # print(sorted_users)
    for i in range(len(sorted_users)):
        ret += sorted_users[i][0] + "    ---------    " + \
            str(sorted_users[i][1]) + "\n"
    await ctx.channel.send(ret)


bot.run('sowwies, no token here :p')
