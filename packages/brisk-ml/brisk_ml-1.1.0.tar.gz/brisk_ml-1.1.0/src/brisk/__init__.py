"""brisk-ml

A framework that helps train machine learning models using scikit-learn.

This package provides utilities and functionalities to streamline the
process of training and evaluating machine learning models. It is designed to
work seamlessly with scikit-learn while also allowing users to add their own
custom algorithms, metrics and evaluation methods.

Attributes:
    __version__ (str): The current version of the brisk-ml package.

Usage:
    You can access the version number of the package as follows:

    >>> from brisk import __version__
    >>> print(__version__)

For more information, please refer to the documentation or the README file.
"""
from brisk.configuration.algorithm_wrapper import AlgorithmWrapper
from brisk.configuration.algorithm_collection import AlgorithmCollection
from brisk.configuration.configuration_manager import ConfigurationManager
from brisk.configuration.configuration import Configuration
from brisk.data.data_manager import DataManager
from brisk.defaults.regression_algorithms import REGRESSION_ALGORITHMS
from brisk.defaults.regression_metrics import REGRESSION_METRICS
from brisk.defaults.classification_algorithms import CLASSIFICATION_ALGORITHMS
from brisk.defaults.classification_metrics import CLASSIFICATION_METRICS
from brisk.evaluation.metric_manager import MetricManager
from brisk.evaluation.metric_wrapper import MetricWrapper
from brisk.evaluation.evaluation_manager import EvaluationManager
from brisk.evaluation.evaluators.plot_evaluator import PlotEvaluator
from brisk.evaluation.evaluators.measure_evaluator import MeasureEvaluator
from brisk.evaluation.evaluators.registry import EvaluatorRegistry
from brisk.training.training_manager import TrainingManager
from brisk.training.workflow import Workflow
from brisk.version import __version__
