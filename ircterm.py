#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from printer import ThermalPrinter as tp
from datetime import datetime,timedelta,time
import logging
from logging import StreamHandler as sh
from logging.handlers import TimedRotatingFileHandler as trfh
from textwrap import TextWrapper
import signal

class IRCScrollback(object):
    def __init__(self,port=None):
        if port is not None:
            self.printer = tp(serialport=port)
        else:
            self.printer = tp(serialport=tp.SERIALPORT)
        self.printer.font_b_on()

        # setting up logging
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileHandler = trfh('irc.log',when='midnight',backupCount=7)
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)
        consoleHandler = sh()
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)
        logger = logging.getLogger('IRCScrollback')
        logger.addHandler(fileHandler)
        logger.addHandler(consoleHandler)
        logger.setLevel(logging.DEBUG)

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
        logger = logging.getLogger('IRCScrollback.print_line')
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
        logger = logging.getLogger('IRCScrollback.next_day')
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
        self.

if __name__ == '__main__':
    import sys, os
    logger = logging.getLogger('IRCScrollback.main')
    if len(sys.argv) == 2:
        i = IRCScrollback(sys.argv[1])
    else:
        i = IRCScrollback()

    logger.debug("Testing printer on port %s" % i.printer.SERIALPORT)
    i.print_line('<@agmlego> Hello world!')
    i.print_line('<@agmlego> Hello i3ircterm!',highlight=True)
    i.print_line('<@agmlego> I *love* that this printer does stuff onboard for you.')
    i.printer.linefeed()
    i.printer.linefeed()
    i.printer.linefeed()
