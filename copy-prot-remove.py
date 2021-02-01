#!/usr/bin/python3

# Left to do:
# Ballyhoo (have a fix already)
# Border Zone (don't remember)
# Cutthroats (have a complicated fix)
# Infidel (I was unable to find a good solution in the 1990s--try again?)
# Seastalker 
# Shogun (ugh... I don't remember)
# Stationfall (have a fix already)
# Zork Zero (TONS of copy protection--need to review)
# Moonmist (impossible, utterly impossible)
# Wishbringer (Matchbook desc and telegram)

# Suspended (no copy prot)
# Suspect (No copy protection)
# Trinity (no copy protection per se--though it helps)
# Witness (no copy protection?)
# HH Guide (no copy prot)
# Beyond Zork (No copy prot? I don't recall)
# Plundered Hearts (no copy prot)
# Sherlock (No copy prot? Don't know very well)


# Version 0.1
# Master copy here: https://github.com/allengarvin/infocom-copy-protection

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

# Including these, because occasionally there is text like "See the manual", to save space.
# If the game file is not close to the zmachine limit, I should be able to encoude a new zstring
# and append to the end of the file, then switch out the address reference.

class Witness_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Witness"
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.desc = ("The Witness has a matchbook and note. I'll encode these in new strings and add to the "
                     "end of the file, then change the description addresses.")

    def fix(self):
        note_text = "Monica dearest,\n\nI can live with this sadness no longer. For twenty nine years, your father has lived his own life without me. Now I am taking the only way out.\n\nMonica, you musn't blame yourself in any way for what I am about to do. Nor should you blame Ralph. The affair with him was only a futile attempt to prove I was a woman, not just a piece in Freeman's collection.\n\nTell your illustrious father how deeply I regret soiling one of his precious revolvers.\n\nMonica\n"
        matchbook_text = "Chandler 1729"

        print("I haven't written the zscii encode routines yet.")

class Seastalker_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Seastalker"
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.desc = ("Seastalker has no explicit copy-prot, but it does have a lot of text that you have to "
                     "read from the feelies. I'm going to fix up the object descriptions and encrypt in new "
                     "strings, added to the end of the game file.")

    def fix(self):
        tip_text = "Tip is your closest pal and constant companion. Basically, there's nothing this guy can't do. He's an expert pilot, submariner, surfer, and swimmer. He's more of a jock than an inventor such as yourself, but his bulldog courage and rollicking high spirits make him a great companion in any adventure."
        bly_text = "This woman's delicate beauty is hard to resist, but when you start to talk to her--wow, what a tough one she is. For one thing, she's a champion athlete and a superachiever. For the past three months now, she's been commander at the Aquadome. She's an honor graduate of the Navy Frogman School and the Galley Institute of Technology. You'll see soon enough that she doesn't have much patience with people who don't meet her standards. And that attitude tends to make some people real mad."
        mick_text = "Mick was probably out earning a buck before most of us were born. In fact, you won't find anybody who knows more about nuclear power, undersea navigation, or communications. That's pretty good for a guy who never had a formal education. But Mick doesn't like to settle arguments with his tongue; he'd rather use his fists. Naturally, he doesn't take well to Commander Bly's kind of discipline."
        bill_text = "Bill comes from a different background altogether. Basically, he used to be a beach bum with a knack for scuba diving and \"shade tree\" mechanic work. Now he's joined society in a big way. He's cut his hair and found himself a job as a crack scuba diver at the Aquadome."
        horvak_text = "Walt's probably the most dedicated scientist around, so dedicated that sometimes you get the impression he's a loner. He's always working on some new experiment or scuba diving. Walt doesn't look like the \"doctor\" type, but he spent a lot of time working in a hospital before he got interested in marine biochemistry. If you're looking for any kind of medical advice, he's the one to ask."
        sharon_text = "She's fresh out of college--The Massachusetts Institute of Technology. Naturally, she's pretty familiar with all types of science and technology, and this job as an inventor's assistant fits her well. Her father was a famous college professor and an old friend of your father's. In fact, sometimes you get the feeling that she's your own sister. But there's something about her that you can't get close to."
        amy_text = "She's a Navy woman through and through. Always a tomboy at heart, Amy's been to the Navy Frogman School and had lots of neat jobs like this one. She's still in college at Columbia University and works at the Aquadome during the summer."
        jerome_text = "Dr. Thorpe is one of those scientific geniuses who lock themselves up in their labs and discover things. Unfortunately, sometimes the things they discover or create aren't too good. Thorpe's claim to fame is his AH (AMINO-HYDROPHASE) organisms that he supposedly manufactured from the AH molecule. There's an interesting article about him and his experiments in the Science World magazine."


        computestor_text = "It's a machine for troubleshooting your own inventions, machines, or systems. It is connected to several other machines in the lab. To use it type ASK COMPUTESTOR ABOUT (a device)."
        print("I haven't written the zscii encode routines yet.")

class Zork_fix(Fix):
    def __init__(self, gf):
        self.game_name = "Zork"

class Deadline_fix(Fix):
    def __init__(self, gf):
        self.game_name = "Deadline"

class Enchanter_fix(Fix):
    def __init__(self, gf):
        self.game_name = "Enchanter"

class AMFV_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.game_name = "AMFV"
        self.desc = ("AMFV uses a code wheel where you match and type in an integer code."
                     " This fix will reverse the branching, so an correct answer will fail, "
                     " and an incorrect will always pass.")

    # UNTESTED
    def fix(self): 
        if self.gamefile.release == 1:
            print("Release 1 is a very early beta with no copy protection.")
            return 0
        elif self.gamefile.release == 47 or self.gamefile.release == 131:
            print("Game file is corrupt. I haven't been able to get it working.")
            return 0
        elif self.gamefile.release == 84:
            print("Release 84 is a beta version that tells you to just type '99'")
            return 0
        elif self.gamefile.release == 77:
            self.set_byte(0x334fb, self.contents[0x334fb] | 128)
            self.set_byte(0x33503, self.contents[0x33503] | 128)
        elif self.gamefile.release == 79:
            self.set_byte(0x3350b, self.contents[0x3350b] | 128)
            self.set_byte(0x3350f, self.contents[0x3350f] | 128)
        else:
            print("BUG? Uknown AMFV version")
            return 0
        return 1

class Starcross_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.game_name = "Starcross"
        self.desc = ("Starcross was the first Infocom game with copy protection in the feelies, "
                     "for coordinates to the mysterious 'mass'. Here, we'll modify the file so that "
                     "no matter what destination you put in, you will always end up at the Artifact.")

    # UNTESTED
    def fix(self):
        # We change every "je" branch statement so that no matter where you
        # punch a coordinate, you go to the space ship

        if self.gamefile.release == 15:
            self.set_byte(0x8105, 0x19)
            self.set_byte(0x8108, 0x1a)

            self.set_byte(0x9269, 0x1a)
            self.set_byte(0x930e, 0x1a)

            self.set_byte(0x9435, 0x1a)

            self.set_byte(0xbc50, 0x1a)
            return 1
        if self.gamefile.release == 17:
            self.set_byte(0x8057, 0x19)
            self.set_byte(0x805a, 0x1a)

            self.set_byte(0x914f, 0x1a)
            self.set_byte(0x91f4, 0x1a)

            self.set_byte(0x930f, 0x1a)

            self.set_byte(0xba29, 0x1a)
            return 1
        if self.gamefile.release == 18:
            pass
            # DOOO THIS VERSION!!!!!!!
        
class Arthur_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.game_name = "Arthur"
        self.desc = ("With Arthur, we change it so that every password is correct.")

    # UNTESTED
    def fix(self):
        if self.gamefile.release == 74:
            start = 0x1e01e
        elif self.gamefile.release == 63:
            start = 0x1e63e
        elif self.gamefile.release == 54:
            start = 0x1e42e
        elif self.gamefile.release == 41:
            start = 0x1cb12
        else:
            print("BUG? Unknown Arthur")
            return 0
        self.set_byte(start, 0xff)
        self.set_byte(start + 1, 0xc1)
        return 1

class Spellbreaker_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        self.game_name = "Spellbreaker"
        self.desc = ("Spellbreaker uses several wizard cards describing big-name wizards, "
                     "and Belboz cite their attributes expecting a name back. We change it so "
                     "that he always thinks you're genuine, not a fake version of you.")

    # UNTESTED
    def fix(self):
        if self.gamefile.release == 63:
            start = 0x10fc4
        elif self.gamefile.release == 86:
            start = 0x11038
        elif self.gamefile.release == 87:
            start = 0x1102c
        else:
            print("Bug? This is an unknown release of Spellbreaker")
            return 0
        self.set_byte(start, 0xff)
        self.set_byte(start + 2, 36)
        return 1
        
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

class Bureaucracy_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.gamefile = gf
        self.contents = bytearray(gf.contents)
        elf.game_name = "Bureaucracy"
        selfdesc = ("I got this fix from Mark Knibb's patches from ftp.gmd.de/ifarchive.")

    # Untested
    def fix(self):
        if self.gamefile.release == 86:
            start1, start2 = 0x27640, 0x27668
        elif self.gamefile.release == 116:
            start1, start2 = 0x27691, 0x276BB
        elif self.gamefile.release == 160:
            print("This throws an exception in txd, so I haven't done it yet. I'm working on a txd replacement.")
            print("Fatal: too many orphan code fragments")
            return 0
        for addr in range(start1, start1 + 5):
            self.set_byte(addr, 0xb4)
        for addr in range(start2, start2 + 3):
            self.set_byte(addr, 0xb4)
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
    ("841226", 1) :   AMFV_fix,
    ("850313", 47) :  AMFV_fix,
    ("850516", 84) :  AMFV_fix,
    ("850628", 131) : AMFV_fix,
    ("850814", 77) :  AMFV_fix,
    ("851122", 79) :  AMFV_fix,

    ("830524", 13) : Witness_fix,
    ("830910", 18) : Witness_fix,
    ("831119", 20) : Witness_fix,
    ("831208", 21) : Witness_fix,
    ("840924", 22) : Witness_fix,
    ("840925", 23) : Witness_fix,

    ("870506", 203) : Lurking_fix,
    ("870912", 219) : Lurking_fix,
    ("870918", 221) : Lurking_fix,

    ("000000", 67) : Sorcerer_fix,
    ("831208", 67) : Sorcerer_fix,
    ("840106", 85) : Sorcerer_fix,
    ("840131", 4) :  Sorcerer_fix,
    ("840508", 6) :  Sorcerer_fix,
    ("851021", 13) : Sorcerer_fix,
    ("851108", 15) : Sorcerer_fix,
    ("860904", 18) : Sorcerer_fix,

    ("890502", 40) : Arthur_fix,
    ("890504", 41) : Arthur_fix,
    ("890606", 54) : Arthur_fix,
    ("890622", 63) : Arthur_fix,
    ("890714", 74) : Arthur_fix,

    ("820311", 18) : Deadline_fix,
    ("820427", 19) : Deadline_fix,
    ("820512", 21) : Deadline_fix,
    ("820809", 22) : Deadline_fix,
    ("821108", 26) : Deadline_fix,
    ("831005", 27) : Deadline_fix,
    ("850129", 28) : Deadline_fix,

    ("830810", 10) : Enchanter_fix,
    ("831107", 15) : Enchanter_fix,
    ("831118", 16) : Enchanter_fix,
    ("840518", 16) : Enchanter_fix,
    ("851118", 24) : Enchanter_fix,
    ("860820", 29) : Enchanter_fix,
    ("850916", 63) : Spellbreaker_fix,
    ("860829", 86) : Spellbreaker_fix,
    ("860904", 87) : Spellbreaker_fix,
    ("820901", 15) : Starcross_fix,
    ("821021", 17) : Starcross_fix,
    ("830114", 18) : Starcross_fix,

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
    ("880113", 3) :  Zork_fix,
    ("880429", 119): Zork_fix,
    ("890613", 15) : Zork_fix,
    ("AS000C", 2) :  Zork_fix,
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
    ("UG3AU5", 7) :  Zork_fix,
    ("820818", 10) : Zork_fix,
    ("821025", 12) : Zork_fix,
    ("830331", 15) : Zork_fix,
    ("830410", 16) : Zork_fix,
    ("840518", 15) : Zork_fix,
    ("840727", 17) : Zork_fix,
    ("860811", 25) : Zork_fix,

    ("840320", 86) : Seastalker_fix,
    ("840501", 15) : Seastalker_fix,
    ("840522", 15) : Seastalker_fix,
    ("840612", 15) : Seastalker_fix,
    ("840716", 15) : Seastalker_fix,
    ("850208", 17) : Seastalker_fix,
    ("850515", 16) : Seastalker_fix,
    ("850603", 16) : Seastalker_fix,
    ("850919", 18) : Seastalker_fix,

    ("870212", 86) :  Bureaucracy_fix,
    ("870602", 116) : Bureaucracy_fix,
    ("880521", 160) : Bureaucracy_fix,

}

def make_zword(n):
    if n < 0:
        n = 65536 + n
    return (n // 256, n % 256)

class Zscii:
    alphabet = [
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        " \n0123456789.,!?_#'\"/\\-:()"
    ]
    
    def alphabet_number(c):
        for i in range(3):
            for j in range(26):
                if self.alphabet[i][j] == c:
                    return i

        # Let's see if we can get by without implementing complete ascii or utf8 encoding, for now
        print("Text encode: alphabet_number() unable to find `{:s}' (ord: {:d}) in alphabet\n".format(c, ord(c)))
        sys.exit(0)

    def string_index(c):
        for i in range(3):
            for j in range(26):
                if self.alphabet[i][j] == c:
                    return j
        print("Text encode: alphabet_number() unable to find `{:s}' (ord: {:d}) in alphabet\n".format(c, ord(c)))
        sys.exit(0)
        
    def encode_text(s):
        zchars = len(s) * 2 + 1
        # will do later

def word(w):
    return w[0] * 256 + w[1]

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
