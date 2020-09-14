import discord
from discord.ext import commands
import pymongo
import os
from pymongo import MongoClient

#passw = os.environ["passw"]
passw 
cluster = MongoClient(passw)
db = cluster.db
col = db.collection

bot = commands.Bot(command_prefix = "/",help_command = None)


@bot.event
async def on_ready():
  print("Running")
  
  
  
@bot.event
async def on_guild_join(guild):
  col.insert_one({"_id":guild.id})



@bot.event
async def on_guild_remove(guild):
  col.delete_one({"_id":guild.id})

async def db(ctx):
  x = col.find_one({"_id":ctx.guild.id})
  if x == None:
    col.insert_one({"_id":ctx.guild.id})
    x = col.find_one({"_id":ctx.guild.id})
  return x


@bot.command()
@commands.has_permissions(administrator = True)
async def setup_applications(ctx, channel : discord.TextChannel):
  x = await db(ctx)
  col.update_one({"_id":ctx.guild.id},{"$set":{"q":[]}})
  col.update_one({"_id":ctx.guild.id},{"$set":{"qchannel":channel.id}})
  await ctx.send("Applications are set up , you can start adding questions now!")



@bot.command()
@commands.has_permissions(administrator = True)
async def addq(ctx , * , q):
  x = await db(ctx)
  try:
    x["q"]
  except:
    return
  col.update_one({"_id":ctx.guild.id},{"$push":{"q":q}})
  await ctx.send("Question was added!")



@bot.command()
@commands.has_permissions(administrator = True)
async def q(ctx):
  x = await db(ctx)
  try:
    x["q"]
  except:
    return
  q = discord.Embed(title = "Application Questions" , color = discord.Color.blue())
  n = 0
  for question in x["q"]:
    n += 1
    q.add_field(name = f"Question {n}",value = question)
  await ctx.send(embed = q)



@bot.command()
@commands.has_permissions(administrator = True)
async def qpop(ctx , num:int):
  x = await db(ctx)
  try:
    x["q"]
  except:
    return
  num -= 1
  x["q"].pop(num)
  col.update_one({"_id":ctx.guild.id} , {"$set":x})
  await ctx.send("Question was removed!")



@bot.command()
async def set_applications_channel(ctx , channel : discord.TextChannel):
  x = await db(ctx)
  col.update_one({"_id":ctx.guild.id},{"$set":{"qchannel":channel.id}})
  await ctx.send(f"Applications channel was changed to {channel}")
  


@bot.command(name = "apply")
async def _apply(ctx):
  x = await db(ctx)
  try:
    x["q"]
    if not x["q"]:
      return
  except:
    return
  n = 0
  answer = discord.Embed(title = f"{ctx.author}\'s Application", color = discord.Color.blue())
  def check(m):
    return m.author == ctx.author and m.guild is None
  for question in x["q"]:
    n += 1
    q = discord.Embed(color = discord.Color.blue())
    q.add_field(name=f"Question {n}",value = question)
    await ctx.author.send(embed = q)
    try:
      msg = await bot.wait_for('message',timeout = 600 , check=check)
      msg = msg.content
      
    except:
      msg = "DNF the message!"
      await ctx.send("Too long! Next Question!")
    answer.add_field(name = question , value = msg)
  answer.set_footer(text = f"{ctx.author}\'s ID : {ctx.author.id}")
  channel = bot.get_channel(x["qchannel"])
  try:
    await channel.send(embed = answer)
    await ctx.author.send("Application was sent!")
  except:
    await ctx.author.send("Application wasnt sent, please contact staff! If they cant fix it tell them to ask in Support Server!")



@bot.command()
@commands.has_permissions(administrator = True)
async def accept(ctx , member : discord.Member):
  await member.send("Your application was Accepted!")
  await ctx.send("DM was sent!")



@bot.command()
@commands.has_permissions(administrator = True)
async def deny(ctx , member : discord.Member):
  await member.send("Your application was Denied!")
  await ctx.send("DM was sent!")



@bot.command()
@commands.has_permissions(administrator=True)
async def set_counting_channel(ctx , channel : discord.TextChannel):
  x = await db(ctx)
  col.update_one({"_id":ctx.guild.id},{"$set":{"counting":channel.id}})
  await ctx.send(f"Counting Channel set to {channel}")
  await channel.send("0")


@bot.event
async def on_message(message):
  await bot.process_commands(message)
  if message.author.bot:
    return
  x = col.find_one({"_id":message.guild.id})
  c = False
  try:
    x["counting"]
    c = True
  except:
    pass
  if c:
    if message.channel.id == x["counting"]:
      if message.author.bot:
        return
      async for last_msg in message.channel.history(limit=2):
        msg = last_msg.content
      try:
        msg = int(msg) + 1
      except:
        await message.delete()
    
        
      m = last_msg.author
      if message.content == str(msg):
        if message.author == m:
          try:
            await message.author.send('You cant count twice in a row!')
          except:
            pass
          
          await message.delete()
        else:
          return
      else:
        await message.delete()
  s = False
  try:
    x["suggestions"]
    s = True
  except:
    pass
  if s:
    if message.channel.id == x["suggestions"]:
      async for last_msg in message.channel.history(limit=2):
        last_msg
  
      suggestion = discord.Embed(color = discord.Color.blue())
      suggestion.set_author(name = message.author , icon_url= message.author.avatar_url_as(static_format='webp', size=1024))
      suggestion.add_field(name = f"Suggestion {x['suggestionsn']}",value=message.content)
      suggestion.set_footer(text = f"User\'s ID : {message.author.id}")
      msg0 = await message.channel.send(embed = suggestion)
      await msg0.add_reaction("🟢")
      await msg0.add_reaction("🔴")
      x["suggestionsn"] += 1
      col.update_one({"_id":message.guild.id},{"$set":x})
      await message.delete()
      channel = bot.get_channel(x["suggestions"])
      try:
        await last_msg.delete()
        
        await channel.send(last_msg.content)
      except:
        await channel.send("To suggest just type your suggestion!\n(Bot will automatically turn it into embed!)")



@bot.command()
@commands.has_permissions(administrator=True)
async def set_suggestions_channel(ctx , channel : discord.TextChannel):
  x = await db(ctx)
  col.update_one({"_id":ctx.guild.id},{"$set":{"suggestions":channel.id}})
  col.update_one({"_id":ctx.guild.id},{"$set":{"suggestionsn":1}})
  await channel.send("To suggest just type your suggestion!\n(Bot will automatically turn it into embed!)")
  await ctx.send(f"Suggestions were set up , start suggesting in `{channel}`")



@bot.command()
@commands.has_permissions(administrator=True)
async def set_ticket_category(ctx , tid : int):
  x = await db(ctx)
  col.update_one({"_id":ctx.guild.id},{"$set":{"tcategory":tid}})
  await ctx.send("Ticket category was set!")



@bot.command()
@commands.has_permissions(administrator=True)
async def set_ticket_message(ctx ,* ,msg):
  x = await db(ctx)
  col.update_one({"_id":ctx.guild.id},{"$set":{"tmsg":msg}})
  await ctx.send("Ticket message was set up!")



@bot.command()
@commands.has_permissions(administrator=True)
async def send_ticket(ctx):
  x = await db(ctx)
  try:
    x["tmsg"]
    x["tcategory"]
  except:
    await ctx.send("You didnt set up tickets yet!")
    return
  ticket = discord.Embed(color = discord.Color.blue())
  ticket.add_field(name = "Tickets",value = x["tmsg"])
  msg = await ctx.send(embed = ticket)
  await msg.add_reaction("📁")
  col.update_one({"_id":ctx.guild.id},{"$set":{"tid":msg.id}})



@bot.event
async def on_raw_reaction_add(payload):
  x = col.find_one({"_id":payload.guild_id})
  guild = bot.get_guild(payload.guild_id)
  channel_id = payload.channel_id
  member = guild.get_member(payload.user_id)
  if member.bot:
    return
  try:
    x["tid"]
  except:
    return
  if payload.message_id == x["tid"]:
    category = bot.get_channel(x["tcategory"])
    
    overwrites = {
    guild.default_role: discord.PermissionOverwrite(read_messages=False),
    member: discord.PermissionOverwrite(read_messages=True)
}

    await guild.create_text_channel(name = f"{member}\'s Ticket" ,overwrites = overwrites, category = category)
    channel = bot.get_channel(channel_id)
    msg = await channel.fetch_message(x["tid"])
    await msg.remove_reaction(member=member, emoji = payload.emoji)



@bot.command()
async def c(ctx):
  x = await db(ctx)
  try:
    x["tid"]
  except:
    return
  if ctx.channel.category_id == x["tcategory"]:
    def check(m):
      return m.channel == ctx.channel
    await ctx.send('Type anything in next 10 secs to cancel!')
    try:
      await bot.wait_for('message' , timeout = 10.0 , check = check)
    except:
      await ctx.channel.delete()



@bot.command(name = "help")
async def _help(ctx , arg=None):
  if arg is None:
    e = discord.Embed(title = "Help" , color = discord.Color.blue())
    e.add_field(name = "Applications",value = "`/help applications`")
    e.add_field(name = "Counting",value = "`/help counting`")
    e.add_field(name = "Suggestions",value = "`/help suggestions`")
    e.add_field(name = "Tickets",value = "`/help tickets`")
    e.add_field(name = "Note",value = "All setup commands require administrator perms!")
    await ctx.send(embed = e)
  
  
  
  elif arg.lower() == "applications":
    e = discord.Embed(title = "Applications",color = discord.Color.blue())
    e.add_field(name = "Setup",value = "Follow this simple steps to setup applications!")
    e.add_field(name = "(NEEDED) Setup applications.",value ="`/setup_applications <#CHANNEL_APPLICATIONS_WILL_BE_SENT_IN>`")
    e.add_field(name = "Changing applications channel .", value = "`/set_applications_channel <#NEW_APPLICATIONS_CHANNEL>`")
    e.add_field(name = "Adding questions.", value = "`/addq This Question is Example?`")
    e.add_field(name = "Check your application questions",value = "`/q`")
    e.add_field(name = "Remove questions",value = "`/qpop 1` (Removes 1st question)")
    e.add_field(name = "(DMS) Accept application (Sends simple DM)",value = "`/accept <USER>`")
    e.add_field(name = "(DMS) Deny application (Sends simple DM)",value = "`/deny <USER>`")
    e.add_field(name = "Disable applications (Do setup again to enable applications again.)",value = "`/disable_applications`")
    await ctx.send(embed = e)
  
  
  
  elif arg.lower() == "counting":
    e = discord.Embed(title = "Counting",color = discord.Color.blue())
    e.add_field(name = "Set counting channel.", value = "`/set_counting_channel <#COUNTING_CHANNEL>`")
    e.add_field(name = "Disable counting. (Set counting channel again to enable counting again.)",value = "`/disable_counting`")
    await ctx.send(embed = e)
  
  
  
  elif arg.lower() == "suggestions":
    e = discord.Embed(title = "Suggestions" , color = discord.Color.blue())
    e.add_field(name = "Set suggestions channel.", value = "`/set_suggestions_channel <#SUGGESTIONS_CHANNEL>`")
    e.add_field(name = "Disable suggestions. (Set suggestion channel to enable suggestions again.)",value = "`/disable_suggestions`")
    await ctx.send(embed = e)
  
  
  
  elif arg.lower() == "tickets":
    e = discord.Embed(title = "Tickets" , color = discord.Color.blue())
    e.add_field(name = "Setup",value = "Follow these easy steps to setup your tickets.")
    e.add_field(name = "Set the category in which tickets will be made.",value = "`/set_ticket_category <CATEGORY_ID>`")
    e.add_field(name = "Set the ticket msg.",value = "`/set_ticket_message React to this message (example btw)!`")
    e.add_field(name = "Send the ticket message in embed fully set up.",value = "`/send_ticket`")
    e.add_field(name = "Close the ticket.",value = "`/c`")
    e.add_field(name = "Disable suggestions. (Do the setup again to enable tickets again.)",value = "`/disable_tickets`")
    await ctx.send(embed = e)



@bot.command()
@commands.has_permissions(administrator=True)
async def disable_applications(ctx):
  x = await db(ctx)
  try:
    x.pop("q")
    x.pop("qchannel")
    col.replace_one({"_id":ctx.guild.id}, x)
    await ctx.send("Applications were disabled. (To enable them again do `/help applications` and follow the steps again!")
  except:
    await ctx.send("You cant disable something that was never enabled!")



@bot.command()
@commands.has_permissions(administrator=True)
async def disable_counting(ctx):
  x = await db(ctx)
  try:
    x["counting"]
    x.pop("counting")
    col.replace_one({"_id":ctx.guild.id},x)
    await ctx.send("Counting was disabled. (To enable counting set counting channel again.)")
  except:
    await ctx.send("Counting was never even enabled!")



@bot.command()
@commands.has_permissions(administrator=True)
async def disable_suggestions(ctx):
  x = await db(ctx)
  try:
    x["suggestions"]
    x["suggestionsn"]
    x.pop("suggestions")
    x.pop("suggestionsn")
    col.replace_one({"_id":ctx.guild.id},x)
    await ctx.send("Suggestions were disabled. ( To enable suggestions set the suggestions channel again.)")
  except:
    await ctx.send("Suggestions were never even set up.")



@bot.command()
@commands.has_permissions(administrator=True)
async def disable_tickets(ctx):
  x = await db(ctx)
  try:
    x
    x.pop("tid")
    x.pop("tmsg")
    x.pop("tcategory")
    col.replace_one({"_id":ctx.guild.id},x)
    await ctx.send("Tickets were disabled. (To enable them setup tickets again!)")
  except:
    await ctx.send("Tickets werent fully set up yet!")



@bot.command()
async def set_telephone_channel(ctx , channel:discord.TextChannel):
  col.update_one({"_id":ctx.guild.id},{"$set":{"telephonechannel":channel.id}})
  await ctx.send("Telephone channel was set up!")



@bot.command()
async def joincall(ctx):
  z = col.find_one({"_id":ctx.channel.id})
  if z["telephonechannel"] != ctx.channel.id:
    return
  x = col.find_one({"_id":0})
  x["queue"].append(ctx.channel.id)
  col.update_one({"_id":0},{"$set":x})
  x = col.find_one({"_id":0})
  y = x["queue"].index(ctx.channel.id)
  if y == 0 or y % 2 == 0:
    await ctx.send("Connecting...")
  else:
    await ctx.send("Connected to server!")
    channel = bot.get_channel(x["queue"][y - 1])
    await channel.send("Connected to server!")



@bot.command()
async def s(ctx,*,msg):
  x = col.find_one({"_id":0})
  if ctx.channel.id not in x["queue"]:
    return
  try:
    z = x["queue"].index(ctx.channel.id)
  except:
    return
  if z == 0 or z % 2 == 0:
    channel = bot.get_channel(x["queue"][z + 1])
  else:
      channel = bot.get_channel(x["queue"][z - 1])
  await channel.send(f"{ctx.author} : {msg}")



bot.run("")
#bot.run(os.environ["token"])
