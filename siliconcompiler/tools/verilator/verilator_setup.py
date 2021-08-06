import os
import subprocess
import re
import sys
import siliconcompiler
import shutil

from siliconcompiler.schema import schema_istrue
from siliconcompiler.schema import schema_path

################################
# Setup Tool (pre executable)
################################

def setup_tool(chip, step):
    ''' Per tool function that returns a dynamic options string based on
    the dictionary settings.
    '''

    # Standard Setup
    tool = 'verilator'
    chip.add('eda', tool, step, 'threads', '4')
    chip.add('eda', tool, step, 'format', 'cmdline')
    chip.add('eda', tool, step, 'copy', 'false')
    chip.add('eda', tool, step, 'exe', 'verilator')
    chip.add('eda', tool, step, 'vendor', 'verilator')
    chip.add('eda', tool, step, 'option', '-sv')

    # Differentiate between import step and compilation
    if step in ['import', 'lint']:
        chip.add('eda', tool, step, 'option', '--lint-only --debug')
    elif (step == 'sim'):
        chip.add('eda', tool, step, 'option', '--cc')
    else:
        chip.logger.error('Step %s not supported for verilator', step)
        sys.exit()

    #Include cwd in search path (verilator default)
    chip.add('eda', tool, step, 'option', '-I../../../')

    #Source Level Controls
    for value in chip.cfg['ydir']['value']:
        chip.add('eda', tool, step, 'option', '-y ' + schema_path(value))
    for value in chip.cfg['vlib']['value']:
        chip.add('eda', tool, step, 'option', '-v ' + schema_path(value))
    for value in chip.cfg['idir']['value']:
        chip.add('eda', tool, step, 'option', '-I' + schema_path(value))
    for value in chip.cfg['define']['value']:
        chip.add('eda', tool, step, 'option', '-D' + schema_path(value))
    for value in chip.cfg['cmdfile']['value']:
        chip.add('eda', tool, step, 'option', '-f ' + schema_path(value))
    for value in chip.cfg['source']['value']:
        chip.add('eda', tool, step, 'option', schema_path(value))

    #Make warnings non-fatal in relaxed mode
    if len(chip.cfg['relax']['value']) > 0:
        if schema_istrue(chip.cfg['relax']['value']):
            chip.add('eda', tool, step, 'option', '-Wno-fatal')

################################
# Post_process (post executable)
################################

def post_process(chip, step):
    ''' Tool specific function to run after step execution
    '''

    # Creating single file "pickle' synthesis handoff
    subprocess.run('egrep -h -v "\\`begin_keywords" obj_dir/*.vpp > verilator.v',
                   shell=True)

    # setting top module of design
    modules = 0
    if len(chip.cfg['design']['value']) < 1:
        with open("verilator.v", "r") as open_file:
            for line in open_file:
                modmatch = re.match(r'^module\s+(\w+)', line)
                if modmatch:
                    modules = modules + 1
                    topmodule = modmatch.group(1)
        # Only setting design when possible
        if (modules > 1) & (chip.cfg['design']['value'] == ""):
            chip.logger.error('Multiple modules found during import, \
            but sc_design was not set')
            sys.exit()
        else:
            chip.logger.info('Setting design (topmodule) to %s', topmodule)
            chip.cfg['design']['value'].append(topmodule)
    else:
        topmodule = chip.cfg['design']['value'][-1]

    # Copy files from inputs to outputs
    shutil.copytree("inputs", "outputs", dirs_exist_ok=True)

    # Moving pickled file to outputs
    os.rename("verilator.v", "outputs/" + topmodule + ".v")

    # Clean up
    shutil.rmtree('obj_dir')

    #Return 0 if successful
    return 0

##################################################
if __name__ == "__main__":

    # File being executed
    prefix = os.path.splitext(os.path.basename(__file__))[0]
    output = prefix + '.json'

    # create a chip instance
    chip = siliconcompiler.Chip(defaults=False)
    # load configuration
    setup_tool(chip, step='import')
    # write out results
    chip.writecfg(output)