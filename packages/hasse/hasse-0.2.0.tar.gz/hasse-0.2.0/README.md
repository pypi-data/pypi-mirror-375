# hasse
Python library for representing Partially Ordered sets via Hasse Diagrams.

[![Build Status](https://cloud.drone.io/api/badges/mvcisback/hasse/status.svg)](https://cloud.drone.io/mvcisback/hasse)
[![PyPI version](https://badge.fury.io/py/hasse.svg)](https://badge.fury.io/py/hasse)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)

# Installation

If you just need to use `hasse`, you can just run:

`$ pip install hasse`

For developers, note that this project uses the
[poetry](https://poetry.eustace.io/) python package/dependency
management tool. Please familarize yourself with it and then
run:

`$ poetry install`

# Usage

`hasse` is centered around the `hasse.PoSet` class.  An example is
given below.

```python
import hasse

poset = hasse.PoSet.from_chains(
    [1, 2, 4],  # 1 < 2 < 4
    [1, 3, 4],  # 1 < 3 < 4
)

# Test membership and size.
assert 2 in poset
assert len(poset) == 4
assert set(poset) == {1,2,3,4}

# Perform pair wise comparison.
assert poset.compare(1, 1) == '='
assert poset.compare(1, 4) == '<'
assert poset.compare(4, 2) == '>'
assert poset.compare(2, 3) == '||'

# Add an edge.
poset2 = poset.add([2, 1])
poset2.compare(1, 2) == '='
```
PoSet must be a DAG.  For large posets we encourage batching via from_chains over many small add() calls.
