import os
import sys

generated_files_path = os.path.abspath(os.path.dirname(__file__))

def _alias_local_pb2_modules():
	import importlib
 
	pb2_names = [
		'boot_msgs_pb2', 'common_msgs_pb2', 'config_msgs_pb2', 'control_msgs_pb2',
		'cri_msgs_pb2', 'device_msgs_pb2', 'ethercat_msgs_pb2', 'moby_msgs_pb2',
		'rtde_msgs_pb2', 'teleop_dev_pb2', 'plotting_pb2',
		'boot_pb2', 'config_pb2', 'control_pb2', 'cri_pb2', 'device_pb2',
		'ethercat_pb2', 'linear_pb2', 'moby_pb2', 'rtde_pb2', 'indyeye_pb2', 'eyetask_pb2',
	]
	for name in pb2_names:
		try:
			mod = importlib.import_module(f'.{name}', __name__)
			sys.modules[name] = mod
		except Exception:
			pass

	pb2_grpc_names = [
		'boot_pb2_grpc', 'config_pb2_grpc', 'control_pb2_grpc', 'cri_pb2_grpc',
		'device_pb2_grpc', 'ethercat_pb2_grpc', 'linear_pb2_grpc', 'moby_pb2_grpc',
		'rtde_pb2_grpc', 'teleop_dev_pb2_grpc', 'plotting_pb2_grpc', 'indyeye_pb2_grpc',
		'eyetask_pb2_grpc',
	]
	for name in pb2_grpc_names:
		try:
			mod = importlib.import_module(f'.{name}', __name__)
			sys.modules[name] = mod
		except Exception:
			pass

_alias_local_pb2_modules()

# gRPC service stubs
from .boot_pb2_grpc         import *
from .config_pb2_grpc       import *
from .control_pb2_grpc      import *
from .cri_pb2_grpc          import *
from .device_pb2_grpc       import *
from .ethercat_pb2_grpc     import *
from .linear_pb2_grpc       import *
from .moby_pb2_grpc         import *
from .rtde_pb2_grpc         import *
from .teleop_dev_pb2_grpc   import *

# Protocol message types
from . import boot_msgs_pb2     as boot_msgs
from . import common_msgs_pb2   as common_msgs
from . import config_msgs_pb2   as config_msgs
from . import control_msgs_pb2  as control_msgs
from . import cri_msgs_pb2      as cri_msgs
from . import device_msgs_pb2   as device_msgs
from . import ethercat_msgs_pb2 as ethercat_msgs
from . import moby_msgs_pb2     as moby_msgs
from . import rtde_msgs_pb2     as rtde_msgs
from . import teleop_dev_pb2    as teleop_data
