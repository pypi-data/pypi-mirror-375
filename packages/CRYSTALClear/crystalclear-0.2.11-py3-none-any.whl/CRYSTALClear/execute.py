#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""


def set_runcry_path(path):
    """
    Set the path for the Runcry executable.

    Args:
        path (str): The path to the Runcry executable.

    Returns:
        None
    """
    import os
    import re

    this_file = os.path.realpath(__file__)
    # Read the current settings file
    file = open(this_file, 'r')
    lines = file.readlines()
    file.close()

    for i, line in enumerate(lines):
        if re.match(r'    runcry_path', line) != None:
            if len(path) > 0:
                lines[i] = '    runcry_path = \'%s\'\n' % (path)

    # Write the newly defined variables to the settings file
    file = open(this_file, 'w')
    for line in lines:
        file.writelines(line)
    file.close()


def set_runprop_path(path):
    """
    Set the path for the Runprop executable.

    Args:
        path (str): The path to the Runprop executable.

    Returns:
        None
    """
    import os
    import re

    this_file = os.path.realpath(__file__)
    # Read the current settings file
    file = open(this_file, 'r')
    lines = file.readlines()
    file.close()

    for i, line in enumerate(lines):
        if re.match(r'    runprop_path', line) != None:
            if len(path) > 0:
                lines[i] = '    runprop_path = \'%s\'\n' % (path)

    # Write the newly defined variables to the settings file
    file = open(this_file, 'w')
    for line in lines:
        file.writelines(line)
    file.close()


def runcry(file_name, guessp=None):
    """
    Run Runcry calculation.

    Args:
        file_name (str): The name of the file to run the calculation.
        guessp (str, optional): The guessp parameter. Default is None.

    Returns:
        str: The result of the calculation or an error message.
    """
    runcry_path = '/Users/brunocamino/crystal/runcry17'
    if runcry_path is None:
        return 'Please set the runcry path before calling this function'

    import re
    import subprocess
    import sys

    converged = False
    index = 0

    # file_name = file_name.split('.')[0]

    if converged is False:
        if index > 3:
            return None
        else:
            if guessp is not None:
                run_calc = runcry_path + ' ' + file_name + ' ' + guessp
            else:
                run_calc = runcry_path + ' ' + file_name
            process = subprocess.Popen(
                run_calc.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            index += 1
            try:
                file = open('%s.out' % file_name, 'r')
                data = file.readlines()
                file.close()
            except:
                print('EXITING: a .out file needs to be specified')
                sys.exit(1)
            for i, line in enumerate(data[::-1]):
                if re.match(r'^ EEEEEEEEEE TERMINATION', line) is not None:
                    converged = True
                    return '%s.out calculation successfully completed' % file_name


def runprop(prop_name, wf_file):
    """
    Run Runprop calculation.

    Args:
        prop_name (str): The name of the property to calculate.
        wf_file (str): The name of the wavefunction file.

    Returns:
        str: The result of the calculation or an error message.
    """
    runprop_path = '/Users/brunocamino/crystal/runprop17'
    if runprop_path is None:
        return ('Please set the runprop path before calling it')

    import re
    import subprocess
    import sys

    wf_file = wf_file.split('.')[0]
    prop_name = prop_name.split('.')[0]
    converged = False

    index = 0
    while index < 3:
        run_calc = runprop_path + ' ' + prop_name + ' ' + wf_file
        process = subprocess.Popen(
            run_calc.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        index = index + 1
        try:
            file = open(prop_name+'.outp', 'r')
            data = file.readlines()
            file.close()
        except:
            print('EXITING: a .out file needs to be specified')
            sys.exit(1)
        for i, line in enumerate(data[::-1]):
            if re.match(r'^ EEEEEEEEEE TERMINATION', line) != None:
                converged = True
                return '%s.outp calculation successfully completed' % prop_name

    return None
