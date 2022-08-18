# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/renode-colab-tutorial/blob/main/tutorial.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/renode-colab-tutorial/blob/main/tutorial.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/renode-colab-tutorial/blob/main/tutorial.py)

### Table of contents

1. Intro to Renode
1. Platforms and scripts
1. Running simple tests
1. Getting more info from your simulation
1. Automated tests
1. CFU integration
"""

# %% [markdown]
"""
## Welcome to Renode!

This tutorial will guide you through the basic concepts of Renode usage and its applicability in ML accelerator development.

We will cover basic features like tracing, logging and testing.

This notebook is not intended to be run locally as it aims to run on Ubuntu 18.04 and tries to install many software packages.
Please run it in a Google Colab environment instead, inside a VM or a container.

A note on the syntax:
"""

# %%
! echo "this is a Bash command, it starts with a '!'"

print("This is Python, it has no prefix")

%env MESSAGE="This is IPython Magic, starting with a '%'"

# %% [markdown]
"""
## What is Renode?

* open source!
* instruction set simulator
* functional simulator
* single and multi-node scenarios support
* determinism and controlability
* running the same software you'd put on hardware

Go and see the [Renode website](https://renode.io), download [sources](https://github.com/renode/renode), check out the [slide deck](https://about.renode.io), or read the [documentation](https://docs.renode.io/).
"""

# %% [markdown]
"""
## Context of the workshop

As a part of the VEDLIoT project, we have developed several features in Renode to accelerate ML testing.

We added support for RISC-V Custom Function Units - small accelerators tailored for specific use cases, tightly integrated with the CPU.

CFUs are implemented in HDL and compiled with Verilator to create a cycle-accurate model.
Together with Renode functional simulation, using the interface developed in VEDLIoT, they create a so-called co-simulation setup.

<img src="https://antmicro.com/blog/images/CFU-renode-diagram.svg" width="1200">

See it in practice on Google's [CFU Playground](https://github.com/google/CFU-Playground/)!

![System overview](https://raw.githubusercontent.com/antmicro/renode-colab-tutorial/main/images/system.png)

Our system is built from the [LiteX](https://github.com/enjoy-digital/litex/) soft SoC generator, using the [VexRiscv core](https://github.com/SpinalHDL/VexRiscv), targeting the Digilent Arty with Xilinx Artix-7 FPGA. 

<img src="https://raw.githubusercontent.com/antmicro/renode-colab-tutorial/main/images/arty.png" width="700">
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git # only needed in the Colab environment
! pip install -q git+https://github.com/antmicro/renode-run.git # one of the ways to get Renode (Linux only)
! pip install -q https://github.com/antmicro/pyrenode/archive/mh/flushing.zip # a library to talk to Renode from Python
! pip install -q robotframework==4.0.1 # testing framework used by Renode
# as the compilation process takes several minutes, we will conveniently skip it here and use precompiled binaries
! git clone https://github.com/antmicro/renode-colab-tutorial # repository with resources for this tutorial
! wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex/tools/litex_json2renode.py  # a helper script

# %% [markdown]
"""
## Getting Renode

Go to https://builds.renode.io and download a nightly build for your OS.
Visit [Renode's README](https://github.com/renode/renode/blob/master/README.rst#installation) for full installation instructions.

Quick links:

- [Linux portable package](https://dl.antmicro.com/projects/renode/builds/renode-latest.linux-portable.tar.gz)
- [Windows portable package](https://dl.antmicro.com/projects/renode/builds/renode-latest.zip)
- [MacOS dmg installer](https://dl.antmicro.com/projects/renode/builds/renode-latest.dmg)

If you're on Linux, you can use the ``renode-run`` PIP package:
"""

# %%
! renode-run download

# %% [markdown]
"""
## Start Renode

To start Renode locally, unpack or install the downloaded package and run the ``./renode`` command.

If you installed Renode via ``renode-run``, just run ``renode-run``.

You will see the following window, the Renode Monitor:

![Renode](https://raw.githubusercontent.com/antmicro/renode-colab-tutorial/main/images/renode-monitor-cli.png)

The Monitor allows you to use Renode interactively.
Due to the nature of Google Colab and Jupyter Notebooks, this tutorial will focus on a Python-based interaction with Renode.

We will start Renode with the help of the ``pyrenode`` package:
"""

# %%
# Re-run this snippet if your Colab seems to be stuck!
from pyrenode import connect_renode, get_keywords, shutdown_renode

def restart_renode():  # this might be useful if you ever see Renode not responding!
  shutdown_renode()
  connect_renode()
  get_keywords()

restart_renode()

# %% [markdown]
"""
## Interaction with Renode

Renode uses two file types to set up the simulation:

* REPL - Renode Platform
* RESC - Renode Script

Platforms define SoCs and boards, scripts describe the interconnection between
platforms and the outside world, select software payloads, and tune emulation parameters.

Platform files can either be written by hand (see our [Supported boards](https://renode.readthedocs.io/en/latest/introduction/supported-boards.html) page!)
or generated from:

* device tree (see [Renode Zephyr Dashboard!](https://zephyr-dashboard.renode.io/))
* LiteX platform configuration
* OpenTitan platform configuration
* ...
"""

# %% [markdown]
"""
## Building platform from LiteX json
"""

# %%
! cat renode-colab-tutorial/conf/csr.json

# %%
! python ./litex_json2renode.py --repl digilent_arty_generated.repl renode-colab-tutorial/conf/csr.json
! echo "============="
! echo "Platform file:"
! cat digilent_arty_generated.repl
! echo -e "\n\nCFU-specific part:\n==================\n\n"
! cat renode-colab-tutorial/conf/digilent_arty.repl

# %% [markdown]
"""
## Preparing a simulation script

It will be responsible for loading the platform description and loading binaries.
"""

# %%
%%writefile script.resc

using sysbus                                          # a convenience - allows us to write "uart" instead of "sysbus.uart"
mach create "digilent_arty"
machine LoadPlatformDescription $ORIGIN/renode-colab-tutorial/conf/digilent_arty.repl       # load the repl file we just created
uart RecordToAsciinema $ORIGIN/output.asciinema       # movie-like recording of the UART output, open with https://github.com/asciinema/asciinema-player/
showAnalyzer uart                                     # open a console window for UART, or put the output to the log
logFile $ORIGIN/log true                              # enable logging to file, flush after every write

macro reset
"""
    cpu.cfu0 SimulationFilePathLinux $ORIGIN/renode-colab-tutorial/binaries/libVtop.so       # actual verilated CFU
    sysbus LoadELF $ORIGIN/renode-colab-tutorial/binaries/software.elf                       # software we're going to run
"""
runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
def Restart():
  ResetEmulation()                # Does this hang for you? Replace with `restart_renode()`
  ExecuteScript("script.resc")
  CreateTerminalTester("sysbus.uart", timeout=5)

Restart()
StartEmulation()
WaitForLineOnUart("Hello World!") # Is this correct?
WaitForPromptOnUart("main>")


# %% [markdown]
"""## UART output"""

# %%
ResetEmulation()  # flush the asciinema output
from renode_colab_tools import asciinema
asciinema.display_asciicast('output.asciinema')

# %% [markdown]
"""## Run some tests"""

# %%
Restart()
StartEmulation()

WaitForLineOnUart("Hello, World!")
WaitForPromptOnUart("main>")

WriteToUart("1")
WaitForPromptOnUart("models>")

# %% [markdown]
"""
## Tracing execution

Renode has plenty of different tracing and logging options.

You can trace:

* executed functions or code blocks as logs or interactive graphs
* memory and peripheral accesses
* executed opcodes
* ...
"""

# %% [markdown]
"""
## Function names logging

When loading ELF files with function symbols, we can use this information for logging purposes.

This gives you a good overview of the application progress and makes it easy to analyze bugs.
"""

# %%
Restart()
ExecuteCommand("cpu LogFunctionNames true true") # this enables logging of functions
StartEmulation()

WaitForLineOnUart("Hello, World!")
WaitForPromptOnUart("main>")

WriteToUart("1")
WaitForPromptOnUart("models>")

# %%
# flush the log and print it out
ResetEmulation()
! cat log

# %% [markdown]
"""
## Need more context!

Function names would be more useful if we actually knew what was happening in the SoC!
"""

# %%
Restart()

ExecuteCommand("cpu LogFunctionNames true true")
ExecuteCommand("sysbus LogAllPeripheralsAccess true")

# You can also decide to be more precise:
# ExecuteCommand("cpu LogFunctionNames true 'uart_' true")
# ExecuteCommand("sysbus LogPeripheralAccess uart")

StartEmulation()

WaitForLineOnUart("Hello, World!")
WaitForPromptOnUart("main>")

WriteToUart("1")
WaitForPromptOnUart("models>")

# %% [markdown]
"""
## Speedscope traces

Renode allows for different types of graphical traces.

We currently support the https://www.speedscope.app/ viewer and are working on https://perfetto.dev.

Also, GCOV tracing support is in progress.
"""

# %%
Restart()
ExecuteCommand("cpu EnableProfiler true $CWD/speedscope.log true")
StartEmulation()

WaitForLineOnUart("Hello, World!")
WaitForPromptOnUart("main>")

WriteToUart("1")
WaitForPromptOnUart("models>")

WriteToUart("2")
WaitForPromptOnUart("mnv2>")

WriteToUart("1")
WaitForPromptOnUart("mnv2>")

# %%
ResetEmulation()
# download the tracefile
# you can open it here: https://www.speedscope.app/
from google.colab import files
files.download('speedscope.log') 

# %% [markdown]
"""
## Opcodes counting

The CFU scenario, where we try to offload complex computation to another unit, can benefit from analysis if the application is using the accelerator effectively.

The same features can be used to analyze the usefulness of other extensions as well, e.g. vector instructions.
"""

# %%
Restart()
ExecuteCommand("cpu EnableRiscvOpcodesCounting")
ExecuteCommand("cpu EnableCustomOpcodesCounting")
StartEmulation()

WaitForLineOnUart("Hello, World!")
WaitForPromptOnUart("main>")

WriteToUart("1")
WaitForPromptOnUart("models>")

WriteToUart("2")
WaitForPromptOnUart("mnv2>")

WriteToUart("1")
WaitForPromptOnUart("mnv2>")

ExecuteCommand("pause")
result = ExecuteCommand("cpu GetAllOpcodesCounters")
print(result)

# %% [markdown]
"""
## Renode metrics analysis

There's a lot more data that can be analyzed!

Renode allows you to track virtually any event.

We provide an infrastructure to record executed instructions, memory accesses, CPU exceptions, and peripheral accesses.
"""

# %%
Restart()
ExecuteCommand("machine EnableProfiler $CWD/metrics.dump")
StartEmulation()

WaitForLineOnUart("Hello, World!")
WaitForPromptOnUart("main>")

WriteToUart("1")
WaitForPromptOnUart("models>")

WriteToUart("2")
WaitForPromptOnUart("mnv2>")

# %% [markdown]
"""
On your host you'd run a Python script that would generate PNG images of graphs, or you'd use our library to parse data.

In Colab we use our helper scripts to display things inline.
"""
# %%
ResetEmulation()
import sys
from pathlib import Path
renode_path = Path('/root/.config/renode/renode-run.path').read_text()
sys.path.append(renode_path)

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)

# %% [markdown]
"""
## Testing with Renode

Renode is very useful for interactive development, but one of its most important applications is in testing.

Continuous Integration environment can work with Renode in many different ways, e.g. using the Python library we used above.

The most robust approach to Renode testing, also used in our own CI systems, is via the [Robot Framework](https://robotframework.org/).

![Robot](https://robotframework.org/img/RF.svg)

Robot offers a scripting languagevto describe test cases and can integrate with so-called keywords provided by external applications.

You already know these keywords: ``ExecuteCommand``, ``StartEmulation``, ``WaitForLineOnUart`` etc.
"""

# %%
%%writefile test.robot

*** Settings ***
Suite Setup                   Setup
Suite Teardown                Teardown
Test Setup                    Reset Emulation
Test Teardown                 Test Teardown
Resource                      ${RENODEKEYWORDS}

*** Keywords ***
Create Machine
    Execute Command          include @${CURDIR}/script.resc
    Create Terminal Tester   sysbus.uart

    Start Emulation

*** Test Cases ***
Should Run Mobile Net V2 Golden Tests
    Create Machine

    Wait For Line On Uart    CFU Playground
    Wait For Prompt On Uart  main>
    Write Line To Uart       1
    Wait For Prompt On Uart  models>
    Write Line To Uart       2
    Wait For Prompt On Uart  mnv2>
    Write Line To Uart       g
    Wait For Line On Uart    Golden tests passed  120 
    Wait For Prompt On Uart  mnv2>


Should Run TFLite Unit Tests
    Create Machine

    Write Line To Uart       5
    Wait For Line On Uart    CONV TEST:
    Wait For Line On Uart    ~~~ALL TESTS PASSED~~~
    Wait For Line On Uart    DEPTHWISE_CONV TEST:
    Wait For Line On Uart    ~~~ALL TESTS PASSED~~~
    Wait For Prompt On Uart  main>


Should Run 1x1 Conv2D Golden Tests
    Create Machine

    Write Line To Uart       3
    Wait For Prompt On Uart  mnv2_first>
    Write Line To Uart       1
    Wait For Line On Uart    OK - output tensor matches
    Wait For Prompt On Uart  mnv2_first>

# %%
renode_path = Path('/root/.config/renode/renode-run.path').read_text()
! {renode_path}/renode-test test.robot

# %% [markdown]
"""
## CFU Integration

Based on Verilator, Renode's co-simulation infrastructure lets you connect signals of different IP blocks written in HDL.

The interface for CFU Playground [is common for all examples on their repository](https://github.com/google/CFU-Playground/tree/main/common/renode-verilator-integration).

Each bus we use to connect to verilated peripherals requires a specific interface, and Renode specifies [one for CFUs as well](https://github.com/renode/renode/blob/master/src/Plugins/VerilatorPlugin/VerilatorIntegrationLibrary/src/buses/cfu.cpp).

<img src="https://antmicro.com/blog/images/CFU-renode-diagram.svg" width="1200">

"""