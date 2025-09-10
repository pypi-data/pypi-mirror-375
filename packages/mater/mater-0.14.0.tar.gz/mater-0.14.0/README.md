# MATER

Metabolic Analysis for Transdisciplinary Ecological Research

[TOC]

## 📋 Requirements

- Python 3.12 or higher

We recommend using one virtual environment per Python project to manage dependencies and maintain isolation. You can use a package manager like [uv](https://docs.astral.sh/uv/) to help you with library dependencies and virtual environments.

## Quick start

**Use [init-mater-project](https://gricad-gitlab.univ-grenoble-alpes.fr/isterre-dynamic-modeling/mater-project/init-mater-project) (recommended)**.  
It provides a complete project structure, CLI tools, and data pipeline in minutes.

> 💡 Direct MATER Core usage is only recommended for:  
> - Custom integrations in existing codebases
> - Advanced users building specialized tools
> - Contributing to the MATER framework itself

## Direct MATER Core usage

Install the `mater` package in your project via **UV (recommended)** or pip:

```bash
uv add mater
# Or
pip install mater
```

### Example: Run a Simulation with an Excel file

Create a Python script in your working directory to run simulations. Ensure the required [Excel input file](https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version) (chose a compatible version) is located in the root of your working directory.

Create a file named `simulate.py` (or any name you prefer) with the following content:

```python
"""
MATER simulation script.
"""

# === CONFIGURATION ===
INPUT_FILE = "your_file.xlsx"  # Name of your Excel input file
OUTPUT_FOLDER = "run0"         # Name of the folder where outputs are stored
START_TIME = 1901              # Initial time step
END_TIME = 2100                # Final time step
TIME_FREQUENCY = "YS"          # Time frequency
# === END CONFIGURATION ===

from mater import Mater

def main():
    """Run MATER simulation."""
    model = Mater()
    model.run_from_excel(
        OUTPUT_FOLDER,
        INPUT_FILE,
        simulation_start_time=START_TIME,
        simulation_end_time=END_TIME,
        time_frequency=TIME_FREQUENCY,
    )

if __name__ == "__main__":
    main()
```

To run your simulation:

1. Edit the configuration values at the top of the script

2. Save the file

3. Execute the script:

```python
uv run simulate.py
```

## Output variables description

| **Output variable**        | **Unit**                          | **Definition**                                         | **Example**                                                                                                      |
|----------------------------|-----------------------------------|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| control_flow               | <object_unit>/time                | Object footprint demand before trade between locations | Number of cars consumed in China (included the imported ones)                                                     |
| extraneous_flow            | <object_unit>/time                | Object consumption or coproduction                     | C02 coproduced (+ value) and coal consumed (- value) by the electricity production process of a coal power plant |
| in_use_stock               | <object_unit>                     | Object in use stock                                    | Number of cars in use                                                                                            |
| old_stock                  | <object_unit>                     | Object stock in landfill                               | Number of end of life cars unrecycled                                                                            |
| process                    | <process_unit>/time               | Number of process made by an object                    | Transportation process (km/year) made by cars                                                                    |
| recycling_flow             | <object_unit>/time                | Quantity of recycled objects                           | Recycled end of life cars                                                                                        |
| reference_intensity_of_use | <process_unit>/<object_unit>/time | Intensity of use                                       | Number of km per year made by a car                                                                              |
| reference_stock            | <object_unit>                     | How many objects should be in the in use stock         | Installed power plant capacity to fulfill the electricity demand                                                 |
| secondary_production       | <object_unit>/time                | Coproduction due to recycling processes                | Quantity of steel recycled (coproduce by recycling) in a year                                                    |
| self_disposal_flow         | <object_unit>/time                | End of life flow                                       | Number of cars that cannot work anymore                                                                       |
| traded_control_flow        | <object_unit>/time                | Object supply after trade between locations            | Number of cars produced in China (included the exported ones)                                                    |

### Accessing the Results from a Python Script

Below is an example Python script using `pandas` and `matplotlib` to plot specific simulation results. Each folder in the output directory corresponds to a variable that can be loaded with `pandas`.

```python
# Import the MATER package and matplotlib.pyplot
import matplotlib.pyplot as plt
from mater import Mater

# Create a Mater instance
model = Mater()

# Select the output directory where the run results are stored
model.set_output_dir()  # Defaults to the working directory

# Set the run directory name
model.set_run_name("run0")

# Get a variable
in_use_stock = model.get("in_use_stock")

# Transform the dataframe and plot the results
in_use_stock.groupby(level=["location", "object"]).sum().T.plot()
plt.show()
```

This example demonstrates how to access and plot variables from simulation outputs. Adjust the code to fit your analysis needs.

## 🤝 Contributing

We welcome contributions to the MATER project! To get started, please refer to the [CONTRIBUTING](CONTRIBUTING.md) file for detailed guidelines.

## 📚 Online Documentation

For more information, refer to the official **[MATER documentation](https://isterre-dynamic-modeling.gricad-pages.univ-grenoble-alpes.fr/mater-project/mater/)**.
