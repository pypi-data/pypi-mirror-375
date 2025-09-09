.. _examples_modelling_cbed_distortion_estimation_analyzing_ml_model_testing_results_sec:

Analyzing machine learning model testing results
================================================

This page summarizes briefly the contents of the Jupyter notebook at the file
path
``<root>/examples/modelling/cbed/distortion/estimation/notebooks/analyzing_ml_model_testing_results.ipynb``,
where ``<root>`` is the root of the ``emicroml`` repository.

In this notebook, we analyze the output that results from performing the
"actions" described in the following pages:

1. :ref:`examples_modelling_cbed_simulations_MoS2_on_amorphous_C_generate_cbed_pattern_sets_sec`
2. :ref:`examples_modelling_cbed_distortion_estimation_generate_ml_datasets_for_ml_model_test_set_1_sec`
3. :ref:`examples_modelling_cbed_distortion_estimation_combine_ml_datasets_for_ml_model_test_set_1_sec`
4. :ref:`examples_modelling_cbed_distortion_estimation_run_ml_model_test_set_1_sec`
5. :ref:`examples_modelling_cbed_distortion_estimation_run_rgm_test_set_1_sec`

In short, in this notebook we analyze the performance results of the "first" set
of machine learning (ML) model tests for the ML task of estimating distortion in
convergent beam electron diffraction (CBED). These performance results are
benchmarked against those obtained by the radial gradient maximization (RGM)
approach to estimating distortion.

In order to execute the cells in this notebook as intended, a set of Python
libraries need to be installed in the Python environment within which the cells
of the notebook are to be executed. See :ref:`this page
<examples_prerequisites_for_execution_without_slurm_sec>` for instructions on
how to do so. Additionally, a subset of the output that results from performing
the aforementioned actions is required to execute the cells in this notebook as
intended. One can obtain this subset of output by executing said actions,
however this requires significant computational resources, including significant
walltime. Alternatively, one can copy this subset of output from a Federated
Research Data Repository dataset by following the instructions given on
:ref:`this page
<examples_modelling_cbed_distortion_estimation_copying_subset_of_output_from_frdr_dataset_sec>`.

It is recommended that you consult the documentation of the :mod:`emicroml`
library as you explore the notebook. Moreover, users should execute the cells in
the order that they appear, i.e. from top to bottom, as some cells reference
variables that are set in other cells above them.
