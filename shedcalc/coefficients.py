"""
* This file holds the pre-calculated coefficients for the models offered by SHED Earth
"""
from numpy import array
class ShedInfo:
    """
    * Static class just to hold the coefficients for the various models
    """
    # coefficients for the various models
    coefficients = {

        # british calibration curve
        'britain': {
            'cronus_age': {
                "model" : "linear",
                "samples": 65,
                "beta": array([-0.59143639, 38.72649816]),
                "eps": 2.0031047998286873,
                "cov": array([[ 3.16847691e-04, -1.29688911e-02], [-1.29688911e-02,  5.55583334e-01]]),
                },
            'balco_age': {
                "model" : "linear",
                "samples": 65,
                "beta": array([-0.55901154, 36.68248565]),
                "eps": 1.9113387857563975,
                "cov": array([[ 3.06362157e-04, -1.24978103e-02], [-1.24978103e-02,  5.34614878e-01]]),
                },
            'lochlomond_age': {
                "model" : "linear",
                "samples": 65,
                "beta": array([-0.59426795, 39.01841865]),
                "eps": 1.5930938747243486,
                "cov": array([[ 3.14671782e-04, -1.28346846e-02], [-1.28346846e-02,  5.48310912e-01]]),
                },
            'rannoch_age': {
                "model" : "linear",
                "samples": 65,
                "beta": array([-0.59576876, 39.1067083 ]),
                "eps": 1.6653089789323747,
                "cov": array([[ 3.15469391e-04, -1.28843006e-02],[-1.28843006e-02,  5.51312984e-01]]),
                },
            'glenroy_age': {
                "model" : "linear",
                "samples": 65,
                "beta": array([-0.5601624, 36.80687893]),
                "eps": 1.5083173595741872,
                "cov": array([[ 3.05141122e-04, -1.24390907e-02], [-1.24390907e-02,  5.31919744e-01]]),
                },
            },

        # Pyrenees calibration curve
        'pyrenees': {
            'cronus_age': {
                "model" : "log",
                "samples": 54,
                "beta": array([-102.15108181,  187.82142242]),
                "eps": 1.9924478773251222,
                "cov": array([[ 10.54929422, -17.71139805], [-17.71139805,  29.78310211]]),
                },
            'balco_age': {
                "model" : "log",
                "samples": 54,
                "beta": array([-97.9763649, 180.0676902]),
                "eps": 1.9666065734174811,
                "cov": array([[ 10.48838616, -17.58666257],[-17.58666257,  29.57576888]]),
                },
            'lochlomond_age': {
                "model" : "log",
                "samples": 54,
                "beta": array([-103.85967253,  191.08943038]),
                "eps": 1.7116440658423313,
                "cov": array([[ 11.33268008, -19.03901768],[-19.03901768,  31.99435932]]),
                },
            'rannoch_age': {
                "model" : "log",
                "samples": 54,
                "beta": [-103.98232945,  191.26860298],
                "eps": 1.7722777321317267,
                "cov": [[ 11.30959993, -18.95497403],[-18.95497403,  31.83834425]],
                },
            'glenroy_age': {
                "model" : "log",
                "samples": 54,
                "beta": array([-98.68890599, 181.39081739]),
                "eps": 1.6540923908763592,
                "cov": array([[ 10.45493824, -17.53969322],[-17.53969322,  29.45222786]]),
                }
            }
        }
