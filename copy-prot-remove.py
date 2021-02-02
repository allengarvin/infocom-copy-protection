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

# Suspended (no copy prot, but hard to play without the package)
# Suspect (No copy protection, but some text referring to the package)
# Trinity (no copy protection per se--though it helps)
# HH Guide (no copy prot)
# Beyond Zork (No copy prot? I don't recall -- I guess the book?)
# Plundered Hearts (no copy prot)
# Sherlock (No copy prot? Don't know very well)

# Version 0.1
# Master copy here: https://github.com/allengarvin/infocom-copy-protection

# Copyright 2021 "Allen Garvin" <aurvondel@gmail.com>
# License: 3-clause BSD

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

        if self.gamefile.zcode_version == 3:
            w = make_zword(self.gamesize // 2)
        elif 4 <= self.gamefile.zcode_vesion <= 5:
            w = make_zword(self.gamesize // 4)
        else:
            w = make_zword(self.gamesize // 8)
        self.set_byte(0x1a, w[0])
        self.set_byte(0x1b, w[1])

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

class Infidel_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Infidel"
        self.gamefile = gf
        self.gamesize = gf.gamesize
        self.contents = bytearray(gf.contents)
        self.desc = "Infidel relies on the game map to give coordinates. Here, I'll add those to the description of the map."

    def fix(self):
        print("This one will be a bit difficult. It uses a print_ret so we'll need to fit it less than the number of bytes in the function")
        print("If it's not exact, txd will choke (I think the game should still function, but it seems rude to break tools)")

#        The code is:
#        print_ret "This is a reproduction of the map the Professor made while on his expedition. It indicates where he hoped to find the lost pyramid. It is included in your game package."
#
#        We want to change to something like: 
#        The map records that he found the hieroglyphic cube at longitude 12'43\" and latitude 11'3\" on 27 September 1920.";
        return 0

class Stationfall_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Stationfall"
        self.gamefile = gf
        self.gamesize = gf.gamesize
        self.contents = bytearray(gf.contents)
        self.desc = ("Like Starcross, Stationfall needs coordinates from the documentation. We'll set it up so that "
                     "every coordinate leads to the space station.")

    # untested
    def fix(self):
        if self.gamefile.release == 1:
            print("This beta version has issues. TXD exits, and I'm not sure if it has protection anyway.")
            return 0

        elif self.gamefile.release == 107:
            self.set_byte(0xbee0, 0x6c)
            self.set_byte(0xbef4, 1)
            return 1
        else:
            print("This will take some study on my part--it relies on global variable settings.")
            return 0


class Witness_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Witness"
        self.gamefile = gf
        self.gamesize = gf.gamesize
        self.contents = bytearray(gf.contents)
        self.desc = ("The Witness has a matchbook and note. I'll encode these in new strings and add to the "
                     "end of the file, then change the description addresses.")

    def fix(self):
        note_text = "Monica dearest,\n\nI can live with this sadness no longer. For twenty nine years, your father has lived his own life without me. Now I am taking the only way out.\n\nMonica, you musn't blame yourself in any way for what I am about to do. Nor should you blame Ralph. The affair with him was only a futile attempt to prove I was a woman, not just a piece in Freeman's collection.\n\nTell your illustrious father how deeply I regret soiling one of his precious revolvers.\n\nMonica\n"
        matchbook_text = "Written on the inner fold of the matchook is \"Chandler 1729\"."

        if self.gamefile.release == 23:
            matchbook_read_addr = 0xfd5
        else:
            print("I haven't written the zscii encode routines yet.")
            return 0

        bytes = self.gamefile.zscii.encode_text(matchbook_text)

        # zmachine 3 is packed with doubles:
        str_addr = self.gamesize // 2
        self.contents += bytes
        self.gamesize += len(bytes)
        self.contents[matchbook_read_addr:matchbook_read_addr+2] = [str_addr >> 8, str_addr & 255]
        return 1

        

class Seastalker_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Seastalker"
        self.gamefile = gf
        self.gamesize = gf.gamesize
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

class Moonmist_fix(Fix):
    needed = True

    def __init__(self, gf):
        self.game_name = "Moonmist"
        slef.desc = ("Moonmist has numerous references to the manuals, but the game is very very close to the max filesize for "
                     "z3 games. The best bet would be to port it to zmachine 4 and compile it with no text, but that's outside "
                     "the scope for this game.")

    def fix(self):
        return 0


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
        self.gamesize = gf.gamesize
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
        self.gamesize = gf.gamesize
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
        self.gamesize = gf.gamesize
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
        self.gamesize = gf.gamesize
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
        self.gamesize = gf.gamesize
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
        self.gamesize = gf.gamesize
        elf.game_name = "Bureaucracy"
        selfdesc = ("I got this fix from Mark Knibb's patches from ftp.gmd.de/ifarchive.")

    # Untested
    def fix(self):
        if self.gamefile.release == 86:
            start1, start2 = 0x27640, 0x27668
        elif self.gamefile.release == 116:
            start1, start2 = 0x27691, 0x276BB
        elif self.gamefile.release == 160:
            print("This throws an exception in txd, so I haven't done it yet. I'm working on a txd replacement so perhaps I can figure out why. The game still plays.")
            print("TXD's error is: Fatal: too many orphan code fragments")
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
        self.gamesize = gf.gamesize
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
        
def word(w):
    return w[0] * 256 + w[1]
    
# I removed the part from z1 and z2. For full version, see my ztools
class Zscii:
    modern_zscii = [
      " ^^^^^abcdefghijklmnopqrstuvwxyz ",
      " ^^^^^ABCDEFGHIJKLMNOPQRSTUVWXYZ ",
      " ^^^^^ \n0123456789.,!?_#'\"/\\-:() ",
    ]

    story = None

    def __init__(self, s_obj):
        self.story = s_obj
        self.bytes_read = None

        v = s_obj.header["version"]
        self.zscii = self.modern_zscii

    
    def convert_zscii_bytes(self, bytes):
        zstring = ""
        shift, abbrev_flag, ascii_flag = -1, False, False

        v = self.story.header["version"]
        zscii = self.zscii

        for i, b in enumerate(bytes):
            if ascii_flag:
                ascii_flag = False
                i += 1
                if i == len(bytes):
                    return zstring
                zstring += chr(bytes[i-1] << 5 | b)
                continue
            if abbrev_flag:
                ndx = 32 * (bytes[i-1]-1) + b
                zstring += self.story.abbreviations[ndx]
                #print("ABBREV", self.story.abbreviations[ndx], ndx, "pre-byte", bytes[i-1], "byte", b)
                abbrev_flag = False
                shift = -1
                continue

            if b == 0:
                zstring += " "
                continue
            elif b == 1:
                if v < 2:
                    zstring += "\n"
                else:
                    abbrev_flag = True
                continue
            elif b == 2:
                abbrev_flag = True
                continue
            elif b == 3:
                abbrev_flag = True
                continue
            elif b == 4:
                shift = 1
                abbrev_flag = False
                continue
            elif b == 5:
                shift = 2
                abbrev_flag = False
                continue
            elif b == 6:
                if shift == 2:
                    shift = -1
                    ascii_flag = True
                    continue

            if shift > -1:
                zstring += zscii[shift][b]
            else:
                zstring += zscii[0][b]
            shift = -1
            abbrev_flag = False
        return zstring

    modern_zscii_convert = [
      "abcdefghijklmnopqrstuvwxyz ",
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ ",
      " \n0123456789.,!?_#'\"/\\-:() ",
    ]

    def find_char(self, c):
        for i, alphabet in enumerate(self.modern_zscii_convert):
            if c in alphabet:
                return i, alphabet.index(c) + 6

        return None, None

    def convert_to_bytes(self, text):
        i = 0
        bytes = []

        while i < len(text):
            aflag = False
            for ndx, abbr in enumerate(self.story.abbreviations):
                if text[i:].startswith(abbr):
                    a, b = divmod(ndx, 32)
                    #print("ABBR", abbr, a, b)
                    bytes.append(a+1)
                    bytes.append(b)
                    i += len(abbr)
                    aflag = True
                    break
            if aflag:
                continue
            if text[i] == ' ':
                bytes.append(0)
                i += 1
                continue
            alphabet, ndx = self.find_char(text[i])
            if alphabet == None:
                print("Char `{}': ASCII functionality not yet added. See zscii class.".format(text[i]))
                return None
            if alphabet:
                bytes.append(3 + alphabet)
            bytes.append(ndx)
            i += 1
        if len(bytes) % 3:
            bytes += [5] * (3 - len(bytes) % 3)
            #bytes.append(5)

        return bytes

    def encode_bytes(self, bytes):
        it = iter(bytes)
        
        zs = bytearray()
        for c1 in it:
            c2 = next(it)
            c3 = next(it) 
            w = (c1 << 10) | (c2 << 5) | c3
            zs.append(w >> 8)
            zs.append(w & 255)
        zs[-2] |= 2 ** 7

        return zs
        
    def encode_text(self, text):
        bytes = self.convert_to_bytes(text)
        return self.encode_bytes(bytes)

    def read_text(self, addr, len, inform_escapes=False, full_return=False):
        bytes = []
        real_bytes = []
        
        i = 0
        for i in range(len):
            w = word(self.story.contents[addr + i * 2:addr + i * 2 + 2])
            real_bytes = real_bytes + [(w >> 8, w & 255)]
            bit = w >> 15
            c3 = w & 31
            c2 = (w & 0x3e0) >> 5
            c1 = (w & 0x7c00) >> 10

            bytes += [ c1, c2, c3 ]
            if bit: 
                i += 1
                break

        self.bytes_read = i * 2
        zs = self.convert_zscii_bytes(bytes)
        if inform_escapes:
            zs = zs.replace('"', "~").replace("\n", "^")
        if full_return:
            return self.bytes_read, bytes, real_bytes, zs
        return zs

class Story:
    zscii = False
    configuration = None

    def fatal(self, s):
        print("{0}: {1}".format(self.filename, s))
        sys.exit(1)
        
    def parse_header(self):
        h = self.header = dict()
        c = self.contents

        if 0 < c[0] < 9:
            h["version"] = version = c[0]
            self.zcode_version = version
        else:
            self.fatal("unknown zmachine version (byte 0x00={:d}, expecting 1-8)".format(c[0]))

        h["flags"] = c[1]
        h["release"] = word(c[2:4])
        h["highmem"] = word(c[4:6])
        h["pc"]      = word(c[6:8])
        h["dict"]    = word(c[8:10])
        h["otable"]  = word(c[0xa:0xc])
        h["globals"] = word(c[0xc:0xe])
        h["static"]  = word(c[0xe:0x10])
        h["gflags"]  = word(c[0x10:0x12])
        h["serial"]  = c[18:24].decode("utf-8")
        if version >= 2:
            h["abbr"]    = word(c[0x18:0x1a])
        else:
            h["abbr"] = None
        h["filelen"] = word(c[0x1a:0x1c])
        h["cksum"]   = word(c[0x1c:0x1e])

        # reasons: I'll clean up later
        self.release = h["release"]
        self.serial = h["serial"]
        self.gamesize = h["filelen"]
        if 1 <= self.zcode_version <= 3:
            self.gamesize *= 2
        elif 4 <= self.zcode_version <= 5:
            self.gamesize *= 4
        else:
            self.gamesize *= 8
        if len(self.contents) < self.gamesize:
            print("{0}: file is truncated (less than header gamesize)".format(fn))
            sys.exit(1)

    def read_high(self, addr):
        n, b, rb, s = self.zscii.read_text(addr, 0xffff, full_return=True)
#        print(n)
#        print("literal bytes", rb)
#        print("binary literal bytes", ["({:08b},{:08b})".format(x[0], x[1]) for x in rb])
#        print("5-bit zbytes", ["{:05b}".format(x) for x in b])
#        print("zbytes", b)
#        print(s)
        return b, s

    def __init__(self, storyfile):
        self.filename = storyfile
        try:
            fd = open(storyfile, "rb")
        except OSError as err:
            self.fatal(err)

        self.contents = fd.read()
        if len(self.contents) < 0x40:
            self.fatal("story file too short to be zmachine file")

        self.abbreviations = None
        self.addr_to_dict = dict()

        self.parse_header()

        self.zscii = Zscii(self)
        self.read_abbreviations()

    def read_abbreviations(self):
        v = self.header["version"]
        hi, lo = -1, 0x7ffff

        if v == 1:
            return

        z = self.zscii
        addr = self.header["abbr"]
        if not addr:
            return

        max_a = 32 if v == 2 else 96
        abbr = self.abbreviations = [0] * max_a

        zo = self.zscii
        for i in range(max_a):
            abbr[i] = z.read_text(word(self.contents[addr:addr+2]) * 2, 753)
            lo = min(word(self.contents[addr:addr+2]) * 2, lo)
            hi = max(word(self.contents[addr:addr+2]) * 2 + z.bytes_read - 1, hi)
            addr += 2

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

    ("861017", 1)   : Stationfall_fix,
    ("870218", 63)  : Stationfall_fix,
    ("870326", 87)  : Stationfall_fix,
    ("870430", 107) : Stationfall_fix,

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

    ("000000", 65) : Moonmist_fix,
    ("860918", 4) :  Moonmist_fix,
    ("861022", 9) :  Moonmist_fix,
    ("880501", 13) : Moonmist_fix,

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

    ("830916", 22) : Infidel_fix,
    ("840522", 22) : Infidel_fix,

}

def make_zword(n):
    if n < 0:
        n = 65536 + n
    return (n // 256, n % 256)

# class Gamefile:
#     def __init__(self, fn):
#         self.filename = fn
# 
#         try:
#             fd = open(fn, "rb")
#         except IOError as err:
#             print(err)
#             sys.exit(1)
# 
#         self.contents = contents = fd.read()
#         
#         if len(self.contents) < 0x40:
#             print("{fn}: too short to be Infocom game file".format(fn=fn))
#             sys.exit(1)
# 
#         self.zcode_version = self.contents[0]
#         if self.zcode_version >= 6:
#             print("{fn}: not a zmachine file (version too high)".format(fn=fn))
# 
#         self.serial = contents[18:24].decode("ascii")
#         self.release = word(contents[2:4])
#         self.gamesize = word(contents[0x1a:0x1c])
#         if 1 <= self.zcode_version <= 3:
#             self.gamesize *= 2
#         elif 4 <= self.zcode_version <= 5:
#             self.gamesize *= 4
#         else:
#             self.gamesize *= 8
# 
#         if len(self.contents) < self.gamesize:
#             print("{0}: file is truncated (less than header gamesize)".format(fn))
#             sys.exit(1)
        

def main(args):
    gf = Story(args.gamefile)

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
