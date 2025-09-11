import zalfmas_capnp_schemas
import sys
import os

sys.path.append(os.path.dirname(zalfmas_capnp_schemas.__file__))

from . import a_capnp
from . import climate_capnp
from . import cluster_admin_service_capnp
from . import common_capnp
from . import config_capnp
from . import crop_capnp
from . import date_capnp
from . import fbp_capnp
from . import frontend_capnp
from . import geo_capnp
from . import grid_capnp
from . import jobs_capnp
from . import management_capnp
from . import model_capnp
from . import persistence_capnp
from . import registry_capnp
from . import service_capnp
from . import soil_capnp
from . import storage_capnp
from . import x_capnp

__all__ = [
    "a_capnp",
    "climate_capnp",
    "cluster_admin_service_capnp",
    "common_capnp",
    "config_capnp",
    "crop_capnp",
    "date_capnp",
    "fbp_capnp",
    "frontend_capnp",
    "geo_capnp",
    "grid_capnp",
    "jobs_capnp",
    "management_capnp",
    "model_capnp",
    "persistence_capnp",
    "registry_capnp",
    "service_capnp",
    "soil_capnp",
    "storage_capnp",
    "x_capnp",
]
