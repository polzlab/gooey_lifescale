import os
import re
from datetime import datetime
from functools import partial
from operator import itemgetter
from gooey import Gooey, GooeyParser
import naive_peaks
import configure_peakcaller

DISPATCHER = {
    "call_peaks": naive_peaks.call_peaks,
    "config": configure_peakcaller.configure_peakcaller
}

def show_error_modal(error_msg):
    """ Spawns a modal with error_msg"""
    # wx imported locally so as not to interfere with Gooey
    import wx
    app = wx.App()
    dlg = wx.MessageDialog(None, error_msg, 'Error', wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def add_call_peak_gui(subs, config):
    p = subs.add_parser('call_peaks', prog='Call Mass Peaks', help='Get Mass Peaks from Raw Lifescale Data')
    p.add_argument(
        'experiment',
        metavar='Choose an Experiment',
        help='Choose the name of an experiment',
        widget='Dropdown',
        choices=naive_peaks.list_experiments(config)[0])
    p.add_argument('output_folder', widget="DirChooser")
    p.add_argument('--metadata_file', '-f', widget="FileChooser", help="If provided, convert vial ids to sample names. Should be the exported csv file called PanelData.csv.")

def add_config_gui(subs, config):
    p = subs.add_parser('config', prog="Configure Program", help="Options to change where this program looks for data, and the calibration used for frequency to mass conversion.")
    p.add_argument('--raw_data_folder', widget="DirChooser", help="currently {}".format(config["raw_data_folder"]))
    p.add_argument('--mass_transformation', type=float, help='currently {} Hz/fg'.format(config["mass_transformation"]))
    p.add_argument('--mass_cutoff', '-m', type=float, default=20, help='currently {} fg - minimum mass of the peak (minimum 5fg recommended)'.format(config["mass_cutoff"]))
    p.add_argument('--peak_width_cutoff', '-w', type=float, default=5, help='currently {} - width cutoff for peaks - minimum datapoints looking larger than noise'.format(config["peak_width_cutoff"]))
    p.add_argument('--peak_distance_cutoff', '-d', type=float, default=5, help='currently {} - distance cutoff for peaks - minimum datapoints between peaks'.format(config["peak_distance_cutoff"]))

@Gooey(program_name='Mass Peak Caller', image_dir='./images', required_cols=1)
def main():
    current_config, file_not_found = configure_peakcaller.load_config()
    if file_not_found:
        show_error_modal("No configuration file found at {}.\nWrote default configuration to that location.\nContinuing with default config.".format(file_not_found))

    parser = GooeyParser(description='Get Mass Peaks from Raw Lifescale Data')
    subs = parser.add_subparsers(help='commands', dest='command')
    add_call_peak_gui(subs, current_config)
    add_config_gui(subs, current_config)

    args = parser.parse_args()
    opts = vars(args)
    func = partial(DISPATCHER[args.command], config=current_config)
    current_config = func(**opts)

if __name__ == '__main__':
    main()
