Tools
===================================

SiliconCompiler execution depends on implementing adapter code "drivers" for each tool called in a flowgraph. Tools are referenced as named modules by the flowgraph and searched using the find_files() method. A complete set of supported tools can be found in the :ref:`Tools Directory`. The table below shows the function interfaces supported in setting up tools.

.. list-table::
   :widths: 10 10 10 10 10 10
   :header-rows: 1

   * - Function
     - Description
     - Arg
     - Returns
     - Used by
     - Required

   * - **setup_tool**
     - Configures tool
     - chip
     - chip
     - run()
     - yes

   * - **runtime_options**
     - Resolves paths at runtime
     - chip
     - list
     - run()
     - no

   * - **parse_version**
     - Returns executable version
     - stdout
     - version
     - run()
     - yes

   * - **pre_process**
     - Pre-executable logic
     - chip
     - chip
     - run()
     - no

   * - **post_process**
     - Post-executable logic
     - chip
     - chip
     - run()
     - yes

   * - **make_docs**
     - Doc generator
     - None
     - chip
     - sphinx
     - no

For a complete example of a tool setup module, see `OpenROAD <https://github.com/siliconcompiler/siliconcompiler/blob/main/siliconcompiler/tools/openroad/openroad.py>`_. For more in depth information about the various 'eda' parameters, see the :ref:`Schema <SiliconCompiler Schema>` section of the reference manual.


setup_tool(chip)
-----------------

Tool setup is done for each step and index within the run() function prior to launching each individual task. Tools can be configured independently for different steps (ie. the place step is different from the route step), so we need a method for passing information about the current step and index to the setup function. This is accomplished with the reserved 'scratch' parameters shown below. ::

  step = chip.get('arg','step')
  index = chip.get('arg','index')

All tools are required to bind the tool name to an executable name and to define any required command line options. ::

  chip.set('eda', <toolname>, step, index, 'exe', <exename>)
  chip.set('eda', <toolname>, step, index, 'option', <option>)

For tools such as TCL based EDA tools, we also need to define the entry script and any associated script directories. ::

  chip.set('eda', <toolname>, step, index, 'script', <entry_script>)
  chip.set('eda', <toolname>, step, index, 'refdir', <scriptdir>)
  chip.set('eda', <toolname>, step, index, 'format', <scripformat>)

To leverage the run() function's internal setup checking logic, it is highly recommend to define the parameter requirements, required inputs, expected output, version switch, and supported version numbers using the commands below::

  chip.set('eda', <toolname>, step, index, 'input', <list>)
  chip.set('eda', <toolname>, step, index, 'output', <list>)
  chip.set('eda', <toolname>, step, index, 'require', <list>)
  chip.set('eda', <toolname>, step, index, 'version', <list>)
  chip.set('eda', <toolname>, step, index, 'vswitch', "<string>")
  chip.set('eda', <toolname>, step, index, 'report', "<list>")

parse_version(stdout)
-----------------------
The run() function includes built in executable version checking, which can be enabled or disabled with the 'vercheck' parameter. The executable option to use for printing out the version number is specified with the 'vswitch' parameter within the setup_tool() function. Commonly used options include '-v', '\-\-version', '-version'. The executable output varies widely, so we need a parsing function that processes the output and returns a single uniform version string. The example shows how this function is implemented for the Yosys tool. ::

  def parse_version(stdout):
      # Yosys 0.9+3672 (git sha1 014c7e26, gcc 7.5.0-3ubuntu1~18.04 -fPIC -Os)
      version = stdout.split()[1]
      return version.split('+')[0]

The run() function compares the returned parsed version against the 'version' parameter specified in the setup_tool() function to ensure that a qualified executable version is being used.

pre_process(chip)
-----------------------
For certain tools and steps, we may need to set some Schema parameters immediately before task execution. For example, we may want to set the die and core area before the floorplan step based on the area result from the synthesis step.

post_process(chip)
-----------------------
The post process step is required to extract metrics from the tool log files. At a minimum the post process step should extract the number of warnings and errors from the tool log file and insert the value into the Schema. The post_process() logic is straight forward, but the regular expression logic can get involved for complex log files. Perhaps some day, EDA tools will produce SiliconCompiler compatible JSON metrics files.

The post_process function can also be used to post process the output data in the case of command line executable to produce an output that can be ingested by the SiliconCompiler framework. The Surelog post_process() implementation illustrates the power of the post_process functionality. ::

  def post_process(chip):
    ''' Tool specific function to run after step execution
    '''
    design = chip.get('design')
    step = chip.get('arg', 'step')

    if step != 'import':
        return 0

    # Look in slpp_all/file_elab.lst for list of Verilog files included in
    # design, read these and concatenate them into one pickled output file.
    with open('slpp_all/file_elab.lst', 'r') as filelist, \
            open(f'outputs/{design}.v', 'w') as outfile:
        for path in filelist.read().split('\n'):
            if not path:
                # skip empty lines
                continue
            with open(path, 'r') as infile:
                outfile.write(infile.read())
            # in case end of file is missing a newline
            outfile.write('\n')

    # Copy files from inputs to outputs. Need to skip pickled Verilog and
    # manifest since new versions of those are written.
    utils.copytree("inputs", "outputs", dirs_exist_ok=True, link=True,
                   ignore=[f'{design}.v', f'{design}.pkg.json'])

    # Clean up
    shutil.rmtree('slpp_all')

    return 0

Note that the return value of the post_process() function is interpreted as an integer error code where zero indicates success. This can be used to signal errors that should halt execution but do not trigger a non-zero exit status from the executable itself.

runtime_options(chip)
-----------------------
The distributed execution model of SiliconCompiler mandates that absolute paths be resolved at task run time. The setup_tool() function is run at run() launch to check flow validity, so we need a second function interface (runtime_options) to create the final commandline options. The runtime_options() function inspects the Schema and returns a cmdlist to be used by the 'exe' during task execution. The sequence of items used to generate the final command line invocation is as follows:

::

  <'eda',...,'exe'> <'eda',...,'option'> <'eda',...,'script'> <runtime_options()>

The Surelog example below illustrates the process of defining a runtime_options function. ::

  def runtime_options(chip):

    ''' Custom runtime options, returns list of command line options.
    '''

    step = chip.get('arg','step')
    index = chip.get('arg','index')

    cmdlist = []

    # source files
    for value in chip.find_files('ydir'):
        cmdlist.append('-y ' + value)
    for value in chip.find_files('vlib'):
        cmdlist.append('-v ' + value)
    for value in chip.find_files('idir'):
        cmdlist.append('-I' + value)
    for value in chip.get('define'):
        cmdlist.append('-D' + value)
    for value in chip.find_files('cmdfile'):
        cmdlist.append('-f ' + value)
    for value in chip.find_files('source'):
        cmdlist.append(value)

    cmdlist.append('-top ' + chip.get('design'))
    # make sure we can find .sv files in ydirs
    cmdlist.append('+libext+.sv')

    # Set up user-provided parameters to ensure we elaborate the correct modules
    for param in chip.getkeys('param'):
        value = chip.get('param', param)
        cmdlist.append(f'-P{param}={value}')

    return cmdlist

make_docs()
-----------------------
The SiliconCompiler includes automated document generators that search all tool modules for functions called make_docs(). It is highly recommended for all tools to include a make_docs() function. The function docstring is used for general narrative, while the body of the function is used to auto-generate a settings table based on the manifest created. At a minimum, the docstring should include a short description and links to the Documentation, Sources, and Installation. The example below shows the make_docs function for surelog. ::

  def make_docs():
    '''
    Surelog is a SystemVerilog pre-processor, parser, elaborator,
    and UHDM compiler that provides IEEE design and testbench
    C/C++ VPI and a Python AST API.

    Documentation: https://github.com/chipsalliance/Surelog

    Sources: https://github.com/chipsalliance/Surelog

    Installation: https://github.com/chipsalliance/Surelog

    '''

    chip = siliconcompiler.Chip()
    chip.set('arg','step','import')
    chip.set('arg','index','0')
    chip.set('design', '<design>')
    setup_tool(chip)
    return chip


TCL interface
--------------

.. note::

   SiliconCompiler configuration settings are communicated to all script based tools as TCL nested dictionaries.

Schema configuration handoff from SiliconCompiler to script based tools is accomplished within the run() function by using the write_manifest() function to write out the complete schema as a nested TCL dictionary. A snippet of the resulting TCL dictionary is shown below.

.. code-block:: tcl

   dict set sc_cfg asic targetlib [list  NangateOpenCellLibrary ]
   dict set sc_cfg asic maxfanout [list  64 ]
   dict set sc_cfg design [list  gcd ]
   dict set sc_cfg constraint [list gcd.sdc ]
   dict set sc_cfg source [list gcd.v ]

It is the responsibility of the tool reference flow developer to bind the standardized SiliconCompiler TCL schema to the tool specific TCL commands and variables. The TCL snippet below shows how the `OpenRoad TCL reference flow <https://github.com/siliconcompiler/siliconcompiler/blob/main/siliconcompiler/tools/openroad/sc_apr.tcl>`_ remaps the TCL nested dictionary to simple lists and scalars at the beginning of the flow for the sake of clarity.


.. code-block:: tcl

   #Design
   set sc_design     [dict get $sc_cfg design]
   set sc_optmode    [dict get $sc_cfg optmode]

   # APR Parameters
   set sc_mainlib     [lindex [dict get $sc_cfg asic targetlib] 0]
   set sc_targetlibs  [dict get $sc_cfg asic targetlib]
   set sc_stackup     [dict get $sc_cfg asic stackup]
   set sc_density     [dict get $sc_cfg asic density]
   set sc_hpinlayer   [dict get $sc_cfg asic hpinlayer]
   set sc_vpinlayer   [dict get $sc_cfg asic vpinlayer]
   set sc_hpinmetal   [dict get $sc_cfg pdk grid $sc_stackup $sc_hpinlayer name]
   set sc_vpinmetal   [dict get $sc_cfg pdk grid $sc_stackup $sc_vpinlayer name]
