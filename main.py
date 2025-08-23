import requests, time, json, pytz, dotenv
from datetime import datetime

# env variables
import os
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
TIMEZONE = os.environ.get('TIMEZONE', 'America/Chicago')

TRACKS_FILE = "spotify_history.json"

# refresh spotify token
def refresh_access_token():
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(url, data=data).json()
    return r['access_token']

# get recently played tracks
def get_recently_played(token):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers).json().get('items', [])

# save tracks to json file
def save_tracks(tracks):
    try:
        with open(TRACKS_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for t in tracks:
        track_info = {
            "id": t['track']['id'],
            "name": t['track']['name'],
            "artist": [a['name'] for a in t['track']['artists']],
            "played_at": t['played_at']
        }
        if track_info['played_at'] not in [x['played_at'] for x in data]:
            data.append(track_info)

    with open(TRACKS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# run from aug 23 1am to aug 26 1 am
def main():
    tz = pytz.timezone(TIMEZONE)
    start_time = tz.localize(datetime(2025, 8, 23, 1, 0, 0))   # Aug 23, 1:00 AM CST
    end_time   = tz.localize(datetime(2025, 8, 26, 1, 0, 0))   # Aug 26, 12:00 AM CST

    # wait until start time
    while datetime.now(tz) < start_time:
        print("Waiting for start time:", start_time)
        time.sleep(60)  # check every minute

    # track until end time
    while datetime.now(tz) < end_time:
        token = refresh_access_token()
        tracks = get_recently_played(token)
        save_tracks(tracks)
        time.sleep(300)  # poll every 5 minutes
      

if __name__ == "__main__":
    main()
