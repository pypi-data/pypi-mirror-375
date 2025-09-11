#!/usr/bin/env python3

from re import split, match
import traceback
import sys
from getopt import getopt
from sys import argv
from py3toolset.txt_color import col, Color, bold, frame, print_frame, warn
from py3toolset.cmd_interact import contains_help_switch
from py3toolset.fs import check_file
from pydisper96 import (py_disp96_modfile_ur, py_disp96_modfile_ul,
                        py_disp96_modfile_cr, py_disp96_modfile_cl)
from numpy import linspace


def warn_opt_override(short_opt, long_opt):
    warn(" option -" + short_opt + "|--" + long_opt +
         " set more than once. Overriding old value.")


def check_opt(opt):
    global numfreqs, fmin, fmax, wavetype, mod_filepath, veltype
    if(opt == "veltype"):
        if(veltype.lower() not in ["phase", "group"]):
            raise Exception("veltype must be phase or group")
    if(opt == "numfreqs"):
        if(not match(r"^\d+", numfreqs)):
            raise Exception("numfreqs must be a integer")
        numfreqs = int(numfreqs)
    if(opt == "fmin"):
        fmin = float(fmin)
        if(fmax is not None and float(fmax) <= fmin):
            raise Exception("min freq. must be lower than max freq.")
    elif(opt == "fmax"):
        fmax = float(fmax)
        if(fmin is not None and fmax <= float(fmin)):
            raise Exception("max freq. must be greater than min freq.")
    elif(opt == "wavetype"):
        if(wavetype.upper() not in ["RAYL", "LOVE"]):
            raise Exception("Wave type must be RAYL or LOVE.")
    elif(opt == "mod_filepath"):
        check_file(mod_filepath)


def parse_opts(opts):
    global numfreqs, fmin, fmax, wavetype, veltype, use_c_impl
    for opt, val in opts:
        if(opt in ("-n", "--numfreqs")):
            numfreqs = val
            check_opt("numfreqs")
        elif(opt in ("-f", "--freqs")):
            if(fmin):
                warn_opt_override("f", "freqs")
            if(":" in val and not val.endswith(":")):
                fmin, fmax = split(":", val)
                check_opt("fmin")
                check_opt("fmax")
            else:
                fmin = val
                check_opt("fmin")
        elif(opt in ("-r", "--rayl")):
            if(wavetype):
                warn_opt_override("r|-l", "rayl|--love")
            wavetype = "RAYL"
        elif(opt in ("-l", "--love")):
            if(wavetype):
                warn_opt_override("r|-l", "rayl|--love")
            wavetype = "LOVE"
        elif(opt in ("-g", "--group")):
            if(veltype):
                warn_opt_override("g|-p", "group|--phase")
            veltype = "GROUP"
        elif(opt in ("-p", "--phase")):
            if(veltype):
                warn_opt_override("g|-p", "group|--phase")
            veltype = "PHASE"
        elif opt in ("-s", "--slu"):
            use_c_impl = False


def check_mandatory_opts(interactive):
    global numfreqs, fmin, fmax, wavetype, mod_filepath, veltype
    gen_msg = "mandatory parameter not set: "
    if(not numfreqs):
        if(interactive):
            numfreqs = input("Enter number of frequencies: (int): ")
            check_opt("numfreqs")
        else:
            raise Exception(gen_msg + " number of frequencies (-n|--numfreqs).")
    if(not fmin):
        if(interactive):
            fmin = input("Enter fmin: (float, Hz): ")
            check_opt("fmin")
        else:
            raise Exception(gen_msg + " min frequency (-f|--freqs).")
    if(not fmax):
        if(interactive):
            fmax = input("Enter fmax: (float, Hz): ")
            check_opt("fmax")
        else:
            raise Exception(gen_msg + " max frequency (-f|--freqs).")
    check_opt("fmax")
    if(not wavetype):
        if(interactive):
            wavetype = input("Enter wave type: (RAYL, LOVE): ")
            check_opt("wavetype")
        else:
            raise Exception(gen_msg + " wave type (-r|--rayl|-l|--love).")
    check_opt("wavetype")
    if(not mod_filepath):
        if(interactive):
            mod_filepath = input("Enter the model filepath: ")
            check_opt("mod_filepath")
        else:
            raise Exception(gen_msg + " model filepath.")
    if(not veltype):
        if(interactive):
            veltype = input("Enter wave type: (GROUP, PHASE): ")
            check_opt("veltype")
        else:
            raise Exception(gen_msg + " wave type (-g|--group|-p|--phase).")
    check_opt("veltype")


def usage():
    print(frame("USAGE") + """
    """ + col(Color.BLUE, """

    """ + col(Color.RED, bold(argv[0])) + " " +
              col(Color.RED, bold("-f|--freqs")) +
              " <min_f(Hz)>:<max_f(Hz)> " +
              col(Color.RED, bold("-n|--nfreqs")) +
              " <number_of_freqs_from_min_to_max_freq> " +
              col(Color.RED, bold("-l|--love|-r|--rayl")) + " " +
              col(Color.RED, bold("-g|--group|-p|--phase")) + " " +
              col(Color.RED, bold("[-s|--slu]")) + " " +
              col(Color.RED, bold("<mod_filepath>")) + """
    """ + col(Color.RED, bold(argv[0] + " -h|--help"))) + """

"""+
col(Color.RED, bold("Example of use:"))+"""
          """+argv[0]+""" -f 0.02:0.2 -n 20 -l -g model

          The command above computes the Love group velocities for the twenty
          frequencies evenly spaced into the range spanning from .02 to .2 Hz.

"""+col(Color.RED, bold("Example of model (built using cat):"))+"""
cat > model <<EOF
0.000000      4330       2500        3000      0.0000
10.000000       4763      2750       3000      0.0000
45.000000        6062       3500       4500       0.0000
EOF

"""+
              col(Color.RED, bold("[-s|--slu]")) + ": this option is for "
          "using the Saint-Louis University Herrmann's srfdis96 proprietary "
          "code. Defaultly a BSD licensed C port of srfdis96 is used.\r\n\r\n"

          +col(Color.RED, bold("Syntax notes:"))+"""
        - Parameters enclosed by brackets (`[]') are optional parameters.
        - The pipe character `|' represents an alternative between two options or values.
          For example, `-l|--love' means that users can use -l (short option) or
          --love (long option).
        - The chevron characters `<>' designate a value the user has to set.
          The indicated inner text gives sense to this value.
 """)


def print_params():
    print_frame("PARAMETERS")
    for p in ["wavetype", "fmin", "fmax", "veltype"]:
        if(eval(p) is not None):
            print(p + " = " + str(eval(p)))
    print("Inversion backend (srfdis96):", "C 3-clause BSD license backend" if use_c_impl else
          "Saint-Louis University Herrmann's Fortran backend.")


short_opts = "n:f:lrhgps"
long_opts = ["numfreqs=", "freqs=", "love", "rayl", "help", "group", "phase",
             "slu"]

numfreqs, fmin, fmax, wavetype, veltype, use_c_impl = (None, None, None, None,
                                                       None, True)

mod_filepath = None


def main(fS = 1,  # Spherical correction, if not set to 0
fU = 0,  # System unit ; km for depths, km/s vs and vp, g/cm3 for rho
ic = 0.01,  # Phase velocity search increment
h = 0.001,  # Frequency step for derivation
f1 = 0.,  # ghost parameter, always 0
fM = 1  # mode number, fundamental = 1 then 2,3,4,5...):
        ):
    try:
        global mod_filepath, use_c_impl
        opts, remaining = getopt(argv[1:], short_opts, long_opts)
        r_len = len(remaining)
        if (len(argv) < 2 or contains_help_switch(argv[1:])):
            usage()
        else:
            parse_opts(opts)
            if(r_len > 0):
                mod_filepath = remaining[0]
            check_mandatory_opts(False)
            print_params()
            vel_comp_funcs = {}
            if veltype.lower() == "group":
                if wavetype.lower() == "rayl":
                    vel_comp_func = py_disp96_modfile_ur
                elif wavetype.lower() == "love":
                    vel_comp_func = py_disp96_modfile_ul
            elif veltype.lower() == "phase":
                if wavetype.lower() == "rayl":
                    vel_comp_func = py_disp96_modfile_cr
                elif wavetype.lower() == "love":
                    vel_comp_func = py_disp96_modfile_cl
            t = list(1/linspace(fmin, fmax,
                                numfreqs))
            res_list = vel_comp_func(mod_filepath, numfreqs, fS, fU,
                                     fM, ic, f1,
                                     h, True, t, use_c_impl) # True for rho, vp, vs in SI
                                                 # units (resp. kg/m^3, m/s) instead of resp. g/cm^3 and m/s as in disp96 fortran version
            print_frame("disp96 Results (line format: period, "
                        + veltype+" velocity)", Color.RED)
            for v, t in zip(res_list, t):
                print(t, v)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        msg = str(e)
        if(not msg.lower().startswith("error")):
            msg = "Error: " + msg
        print_frame(msg, Color.RED, centering=False)
        print(col(Color.GREEN, "Use -h, --help option for help."))

if __name__ == '__main__':
    main()
