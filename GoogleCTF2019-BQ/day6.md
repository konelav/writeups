Drive to the target (**coding**)

    Excellent work! With your fine sleuthing skills, you managed to 
    find a picture of the handsome creature with its pet biped. At last 
    friends and companionship may be near! Like all inhabitants of this 
    world, you spend an inordinate amount of time on the site, stalking 
    and comparing your life to that of others. The first thought that 
    springs to your mind is "Why haven't I ever been to Mauritius on 
    holiday?" followed swiftly by "What is a Mauritius anyway?" But 
    after a while and with language successfully deciphered, you've 
    made contact with the lifeform in the picture, you have a "date"? 
    You're given the address of where to meet your potential interest. 
    "1 Banana way, beware of the glass." An odd address, especially 
    that last part. So how do you get there? You land your ship and 
    begin to search.


Going to the given URL we can see web page with simple form where we 
can submit some latitude and longitude. It is quite important to spend 
some time for playing with inputs to achieve as much different messages 
in response as we can. We can increase coordinates slightly, increase 
them significantly, or do not change them at all. Also we can 
experiment with delays between requests. In a few minutes we can see 
that there are 5 basic answers of the server:

    - `getting closer` - obviously this is what we want, probably these 
    new coordinated are somehow nearer to the flag; also we are 
    informed here about our speed, which seems to be limited by 50km/h
    - `getting away` - the opposite
    - `too fast!` - ratio of coordinate's change and request's delay 
    is too big
    - `too far` - change of coordinate's is too big
    - `should move` - no change of coordinates at all.

The task now is pretty clear: we should move step-by-step to the 
certain coordinates where flag is supposed to be, and when we will 
finally arrive, we probably see this flag or some link to it.

First of all, make code of single step: sending request and parsing 
response:


    import urllib
    import re

    URL = 'https://drivetothetarget.web.ctfcompetition.com/?lat={lat:.4f}&lon={lon:.4f}&token={token}'
    RE_LAT = re.compile(r'name="lat" value="(?P<val>[^"]+)"')
    RE_LON = re.compile(r'name="lon" value="(?P<val>[^"]+)"')
    RE_TOKEN = re.compile(r'name="token" value="(?P<val>[^"]+)"')
    RE_SPEED = re.compile(r' (?P<val>[0-9\.])km/h')

    def step(lat, lon, token):
        url = URL.format(**{'token': token, 'lat': lat, 'lon': lon})
        page = urllib.urlopen(url).read()
        
        closer, away, fast, far, stopped  = [page.find(patt) >= 0 for patt in
            ['getting closer', 'getting away', 'too fast!', 'too far', 'should move']]
        if not any(flags):
            print(page)
            raise  # something unexpected happens, hope it's CTF{...} page
        
        lat = float(RE_LAT.search(page).group('val'))
        lon = float(RE_LON.search(page).group('val'))
        token = RE_TOKEN.search(page).group('val')
        speed = 0.0
        if closer or away:
            speed = float(RE_SPEED.search(page).group('val'))
        
        return (lat, lon, token), speed, (closer, away, fast, far, stopped)


In our future tries there almost certainly will be unhandled 
exceptions, need of restarting script and so on. For not to lost all 
immidiate results (as we plan to move constantly to the target) it is 
useful to have some persistent storage that can be used between script 
restarts.


    import json
    
    def save_state(lat, lon, token, nstep, fname='state.json'):
        with open(fname, 'w') as f:
            f.write(json.dumps({"lat": lat, "lon": lon, 
                "token": token, "nstep": nstep})

    def load_state(fname='state.json'):
        try:
            with open(fname, 'r') as f:
                s = json.loads(f.read())
        except:
            print("No state found, starting new session")
            (lat, lon, token), _, _ = step(0, 0, '')
            s = {"lat": lat, "lon": lon, "token": token, "nstep": 0}
        return (s["lat"], s["lon"], s["token"], s["nstep"])

    s = (lat, lon, token, nstep) = load_state()


And it can be forseen that we will need routine that moves us just 
forward in specified direction. Good if it will adaptively change 
velocity and also report it's state to the console so we can control 
the process.


    MAX_SPEEDUP = 1.2
    MAX_SPEEDDOWN = 0.8
    
    def move(state, vel, max_speed, eps=1e-4):
        lat, lon, token, nstep = state
        direction_changed = False
        while True:
            lat += vel[0]
            lon += vel[1]
            (lat, lon, token), speed, flags = step(lat, lon, token)
            nstep += 1
            save_state(lat, lon, token, nstep)
            closer, away, fast, far, stopped = flags
            if far or fast:
                k = MAX_SPEEDDOWN
            elif stopped:
                k = MAX_SPEEDUP
            else:
                k = max(MAX_SPEEDDOWN, min(max_speed / speed, MAX_SPEEDUP))
            if away:
                if direction_changed:
                    return (lat, lon, token, nstep)
                k = -k
                direction_changed = True
            print("[{}] At ({:.4f}, {:.4f}), v({:.4f}, {:.4f}) * {:.4f}; "
                "closer: {}".format(nstep, lat, lon, vel[0], vel[1], k, close))
            vel = map([x*k for x in vel])
            if sum([abs(x) for x in vel]) < eps:
                raise


Now we can think about algorithm. It is trivial to do per-coordinate 
optimization: just move along latitude until flag `closer` is raised, 
the move along latitude and in the final steps we maybe will just need 
to reduce step size (velocity).


    max_speed = 40.0
    while True:
        print("Max speed: {:.4f}".format(max_speed))
        s = move(s, (0.0001, 0.0000), max_speed)
        s = move(s, (0.0000, 0.0001), max_speed)
        max_speed *= 0.5


Penalty for such a simple algorithm is probably not more than 
`sqrt(2)` in time spent for moving, because we are far away from 
Earth's poles and our space can be considered as euclidian with 
latitude and longitude being simple cartesian coordinates.

Alternatively, we can re-invent some wheels.
We do not have the value of our *goal function*, e.g. distance to the 
target place, or delta of this value after step was done. We have only 
sign of it's derivative by chosen direction, though it seems that 
function is very smooth and `dF = F(t+1) - F(t)` is nearly proportional 
to the step size `|p(t+1) - p(t)|` for one particular direction `v`: 
`(dF , v)` (here `v` is 2D-vector in nearly-plane coordinate system on 
Earth's surface and `(a , b)` is scalar product of two vectors).
It gives us a possibility to find gradient of goal function, i.e. 
direction in which it has quickest decreasing (descending). Indeed, 
if we could find two very close directions `v1` and `v2` such that 
`(dF , v1) > 0` and `(dF , v2) < 0`, then direction `v3 = (v1 + v2)/2` 
is very close to that in which `F` is neither increases nor decreases. 
That means `v3` is perpendicular to the direction to target. And this 
direction itself can be calculated as `v = [[v3 , v2] , v3]` where 
`[a , b]` is cross-product of two 3D vectors (here we add 3rd dimension 
`Z` whose axis naturally points to the zenith, i.e. upwards).

This last approach has two flaws:

  - we need to calculate gradient vector, and while we are doing it, 
  even using binary search, we waste time in a single place
  - precision of gradient calculation can't be high enough, because 
  "quant" of coordinates set to 0.0001 and the largest step per request 
  seems to be not more than 0.0004.

So just start per-coordinate search and go to sleep, it will take a 
long time.


    $ python drive.py 
    No state found, starting new session
    Max speed: 40.0000
    [1] At (51.6499, 0.0982), v(0.0001, 0.0000) * -1.2000; closer: False
    [2] At (51.6498, 0.0982), v(-0.0001, -0.0000) * 1.2000; closer: True
    [3] At (51.6496, 0.0982), v(-0.0001, -0.0000) * 1.2000; closer: True
    [4] At (51.6495, 0.0982), v(-0.0002, -0.0000) * 1.2000; closer: True
    [5] At (51.6493, 0.0982), v(-0.0002, -0.0000) * 1.0256; closer: True
    [6] At (51.6490, 0.0982), v(-0.0002, -0.0000) * 0.9756; closer: True
    [7] At (51.6488, 0.0982), v(-0.0002, -0.0000) * 1.0000; closer: True
    ..................
    [729] At (51.4930, 0.0982), v(-0.0002, -0.0000) * 0.8696; closer: True
    [730] At (51.4927, 0.0982), v(-0.0002, -0.0000) * 0.9091; closer: True
    [731] At (51.4925, 0.0982), v(-0.0002, -0.0000) * 1.0811; closer: True
    [733] At (51.4923, 0.0983), v(0.0000, 0.0001) * -1.2000; closer: False
    [734] At (51.4923, 0.0982), v(-0.0000, -0.0001) * 1.2000; closer: True
    [735] At (51.4923, 0.0980), v(-0.0000, -0.0001) * 1.2000; closer: True
    [736] At (51.4923, 0.0979), v(-0.0000, -0.0002) * 1.2000; closer: True
    [737] At (51.4923, 0.0977), v(-0.0000, -0.0002) * 1.2000; closer: True
    ..................
    [1626] At (51.4921, -0.1931), v(0.0001, 0.0000) * 1.2000; closer: True
    [1627] At (51.4922, -0.1931), v(0.0001, 0.0000) * -1.2000; closer: False
    [1628] At (51.4921, -0.1931), v(-0.0001, -0.0000) * 1.2000; closer: True
    [1630] At (51.4919, -0.1930), v(0.0000, 0.0001) * 1.2000; closer: True
    [1631] At (51.4919, -0.1929), v(0.0000, 0.0001) * 1.2000; closer: True
    [1632] At (51.4919, -0.1928), v(0.0000, 0.0001) * -1.2000; closer: False
    [1633] At (51.4919, -0.1929), v(-0.0000, -0.0002) * 1.2000; closer: True
    Max speed: 20.0000
    [1635] At (51.4920, -0.1931), v(0.0001, 0.0000) * 1.2000; closer: True
    [1636] At (51.4921, -0.1931), v(0.0001, 0.0000) * 0.9524; closer: True
    [1637] At (51.4923, -0.1931), v(0.0001, 0.0000) * -0.9524; closer: False
    [1638] At (51.4922, -0.1931), v(-0.0001, -0.0000) * 1.1111; closer: True
    [1640] At (51.4920, -0.1930), v(0.0000, 0.0001) * 1.2000; closer: True
    <!doctype html>
    <html>
      <head>
        <link href="/static/style.css" type="text/css" rel="stylesheet"/>
        <title>Driving to the target</title>
      </head>
      <h1>Driving to the target</h1>
       <body>
         <p>Hurry up, don't be late for you rendez-vous!
          <form method="get" action="/">
            <fieldset>
            <legend>Pick your direction</legend>
             <input type="number" name="lat" value="51.4920337049" min="-90" max="90" step="0.0001">
             <input type="number" name="lon" value="-0.192928297954" min="-180" max="180" step="0.0001">
             <input style="display: none" name="token" value="gAAAAABdFRjjw6E3O68Q1l08uWhTOBz7pOClaIzFjcBcRIaLUpbBDF7JqYtZFgZStE5hgRrCHP9xQORgBCi_NnTv_AfXTfWRVZFc1IVp_D1RjINJTWJ5md3F6y5so2RVJ5vcClJluCkW">
             <button type="submit">go</button>
            </fieldset>
          </form>
          <p>Congratulations, you made it, here is the flag:  CTF{Who_is_Tardis_Ormandy}</p>
       </body>
    </html>


**CTF{Who_is_Tardis_Ormandy}**
