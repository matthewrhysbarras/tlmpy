"""Experimental numerical methods.

APIs in this namespace are research prototypes and may change without notice.
"""

from tlmpy.experimental.parabolic_tlm import (
    ParabolicTLMDiffusion2D,
    TLMStateEstimator,
    parabolic_ys,
)

__all__ = ["ParabolicTLMDiffusion2D", "TLMStateEstimator", "parabolic_ys"]
