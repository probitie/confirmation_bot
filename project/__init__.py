import time
import json
import datetime
import logging
import traceback

from collections import OrderedDict
from dataclasses import dataclass
from typing import Union, List, Tuple, Any, Dict, Optional, NewType, OrderedDict
from urllib3.exceptions import MaxRetryError

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

