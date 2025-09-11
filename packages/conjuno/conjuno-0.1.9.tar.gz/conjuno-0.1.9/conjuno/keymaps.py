# encoding=utf-8
#
# PROGRAM: CONJUNO
# MODULE : keymap
#
# NOTICE THANKS MCPLAY 
# FOR THIS CODE IT WAS
# EDITED BY ADDING ASYNC
# CALLS TO IT
#

import curses
from conjuno import log
        
class Stack:
    def __init__(self):
        self.items = ()

    def push(self, item):
        self.items = (item,) + self.items

    def pop(self):
        self.items, item = self.items[1:], self.items[0]
        return item

class KeymapStack(Stack):
    def process(self, code):
        for keymap in self.items:
            if keymap:
                if (keymap.process(code)):
                    break

class Keymap:
    def __init__(self):
        self.methods = [None] * curses.KEY_MAX

    def bind(self, key, method, args=None):
        if type(key) is str:
            ki = ord(key)
            self.methods[ki] = (method, args)
        if type(key) in (tuple, list):
            for ki in key:
                if type(ki) is str:
                    ki = ord(ki)
                self.methods[ki] = (method, args)
        if type(key) is range:
            for k in key:
                self.methods[k] = (method, args)

    async def process_async(self, method, args):
        await method(*args)

    def process(self, key):
        try:
            if self.methods[key] is None: return 0
        except IndexError:
            return 0
        method, args = self.methods[key]
        try:
            if args is None: 
              args = (key,)
            #import inspect
            import asyncio
            if asyncio.iscoroutinefunction(method)==True:
              asyncio.ensure_future(method(*args))
              #asyncio.ensure_future(self.process_async(method,*args))
              #asyncio.run(method(*args))
              #asyncio.get_event_loop().run_until_complete(method(*args))
            else:
              method(*args)
        except Exception as e:
            log("[!] keymaps.process exception: "+str(e)) 

        return(1)

