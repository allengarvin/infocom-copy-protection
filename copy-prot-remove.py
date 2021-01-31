#!/usr/bin/python3

# Version 0.1

# Copyright 2021 "Allen Garvin" <aurvondel@gmail.com>
# License: 3-clause BSD
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Note: I wrote an earlier version of this in C in the 1990s, to help a
# blind player who was having trouble trying to play Infocom's games.
# I thought I'd rewrite it in Python now, to included all known releases
# of Infocom games.

import argparse
import datetime as dt
import os
import sys
import textwrap

class Fix:
    needed = False

    def write_file(self, fn):
        try:
            fd = open(fn, "wb")
        except IOError as err:
            print(err)
            sys.exit(1)

        new_cksum = 0
        for b in range(0x40, self.gamefile.gamesize):
            new_cksum += self.contents[b]

        new_cksum %= 0x10000
        w = make_zword(new_cksum)
        self.set_byte(0x1c, w[0])
        self.set_byte(0x1d, w[1])

        new_serial = dt.datetime.now().strftime("%y%m%d")
        for i in range(6):
            self.set_byte(18 + i, ord(new_serial[i]))
        fd.write(self.contents)

    def set_byte(self, addr, byte):
        fcontents = self.contents
        fcontents[addr] = byte
        self.contents = fcontents

    def name(self):
        return self.game_name

    def description(self):
        return self.desc

class Zork_fix(Fix):
    def __init__(self, gf):
        self.game_name = "Zork"

class Lurking_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.game_name = "Lurking Horror"
        self.desc = ("In Lurking Horror, one must log into the computer with a user/pass from "
                    "the feelies. Here we set it so any input will work.")

    # All version verified to work - 2021-01-31
    def fix(self):
        if self.gamefile.release == 203:
            start = 0x18251
            zw = make_zword(65536 - (0x18251 - 0x18180 + 1))
        elif self.gamefile.release == 219 or self.gamefile.release == 223:
            # These differ in trivial ways
            start = 0x18485
            zw = make_zword(65536 - (0x18485 - 0x183b4 + 1))
        else:
            print("Unknown Lurking Horror version? Bug?")
            return 0

        self.set_byte(start, 0x8c)
        self.set_byte(start + 1, zw[0])
        self.set_byte(start + 2, zw[1])
        return 1

class Sorcerer_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        elf.game_name = "Sorcerer"
        self.desc = ("In Sorcerer, the copy protection consists of an Infotater wheel "
                "where the player looks up one of 12 monsters and gets a color code "
                "for pushing buttons to open a trunk. "
                "We fix this by making an unconditional jump, so that no matter what "
                "button you press, it will always open the trunk.")


    # All version verified to work - 2021-01-31
    def fix(self):
        zw = make_zword(-58)
        if self.gamefile.release == 67: # both versions the same
            start = 0xfadc
        elif self.gamefile.release == 85:
            start = 0xfcc6
        elif self.gamefile.release == 4:
            start = 0xfbf6
        elif self.gamefile.release == 6:
            start = 0xfb92
        elif self.gamefile.release == 13:
            start = 0xfae2
        elif self.gamefile.release == 15:
            start = 0xfad8
        elif self.gamefile.release == 18:
            start = 0x10434
        else:
            print("BUG?? Unknown Sorcerer version.")
            return 0
        self.set_byte(start, 0x8c)
        self.set_byte(start+1, zw[0])
        self.set_byte(start+2, zw[1])
        return 1
        

games = {
    ("870506", 203) : Lurking_fix,
    ("870912", 219) : Lurking_fix,
    ("870918", 221) : Lurking_fix,

    ("000000", 67) : Sorcerer_fix,
    ("831208", 67) : Sorcerer_fix,
    ("840106", 85) : Sorcerer_fix,
    ("840131", 4) : Sorcerer_fix,
    ("840508", 6) : Sorcerer_fix,
    ("851021", 13) : Sorcerer_fix,
    ("851108", 15) : Sorcerer_fix,
    ("860904", 18) : Sorcerer_fix,

    ("000000", 5) : Zork_fix,
    ("000000", 20) : Zork_fix,
    ("000000", 20) : Zork_fix,
    ("820428", 23) : Zork_fix,
    ("820515", 25) : Zork_fix,
    ("820803", 26) : Zork_fix,
    ("821013", 28) : Zork_fix,
    ("830330", 30) : Zork_fix,
    ("830929", 75) : Zork_fix,
    ("840509", 76) : Zork_fix,
    ("840509", 76) : Zork_fix,
    ("840726", 88) : Zork_fix,
    ("840726", 88) : Zork_fix,
    ("871125", 52) : Zork_fix,
    ("880113", 3) : Zork_fix,
    ("880429", 119) : Zork_fix,
    ("890613", 15) : Zork_fix,
    ("AS000C", 2) : Zork_fix,
    ("840330", 15) : Zork_fix,
    ("UG3AU5", 15) : Zork_fix,
    ("820308", 15) : Zork_fix,
    ("820427", 17) : Zork_fix,
    ("820517", 18) : Zork_fix,
    ("820721", 19) : Zork_fix,
    ("830331", 22) : Zork_fix,
    ("830411", 23) : Zork_fix,
    ("840518", 22) : Zork_fix,
    ("840904", 48) : Zork_fix,
    ("860811", 63) : Zork_fix,
    ("UG3AU5", 7) : Zork_fix,
    ("820818", 10) : Zork_fix,
    ("821025", 12) : Zork_fix,
    ("830331", 15) : Zork_fix,
    ("830410", 16) : Zork_fix,
    ("840518", 15) : Zork_fix,
    ("840727", 17) : Zork_fix,
    ("860811", 25) : Zork_fix,

}

def word(w):
    return w[0] * 256 + w[1]

def make_zword(n):
    if n < 0:
        n = 65536 + n
    return (n // 256, n % 256)

class Gamefile:
    def __init__(self, fn):
        self.filename = fn

        try:
            fd = open(fn, "rb")
        except IOError as err:
            print(err)
            sys.exit(1)

        self.contents = contents = fd.read()
        
        if len(self.contents) < 0x40:
            print("{fn}: too short to be Infocom game file".format(fn=fn))
            sys.exit(1)

        self.zcode_version = self.contents[0]
        if self.zcode_version >= 6:
            print("{fn}: not a zmachine file (version too high)".format(fn=fn))

        self.serial = contents[18:24].decode("ascii")
        self.release = word(contents[2:4])
        self.gamesize = word(contents[0x1a:0x1c])
        if 1 <= self.zcode_version <= 3:
            self.gamesize *= 2
        elif 4 <= self.zcode_version <= 5:
            self.gamesize *= 4
        else:
            self.gamesize *= 8

        if len(self.contents) < self.gamesize:
            print("{0}: file is truncated (less than header gamesize)".format(fn))
            sys.exit(1)
        

def main(args):
    gf = Gamefile(args.gamefile)

    identifier = (gf.serial, gf.release)

    if identifier not in games:
        print("Not in my database: Serial={0}/Release={1}/Filesize=0x{2:05X}/zvers={3}".format(gf.serial, gf.release, len(gf.contents), gf.zcode_version))
        return

    fix = games[identifier](gf)
    if not fix.needed:
        print("{0} does not have copy protection.".format(fix.name()))
        return

    col = os.get_terminal_size().columns
    print(fix.name().center(col))
    print()
    print("\n".join(textwrap.wrap(fix.description(), width=col)))

    if args.dryrun:
        return
    
    if not fix.fix():
        return
    fix.write_file(args.destination)
    print("\n{0}: written".format(args.destination))
    
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Remove copy protection from infocom games")
    ap.add_argument("-l", "--list", action="store_true", help="List Infocom games")
    ap.add_argument("-d", "--dryrun", action="store_true", help="Check game, do not modify")
    ap.add_argument("gamefile", help="Infocom game file")
    ap.add_argument("destination", help="Where to write fixed version")

    args = ap.parse_args()
    if args.destination == args.gamefile:
        print("Destination and source cannot be the same: {0}".format(args.gamefile))
        sys.exit(1)
    main(args)
    sys.exit(0)