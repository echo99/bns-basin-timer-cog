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
        self.bossOrder = ["thunder", "sand", "rain"]
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
    async def mycom(self):
        """This does stuff!"""

        #Your code will go here
        await self.bot.say("I can do stuff!")
    
    @commands.command()
    async def basinnext(self):
        currentTime = int(time.time())
        bossType = self.currentBossType
        nextAnnouncementTime = self.nextAnnouncementTime
        while nextAnnouncementTime < currentTime:
            nextAnnouncementTime += self.spawnInterval
            bossType += 1
        self.nextAnnouncementTime = nextAnnouncementTime
        self.currentBossType = bossType % 3
        bossName = self.getbossname(bossType)
        await self.bot.say("Next announcement at " + datetime.fromtimestamp(nextAnnouncementTime).strftime("%I:%M:%S %p PST") + "\n" + "Projected boss: " + bossName)


    @commands.command()
    async def startbasintimer(self):
        if self.trackerInit:
            await self.bot.say("Basin tracker already started!")
        else:
            self.trackerInit = True;
            await self.bot.say("Tracking basin times!")
            nextAnnouncementTime = self.baseTime
            bossType = 0
            while self.trackerInit:
                currentTime = int(time.time())
                #await self.bot.say("Current time: " + str(currentTime))
                while (nextAnnouncementTime - self.alertTime) < currentTime:
                    nextAnnouncementTime += self.spawnInterval
                    bossType += 1
                #await self.bot.say("Next announcement time: " + str(nextAnnouncementTime))
                timeToAlert = nextAnnouncementTime - self.alertTime - currentTime
                #await self.bot.say("Time to next alert: " + str(timeToAlert))
                if timeToAlert > 1:
                    await asyncio.sleep(timeToAlert)
                    bossWeather = self.bossOrder[bossType % 3]
                    bossName = self.getbossname(bossWeather)
                    await self.bot.say("@here Next Celestial Basin boss announcement is in 5 minutes! Projected boss: " + bossName)
    
    @commands.command()
    async def stopbasintimer(self):
        self.trackerInit = False
        await self.bot.say("Tracker stopped")


def setup(bot):
    bot.add_cog(BasinTimer(bot))
