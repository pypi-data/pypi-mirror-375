.. _examples_prerequisites_for_execution_without_slurm_sec:

Prerequisites for running example scripts or Jupyter notebooks without using a SLURM workload manager
=====================================================================================================

Prior to running any scripts or Jupyter notebooks in the directory
``<root>/examples`` without using a SLURM workload manager, where ``<root>`` is
the root of the ``emicroml`` repository, a set of Python libraries need to be
installed in the Python environment within which any such scripts or Jupyter
notebooks are to be executed.

The Python libraries that need to be installed in said Python environment are::

  numpy
  numba
  hyperspy
  h5py
  pytest
  ipypml
  jupyter
  torch
  kornia
  blosc2
  msgpack
  pyopencl
  pyFAI
  pyprismatic>=2.0
  czekitout
  fancytypes
  h5pywrappers
  distoptica
  fakecbed>=0.3.6
  empix
  embeam
  prismatique
  emicroml

With appropriately chosen command line arguments, the script
:download:`<root>/default_env_setup_for_slurm_jobs.sh
<../../default_env_setup_for_slurm_jobs.sh>` will attempt to create a virtual
environment, then activate it, and then install the above Python libraries. If
the script is executed on a Digital Alliance of Canada (DRAC) high-performance
computing (HPC) server, then the virtual environment is created via
``virtualenv``. Otherwise, the virtual environment is created via ``conda``. For
the latter scenario, an ``anaconda`` or ``miniconda`` distribution must be
installed prior to running the script.

The correct form of the command to run the script is::

  source <path_to_current_script> <env_name> <install_extras>

where ``<path_to_current_script>`` is the absolute or relative path to the
script :download:`<root>/default_env_setup_for_slurm_jobs.sh
<../../default_env_setup_for_slurm_jobs.sh>`; ``<env_name>`` is the path to the
virtual environment, if the script is being executed on a DRAC HPC server, else
it is the name of the ``conda`` virtual environment; and ``<install_extras>`` is
a boolean, i.e. it should either be ``true`` or ``false``. If
``<install_extras>`` is set to ``true``, then the script will attempt to install
within the environment the dependencies required to run all of the examples in
the repository, in addition to installing ``emicroml``. Otherwise, the script
will attempt to install only ``emicroml`` and its dependencies, i.e. not the
additional libraries required to run the examples.

If for whatever reason the script
:download:`<root>/default_env_setup_for_slurm_jobs.sh
<../../default_env_setup_for_slurm_jobs.sh>` fails to create and the activate
successfully a virtual environment equipped with the Python libraries listed
above, then one will need to do so manually according to the constraints imposed
by the machine or server on which you intend to run examples.
