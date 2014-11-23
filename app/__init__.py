__author__ = 'minhtule'

from flask import Flask

app = Flask(__name__)

STATIC_PATH = './app/static'

import cube
import process
import controllers
import cut_image
