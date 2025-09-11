# ModularCirc

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

The scope of this package is to provide a framework for building **0D models** and **simulating cardiovascular flow** and **mechanics**. Conceptually, the models can be split into three types of components:
1. **Heart chambers**
2. **Valves**
3. **Vessels**

The current version of the published package contains two models:
1. Naghavi model.
2. Korakianitis Mixed model.

For other models currently under development, see the `dev` branch.

## Setup Conda or python virtual environment

Before installation of the ModularCirc package, please setup a virtual environment using either Conda or python virtual environment.

### Conda setup

Install Conda from https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html

Run:

```
conda create --name <yourenvname>
conda activate <yourenvname>
```

Proceed to installing the ModularCirc package.

### Python virtual environment setup

Run `python3 -m venv venv`. This creates a virtual environment called `venv` in your base directory.

Activate the python environment: `source venv/bin/activate`

Proceed to installing the ModularCirc package.

## Installing ModularCirc

### pip install

To install the pip package:

```bash
python -m pip install ModularCirc
```

### Installation from source:

Clone the ModularCirc GitHub repo locally.

Run:

```
git clone https://github.com/alan-turing-institute/ModularCirc
cd ModularCirc
```

After downloading the GitHub repository, from the repo directory run:

```bash
pip install ./
```

This will install the package based on the `pyproject.toml` file specifications.


## Steps for running basic models
1. Load the classes for the model of interest and the parameter object used to paramterise the said model:
```python
from ModularCirc.Models.NaghaviModel import NaghaviModel, NaghaviModelParameters
```

2. Load the ODE system solver class object:
```python
from ModularCirc.Solver import Solver
```

3. Define a dictionary for parameterising the temporal discretization:
```python
TEMPLATE_TIME_SETUP_DICT = {
    'name'       :  'TimeTest',
    'ncycles'    :  40,
    'tcycle'     :  1.0,
    'dt'         :  0.001,
    'export_min' :  1
 }
```
Here, `ncycles` indicates the maximum number of heart cycles to run, before the simulation finishes.
If the simulation reaches steady state faster than that, the simulation will end provided the number of cycles is higher than `export_min`.
`tcycle` indicates the duration of the heart beat and `dt` represent the time step size used in the temporal discretization.
These measurements assume that time is measured in **seconds**.
If the units used are different, ensure this is done consistently in line with other parameters.

4. Create an instance of the parameter object and used it to change the default values:
```python
parobj = NaghaviModelParameters()
```
**Note 4.1**: the model and parameter object classes are usually defined in pairs and, as such using mismatched types may cause the simulation to behave unexpectedly or may result in a crash.

**Note 4.2**: the method used to parameterise components is typically dependent on the component type, see for example: `set_chamber_comp`, `set_rc_comp` or `set_activation_function`.

5. Create an instance of the model:
```python
model = NaghaviModel(time_setup_dict=TEMPLATE_TIME_SETUP_DICT, parobj=parobj)
```

6. Create an instace of the solver used to peform the simulation:
```python
solver = Solver(model=model)
solver.setup()
```

7. Run the simulation
```python
solver.solve()
```

8. Extract the state variable values of interest.
```python
v_lv = solver.model.components['lv'].V.values
p_lv = solver.model.components['lv'].P_i.values
```

## Example values pv loops for all 4 chambers:
![Example PV loops!](Figures/PV_loops.png)

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/alan-turing-institute/ModularCirc/workflows/CI/badge.svg
[actions-link]:             https://github.com/alan-turing-institute/ModularCirc/actions
[pypi-link]:                https://pypi.org/project/ModularCirc
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/ModularCirc
[pypi-version]:             https://img.shields.io/pypi/v/ModularCirc
<!-- prettier-ignore-end -->
