from .constants import *
from ...treebrd.node import Operator

latex_operator = {
    Operator.select: SELECT_OP,
    Operator.project: PROJECT_OP,
    Operator.rename: RENAME_OP,
    Operator.assign: ASSIGN_OP,
    Operator.cross_join: JOIN_OP,
    Operator.natural_join: NATURAL_JOIN_OP,
    Operator.theta_join: THETA_JOIN_OP,
    Operator.full_outer_join: FULL_OUTER_JOIN_OP,
    Operator.left_outer_join: LEFT_OUTER_JOIN_OP,
    Operator.right_outer_join: RIGHT_OUTER_JOIN_OP,
    Operator.union: UNION_OP,
    Operator.difference: DIFFERENCE_OP,
    Operator.intersect: INTERSECT_OP,
}
