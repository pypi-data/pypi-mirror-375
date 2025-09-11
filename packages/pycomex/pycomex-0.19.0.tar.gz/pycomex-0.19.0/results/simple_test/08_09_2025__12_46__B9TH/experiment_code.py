# simple_test configuration file
# Configuration file extending 02_basic.py

# Indicates this is a pycomex configuration file
pycomex: true

# Extend the base experiment
extend: pycomex/examples/02_basic.py

# Configuration name
name: simple_test

# Description for this configuration
description: |
  Configuration file extending 02_basic.py

# Parameters section - contains all parameters from the base experiment
parameters:
  NUM_WORDS: 100
  REPETITIONS: 2