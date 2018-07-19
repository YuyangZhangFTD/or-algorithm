# Solver Demo

## Usage
$$
\begin{aligned}
max & & 2x_1+3x_2 \\
s.t. & & x_1 + 2x_x \leq 8 \\
& & x_1 \leq 16 \\
& & x_2 \leq 12 \\
\end{aligned}
$$

``
from solver.LpSolver import LpSolver


model = LpSolver("lp")
x = model.add_variables(name="x", index=[1, 2])
model.add_constraint(x[1] + 2 * x[2] <= 8)
model.add_constraint(4 * x[1] <= 16)
model.add_constraint(4 * x[2] <= 12)
model.set_objective(2 * x[1] + 3 * x[2], obj_type=MAXIMIZE)
solution, objective = model.solve()
print(solution)
print(objective)
``