"""Wanna make game loops that handle pygame's state?

This module should make that easier.
"""
import pygame
from typing import *
from typing_extensions import *
from ..fp import conditional
from functools import partial, wraps
from threading import Thread

class EventDispatcher:
    pass

class Stop(Exception):...

class Game:
    __slots__ = ('_quit', 'loops', 'size')
    def __init__(self, size = (640, 480)):
        self._quit = False
        self.loops = list()
        self.size = size
    
    def deloop(self, loop):
        try:
            self.loops.remove(loop)
        except: pass
    
    def run(self, threaded: bool = False):
        if threaded:
            run_thread = Thread(target = self._run)
            run_thread.start()
            return run_thread
        else:
            self._run()
    
    def _run(self):
        pygame.init()
        screen = pygame.display.set_mode(self.size)
        while not self._quit:
            screen.fill((0, 0, 0))
            if pygame.event.peek(pygame.QUIT):
                # We don't want to break from the loop right away because
                # there might be handlers that handle the quit event
                # in our loops.
                self._quit = True
            for loop in self.loops:
                try:
                    loop(self, screen)
                    if self._quit == 2:
                        break
                except SystemExit as exit:
                    pygame.quit()
                    raise exit
                except Stop as stop:
                    self._quit = True
                    break
                except: pass
            pygame.display.flip()
        pygame.quit()
        
    def quit(self, immediate: bool = False):
        self._quit = 2 if immediate else True
    
    def loop(self, target):
        self.loops.append(target)
        return target