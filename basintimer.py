import asyncio
import discord
import time
from datetime import datetime
from discord.ext import commands

class BasinTimer:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        self.trackerInit = False
        self.baseTime = 1494469495
        self.spawnInterval = 2580
        self.alertTime = 300 # 5 minutes
        self.bossOrder = ["thunder", "rain", "sand"]
        self.nextAnnouncementTime = self.baseTime;
        self.currentBossType = 0;
        self.nextBoss = self.bossOrder[0];

    def getbossname(self, bossWeather):
        bossName = ""
        if bossWeather == "sand":
            bossName = "Excavation (Sand)"
        elif bossWeather == "rain":
            bossName = "Croxar (Rain)"
        else:
            bossName = "Aomok (Thunder)"
        return bossName
    
    @commands.command()
    async def setorder(self, option):
        """
        Set the spawn order of the bosses
        1) Sand -> Rain -> Thunder
        2) Thunder -> Rain -> Sand
        """

        if option == 1:
            self.bossOrder = ["sand", "rain", "thunder"]
            await self.bot.say("Spawn order set to Sand -> Rain -> Thunder")
        elif option == 2:
            self.bossOrder = ["thunder", "rain", "sand"]
            await self.bot.say("Spawn order set to Thunder -> Rain -> Sand")
        else:
            await self.bot.say(option + " is not a valid option!")
        
    
    @commands.command()
    async def basinnext(self):
        """Get the next boss announcement time"""
        currentTime = int(time.time())
        bossType = self.currentBossType
        nextAnnouncementTime = self.nextAnnouncementTime
        #await self.bot.say(bossType)
        while nextAnnouncementTime < currentTime:
            nextAnnouncementTime += self.spawnInterval
            bossType += 1
        self.nextAnnouncementTime = nextAnnouncementTime
        self.currentBossType = bossType % 3
        #await self.bot.say(bossType)
        bossName = self.getbossname(self.bossOrder[bossType % 3])
        await self.bot.say("Next announcement at " + datetime.fromtimestamp(nextAnnouncementTime).strftime("%I:%M:%S %p PST") + "\n" + "Projected boss: " + bossName)


    @commands.command()
    async def startbasintimer(self):
        """Start the Celestial Basin boss timer"""
        if self.trackerInit:
            await self.bot.say("Basin timer already started!")
        else:
            self.trackerInit = True;
            await self.bot.say("Celestial basin timer started!")
            nextAnnouncementTime = self.baseTime
            bossType = 0
            while self.trackerInit:
                currentTime = int(time.time())
                while (nextAnnouncementTime - self.alertTime) < currentTime:
                    nextAnnouncementTime += self.spawnInterval
                    bossType += 1
                timeToAlert = nextAnnouncementTime - self.alertTime - currentTime
                if timeToAlert > 1:
                    await asyncio.sleep(timeToAlert)
                    bossWeather = self.bossOrder[bossType % 3]
                    bossName = self.getbossname(bossWeather)
                    await self.bot.say("@here Next Celestial Basin boss announcement is in 5 minutes! Projected boss: " + bossName)
    
    @commands.command()
    async def stopbasintimer(self):
        """Stop the Celestial Basin boss timer"""
        self.trackerInit = False
        await self.bot.say("Timer stopped")


def setup(bot):
    bot.add_cog(BasinTimer(bot))
