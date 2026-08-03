from z3 import *
from itertools import *

io_pairs = [
   ((3, 5, 2),192),
   ((6, 9, 3),9216),
   ((23, 1, 1),46),  
   ((16, 6, 5),5120),  
   ((8, 9, 1),4096)
]

NUM_INPUTS = 3

'''
Convenience functions for creating a constraint using a flag with identifier
'i' that toggles whether the operator is used for operands x1 and x2.
Use is OPTIONAL.
'''
def mul(i, x1, x2):
    return If(Bool(f'B{i}'), (x1 * x2), BitVecVal(0, 16))

def shl(i, x1, x2):
    return If(Bool(f'B{i}'), (x1 << x2), BitVecVal(0, 16))

'''
The main steps of the synthesis process are as follows:

1. Define Z3 variables and expressions for the possible operations.
2. Add a constraints to only allow one operation to be part of the solution per line.
3. Add constraints for each input-output pair.
4. Solve the Z3 formula to synthesize the function.
'''
def formula(pairs):
    constraint = True
    for i, (inputs, output) in enumerate(io_pairs):
        # we will be setting up a program that looks like:
        # z0 := input[0] # step (1)
        # z1 := input[1] # step (1)
        # z2 := input[2] # step (1)
        # z3 := f?(z?,z?) # step (2)
        # z4 := f?(z3,z?) # step (3)
        # output == z4 # step (4)

        # step (1) set the first 3 vars (z0,z1,z2) of the program equal to the inputs
        z0 = BitVec(f"z0_{i}", 16)
        z1 = BitVec(f"z1_{i}", 16)
        z2 = BitVec(f"z2_{i}", 16)
        input_constr = And(*[BitVec(f"z{j}_{i}", 16) == inputs[j] for j in range(NUM_INPUTS)])
        constraint = And(constraint, input_constr)

        # step (2) set the fourth var (z3) equal to a binary function. we will synthesize the function and its inputs

        # value constraints for the first function
        z3 = BitVec(f"z3_{i}", 16) # output
        z3_lhs = BitVec(f"z3_lhs_{i}", 16) # lhs input
        z3_rhs = BitVec(f"z3_rhs_{i}", 16) # rhs input
        z3_constr = mul(0, z3_lhs, z3_rhs) + shl(1, z3_lhs, z3_rhs) == z3 # choose a function (component)
        z3_one_comp_constr = sum([If(Bool(f'B{i}'), 1, 0) for i in [0,1]]) == 1 # chose ONE function
        constraint = And(constraint, z3_constr)
        constraint = And(constraint, z3_one_comp_constr)

        # label constraints for the first function
        l_z3_lhs = Int("l_z3_lhs") # label for the lhs input
        l_z3_rhs = Int("l_z3_rhs") # label for the rhs input
        l_z3_lhs_constr = And(0 <= l_z3_lhs, l_z3_lhs < 3) # lhs input label can only be one of the three inputs
        l_z3_rhs_constr = And(0 <= l_z3_rhs, l_z3_rhs < 3) # rhs input label can only be one of the three inputs
        constraint = And(constraint, l_z3_lhs_constr)
        constraint = And(constraint, l_z3_rhs_constr)

        # constraint \psi_{conn}
        # encodes the value of vars based on locations
        z3_lhs_loc_constr = [Implies(Int("l_z3_lhs") == j, BitVec(f"z3_lhs_{i}", 16) == BitVec(f"z{j}_{i}", 16)) for j in range(3)]
        z3_rhs_loc_constr = [Implies(Int("l_z3_rhs") == j, BitVec(f"z3_rhs_{i}", 16) == BitVec(f"z{j}_{i}", 16)) for j in range(3)]
        constraint = And(constraint, *z3_lhs_loc_constr)
        constraint = And(constraint, *z3_rhs_loc_constr)

        # step (3) set the fifth var (z4) equal to a binary function. we will synthesize the function and its inputs

        # value constraints for the second function
        z4 = BitVec(f"z4_{i}", 16) # output
        # no need to specify a z4_lhs variable: we know it's just z3
        z4_rhs = BitVec(f"z4_rhs_{i}", 16) # rhs input
        z4_constr = mul(2, z3, z4_rhs) + shl(3, z3, z4_rhs) == z4 # choose a function (component)
        z4_one_comp_constr = sum([If(Bool(f'B{i}'), 1, 0) for i in [2,3]]) == 1 # chose ONE function
        constraint = And(constraint, z4_constr)
        constraint = And(constraint, z4_one_comp_constr)

        # label constraints for the second function
        l_z4_rhs = Int("l_z4_rhs") # label for the rhs input
        l_z4_rhs_constr = And(0 <= l_z4_rhs, l_z4_rhs < 3) # rhs input label can only be one of the three inputs
        constraint = And(constraint, l_z4_rhs_constr)

        # constraint \psi_{conn}
        # encodes the value of vars based on locations
        # in the second function, the rhs var is one of the inputs (the lhs var is z3 though)
        z4_rhs_loc_constr = [Implies(Int("l_z4_rhs") == j, BitVec(f"z4_rhs_{i}", 16) == BitVec(f"z{j}_{i}", 16)) for j in range(3)]
        constraint = And(constraint, *z4_rhs_loc_constr)

        # step (4) the fifth var (z4) must equal the output
        output_constr = z4 == output
        constraint = And(constraint, output_constr)
      
    return constraint

if __name__ == '__main__':
    s = formula(io_pairs)
    print(f'Z3 formula: {s}')
    print('Z3 Solution:')
    solve(s)
