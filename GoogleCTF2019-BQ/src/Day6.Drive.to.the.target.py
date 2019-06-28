#!/usr/bin/python
try:
    from urllib import urlencode, urlopen
except:
    from urllib.parse import urlencode
    from urllib.request import urlopen
import re

BASE_URL = 'https://drivetothetarget.web.ctfcompetition.com/'
URL = '{base}?lat={lat:.4f}&lon={lon:.4f}&token={token}'
RE_LAT = re.compile(r'name="lat" value="(?P<val>[^"]+)"')
RE_LON = re.compile(r'name="lon" value="(?P<val>[^"]+)"')
RE_TOKEN = re.compile(r'name="token" value="(?P<val>[^"]+)"')
RE_SPEED = re.compile(r' (?P<val>[0-9\.]+)km/h')


def step(lat, lon, token=None):
    params = ''
    if token is not None:
        params = '?' +  urlencode({'token': token, 
            'lat': lat, 'lon': lon})
    url = BASE_URL + params
    page = urlopen(url).read().decode('utf8')
    
    flags = [page.find(patt) >= 0 for patt in
        ['getting closer', 'getting away', 'too fast!', 'too far', 'should move']]
    
    if (not any(flags) and token is not None) or page.find('CTF{') >= 0:
        print(page)
    
    lat = float(RE_LAT.search(page).group('val'))
    lon = float(RE_LON.search(page).group('val'))
    new_token = RE_TOKEN.search(page).group('val')
    speed = 0.0
    closer, away = flags[:2]
    if closer or away:
        speed = float(RE_SPEED.search(page).group('val'))
    
    return (lat, lon, new_token), speed, flags


import json

def save_state(lat, lon, token, nstep, fname='state.json'):
    with open(fname, 'w') as f:
        f.write(json.dumps({"lat": lat, "lon": lon, 
            "token": token, "nstep": nstep}))

def load_state(fname='state.json'):
    try:
        with open(fname, 'r') as f:
            s = json.loads(f.read())
    except IOError:
        print("No state found, starting new session")
        (lat, lon, token), _, _ = step(0, 0)
        s = {"lat": lat, "lon": lon, "token": token, "nstep": 0}
    return (s["lat"], s["lon"], s["token"], s["nstep"])

s = (lat, lon, token, nstep) = load_state()
save_state(*s)


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
        elif stopped or speed == 0:
            k = MAX_SPEEDUP
        else:
            k = max(MAX_SPEEDDOWN, min(max_speed / speed, MAX_SPEEDUP))
        if away:
            if direction_changed:
                return (lat, lon, token, nstep)
            k = -k
            direction_changed = True
        print("[{}] At ({:.4f}, {:.4f}), v({:.4f}, {:.4f}) * {:.4f}; "
            "closer: {}".format(nstep, lat, lon, vel[0], vel[1], k, closer))
        vel = [x*k for x in vel]
        if sum([abs(x) for x in vel]) < eps:
            raise

max_speed = 40.0
while True:
    print("Max speed: {:.4f}".format(max_speed))
    s = move(s, (0.0001, 0.0000), max_speed)
    s = move(s, (0.0000, 0.0001), max_speed)
    max_speed *= 0.5


def gradient(state, d=0.0002, eps=1e-6):
    def sign(state, dlat, dlon):
        lat, lon, token, _ = state
        lat, lon = lat + dlat, lon + dlon
        _, _, flags = step(lat, lon, token)
        (closer, away, fast, far, stopped) = flags
        if closer:
            #print("  *****   sign[{:.5f}, {:.5f}] +1".format(dlat, dlon))
            return 1
        if away:
            #print("  *****   sign[{:.5f}, {:.5f}] -1".format(dlat, dlon))
            return -1
        print("Sign of dF measuring warning: flags = {}".format(flags))
        return None

    north_east = sign(state, d, 0), sign(state, 0, d)
    left, right = {  # choose appropriate quadrant
        ( 1,  1): ([d,  0], [0, -d]),
        ( 1, -1): ([0,  d], [d,  0]),
        (-1,  1): ([d,  0], [0,  d]),
        (-1, -1): ([0, -d], [d,  0])
    }[north_east]
    while True:
        #print("range {} .. {}".format(left, right))
        dr = sum([(left[i] - right[i])**2 for i in range(2)]) ** 0.5
        if dr < eps:
            break
        m = [0.5 * (left[i] + right[i]) for i in range(2)]
        k = d / sum([x**2 for x in m]) ** 0.5
        if sign(state, k*m[0], k*m[1]) > 0:
            left = m
        else:
            right = m
    v2 = x2, y2 = left
    v3 = x3, y3 = [0.5 * (left[i] + right[i]) for i in range(2)]
    vr = [-y3*(x3*y2 - y3*x2), x3*(x3*y2 - y3*x2)]
    k = d / sum([x**2 for x in vr]) ** 0.5
    return [vr[0] * k, vr[1] * k]

max_speed = 40.0
while True:
    print("Max speed: {:.4f}".format(max_speed))
    grad = gradient(s)
    print("Gradient = ({:.4f}, {:.4f})".format(*grad))
    s = move(s, grad, max_speed)
    max_speed *= 0.5

max_speed = 40.0
while True:
    print("Max speed: {:.4f}".format(max_speed))
    s = move(s, (0.0001, 0.0000), max_speed)
    s = move(s, (0.0000, 0.0001), max_speed)
    max_speed *= 0.5
