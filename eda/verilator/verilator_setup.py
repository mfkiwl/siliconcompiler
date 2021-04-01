import os
import subprocess
import re
from siliconcompiler.schema import schema_istrue

################################
# Setup Verilator
################################

def setup_tool(chip, step):
    ''' Sets up default settings on a per step basis
    '''
    chip.logger.debug("Setting up Verilator")
    
    chip.add('flow', step, 'threads', '4')
    chip.add('flow', step, 'format', 'cmdline')
    chip.add('flow', step, 'copy', 'false')
    chip.add('flow', step, 'exe', 'verilator')
    chip.add('flow', step, 'vendor', 'verilator')
    chip.add('flow', step, 'refdir', '')
    chip.add('flow', step, 'script', '')
        
################################
# Set Verilator Runtime Options
################################

def setup_options(chip, step):
    ''' Per tool/step function that returns a dynamic options string based on
    the dictionary settings.
    '''

    #Get default opptions from setup
    #TODO: add options for:
    #sc/scc
    #clk
    #-stats --stats-vars -profile-cfuncs
    #-trace --trace-structs
    #-CFLAGS
    #-O3
    #
    if step == 'import':
        chip.add('flow', step, 'option', '--lint-only --debug')
    else:
        chip.add('flow', step, 'option', '--cc')
    
    options = chip.get('flow', step, 'option')

    #Include cwd in search path (verilator default)

    cwd = os.getcwd()    
    options.append('-I' + cwd + "/../../../")

    #Source Level Controls

    for value in chip.cfg['ydir']['value']:
        options.append('-y ' + value)

    for value in chip.cfg['vlib']['value']:
        options.append('-v ' + value)                    

    for value in chip.cfg['idir']['value']:
        options.append('-I' + value)

    for value in chip.cfg['define']['value']:
        options.append('-D ' + value)

    for value in chip.cfg['cmdfile']['value']:
        options.append('-f ' + value)
        
    for value in chip.cfg['source']['value']:
        options.append(value)

    #Relax Linting
    supress_warnings = ['-Wno-UNOPTFLAT',
                        '-Wno-SELRANGE',
                        '-Wno-WIDTH',
                        '-Wno-fatal']
    
    if schema_istrue(chip.cfg['relax']['value']):
        for value in supress_warnings:
            options.append(value)

    return options

################################
# Pre and Post Run Commands
################################
def pre_process(chip, step):
    ''' Tool specific function to run before step execution
    '''
    pass

def post_process(chip, step):
    ''' Tool specific function to run after step execution
    '''

    # filtering out debug garbage
    subprocess.run('egrep -h -v "\`begin_keywords" obj_dir/*.vpp > verilator.v',
                   shell=True)
                   
    # setting top module of design
    modules = 0
    if(len(chip.cfg['design']['value']) < 1):
        with open("verilator.v", "r") as open_file:
            for line in open_file:
                modmatch = re.match('^module\s+(\w+)', line)
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

    # Creating file for handoff to synthesis  
    subprocess.run("cp verilator.v " + "outputs/" + topmodule + ".v",
                   shell=True)


