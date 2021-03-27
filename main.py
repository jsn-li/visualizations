import os
import tempfile

import yaml
import requests
from bokeh.util import logconfig
from bokeh.io import curdoc

from layout import VisualizationLayout


def process_filepath(path):
    # If the filepath is a URL, download it and return its path. Otherwise, just return the input path.
    if os.getenv('DOWNLOAD', 'false').lower() == 'true':
        file = tempfile.NamedTemporaryFile(delete=False)
        logconfig.log.info(f"Downloading file at {path}")
        download = requests.get(path)
        logconfig.log.info(f"Download completed, status code: {download.status_code}")
        file.write(download.content)
        return file.name
    return path


# Read yaml config
config_file_file = process_filepath(os.getenv("CONFIG_FILE"))
logconfig.log.info(f"Using config file at {config_file_file}")
with open(config_file_file, 'r') as stream:
    config_data = yaml.safe_load(stream)
vis_config = config_data['visualizations'][0][list(config_data['visualizations'][0].keys())[0]]

# Read last updated date and add to config (if it doesn't exist, will not display it)
last_updated_file = process_filepath(os.getenv("LAST_UPDATED_FILE"))
logconfig.log.info(f"Reading last updated time from {last_updated_file}")
last_updated_time = None
if os.path.exists(last_updated_file):
    with open(last_updated_file, 'r') as stream:
        last_updated_time = stream.readline()
logconfig.log.info(f"Last updated: {last_updated_time}")
vis_config["last_updated_time"] = last_updated_time

# Set pickle file
vis_config["pickle_file"] = process_filepath(os.getenv("PICKLE_FILE"))

# Render!
layout = VisualizationLayout(**vis_config)
curdoc().title = config_data.get("page_title", "Green Zone Visualizations")
layout.render()
