# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import siliconcompiler

def test_create_env():

    chip = siliconcompiler.Chip()
    chip.target('asicflow_freepdk45')
    chip.create_env()

#########################
if __name__ == "__main__":
    test_create_env()
