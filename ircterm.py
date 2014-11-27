#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# printer imports
from printer import ThermalPrinter as tp
from datetime import datetime,timedelta,time
import logging
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from textwrap import TextWrapper
import signal

# irc imports
from oyoyo.client import IRCClient
import oyoyo.parse
from oyoyo import helpers
from oyoyo.cmdhandler import DefaultCommandHandler
from termcolor import colored,cprint


# setting up logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler = TimedRotatingFileHandler('irc.log',when='midnight',backupCount=7)
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)
consoleHandler = StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)
logger = logging.getLogger('IRCTerm')
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

class IRCMain(object):
    def __init__(self,server='irc.freenode.net',port=6667,channel='#i3detroit',
                 nick='i3ircterm',realname='IRC Terminal at i3Detroit',
                 user='i3ircterm',password=None,printer=None):
        logger = logging.getLogger('IRCTerm.IRCMain')
        # setting up connection parameters
        self.server = server
        self.port = port
        self.channel = channel
        self.nick = nick
        self.realname = realname
        self.user = user
        self.password = password
        self.printer = printer
        self.cli = None
        
        if self.printer is None:
            logger.warn('No printer in use, using console instead')
        
    def connect(self):
        logger = logging.getLogger('IRCTerm.IRCMain.connect')
        if self.cli is None:
            logger.debug('Connecting to %s:%s as %s'%\
                         (self.server,self.port,self.nick))
            self.cli = IRCClient(IRCHandler, host=self.server, port=self.port,
                                   nick=self.nick, connect_cb=self.connect_callback)
            self.cli.command_handler.printer = self.printer
            self.conn = self.cli.connect()
        else:
            logger.warn('Already connected...')
        return self.conn

    def connect_callback(self,cli):
        logger = logging.getLogger('IRCTerm.IRCMain.connect_callback')
        logger.debug('user %s realname %s nick %s'%\
                (self.user,self.realname,self.nick))
        helpers.user(self.cli,self.user,self.realname)
        
        if self.password is not None:
            logger.debug('Identifying %s with %s'%(self.nick,self.password))
            helpers.identify(self.cli,self.password)
        else:
            logger.debug('No identify required')
        logger.info('Joining %s'%self.channel)
        helpers.join(self.cli,self.channel)

class IRCHandler(DefaultCommandHandler):
    def print_line(self,text,timestamp=True,highlight=False):
        if self.printer is None:
            if timestamp:
                if highlight:
                    cprint('%s %s'%(datetime.now(),text),'red')
                else:
                    cprint('%s %s'%(datetime.now(),text),'green')
            else:
                if highlight:
                    cprint(text,'red')
                else:
                    cprint(text,'green')
        else:
            self.printer.print_line(text,timestamp,highlight)

    def privmsg(self, nick, chan, msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.privmsg')
        logger.debug('PRIVMSG from %s in %s: %s'%(nick,chan,msg))
        nick,host = nick.split('!')
        highlight = (self.client.nick in msg or self.client.nick in chan)
        if self.client.nick in chan:
            chan = 'PRIVATE'
        self.print_line('%s: <%s> %s'%(chan,nick,msg),True,highlight)
    
    def notice(self,server,target,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.notice')
        logger.debug('NOTICE from %s to %s: %s'%(server,target,msg))
        highlight = (self.client.nick in target or '*' in target)
        self.print_line('%s: *%s* %s'%(server,target,msg),True,highlight)
        
    def welcome(self,server,target,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.welcome')
        logger.debug('WELCOME from %s to %s: %s'%(server,target,msg))
        highlight = (self.client.nick in target or '*' in target)
        self.print_line('%s: *%s* %s'%(server,target,msg),True,highlight)
        
    def motdstart(self,server,target,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.motd')
        logger.debug('MOTD from %s to %s: %s'%(server,target,msg))
        highlight = (self.client.nick in target or '*' in target)
        self.print_line('%s: %s'%(server,msg),True,highlight)
        
    def motd(self,server,target,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.motd')
        logger.debug('MOTD from %s to %s: %s'%(server,target,msg))
        highlight = (self.client.nick in target or '*' in target)
        self.print_line('%s: %s'%(server,msg),True,highlight)
    
    def endofmotd(self,server,target,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.motd')
        logger.debug('MOTD from %s to %s: %s'%(server,target,msg))
        highlight = (self.client.nick in target or '*' in target)
        self.print_line('%s: %s'%(server,msg),True,highlight)
        
    def mode(self,*args):
        logger = logging.getLogger('IRCTerm.IRCHandler.mode')
        if len(args) == 4:
            mod,chan,mode,target = args
        elif len(args) == 3:
            mod,target,mode = args
            chan = 'none'
        else:
            logger.warn('No idea what this is: %s'%(repr(args)))
            return
        logger.debug('MODE by %s to %s in %s: %s'%(mod,target,chan,mode))
        mod = mod.split('!')[0]
        self.print_line('-!- mode/%s (%s %s) by %s'%(chan,mode,target,mod))
        
    def currenttopic(self,server,target,chan,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.topic')
        logger.debug('CURRENTTOPIC on %s of %s to %s: %s'%(server,chan,target,msg))
        self.print_line('-!- Topic for %s: %s'%(chan,msg))
        
    def topicinfo(self,server,target,chan,user,date):
        logger = logging.getLogger('IRCTerm.IRCHandler.topic')
        logger.debug('TOPIC on %s of %s to %s: set by %s on %s'%(server,chan,target,user,date))
        date = datetime.fromtimestamp(int(date))
        user,host = user.split('!')
        self.print_line('-!- Topic set by %s <%s> (%s)'%(user,host,date))
        
    def join(self,user,chan):
        logger = logging.getLogger('IRCTerm.IRCHandler.join')
        logger.debug('JOIN of %s to %s'%(user,chan))
        user,host = user.split('!')
        self.print_line('-!- %s <%s> has joined %s'%(user,host,chan))
        
    def part(self,user,chan,msg):
        logger = logging.getLogger('IRCTerm.IRCHandler.part')
        logger.debug('PART of %s from %s: %s'%(user,chan,msg))
        user,host = user.split('!')
        self.print_line('-!- %s <%s> has left %s: %s'%(user,host,chan,msg))
        
    def namreply(self,server,target,null,chan,names):
        logger = logging.getLogger('IRCTerm.IRCHandler.names')
        logger.debug('NAMES in %s: %s'%(chan,names))
        names = ' '.join(sorted(names.split(' ')))
        self.print_line('-!- %s users in %s'%(len(names),chan))
        self.print_line('%s'%names)

    def __unhandled__(self,*args):
        logger = logging.getLogger('IRCTerm.IRCHandler.__unhandled__')
        logger.info('UNHANDLED: %s'%(repr(args)))
        

class IRCScrollback(object):
    def __init__(self,port=None):
        if port is not None:
            self.printer = tp(serialport=port)
        else:
            self.printer = tp(serialport=tp.SERIALPORT)
        self.printer.font_b_on()

        # setting up text wrapper
        self.wrapper = TextWrapper(initial_indent='',subsequent_indent=' '*9,
                                   width=42,drop_whitespace=True)

        # setting up the 'day-changed' printout
        signal.signal(signal.SIGALRM,self.day_change)
        self.day_change(None,None)

    def split_format(self,text,fmt):
        splits = []
        while True:
            
            # find the starting token
            start = text.find(' '+fmt)
            if start < 0:
                # there was no start, no format needed
                return splits + [text]

            # find the ending token
            end = text.find(fmt+' ',start+2)
            if end < 0:
                # there was no ending, no format needed
                return splits
            # there *was* an end, trim the text and add the section to the list
            splits.append(text[start+2:end])
            text = text[end+2:]

    def print_line(self,text,timestamp=True,highlight=False):
        logger = logging.getLogger('IRCTerm.IRCScrollback.print_line')
        logger.debug('text: |%s|\nts: %s hl: %s'%(text,timestamp,highlight))

        text = text.encode('cp437',errors='replace')
        
        # print a timestamp on the line
        if timestamp:
            text = datetime.now().strftime('%H:%M:%S') + ' ' + text

        # highlight a row of text
        if highlight:
            self.printer.inverse_on()
        
        '''
        # handle *bold* and _underlined_ text
        bold_sections = self.split_format(text,'*')
        under_sections = self.split_format(text,'_')

        for bold in bold_sections:
            text = text.replace(' *%s* '%bold,'>|<B>|<')
        
        for under in under_sections:
            text = text.replace(' _%s_ '%under,'>|<U>|<')
        '''

        # print the line
        self.printer.print_text(self.wrapper.fill(text) + '\n')
        
        if highlight:
            self.printer.inverse_off()

    def next_day(self):
        '''Calculate the number of seconds to the next day.'''
        logger = logging.getLogger('IRCTerm.IRCScrollback.next_day')
        today = datetime.now().date()
        tomorrow = datetime.combine(today + timedelta(days=1),time(0,0,0))
        alarm_time = (tomorrow-datetime.now()).total_seconds()
        logger.debug('%s->%s = %s'%(datetime.now(),tomorrow,alarm_time))
        return int(alarm_time)

    def day_change(self,signum,frame):
        '''Print out a line to indicate the day changed.'''
        self.print_line('------- Day changed to %s -------'%(datetime.now().date()),timestamp=False,highlight=False)
        signal.alarm(self.next_day())

class IRCInput(object):
    def __init__(self):
        self.port = serial.Serial('/dev/ttyO2',38400)

if __name__ == '__main__':
    import sys, os
    logger = logging.getLogger('IRCTerm.main')
    
    p = 'pants'
    if len(sys.argv) == 2:
        p = IRCScrollback(sys.argv[1])
    else:
        p = IRCScrollback()

    irc = IRCMain(printer=p)
    conn = irc.connect()
    while True:
        conn.next()
