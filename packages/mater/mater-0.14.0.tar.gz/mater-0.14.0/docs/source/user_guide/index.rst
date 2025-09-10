.. _user_guide:

==========
User Guide
==========

.. .. include:: ../../../README.md
..    :parser: myst_parser.sphinx_

Use `init-mater-project <https://gricad-gitlab.univ-grenoble-alpes.fr/isterre-dynamic-modeling/mater-project/init-mater-project>`_ (recommended)
================================================================================================================================================

It provides a complete project structure, CLI tools, and data pipeline in minutes.

Direct MATER Core usage
=======================

It is only recommended for:  

* Custom integrations in existing codebases
* Advanced users building specialized tools
* Contributing to the MATER framework itself

Example: Run a Simulation with an Excel file
-----------------------------------

Install the `mater` package in your project via **UV (recommended)** or pip:

.. code-block:: bash

    uv add mater
    # Or
    pip install mater

Create a Python script in your working directory to run simulations. Ensure the required `Excel input file <https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version>`_ (chose a compatible version) is located in the root of your working directory.

Create a file named ``simulate.py`` (or any name you prefer) with the following content:

.. code-block:: python

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

To run your simulation:

1. Edit the configuration values at the top of the script

2. Save the file

3. Execute the script:

.. code-block:: bash

    uv run simulate.py