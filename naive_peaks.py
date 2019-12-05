""" GUI application for processing LifeScale data.

copyright 2019 Joseph Elsherbini
all rights reserved
"""

import os
import struct
import json
import re
import datetime
from itertools import chain
from operator import itemgetter
from gooey import Gooey, GooeyParser
import numpy as np
import pandas as pd
import scipy.signal

NOW = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def list_experiments(config):
    raw_data_files = [f for f in os.listdir(os.path.expanduser(config["raw_data_folder"])) if re.search(r"(.+)_(\d{6})_(\d{6})", f) and os.path.splitext(f)[1] == ""]
    unique_experiments = sorted(sorted(list(set([re.search(r"(.+)_(\d{6})_(\d{6})", f).groups() for f in raw_data_files])),
                         key=itemgetter(2), reverse=True), key=itemgetter(1), reverse=True)
    return (["{} {}".format(e[0], get_date_time(e[1], e[2])) for e in unique_experiments], ["_".join(e) for e in unique_experiments])

def get_date_time(date, time):
    fmt_string = "%m/%d/%Y %H:%M:%S"
    return datetime.datetime(2000+int(date[0:2]), int(date[2:4]), int(date[4:6]), int(time[0:2]), int(time[2:4]), int(time[4:6])).strftime(fmt_string)


def call_peaks(experiment, output_folder, metadata_file, config, command):
    update_now()
    all_experiments= list_experiments(config)
    exp_name = [e[1] for e in zip(all_experiments[0], all_experiments[1]) if e[0] == experiment][0]
    exp_files = [os.path.join(os.path.expanduser(config["raw_data_folder"]), f) for f in os.listdir(os.path.expanduser(config["raw_data_folder"])) if exp_name in f and os.path.splitext(f)[1] == ""]
    print(exp_name, exp_files)
    peaks = write_peaks(exp_name, exp_files, output_folder, metadata_file, config)
    write_summary(exp_name, peaks, output_folder)
    # TODO write_plots(exp_name, peaks, output_folder, config)
    write_config(exp_name, output_folder, config)
    return config

def update_now():
    global NOW
    NOW = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def parse_metadata(metadata_file):
    return pd.read_csv(metadata_file)[["Id", "Well"]]

def load_raw_data(exp_name, exp_files):
    for f_path in exp_files:
        m = re.search(r"(.+)_(\d{6})_(\d{6})_c(\d+)_v(\d+)", f_path)
        exp_date, exp_time, exp_cycle, exp_measurement = m.group(2,3,4,5)
        print(exp_name, exp_date, exp_time, exp_cycle, exp_measurement)
        n_datapoints = int(os.path.getsize(f_path) / 8)
        with open(f_path, "rb") as f:
            content = f.read()
            a = np.array(struct.unpack("d"*n_datapoints, content))[10:]
        yield dict(zip(["exp_name", "exp_date", "exp_time", "exp_cycle", "exp_measurement", "data_array"],
                       [exp_name, exp_date, exp_time, exp_cycle, exp_measurement, a]))

def generate_peaks(measurement, config):
    filtered_signal = scipy.signal.savgol_filter(measurement["data_array"], window_length=5, polyorder=3)
    peaks, _ = scipy.signal.find_peaks(-filtered_signal, width=config["peak_width_cutoff"], prominence=config["mass_cutoff"]*config["mass_transformation"], distance=config["peak_distance_cutoff"])
    masses = scipy.signal.peak_prominences(-filtered_signal, peaks)[0]*(1/config["mass_transformation"])
    for peak, mass in zip(peaks, masses):
        yield dict(zip(["exp_name", "exp_date", "exp_time", "exp_cycle", "exp_measurement", "event_index","event_mass"],
                       [measurement["exp_name"], measurement["exp_date"],measurement["exp_time"],measurement["exp_cycle"],measurement["exp_measurement"], peak, mass]))

def write_peaks(exp_name, exp_files, output_folder, metadata_file, config):
    peaks = pd.DataFrame(chain.from_iterable([generate_peaks(measurement, config) for measurement in load_raw_data(exp_name, exp_files)]))
    if metadata_file:
        metadata = parse_metadata(metadata_file)
        peaks = peaks.astype({'exp_measurement':'int32'}).merge(metadata.astype({'Id':'int32'}), how='left', left_on='exp_measurement', right_on='Id')
        peaks["Well"] = ["".join([w[0],w[1:].zfill(2)]) for w in peaks["Well"]]
    out_path = os.path.join(os.path.expanduser(output_folder), "{}_{}_peaks.csv".format(NOW, exp_name))
    peaks.to_csv(out_path, index=False)
    return peaks

def write_summary(exp_name, peaks, output_folder):
    print(peaks.columns)
    if "Well" in peaks.columns:
        summary = peaks.groupby(["Well", "exp_cycle"])["event_mass"].describe()
    else:
        summary = peaks.groupby(["exp_measurement", "exp_cycle"])["event_mass"].describe()
    out_path = os.path.join(os.path.expanduser(output_folder), "{}_{}_summary.csv".format(NOW, exp_name))
    summary.to_csv(out_path)

def write_config(exp_name, output_folder, config):
    output_path = os.path.join(os.path.expanduser(output_folder), "{}_{}_config.json".format(NOW, exp_name))
    with open(output_path, "w") as f:
        json.dump(config, f)
