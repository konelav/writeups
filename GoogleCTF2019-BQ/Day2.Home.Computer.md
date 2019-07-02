Your Choice!


    Having found the information you were looking for, while detailed, 
    it presents you with an interesting dilemma. There is a network of 
    "computers" not completely dissimilar to your computrator-machine 
    on your ship. You find yourself in possession of the credentials of 
    an individual on the planet named "SarahH." Great, with these you 
    can get right into the secret world of an earthling without them 
    knowing you're there. You access "SarahH home network," to find two 
    computers: "work" and "home." Not knowing what either of these are, 
    you have to make a decision.


No decisions, no compromises - we will hack both. Or else why we are 
sitting with laptop at home in such a great summer weekend?

Start with Home computer (easier).

Home Computer (**forensics**)

    Blunderbussing your way through the decision making process, you 
    figure that one is as good as the other and that further research 
    into the importance of Work Life balance is of little interest to 
    you. You're the decider after all. You confidently use the 
    credentials to access the "Home Computer."

    Something called "desktop" presents itself, displaying a 
    fascinating round and bumpy creature (much like yourself) labeled  
    "cauliflower 4 work - GAN post."  Your 40 hearts skip a beat.  It 
    looks somewhat like your neighbors on XiXaX3.   ..Ah XiXaX3... 
    You'd spend summers there at the beach, an awkward kid from 
    ObarPool on a family vacation, yearning, but without nerve, to talk 
    to those cool sophisticated locals.

    So are these "Cauliflowers" earthlings? Not at all the unrelatable 
    bipeds you imagined them to be.  Will they be at the party?  
    Hopefully SarahH has left some other work data on her home computer 
    for you to learn more.

Unzipping attachment we can see technical `note.txt` that is not for me.
And `family.ntfs`, the name of this file speaks for itself, but we can 
check it:

    $ file family.ntfs 
    family.ntfs: DOS/MBR boot sector, code offset 0x52+2, OEM-ID "NTFS    ", sectors/cluster 8, Media descriptor 0xf8, sectors/track 0, dos < 4.0 BootSector (0x80), FAT (1Y bit by descriptor); NTFS, sectors 51199, $MFT start cluster 4, $MFTMirror start cluster 3199, bytes/RecordSegment 2^(-1*246), clusters/index block 1, serial number 072643f694104cb6f

Ok, just mount it then.

    $ mkdir ntfs
    $ sudo mount family.ntfs ntfs

Quick look tells us that partition is full of empty files. Do find 
non-empty with `find` utility:

    $ find ntfs -size +0 -type f
    ntfs/Users/Family/Documents/credentials.txt
    $ cat ntfs/Users/Family/Documents/credentials.txt 
    I keep pictures of my credentials in extended attributes.

Well, reading file attributes is extremely easy:

    $ getfattr --only-values ntfs/Users/Family/Documents/credentials.txt > attrs
    $ file attrs
    attrs: PNG image data, 1234 x 339, 8-bit/color RGB, non-interlaced

Open it with any image viewer and get the flag:

**CTF{congratsyoufoundmycreds}**
