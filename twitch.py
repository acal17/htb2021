import asyncio
from display import Display
from twitchio.client import Client
from twitchio.ext import commands

class TwitchBot(commands.Bot):
  def __init__(self, twitch_data, database_interface):
    irc_token, client_id, nick, prefix, initial_channels = twitch_data
    self.database_interface = database_interface
    super().__init__(irc_token=irc_token, client_id=client_id, nick=nick, prefix=prefix, initial_channels=initial_channels)

  # Events don't need decorators when subclassed
  async def event_ready(self):
    ws = self._ws
    for channel in self.initial_channels:
      await ws.send_privmsg(channel, f"/me has landed!")

  async def event_message(self, message):
    print(message.content)
    await self.handle_commands(message)

  @commands.command(name="help")
  async def help(self, ctx):
    message = f"{ctx.author.name}, help is as follows: " + ", ".join(["!help - help", "!register - register", "!portfolio - portfolio"]) + "."
    await ctx.send(message)

  @commands.command(name="register")
  async def register(self, ctx):
    self.database_interface.create_user(ctx.author.name)
    await ctx.send(f"{ctx.author.name}, you have been registered!")

  @commands.command(name="reset")
  async def reset(self, ctx):
    if not self.database_interface.user_exists(ctx.author.name):
      await ctx.send(f"{ctx.author.name}, you have not registered!")
    self.database_interface.reset_user(ctx.author.name)
    await ctx.send(f"{ctx.author.name}, your account has been reset!")

  @commands.command(name="portfolio")
  async def portfolio(self, ctx):
    if not self.database_interface.user_exists(ctx.author.name):
      await ctx.send(f"{ctx.author.name}, you have not registered!")
    portfolio = self.database_interface.get_portfolio(ctx.author.name)
    message = f"{ctx.author.name}, your portfolio is as follows: {portfolio}."
    await ctx.send(message)

  @commands.command(name="buy")
  async def buy(self, ctx, ticker, quantity):
    if not self.database_interface.user_exists(ctx.author.name):
      await ctx.send(f"{ctx.author.name}, you have not registered!")
    quantity = float(quantity)
    self.database_interface.buy_asset(ctx.author.name, ticker, quantity, self.display.prices[self.display.tickers.index(ticker)])
    await ctx.send(f"{ctx.author.name}, you have bought {quantity} of {ticker} at {self.display.prices[self.display.tickers.index(ticker)]} per unit.")

  @commands.command(name="sell")
  async def sell(self, ctx, ticker, quantity):
    if not self.database_interface.user_exists(ctx.author.name):
      await ctx.send(f"{ctx.author.name}, you have not registered!")
    quantity = float(quantity)
    self.database_interface.sell_asset(ctx.author.name, ticker, quantity, self.display.prices[self.display.tickers.index(ticker)])
    await ctx.send(f"{ctx.author.name}, you have sold {quantity} of {ticker} at {self.display.prices[self.display.tickers.index(ticker)]} per unit.")