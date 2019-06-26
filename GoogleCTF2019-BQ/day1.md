Arrival & Reconnaissance


    Having successfully figured out this "coordinate" problem. The ship 
    lurches forward violently into space. This is one of the moments 
    when you realize that some kind of thought or plan would have been 
    good, but typically for you and how you found yourself in this 
    situation, you didn't think too much before acting. Only the stars 
    themselves know where you'll end up.

    After what seems like an eternity, or at least one full season of 
    "Xenon's Next Top Galactic Overlord" you arrive in a system of 9 
    planetary bodies, though one of them is exceptionally small. You 
    nostalgically remember playing explodatoid with your friends and 
    hunting down planets like this. But this small planet registers a 
    hive of noise and activity on your ships automated scanners. 
    There's things there! Billions upon trillions of things, moving 
    around, flying, swimming, sliding, falling.

    Of particular interest may be the insect-like creatures flying 
    around this planet, uniformly. One has the words "Osmium 
    Satellites" written on it. Maybe this is a starting point to get to 
    know what's ahead of you.


We can choose not to inspect Osmium immidiately. In this case there 
will be an additional task.

Ad (**ad**)

    We interrupt this program for a commercial break

    https://www.youtube.com/watch?v=QzFuwljOj8Y 
    
Looking short video it can be seen that there are many fast-changing 
scenes, so just download it and look locally frame-by-frame.

    $ ffmpeg -i y2mate.mp4 frame%03d.jpg -hide_banner

And in the `frame438.jpg` we can see it.

**CTF{9e796ca74932912c216a1cd00c25c84fae00e139}**


Satellite (**networking**)

    Placing your ship in range of the Osmiums, you begin to receive 
    signals. Hoping that you are not detected, because it's too late 
    now, you figure that it may be worth finding out what these signals 
    mean and what information might be "borrowed" from them. Can you 
    hear me Captain Tim? Floating in your tin can there? Your tin can 
    has a wire to ground control? Find something to do that isn't 
    staring at the Blue Planet.

In archive we have two files - `README.pdf` and `init_sat`.
The curse of my is an abscence of habit to really truly read README 
files before taking any further actions. To be precise, I read the 
file, but did not look on picture. Though it is not very important.

Ok, let's run `init_sat`. It requests some *satellite name*...
How can we know it? Well, the easy path is to carefully read README.pdf 
and realize that there is sign on the satellite's photo.
But for me it is very hard path because of said above.
So disasming gives the answer either.

    $ r2 init_sat
     -- radare2 contributes to the One Byte Per Child foundation.
    [0x00459520]> aa
    [x] Analyze all flags starting with sym. and entry0 (aa)
    [0x00459520]> afl~main
    0x0042df20   35 909          sym.runtime.main
    0x00454ab0    3 71           sym.runtime.main.func1
    0x00454b00    5 60           sym.runtime.main.func2
    0x004b10f0   38 290          sym.net.isDomainName
    0x004b1220   14 263          sym.net.absDomainName
    0x004f8920   13 1029         sym.main.main
    0x004f8d30   20 1951         sym.main.connectToSat
    0x004f94d0    7 117          sym.main.init
    [0x00459520]> pdf@sym.main.main
    / (fcn) sym.main.main 1029
    |   sym.main.main ();
    |           ; var int32_t var_8h @ rsp+0x8
    ....................
    |    ::|:   0x004f8b47      e8b4fefdff     call sym.bufio.__Reader_.ReadBytes
    |    ::|:   0x004f8b4c      488b442418     mov rax, qword [var_18h]    ; [0x18:8]=-1 ; 24
    |    ::|:   0x004f8b51      488b4c2410     mov rcx, qword [var_10h]    ; [0x10:8]=-1 ; 16
    |    ::|:   0x004f8b56      488b542420     mov rdx, qword [var_20h]    ; [0x20:8]=-1 ; 32
    |    ::|:   0x004f8b5b      488d5c2448     lea rbx, [var_48h]          ; 0x48 ; 'H' ; 72
    |    ::|:   0x004f8b60      48891c24       mov qword [rsp], rbx
    |    ::|:   0x004f8b64      48894c2408     mov qword [var_8h], rcx
    |    ::|:   0x004f8b69      4889442410     mov qword [var_10h], rax
    |    ::|:   0x004f8b6e      4889542418     mov qword [var_18h], rdx
    |    ::|:   0x004f8b73      e818caf4ff     call sym.runtime.slicebytetostring
    |    ::|:   0x004f8b78      488b442428     mov rax, qword [var_28h]    ; [0x28:8]=-1 ; '(' ; 40
    |    ::|:   0x004f8b7d      4889442440     mov qword [var_40h], rax
    |    ::|:   0x004f8b82      488b4c2420     mov rcx, qword [var_20h]    ; [0x20:8]=-1 ; 32
    |    ::|:   0x004f8b87      48894c2468     mov qword [var_68h], rcx
    |    ::|:   0x004f8b8c      48890c24       mov qword [rsp], rcx
    |    ::|:   0x004f8b90      4889442408     mov qword [var_8h], rax
    |    ::|:   0x004f8b95      e8e612feff     call sym.strings.ToLower
    |    ::|:   0x004f8b9a      488b442410     mov rax, qword [var_10h]    ; [0x10:8]=-1 ; 16
    |    ::|:   0x004f8b9f      488b4c2418     mov rcx, qword [var_18h]    ; [0x18:8]=-1 ; 24
    |    ::|:   0x004f8ba4      4883f905       cmp rcx, 5                  ; 5
    |   ,=====< 0x004f8ba8      7512           jne 0x4f8bbc
    |   |::|:   0x004f8baa      813865786974   cmp dword [rax], 0x74697865 ; 'exit'
    |  ,======< 0x004f8bb0      750a           jne 0x4f8bbc
    |  ||::|:   0x004f8bb2      8078040a       cmp byte [rax + 4], 0xa     ; [0x4:1]=255 ; 10
    | ,=======< 0x004f8bb6      0f84ea000000   je 0x4f8ca6
    | |``-----> 0x004f8bbc      4883f907       cmp rcx, 7                  ; 7
    | | ,=====< 0x004f8bc0      751a           jne 0x4f8bdc
    | | |::|:   0x004f8bc2      81386f736d69   cmp dword [rax], 0x696d736f ; 'osmi'
    | |,======< 0x004f8bc8      7512           jne 0x4f8bdc
    | |||::|:   0x004f8bca      66817804756d   cmp word [rax + 4], 0x6d75  ; 'um' ; [0x4:2]=0xffff ; 28021
    | ========< 0x004f8bd0      750a           jne 0x4f8bdc
    | |||::|:   0x004f8bd2      8078060a       cmp byte [rax + 6], 0xa     ; [0x6:1]=255 ; 10
    | ========< 0x004f8bd6      0f84ad000000   je 0x4f8c89
    | -``-----> 0x004f8bdc      48c704240000.  mov qword [rsp], 0
    | |  ::|:   0x004f8be4      488d0576e904.  lea rax, [0x00547561]       ; "Unrecognized satellite: \", required CPU feature\nbad defer entry in panicbad defer size class: i=block index out of rangecan't s"
    | |  ::|:   0x004f8beb      4889442408     mov qword [var_8h], rax
    ....................................................
    [0x00459520]> 


Wow, I'm glad that there is no need to reverse all this application!
Really, there are A LOT of different stuff, including networking, 
of course.
We can see now that for jumping over "Unrecognized satellite" we must 
enter string "osmium". And check is case insensitive - this fact can't 
be seen from README.pdf! Let's use it, just for not feeling myself so 
stupid.

    $ ./init_sat 
    Hello Operator. Ready to connect to a satellite?
    Enter the name of the satellite to connect to or 'exit' to quit
    oSmIuM
    Establishing secure connection to oSmIuM
     satellite...
    Welcome. Enter (a) to display config data, (b) to erase all data or (c) to disconnect

    a
    Username: brewtoot password: ********************	166.00 IS-19 2019/05/09 00:00:00	Swath 640km	Revisit capacity twice daily, anywhere Resolution panchromatic: 30cm multispectral: 1.2m	Daily acquisition capacity: 220,000km²	Remaining config data written to: https://docs.google.com/document/d/14eYPluD_pi3824GAFanS29tWdTcKxP_XUxx7e303-3E

Copy-paste URL to the browser and get:

Satellite Config Data

    VXNlcm5hbWU6IHdpcmVzaGFyay1yb2NrcwpQYXNzd29yZDogc3RhcnQtc25pZmZpbmchCg==

This is obviously base64-encoded data (a-z, A-Z, 0-9, +, / and = for 
padding). Decode it:

    $ echo "VXNlcm5hbWU6IHdpcmVzaGFyay1yb2NrcwpQYXNzd29yZDogc3RhcnQtc25pZmZpbmchCg==" | python -m base64 -d -
    Username: wireshark-rocks
    Password: start-sniffing!

Okay, let's sniff `init_sat`'s traffic. Wireshark certainly rocks, 
but there are other good tools and I'm trying to leave command line 
as rare as possible.

First, open another shell and see what connections `init_sat` has.

    $ netstat -tnpa | grep init_sat
    tcp        0      0 10.137.5.22:41228       34.76.101.29:1337       ESTABLISHED 20996/./init_sat    

Second, start to sniff filtering by port number.

    $ sudo tcpdump -nA port 1337
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes

Then return to `init_sat` and hit (a) again. We see some traffic:

    13:35:38.710493 IP 34.76.101.29.1337 > 10.137.5.22.41228: Flags [F.], seq 380253893, ack 3302414040, win 222, length 0
    ...
    ....9.......&.)P...B...Username: brewtoot password: CTF{4efcc72090af28fd33a2118985541f92e793477f}	166.00 IS-19 2019/05/09 00:00:00	Swath 640km	Revisit capacity twice daily, anywhere Resolution panchromatic: 30cm multispectral: 1.2m	Daily acquisition capacity: 220,000km..	Remaining config data written to: https://docs.google.com/document/d/14eYPluD_pi3824GAFanS29tWdTcKxP_XUxx7e303-3E

    13:36:01.992300 IP 10.137.5.22.41230 > 34.76.101.29.1337: Flags [.], ack 451, win 473, length 0
    ....

I believe that password is substituted for asterisks by `init_sat` 
itself. There are a lot of stuff about regular expressions in it as 
well as a string `CTF{\S{40}}` (and how would I know this if looked 
README's photo?).
Doing data protection on client-side is a Great Evil, so let's try to 
solve this problem in completely another way, not like "networking", 
but like "pwn" problem.

    $ r2 -w init_sat 
     -- ((fn [f s n] (str (f f s n) "dare2")) (fn [f s n] (pr s) (if (> n 0) (f f (str s "ra") (dec n)) s)) "" (/ 1.0 0))
    [0x00459520]> / CTF
    Searching 3 bytes in [0x642420-0x660b78]
    hits: 0
    Searching 3 bytes in [0x62b000-0x642420]
    hits: 0
    Searching 3 bytes in [0x4fa000-0x62ac02]
    hits: 2
    Searching 3 bytes in [0x400000-0x4f9770]
    hits: 0
    0x00544c74 hit0_0 .e.sp=<invalid opCTF{\S{40}}GOTRACEB.
    0x0054c158 hit0_1 .tact the Google CTF team.go package.
    [0x00459520]> s 0x544c74
    [0x00544c74]> px 8
    - offset -   0 1  2 3  4 5  6 7  8 9  A B  C D  E F  0123456789ABCDEF
    0x00544c74  4354 467b 5c53 7b34                      CTF{\S{4
    [0x00544c74]> w WTF
    [0x00544c74]> px 8
    - offset -   0 1  2 3  4 5  6 7  8 9  A B  C D  E F  0123456789ABCDEF
    0x00544c74  5754 467b 5c53 7b34                      WTF{\S{4
    [0x00544c74]> q
    $ ./init_sat
    Hello Operator. Ready to connect to a satellite?
    Enter the name of the satellite to connect to or 'exit' to quit
    osMiuM
    Establishing secure connection to osMiuM
     satellite...
    Welcome. Enter (a) to display config data, (b) to erase all data or (c) to disconnect

    a
    Username: brewtoot password: CTF{4efcc72090af28fd33a2118985541f92e793477f}	166.00 IS-19 2019/05/09 00:00:00	Swath 640km	Revisit capacity twice daily, anywhere Resolution panchromatic: 30cm multispectral: 1.2m	Daily acquisition capacity: 220,000km²	Remaining config data written to: https://docs.google.com/document/d/14eYPluD_pi3824GAFanS29tWdTcKxP_XUxx7e303-3E


Finally, solved twice.

**CTF{4efcc72090af28fd33a2118985541f92e793477f}**
