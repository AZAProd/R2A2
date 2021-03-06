import glob
import random
import ConfigParser
from pygame import mixer  # Load the required library
import os
import datetime
import time
from config import mainconfig
from flask import Blueprint, request


_configfile = 'config/audio.cfg'

_config = ConfigParser.SafeConfigParser({'sounds_dir': './scripts', 'logfile': 'audio.log', 'volume': '0.3'})
_config.read(_configfile)

if not os.path.isfile(_configfile):
    print "Config file does not exist"
    with open(_configfile, 'wb') as configfile:
        _config.write(configfile)

_defaults = _config.defaults()

_logtofile = mainconfig['logtofile']
_logdir = mainconfig['logdir']
_logfile = _defaults['logfile']

if _logtofile:
    if __debug__:
        print "Opening log file: Dir: %s - Filename: %s" % (_logdir, _logfile)
    _f = open(_logdir + '/' + _logfile, 'at')
    _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : ****** Module Started: audio ******\n")
    _f.flush


_Random_Sounds = ['alarm', 'happy', 'hum', 'misc', 'quote', 'razz', 'sad', 'sent', 'ooh', 'proc', 'whistle', 'scream']
_Random_Files = ['ALARM', 'Happy', 'HUM__', 'MISC_', 'Quote', 'RAZZ_', 'Sad__', 'SENT_', 'OOH__', 'PROC_', 'WHIST',
                'SCREA']

api = Blueprint('audio', __name__, url_prefix='/audio')

@api.route('/', methods=['GET'])
@api.route('/list', methods=['GET'])
def _audio_list():
    """GET gives a comma separated list of available sounds"""
    message = ""
    if request.method == 'GET':
        message += audio.ListSounds()
    return message


@api.route('/<name>', methods=['GET'])
def _audio(name):
    """GET to trigger the given sound"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Sound : " + name + "\n")
	_f.flush
    if request.method == 'GET':
        audio.TriggerSound(name)
    return "Ok"


@api.route('/random/', methods=['GET'])
@api.route('/random/list', methods=['GET'])
def _random_audio_list():
    """GET returns types of sounds available at random"""
    message = ""
    if request.method == 'GET':
        message += audio.ListRandomSounds()
    return message


@api.route('/random/<name>', methods=['GET'])
def _random_audio(name):
    """GET to play a random sound of a given type"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Sound random: " + name + "\n")
	_f.flush
    if request.method == 'GET':
        audio.TriggerRandomSound(name)
    return "Ok"

@api.route('/volume', methods=['GET'])
def _get_volume():
    """GET returns current volume level"""
    message = ""
    if request.method == 'GET':
        message += audio.ShowVolume()
    return message


@api.route('/volume/<level>', methods=['GET'])
def _set_volume(level):
    """GET to set a specific volume level"""
    if _logtofile:
        _f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " : Volume set : " + level + "\n")
	_f.flush
    message = ""
    if request.method == 'GET':
        message += audio.SetVolume(level)
    return message


class _AudioLibrary:
    def init_config(self, sounds_dir):
        """Load in CSV of Audio definitions"""
        if __debug__:
            print "Setting sounds directory to %s" % sounds_dir

    def __init__(self, sounds_dir, volume):
        if __debug__:
            print "Initiating audio"
        self.init_config(sounds_dir)
        mixer.init()
        mixer.music.set_volume(float(volume))

    def TriggerSound(self, data):
        if __debug__:
            print "Playing %s" % data
        audio_file = "./sounds/" + data + ".mp3"
        # mixer.init()
        if __debug__:
            print "Init mixer"
        mixer.music.load(audio_file)  # % (audio_dir, data))
        if __debug__:
            print "%s Loaded" % audio_file
        mixer.music.play()
        if __debug__:
            print "Play"

    def TriggerRandomSound(self, data):
        idx = _Random_Sounds.index(data)
        prefix = _Random_Files[idx]
        print "Random index: %s, prefix=%s" % (idx, prefix)
        file_list = glob.glob("./sounds/" + prefix + "*.mp3")
        file_idx = len(file_list) - 1
        audio_file = file_list[random.randint(0, file_idx)]
        if __debug__:
            print "Playing %s" % data
        mixer.init()
        if __debug__:
            print "Init mixer"
        mixer.music.load(audio_file)  # % (audio_dir, data))
        if __debug__:
            print "%s Loaded" % audio_file
        mixer.music.play()
        if __debug__:
            print "Play"

    def ListSounds(self):
        files = ', '.join(glob.glob("./sounds/*.mp3"))
        files = files.replace("./sounds/", "", -1)
        files = files.replace(".mp3", "", -1)
        return files

    def ListRandomSounds(self):
        types = ', '.join(_Random_Sounds)
        return types

    def ShowVolume(self):
        cur_vol = str(mixer.music.get_volume())
        return cur_vol

    def SetVolume(self, level):
        if level == "up":
            if __debug__:
                print "Increasing volume"
            new_level = mixer.music.get_volume() + 0.025
        elif level == "down":
            if __debug__:
                print "Decreasing volume"
            new_level = mixer.music.get_volume() - 0.025
        else:
            if __debug__:
                print "Volume level explicitly states"
            new_level = level
        if new_level < 0:
            new_level = 0
        if __debug__:
            print "Setting volume to: %s" % new_level
        mixer.music.set_volume(float(new_level))
        return "Ok"


audio = _AudioLibrary(_defaults['sounds_dir'], _defaults['volume'])
