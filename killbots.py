#!/bin/env/python3
#
import curses
import random
import time


class Bot:
    def __init__(self, maxX, maxY):
        self.x = int(random.random() * (maxX-1))
        self.y = int(random.random() * (maxY-1))
        self.disp = 'X'
        self.state = 'OK'

    def chase(self, meX, meY):
        # There is no need to chack limits, because the
        # player will already have checked them in
        # making his move, and the bot isn't going to
        # attempt to move in a direction unless the
        # player's corresponding coordinate is farther
        # in that direction than its own.
        #
        if self.state == 'ded': return
        if self.x < meX: self.x += 1
        if self.x > meX: self.x -= 1
        if self.y < meY: self.y += 1
        if self.y > meY: self.y -= 1

    def die(self):
        self.disp = '*'
        self.state = 'ded'


def move(x, y, dx, dy, bots):
    newx = x + dx
    newy = y + dy

    # addch will raise an exception after writing to the
    # lower right corner, because it will then attempt to
    # advance the cursor (and fail).  So give the right
    # edge a char's extra space.  Give the bottom some
    # space as well, so a status display can go in there
    # at some point.
    #
    if newx >= COLS-1: newx = COLS-2
    elif newx < 0: newx = 0

    if newy >= ROWS-1: newy = ROWS-2
    elif newy < 0: newy = 0

    # Don't let player step on rubbish piles.  You don't
    # know where they've been.
    #
    for b in bots:
        if b.state == 'ded' and newx == b.x and newy ==b.y:
            newx = x
            newy = y

    return newx, newy


def animateScroo(meX, meY, ROWS, COLS):
    # Sonic Screwdriver(TM) animation.
    def ckXY(x, y):
        if x<0 or y<0: return False
        if x>COLS-2 or y>ROWS-2: return False
        return True

    def anim(ekss, weis, chrs):
        for i in range(len(ekss)):
            if not ckXY(meX + ekss[i], meY + weis[i]): continue
            stdscr.addch(meY + weis[i], meX + ekss[i], chrs[i])
        stdscr.refresh()

    ekss1 = [-1,  0,  1, -1,  1, -1,  0,  1]
    weis1 = [-1, -1, -1,  0,  0,  1,  1,  1]
    ekss2 = [-2,  0,  2, -2,  2, -2,  0,  2]
    weis2 = [-2, -2, -2,  0,  0,  2,  2,  2]

    rays = ['\\', '|', '/', '-', '-', '/', '|', '\\']
    clrs = 8 * [' ']

    anim(ekss1, weis1, rays)   #  draw the first set of rays
    time.sleep(.2)             #  let the user have a gander at them
    anim(ekss1, weis1, clrs)   #  clear them

    anim(ekss2, weis2, rays)   #  second verse, same as the first
    time.sleep(.2)             #  gander
    anim(ekss2, weis2, clrs)   #  clear


def decodeMovementKeys(k, x, y, bots):
    newX, newY = x, y

    # Rogue keys, plus 't' for teleport.  All others
    # are a NOP.
    #
    if k == 'h': newX, newY = move(x, y, -1, 0, bots)
    if k == 'j': newX, newY = move(x, y, 0, 1, bots)
    if k == 'k': newX, newY = move(x, y, 0, -1, bots)
    if k == 'l': newX, newY = move(x, y, 1, 0, bots)
    if k == 'y': newX, newY = move(x, y, -1, -1, bots)
    if k == 'u': newX, newY = move(x, y, 1, -1, bots)
    if k == 'b': newX, newY = move(x, y, -1, 1, bots)
    if k == 'n': newX, newY = move(x, y, 1, 1, bots)
    if k == 't':
        newX = int(random.random() * (COLS-1))
        newY = int(random.random() * (ROWS-1))

    return newX, newY


def main(stdscr):
    random.seed()

    stdscr.clear()
    curses.curs_set(0)
    stdscr.refresh()

    global ROWS, COLS
    global meX, meY
    global MAX_BOTS

    ROWS, COLS = curses.LINES, curses.COLS
    meX = int(COLS / 2)
    meY = int(ROWS / 2)
    nBots = MAX_BOTS
    nScroo = 1

    bots = [ Bot(COLS, ROWS) for i in range(nBots) ]

    stdscr.addch(meY, meX, '@')
    for b in bots:
        stdscr.addch(b.y, b.x, b.disp)

    while True:
        k = stdscr.getkey()

        # 'x': exit.
        #
        if k == 'x': return 1

        # 's': use the Sonic Screwdriver(TM), if one is
        # still available.
        #
        if k == 's' and nScroo > 0:
            botsToRedraw = []
            for i in range(-2, 3):
                for j in range(-2, 3):
                    for b in bots:
                        if b.x == meX+i and b.y == meY+j:
                            if b.state == 'OK':
                                b.die()  # state ain't OK no more!
                                nBots -= 1
                            botsToRedraw.append(b)
            nScroo -= 1
            animateScroo(meX, meY, ROWS, COLS)
            for b in botsToRedraw: stdscr.addch(b.y, b.x, b.disp)
        else:
            # Else, move player.
            #
            stdscr.addch(meY, meX, ' ')
            meX, meY = decodeMovementKeys(k, meX, meY, bots)
            stdscr.addch(meY, meX, '@')

        # Operate bots.  First, erase 'em, then redraw 'em.
        # Do this in two loops, so the erase of bots farther
        # from the front of the list doesn't stomp the redraw
        # of the bots that were earlier in the list.
        #
        for b in bots:
            stdscr.addch(b.y, b.x, ' ')

        for b in bots:
            if b.state != 'ded': b.chase(meX, meY)
            stdscr.addch(b.y, b.x, b.disp)

        # Check for collisions between bots.  If a bot is not
        # already dead, and it is attempting to occupy the same
        # space as another bot, living or otherwise, then it
        # becomes dead.  If a non-dead bot is at the same
        # position as the player, then the player, similarly,
        # fails to thrive.
        #
        # n**2.  Can't be helped.  Not easily, anyway.
        #
        for b in bots:
            if b.state == 'ded': continue

            for bb in bots:
                if bb == b: continue
                if b.x == bb.x and b.y == bb.y:
                    b.die()
                    stdscr.addch(b.y, b.x, b.disp)
                    nBots -= 1
                    break  # You only die once.  Same with bots.

            # Die, hyu-man!
            if b.state == 'OK' and b.x ==meX and b.y == meY: return 2

        if nBots == 0: return 0


MAX_BOTS = 5

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()

x = curses.wrapper(main)
if x == 0: print("you've won")
if x == 1: print("meh")
if x == 2: print("you've not won")