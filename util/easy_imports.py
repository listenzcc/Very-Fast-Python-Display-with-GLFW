import math
import random
import numpy as np
import pandas as pd

from pathlib import Path
from omegaconf import OmegaConf

from loguru import logger

CONF = OmegaConf.load('./conf/project.yaml')
logger.add(f'./log/{CONF.project.name}.log', rotation='1 MB')
