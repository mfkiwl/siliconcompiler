# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import os
import siliconcompiler

def test_hash_files():
    chip = siliconcompiler.Chip()
    chip.set('design', 'top')
    chip.target("asicflow_freepdk45")
    chip.write_manifest("raw.json")
    allkeys = chip.getkeys()
    for keypath in allkeys:
        if 'file' in chip.get(*keypath, field='type'):
            chip.hash_files(*keypath)
    chip.write_manifest("hashed.json")

#########################
if __name__ == "__main__":
    test_hash_files()
