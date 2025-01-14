
import os
import sys
import re
import siliconcompiler

############################################################################
# DOCS
############################################################################

def make_docs():
    '''
    The 'skywater130' Open Source PDK is a collaboration between Google and
    SkyWater Technology Foundry to provide a fully open source Process
    Design Kit and related resources, which can be used to create
    manufacturable designs at SkyWater’s facility.

    Skywater130 Process Highlights:
    * 130nm process
    * support for internal 1.8V with 5.0V I/Os (operable at 2.5V)
    * 1 level of local interconnect
    * 5 levels of metal

    PDK content:
    * An open source design rule manual
    * multiple standard digital cell libraries
    * primitive cell libraries and models for creating analog designs
    * EDA support files for multiple open source and proprietary flows

    More information:
    * https://skywater-pdk.readthedocs.io/en/latest/

    Sources:
    * https://github.com/google/skywater-pdk

    '''

    chip = siliconcompiler.Chip()
    setup_pdk(chip)

    return chip

####################################################
# PDK Setup
####################################################

def setup_pdk(chip):
    '''
    Setup function for the skywater130 PDK.
    '''

    ###############################################
    # Process
    ###############################################

    foundry = 'skywater'
    process = 'skywater130'
    rev = 'v0_0_2'
    stackup = '5M1LI'

    # TODO: eventualy support hs libtype as well
    libtype = 'hd'
    node = 130
    # TODO: dummy numbers, only matter for cost estimation
    wafersize = 300
    hscribe = 0.1
    vscribe = 0.1
    edgemargin = 2

    pdkdir = os.path.join('..', 'third_party', 'pdks', foundry, process, 'pdk', rev)

    #if you are calling this file, you are in asic mode
    chip.set('mode','asic', clobber = True)

    # process name
    chip.set('pdk','foundry', foundry)
    chip.set('pdk','process', process)
    chip.set('pdk','node', node)
    chip.set('pdk','version', rev)
    chip.set('pdk','stackup', stackup)
    chip.set('pdk','wafersize', wafersize)
    chip.set('pdk','edgemargin', edgemargin)
    chip.set('pdk','hscribe', hscribe)
    chip.set('pdk','vscribe', vscribe)

    # Values chosen based on
    # https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/59ad47a1325239b578bf1c2b3cf6617e44d05d47/flow/platforms/sky130hd/tapcell.tcl
    chip.set('pdk','tapmax', 14)
    chip.set('pdk','tapoffset', 2)

    # Tech file
    for tool in ('openroad', 'klayout', 'magic'):
        chip.set('pdk','aprtech',tool,stackup, libtype,'lef',
                 pdkdir+'/apr/sky130_fd_sc_hd.tlef')

    # DRC Runsets
    chip.set('pdk','drc','magic', stackup, 'runset', pdkdir+'/setup/magic/sky130A.tech')

    # LVS Runsets
    chip.set('pdk','lvs','netgen', stackup, 'runset', pdkdir+'/setup/netgen/lvs_setup.tcl')

    # Layer map
    chip.set('pdk','layermap','klayout',stackup, 'def', 'gds', pdkdir+'/setup/klayout/skywater130.lyt')

    # Routing Grid Definitions

    # TODO: what should the SC-internal name of the LI layer be?
    chip.set('pdk','grid', stackup, 'li1', 'name', 'li1')
    chip.set('pdk','grid', stackup, 'li1', 'xoffset', 0.23)
    chip.set('pdk','grid', stackup, 'li1', 'xpitch',  0.46)
    chip.set('pdk','grid', stackup, 'li1', 'yoffset', 0.17)
    chip.set('pdk','grid', stackup, 'li1', 'ypitch',  0.34)
    chip.set('pdk','grid', stackup, 'li1', 'adj', 1.0)

    chip.set('pdk','grid', stackup, 'met1', 'name', 'm1')
    chip.set('pdk','grid', stackup, 'met1', 'xoffset', 0.17)
    chip.set('pdk','grid', stackup, 'met1', 'xpitch',  0.34)
    chip.set('pdk','grid', stackup, 'met1', 'yoffset', 0.17)
    chip.set('pdk','grid', stackup, 'met1', 'ypitch',  0.34)
    chip.set('pdk','grid', stackup, 'met1', 'adj', 0.5)

    chip.set('pdk','grid', stackup, 'met2', 'name', 'm2')
    chip.set('pdk','grid', stackup, 'met2', 'xoffset', 0.23)
    chip.set('pdk','grid', stackup, 'met2', 'xpitch',  0.46)
    chip.set('pdk','grid', stackup, 'met2', 'yoffset', 0.23)
    chip.set('pdk','grid', stackup, 'met2', 'ypitch',  0.46)
    chip.set('pdk','grid', stackup, 'met2', 'adj', 0.5)

    chip.set('pdk','grid', stackup, 'met3', 'name', 'm3')
    chip.set('pdk','grid', stackup, 'met3', 'xoffset', 0.34)
    chip.set('pdk','grid', stackup, 'met3', 'xpitch',  0.68)
    chip.set('pdk','grid', stackup, 'met3', 'yoffset', 0.34)
    chip.set('pdk','grid', stackup, 'met3', 'ypitch',  0.68)
    chip.set('pdk','grid', stackup, 'met3', 'adj', 0.5)

    chip.set('pdk','grid', stackup, 'met4', 'name', 'm4')
    chip.set('pdk','grid', stackup, 'met4', 'xoffset', 0.46)
    chip.set('pdk','grid', stackup, 'met4', 'xpitch',  0.92)
    chip.set('pdk','grid', stackup, 'met4', 'yoffset', 0.46)
    chip.set('pdk','grid', stackup, 'met4', 'ypitch',  0.92)
    chip.set('pdk','grid', stackup, 'met4', 'adj', 0.5)

    chip.set('pdk','grid', stackup, 'met5', 'name', 'm5')
    chip.set('pdk','grid', stackup, 'met5', 'xoffset', 1.7)
    chip.set('pdk','grid', stackup, 'met5', 'xpitch',  3.4)
    chip.set('pdk','grid', stackup, 'met5', 'yoffset', 1.7)
    chip.set('pdk','grid', stackup, 'met5', 'ypitch',  3.4)
    chip.set('pdk','grid', stackup, 'met5', 'adj', 0.5)

    ###############################################
    # Libraries
    ###############################################

    rev = 'v0_0_2'
    libname = 'sky130hd' # not sure if this should be something else
    libtype = 'hd' # TODO: update this

    # TODO: should I be using a different name for the corner
    corner = 'typical'

    libdir = os.path.join('..', 'third_party', 'pdks', foundry, process, 'libs', libname, rev)


    chip.set('library', libname, 'type', 'stdcell')

    # rev
    chip.set('library', libname, 'package', 'version', rev)

    # timing
    chip.add('library', libname, 'nldm', corner, 'lib',
             libdir+'/lib/sky130_fd_sc_hd__tt_025C_1v80.lib')

    # lef
    chip.add('library', libname, 'lef',
             libdir+'/lef/sky130_fd_sc_hd_merged.lef')
    # gds
    chip.add('library', libname, 'gds',
             libdir+'/gds/sky130_fd_sc_hd.gds')

    # placement sites
    chip.set('library', libname, 'site', 'unithd', 'symmetry', 'Y')
    chip.set('library', libname, 'site', 'unithd', 'size', (0.46,2.72))

    chip.set('library', libname, 'site', 'unithddbl', 'symmetry', 'Y')
    chip.set('library', libname, 'site', 'unithddbl', 'size', (0.46,5.44))

    # lib arch
    chip.set('library', libname, 'arch', libtype)

    # clock buffers
    chip.add('library', libname, 'cells', 'clkbuf', 'sky130_fd_sc_hd__clkbuf_1')

    # hold cells
    chip.add('library', libname, 'cells', 'hold', 'sky130_fd_sc_hd__buf_1')

    # filler
    chip.add('library', libname, 'cells', 'filler', ['sky130_fd_sc_hd__fill_1',
                                                     'sky130_fd_sc_hd__fill_2',
                                                     'sky130_fd_sc_hd__fill_4',
                                                     'sky130_fd_sc_hd__fill_8'])

    # Tapcell
    chip.add('library', libname, 'cells','tapcell', 'sky130_fd_sc_hd__tapvpwrvgnd_1')

    # Endcap
    chip.add('library', libname, 'cells', 'endcap', 'sky130_fd_sc_hd__decap_4')

    chip.add('library', libname, 'cells', 'ignore', [
        'sky130_fd_sc_hd__probe_p_8',
        'sky130_fd_sc_hd__probec_p_8',
        'sky130_fd_sc_hd__lpflow_bleeder_1',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_1',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_16',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_2',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_4',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_8',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_1',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_16',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_2',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_4',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_8',
        'sky130_fd_sc_hd__lpflow_decapkapwr_12',
        'sky130_fd_sc_hd__lpflow_decapkapwr_3',
        'sky130_fd_sc_hd__lpflow_decapkapwr_4',
        'sky130_fd_sc_hd__lpflow_decapkapwr_6',
        'sky130_fd_sc_hd__lpflow_decapkapwr_8',
        'sky130_fd_sc_hd__lpflow_inputiso0n_1',
        'sky130_fd_sc_hd__lpflow_inputiso0p_1',
        'sky130_fd_sc_hd__lpflow_inputiso1n_1',
        'sky130_fd_sc_hd__lpflow_inputiso1p_1',
        'sky130_fd_sc_hd__lpflow_inputisolatch_1',
        'sky130_fd_sc_hd__lpflow_isobufsrc_1',
        'sky130_fd_sc_hd__lpflow_isobufsrc_16',
        'sky130_fd_sc_hd__lpflow_isobufsrc_2',
        'sky130_fd_sc_hd__lpflow_isobufsrc_4',
        'sky130_fd_sc_hd__lpflow_isobufsrc_8',
        'sky130_fd_sc_hd__lpflow_isobufsrckapwr_16',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_1',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_2',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_4',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_4',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_1',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_2',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_4',
        'sky130_fd_sc_hd__buf_16'
    ])

    # TODO: should probably fill these in, but they're currently unused by
    # OpenROAD flow
    #driver
    chip.add('library', libname, 'driver', '')

    # buffer cell
    chip.add('library', libname, 'cells', 'buf', ['sky130_fd_sc_hd__buf_4/A/X'])

    # tie cells
    chip.add('library', libname, 'cells', 'tie', ['sky130_fd_sc_hd__conb_1/HI',
                                                  'sky130_fd_sc_hd__conb_1/LO'])

    ###############################################
    # Methodology
    ###############################################

    chip.add('asic', 'targetlib', libname)
    chip.set('asic', 'stackup', chip.get('pdk', 'stackup')[0])
    # TODO: how does LI get taken into account?
    chip.set('asic', 'minlayer', "m1")
    chip.set('asic', 'maxlayer', "m5")
    chip.set('asic', 'maxfanout', 5) # TODO: fix this
    chip.set('asic', 'maxlength', 21000)
    chip.set('asic', 'maxslew', 1.5e-9)
    chip.set('asic', 'maxcap', .1532e-12)
    chip.set('asic', 'rclayer', 'clk', 'm5')
    chip.set('asic', 'rclayer', 'data', 'm3')
    chip.set('asic', 'hpinlayer', "m3")
    chip.set('asic', 'vpinlayer', "m2")

    corner = 'typical'
    # hard coded mcmm settings (only one corner!)
    chip.set('mcmm','worst','libcorner', corner)
    chip.set('mcmm','worst','pexcorner', corner)
    chip.set('mcmm','worst','mode', 'func')
    chip.add('mcmm','worst','check', ['setup','hold'])

    # Floorplanning defaults for quick experiments
    chip.set('asic', 'density', 10, clobber=False)
    chip.set('asic', 'aspectratio', 1, clobber=False)
    # Least common multiple of std. cell width (0.46) and height (2.72)
    chip.set('asic', 'coremargin', 62.56, clobber=False)

#########################
if __name__ == "__main__":

    chip = make_docs()
    chip.writecfg('skywater130.json')
