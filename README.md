# icecast-radio
A python program, used in a docker container in combination with an icecast conatiner, to create a simple ip radio system.

---

## What is icecast-radio
`icecast-radio` is a combination of custom software with a default icecast2 container (or instance). The radio with create "channels" (icecast streams) for each folder with a `ffmpeg` playlist file. Icecast can be stream anywhere from your browser to VLC.

The python radio server creates multiple threads of `ffmpeg` to transcode the audio and streams it to the icecast server. The python code is responsible for creating correct the ffmpeg command and launching/monitoring the thread.

The `ffmpeg` command adhears to the following format to stream to icecast2:
```bash
ffmpeg -re -f concat -stream_loop -1 -i {playlist_path} -f mp3 icecast://{self.icecast_user}:{self.icecast_pass}@{self.icecast_ip}:{self.icecast_port}/{stream_name}
```

---

## How to install icecast-radio
0. Pre-reqs
All you need is `docker-compose` or `podman-compose`.

1. Clone this repository.
```bash
git clone https://github.com/n-e-r-k/icecast-radio.git
```

2. Start the compose file.
```bash
# podman
sudo podman-compose up -d

# docker
sudo docker compose up -d
```

---

## How to setup your media?

### Stations

Each directory in the `/data` mount will be treated as it's own station.
For example if you mount `tmp0` to `/data`:
```
tmp0
├── tmp1-0
├── tmp1-1
└── tmp1-2
```

`tmp1-0`, `tmp1-1`, and `tmp1-2` will all be treated as seprate stations.

### Media

The media for each station is defined in a `playlist.txt` file in `ffmpeg` playlist format.

Here is an example of a single station layed out as:
```
tmp1-0
├── playlist.txt
├── song0.mp3
├── song1.mp3
└── song2.mp3
```
The `playlist.txt` could look like:
```txt
ffconcat version 1.0
file 'song0.mp3'
file 'song1.mp3'
file 'song2.mp3'
```
This file will also define the order of the loop.

### Station Name

To set the station name add the name to a plaintext file called `station_name`.
```bash
echo "<STATION_NAME>" > station_name
```

Here is an example from the last section.
```
tmp1-0
├── playlist.txt
├── station_name
├── song0.mp3
├── song1.mp3
└── song2.mp3
```
With `station_name` reading as:
```
tmp1-0
```

You would then connect to the stream through `<HOST>/<STATION_NAME>`.

---

## How to monitor the streams?

Monitor the streams through the Icecast2 web UI accessed at `<HOST>:8000` with the username and password defined in the compose file.

## How to attach as a client?

Any client that works for Icecast2 will work for icecast-radio. Common applications include, `ffplay`, `your web browser`, and `VLC`.
