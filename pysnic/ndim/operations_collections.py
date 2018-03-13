from .operations import *
from .lerp import *
from .norm_sqr import *

nd_computations = {
    "1": NdComputations(lerp1, norm1_sqr_arr),
    "2": NdComputations(lerp2, norm2_sqr_arr),
    "3": NdComputations(lerp3, norm3_sqr_arr),
    "nd": NdComputations(lerp_nd, norm_nd_sqr_arr),
}
