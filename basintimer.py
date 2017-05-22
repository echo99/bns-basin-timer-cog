import asyncio
import discord
import time
from datetime import datetime
from discord.ext import commands

class BasinTimer:
    """My custom cog that does stuff!"""

    BASE_TIME = 1495159900
    SPAWN_INTERVAL = 2580
    ALERT_TIME = 180 # 3 minutes

    def __init__(self, bot):
        self.bot = bot
        self.is_timer_on = False
        self.boss_order = ["sand", "rain", "thunder"]
        self.next_announcement_time = self.BASE_TIME
        self.next_boss_index = 0
        self.timer_states = {}
        self.server_subscribers = {}
        self.server_timer_active = {}
        self.active_timer_count = 0
        self.current_timer_id = 0
        self.rotation_confirmed = False
        self.counter_on = False

    def get_boss_name_from_weather(self, boss_weather):
        if boss_weather == "sand":
            return "Excavation (Sand)"
        elif boss_weather == "rain":
            return "Croxar (Rain)"
        else:
            return "Aomok (Thunder)"

    def get_boss_name_from_index(self, boss_index):
        return self.get_boss_name_from_weather(self.boss_order[boss_index])

    def calculate_next_spawn(self):
        """Calculate the next announcment time and the boss type"""
        current_time = int(time.time())
        next_boss_index = self.next_boss_index
        next_announcement_time = self.next_announcement_time
        while next_announcement_time < current_time:
            next_announcement_time += self.SPAWN_INTERVAL
            next_boss_index += 1
        next_boss_index %= 3
        self.next_announcement_time = next_announcement_time
        self.next_boss_index = next_boss_index

    @commands.command()
    async def setrotation(self, order, lastspawn):
        """Set the spawn rotation of the bosses

        Args:
            order:
                1) Sand -> Rain -> Thunder
                2) Thunder -> Rain -> Sand
            lastspawn: "sand", "rain", or "thunder"
        """

        if order != "1" and order != "2":
            await self.bot.say(order + " is not a valid option!")
            return
        
        if lastspawn not in ["sand", "rain", "thunder"]:
            await self.bot.say(lastspawn + " is not a valid event weather!")
            return

        if order == "1":
            self.boss_order = ["sand", "rain", "thunder"]
            await self.bot.say("Spawn order set to Sand -> Rain -> Thunder")
        elif order == "2":
            self.boss_order = ["thunder", "rain", "sand"]
            await self.bot.say("Spawn order set to Thunder -> Rain -> Sand")

        self.calculate_next_spawn()
        self.next_boss_index = (self.boss_order.index(lastspawn) + 1) % 3
        self.rotation_confirmed = True
        
    @commands.command()
    async def setlastannouncement(self, announcement_time):
        """Set the last known announcement time for a boss as a unix timestamp"""
        self.next_announcement_time = int(announcement_time)
        self.calculate_next_spawn()

    @commands.command()
    async def basinnext(self):
        """Get the next boss announcement time"""
        self.calculate_next_spawn()
        timestamp = datetime.fromtimestamp(self.next_announcement_time).strftime("xx:%M:%S")
        boss = self.get_boss_name_from_index(self.next_boss_index)
        await self.bot.say("Next announcement at " + timestamp + "\n" + "Projected boss: " + boss)
    
    @commands.command()
    async def startcounter(self):
        """Get the next boss announcement time"""
        msg = await self.bot.say("```Starting counter...```")
        self.counter_on = True
        while self.counter_on:
            current_time = int(time.time())
            self.calculate_next_spawn()
            next_announcement_time = self.next_announcement_time
            while current_time < next_announcement_time and self.counter_on:
                time_to_announcement = next_announcement_time - current_time
                minutes_to_annoucement = int(time_to_announcement / 60)
                seconds_to_announcement = time_to_announcement % 60
                timestamp = datetime.fromtimestamp(self.next_announcement_time).strftime("xx:%M:%S")
                text = "```Next announcement at: " + timestamp
                text = "\nTime to next announcement: " + str(minutes_to_annoucement) + ":"
                if seconds_to_announcement < 10:
                    text += "0"
                text += str(seconds_to_announcement)
                text += "\nEstimated boss: "
                if self.rotation_confirmed:
                    boss = self.get_boss_name_from_index(self.next_boss_index)
                    text += boss
                else:
                    text += "Unknown"
                text += "\n```"
                await self.bot.edit_message(msg, text)
                await asyncio.sleep(1)
                current_time = int(time.time())
            next_spawn_time = next_announcement_time + 180
            while current_time < next_spawn_time and self.counter_on:
                time_to_spawn = next_spawn_time - current_time
                minutes_to_spawn = int(time_to_spawn / 60)
                seconds_to_spawn = time_to_spawn % 60
                text = "```\nTime to spawn: " + str(minutes_to_spawn) + ":"
                if seconds_to_spawn < 10:
                    text += "0"
                text += str(seconds_to_spawn)
                text += "\nEstimated boss: "
                if self.rotation_confirmed:
                    boss = self.get_boss_name_from_index(self.next_boss_index)
                    text += boss
                else:
                    text += "Unknown"
                text += "\n```"
                await self.bot.edit_message(msg, text)
                await asyncio.sleep(1)
                current_time = int(time.time())

            
        await self.bot.delete_message(msg)
    
    @commands.command()
    async def stopcounter(self):
        self.counter_on = False

    @commands.command(pass_context=True)
    async def subscribetimer(self, ctx):
        server_id = ctx.message.server.id
        if server_id in self.server_subscribers:
            subscribers = self.server_subscribers[server_id]
            subscribers.add(ctx.message.author)
        else:
            self.server_subscribers[server_id] = {ctx.message.author}
        await self.bot.say("You are now subscribed to Celestial Basin notifications!")
    
    @commands.command(pass_context=True)
    async def unsubscribetimer(self, ctx):
        server_id = ctx.message.server.id
        if server_id in self.server_subscribers:
            subscribers = self.server_subscribers[server_id]
            subscribers.discard(ctx.message.author)
        await self.bot.say("You are now unsubscribed from Celestial Basin notifications!")

    @commands.command(pass_context=True)
    async def printsubscribers(self, ctx):
        server_id = ctx.message.server.id
        if server_id in self.server_subscribers:
            subscribers = self.server_subscribers[server_id]
            subscribers_str = ', '.join(user.mention for user in subscribers)
            await self.bot.say("Timer subscribers: " + subscribers_str)
        else:
            await self.bot.say("No users subscribed to this timer")

    @commands.command(pass_context=True)
    async def startbasintimerv2(self, ctx):
        """Start the Celestial Basin boss timer"""
        # Enhanced timer to prevent multiple instances from running at the same time
        server_id = ctx.message.server.id
        if server_id in self.server_timer_active and self.server_timer_active[server_id]:
            await self.bot.say("Basin timer already running!")
        else:
            self.server_timer_active[server_id] = True
            subscribers = set()
            if server_id in self.server_subscribers:
                subscribers = self.server_subscribers[server_id]
            else:
                self.server_subscribers[server_id] = subscribers
            self.active_timer_count += 1
            # Give this timer a unique ID and increment the counter
            timer_id = self.current_timer_id
            self.current_timer_id += 1
            # Set timer state of this timer to True to indicate it is active
            self.timer_states[timer_id] = True
            await self.bot.say("Celestial basin timer started!")
            # Loop until timer is marked as inactive
            while self.timer_states[timer_id]:
                current_time = int(time.time())
                self.calculate_next_spawn()
                time_to_alert = self.next_announcement_time - self.ALERT_TIME - current_time
                if time_to_alert >= 0:
                    await asyncio.sleep(time_to_alert)
                    if not self.timer_states[timer_id]:
                        break
                    boss = self.get_boss_name_from_index(self.next_boss_index)
                    mentions = "@here"
                    subscribers = self.server_subscribers[server_id]
                    if len(subscribers) > 0:
                        mentions = ' '.join(user.mention for user in subscribers)
                    text = mentions + " Next Celestial Basin boss announcement is in 3 minutes!"
                    if self.rotation_confirmed:
                        text += "\nProjected boss: " + boss
                    msg = await self.bot.say(text)
                    next_announcement_time = self.next_announcement_time
                    while current_time < self.next_announcement_time:
                        time_diff = self.next_announcement_time - current_time
                        # Code to update alert time if it changes, but doesn't work as intended
                        # if time_diff > self.ALERT_TIME:
                        #     await asyncio.sleep(time_diff - self.ALERT_TIME)
                        #     current_time = int(time.time())
                        #     continue
                        text = mentions + " Next Celestial Basin boss announcement is in "
                        mins = int(time_diff / 60)
                        secs = time_diff % 60
                        if mins > 0:
                            text += str(mins) + " minute"
                            if mins != 1:
                                text += "s"
                        if secs > 0:
                            text += " " + str(secs) + " second"
                            if secs != 1:
                                text += "s"
                        text += "!"
                        if self.rotation_confirmed:
                            text += "\nProjected boss: " + boss
                        await self.bot.edit_message(msg, text)
                        await asyncio.sleep(1)
                        current_time = int(time.time())
                    text = mentions + " Next Celestial Basin boss announcement now!"
                    if self.rotation_confirmed:
                        text += "\nProjected boss: " + boss
                    await self.bot.edit_message(msg, text)
                    # Delete message after 6 mintues
                    await asyncio.sleep(self.ALERT_TIME + self.ALERT_TIME)
                    await self.bot.delete_message(msg)
                    #await asyncio.sleep(time_to_alert) # wait awhile so we don't trigger the message twice
                else:
                    await asyncio.sleep(self.ALERT_TIME)
            del self.timer_states[timer_id]
            del self.server_timer_active[server_id]

    @commands.command(pass_context=True)
    async def stopbasintimer(self):
        """Stop the Celestial Basin boss timer"""
        self.is_timer_on = False
        # Iterate through timer states and set them all to False to mark them as inactive
        for k, v in self.timer_states.items():
            self.timer_states[k] = False
        self.active_timer_count = 0
        await self.bot.say("Timer stopped")


def setup(bot):
    bot.add_cog(BasinTimer(bot))
