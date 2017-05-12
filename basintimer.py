import asyncio
import discord
import time
from datetime import datetime
from discord.ext import commands

class BasinTimer:
    """My custom cog that does stuff!"""

    BASE_TIME = 1494546893
    SPAWN_INTERVAL = 2580
    ALERT_TIME = 300 # 5 minutes

    def __init__(self, bot):
        self.bot = bot
        self.is_timer_on = False
        self.boss_order = ["sand", "rain", "thunder"]
        self.next_announcement_time = self.BASE_TIME
        self.next_boss_index = 0
        self.timer_states = {}
        self.active_timer_count = 0
        self.current_timer_id = 0

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
    
    # @commands.command()
    # async def setorder(self, option):
    #     """Set the spawn order of the bosses
    #     1) Sand -> Rain -> Thunder
    #     2) Thunder -> Rain -> Sand
    #     """

    #     if option == 1:
    #         self.boss_order = ["sand", "rain", "thunder"]
    #         await self.bot.say("Spawn order set to Sand -> Rain -> Thunder")
    #     elif option == 2:
    #         self.boss_order = ["thunder", "rain", "sand"]
    #         await self.bot.say("Spawn order set to Thunder -> Rain -> Sand")
    #     else:
    #         await self.bot.say(option + " is not a valid option!")

    @commands.command()
    async def setrotation(self, order, lastspawn):
        """Set the spawn rotation of the bosses

        Args:
            order:
                1) Sand -> Rain -> Thunder
                2) Thunder -> Rain -> Sand
            lastspawn: "sand", "rain", or "thunder"
        """

        if option != 1 or option != 2:
            await self.bot.say(option + " is not a valid option!")
            return
        
        if lastspawn not in ["sand", "rain", "thunder"]:
            await self.bot.say(lastspawn + " is not a valid event weather!")
            return

        if option == 1:
            self.boss_order = ["sand", "rain", "thunder"]
            await self.bot.say("Spawn order set to Sand -> Rain -> Thunder")
        elif option == 2:
            self.boss_order = ["thunder", "rain", "sand"]
            await self.bot.say("Spawn order set to Thunder -> Rain -> Sand")

        self.calculate_next_spawn()
        self.next_boss_index = (self.boss_order.index(lastspawn) + 1) % 3
        
    
    @commands.command()
    async def basinnext(self):
        """Get the next boss announcement time"""
        self.calculate_next_spawn()
        timestamp = datetime.fromtimestamp(self.next_announcement_time).strftime("%I:%M:%S %p PST")
        boss = self.get_boss_name_from_index(self.next_boss_index)
        await self.bot.say("Next announcement at " + timestamp + "\n" + "Projected boss: " + boss)

    # @commands.command()
    # async def startbasintimer(self):
    #     """Start the Celestial Basin boss timer"""
    #     if self.is_timer_on:
    #         await self.bot.say("Basin timer already running!")
    #     else:
    #         self.is_timer_on = True
    #         await self.bot.say("Celestial basin timer started!")
    #         while self.is_timer_on:
    #             current_time = int(time.time())
    #             self.calculate_next_spawn()
    #             time_to_alert = self.next_announcement_time - self.ALERT_TIME - current_time
    #             if time_to_alert >= 0:
    #                 await asyncio.sleep(time_to_alert)
    #                 boss = self.get_boss_name_from_index(self.next_boss_index)
    #                 await self.bot.say("@here Next Celestial Basin boss announcement is in 5 minutes! Projected boss: " + boss)
    #                 await asyncio.sleep(time_to_alert) # wait awhile so we don't trigger the message twice
    #             else:
    #                 await asyncio.sleep(self.ALERT_TIME)
    
    @commands.command()
    async def startbasintimerv2(self):
        """Start the Celestial Basin boss timer"""
        # Enhanced timer to prevent multiple instances from running at the same time
        if self.active_timer_count > 0:
            await self.bot.say("Basin timer already running!")
        else:
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
                    boss = self.get_boss_name_from_index(self.next_boss_index)
                    await self.bot.say("@here Next Celestial Basin boss announcement is in 5 minutes! Projected boss: " + boss)
                    await asyncio.sleep(time_to_alert) # wait awhile so we don't trigger the message twice
                else:
                    await asyncio.sleep(self.ALERT_TIME)
            del self.timer_states[timer_id]
    
    @commands.command()
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
