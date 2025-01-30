import argparse
import subprocess, os, atexit, time, sys, logging, random, argparse
import multiprocessing as mp

class Radio:
    def __init__(self, icecast_ip: str, icecast_port: str, icecast_user: str, icecast_pass: str, operating_dir: str = os.getcwd()):
        if os.path.exists(operating_dir):
            self.operating_dir = operating_dir
        else:
            raise Exception('given operating directory does not exist')

        self.icecast_ip = icecast_ip
        self.icecast_port = icecast_port
        self.icecast_user = icecast_user
        self.icecast_pass = icecast_pass

        self.stations = []
        self.station_control_processes = []

        self.current_temp_station_index = 0

        self.logger = logging.getLogger('nerksys radio')
        logging.basicConfig(filename='radio.log', filemode='w', encoding='utf-8', level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    def _index(self):
        # find command to retrieve all playlist files to create stations
        find_command = f'find {self.operating_dir} -name playlist.txt'
        result = subprocess.run(find_command, shell=True, capture_output=True, text=True).stdout

        self.logger.debug('find command output: %s', result)

        # make sure each path is a file
        for path in result.split('\n'):
            if not os.path.isfile(path):
                self.logger.warning("found bad path %s, skipping...", path)

            else:
                # find station name through file
                station_name_path = os.path.join(os.path.abspath(f'{path}/..'), 'station_name')

                # switch to name generation if no file is found
                if not os.path.isfile(station_name_path):
                    station_name = f'default-{self.current_temp_station_index}'
                    self.logger.warning("no station_name found for %s. using generated: %s", station_name_path, station_name)

                    self.current_temp_station_index += 1

                # process station name
                else:
                    with open(station_name_path, 'r') as file:
                        station_name = file.read().strip()
                        self.logger.info('found station name %s at path %s', station_name, station_name_path)

                # create station dictionary
                data = {
                    'path' : path,
                    'station_name' : station_name,
                    'status' : None
                }

                self.logger.info('addition of station: %s', data)
                self.stations.append(data)

    def _start_station(self, playlist_path: str, stream_name: str):
        command = f'ffmpeg -re -f concat -stream_loop -1 -i {playlist_path} -f mp3 icecast://{self.icecast_user}:{self.icecast_pass}@{self.icecast_ip}:{self.icecast_port}/{stream_name}'
        time.sleep(random.randint(0, 3) * 1)
        self.logger.debug('starting station with command: %s', command)
        return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    def _station_worker(self, playlist_path: str, station_name: str):
        self.logger.debug('station working started for %s...', station_name)

        os.chdir(os.path.abspath(playlist_path + '/..'))

        while True:
            process = self._start_station(playlist_path, station_name)
            atexit.register(process.kill)
            while process.poll() == None:
                time.sleep(5)

    def _launch_stations(self):
        self.logger.info('starting to launch stations...')
        for station in self.stations:
            process = mp.Process(target=self._station_worker, args=(station['path'], station['station_name']))
            station['status'] = 'started'
            process.start()
            self.station_control_processes.append(process)

    def _status(self):
        for process in range(len(self.station_control_processes)):
            current_process = self.station_control_processes[process]
            self.logger.info('station control process %s status: %s', current_process, current_process.is_alive())

    def _kill_all_children_processes(self):
        for process in range(len(self.station_control_processes)):
            self.station_control_processes[process].terminate()

    def launch(self):
        self._index()
        self._launch_stations()
        while True:
            self._status()
            time.sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='nerksys radio', description='nerksys radio backend audio transcoding to icecast2')
    parser.add_argument('icecast_ip')
    parser.add_argument('icecast_port')
    parser.add_argument('user')
    parser.add_argument('password')
    parser.add_argument('directory')
    args = parser.parse_args()

    radio = Radio(args.icecast_ip, args.icecast_port, args.user, args.password, args.directory)
    radio.launch()