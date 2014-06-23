#! /usr/bin/env python
#
# Santa Bot
#
# Joel Wright <joel.wright@gmail.com>

"""
A Santa bot.

This is a Santa bot that uses the SingleServerIRCBot class from
irc.bot.  The bot ignores all messages, but updates the channel topic
every minute with the countdown to christmas day :).
"""
import thread
from datetime import datetime, timedelta, date
from time import sleep

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

class SantaBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "isitchristmas":
            print("Dealing with isitchristmas")
            self.isitchristmas()
        else:
            c.notice(nick, "Not understood: " + cmd)

    def set_topic(self, topic):
        self.connection.topic(self.channel, new_topic=topic)

    def isitchristmas(self):
        c = date(2013, 12, 25)
        n = date.today()
        if c == n:
            self.connection.privmsg(self.channel, "Why, yes it is, but have you been naughty or nice?!")
        elif c > n:
            print("Not yet")
            self.connection.privmsg(self.channel, "Hohoho! No not yet!")
        else:
            self.connection.privmsg(self.channel, "Please leave a message, Santa is taking a well deserved rest")

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: santaBot.py <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    santa = SantaBot(channel, nickname, server, port)
    thread.start_new_thread(santa.start, ())

    christmas = datetime(2013, 12, 25, 0, 0, 0, 0)

    topic = ""
    
    while not topic:
        try:
            now = datetime.now()
            dt = christmas - now
            days = dt.days
            hours = dt.seconds / 3600
            minutes = (dt.seconds - (hours*3600)) / 60
            if minutes > 30:
                hours += 1
            new_topic = "%s Days, %s Hours to Christmas!" % (days, hours)
            santa.set_topic(new_topic)
            topic = new_topic
        except Exception as e:
            print("Ignoring %s" % e)
        sleep(5)

    while True:
        try:
            now = datetime.now()
            dt = christmas - now
            days = dt.days
            hours = dt.seconds / 3600
            minutes = (dt.seconds - (hours*3600)) / 60
            if minutes == 30:
                new_topic = "%s Days, %s Hours to Christmas!" % (days, hours)
                if not topic == new_topic:
                    hours += 1
                    santa.set_topic(new_topic)
                    topic = new_topic
        except Exception as e:
            print("Ignoring %s" % e)   
        sleep(18)

if __name__ == "__main__":
    main()
