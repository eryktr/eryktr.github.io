Title: Designing an Optimal Diet Using Integer Programming
Date: 01-27-2024
Category: Software Engineering
Tags: software-engineering, programming, math, computer-science, optimization
Slug: integer-programming
Author: eryktr
Summary: In this article, I apply integer programming to tackle the Diet Optimization Problem, the challenge of cost-effectively meeting specific nutritional targets.

# Introduction
There are a variety of tools applicable for solving optimization problems. As a first post in the series, I will focus on integer programming.
In this article, I will introduce the concept of integer programming and apply it to a practical problem of optimizing diet cost. I will build the mathematical model and solve it using the GLPK solver.

# Integer Programming
Integer Programming is a branch of mathematics that focuses on finding the best solution out of a large set of possible solutions.

In many real world problems, the decision variables can only take integer values. For example, it's not possible to produce 3.5 cars or sell 10.7 T-Shirts. Yet, the decision variables should meet some linear constraints (For example, we cannot spend more than $500 and items have fixed prices)
In these cases, the problem should be formulated as an Integer Programming Problem.

The main components of any integer programming problem include:

- Objective function - the mathematical expression that explains the goal of the problem - for example, minimizing cost or maximizing profit
- Decision variables - Quantities we want to find out to produce the optimal solution. For example, the number of employees to hire or products to manufacture. The values are required to be integers.
- Constraints - The restrictions that limit feasible solutions. For example - if creating one product uses 5 pieces of wood and we only have 20 pieces of wood, we cannot manufacture 10 products.

# Difference between Linear Programming and Integer Programming
Linear Programming uses **continuous** decision variables. For example, a value of `10.4` or `0.654` is a possible solution. In Integer Programming, all decision variables have to be variables. Because of that, Integer Programming is a way more computationally expensive approach. 

In terms of Linear Programming, there exists a polynomial-time algorithm to find the optimal solution (Simplex). On the other hand, Integer Programming is NP-complete. However, there are advanced techniques allowing us to solve even complex problems quickly and close-to-optimally.

# Hands On - Diet Cost Optimization
Consider the following problem.

> I have to eat 190 grams of protein, 55 grams of fat and 310 grams of carbs everyday (around 2500 calories).

Also, we have the following products available

| Product        | Price   | Protein [g]  | Fat [g] | Carbs [g] |
|----------------|---------|--------------|---------|-----------|
| Bag of rice    | 1       | 7            | 0       | 78        |
| Chicken breast | 4       | 44           | 8       | 0         |
| Pack of almonds| 5       | 20           | 52      | 20        |
| Avocado        | 4       | 2            | 15      | 9         |

I want to compose a daily diet out of the available products so that I meet the nutritional requirements and minimize the cost.

Let's introduce a couple of variables.

$$
\begin{align}
    &N_{r} - \text{Number of bought bags of rice}\\
    &N_{c} - \text{Number of bought chicken breasts}\\
    &N_{al} - \text{Number of bought packs of almonds}\\
    &N_{av} - \text{Number of bought avocados}
\end{align}
$$

## Objective function
We want to **minimize** the total cost. Just multiply item's price by its quantity and sum up.

$$
\text{Minimize}(N_{r} + 4N_{c} + 5N_{al} + 4N_{av})
$$

## Decision variables
We are looking for the quantities of products to be bought.
All of them are integers.

$$
\left(N_{r}, N_{c}, N_{al}, N_{av}\right) \in \mathbb{Z}^4
$$

## Constraints
There are some obvious constraints

* Each of the decision variables have to be non-negative
* At least total 190 grams of protein
* At least toal 55 grams of fat
* At least total 310 grams of carbs
* We do not want to exceed 2600 calories

Which yields the following inequalities

**Sanity checks**
$$
\begin{align}
&N_r \ge 0\\
&N_c \ge 0\\
&N_{al} \ge 0\\
&N_{av} \ge 0\\
\end{align}
$$

**Protein**
$$
7N_r + 44N_c + 20N_{al} + 2N_{av} \ge 190
$$

**Fat**
$$
8N_c + 52N_{al} + 15N_{av} \ge 55
$$

**Carbs**
$$
78N_r + 20N_{al} + 9N_{av} \ge 310
$$

**Total calories**

This table represents calories present in one gram of corresponding nutrient

| Nutrient        | Calories per gram |
|-----------------|-------------------|
| Protein         | 4                 |
| Fat             | 9                 |
| Carb            | 4                 |


$$
\begin{align}
&C_p - \text{Calories from protein}\\
&C_f - \text{Calories from fat}\\
&C_c - \text{Calories from carbs}\\
&C_t - \text{Total calories}\\
\end{align}
$$
Let's calculate it one by one

$$
\begin{align}
&C_p = 4\left(7N_r + 44N_c + 20N_{al} + 2N_{av}\right)= 28N_r + 176N_c + 80N_{al} + 8N_{av}\\
&C_f = 9\left(8N_c + 52N_{al} + 15N_{av}\right) = 72N_c + 468N_{al} + 135N_{av}\\
&C_c = 4\left(78N_r + 20N_{al} + 9N_{av}\right) = 312N_r + 80N_{al} + 36N_{av}\\
&C_t = C_p + C_f + C_c = 340N_r + 248N_c + 628N_{al} + 179N_{av}
\end{align}
$$

And so the final equation

$$
340N_r + 248N_c + 628N_{al} + 179N_{av} \le 2600 
$$


## Solution
We have definied the problem. Now, let's solve it using an LP solver.
To do this, I'll use the `pulp` library for Python. However, this article is not a guide on how to use `pulp`, thus I'll not go
into too much detail.

```
pip install pulp
```

Then, let's reframe our problem in a script

```python
from pulp import LpVariable, LpProblem

prob = LpProblem("Optimizing diet cost")
Nr = LpVariable("Nr", lowBound=0, upBound=None, cat='Integer')
Nc = LpVariable("Nc", lowBound=0, upBound=None, cat='Integer')
Nal = LpVariable("Nal", lowBound=0, upBound=None, cat='Integer')
Nav = LpVariable("Nav", lowBound=0, upBound=None, cat='Integer')

# Minimize total diet cost
prob += Nr * 1 + Nc * 4 + Nal * 5 + Nav * 4

# 190 grams of protein
prob += Nr * 7 + Nc * 44 + Nal * 20 + Nav * 20 >= 190

# 55 grams of fat
prob += Nc * 8 + Nal * 52 + Nav * 15 >= 55

# 310 grams of carbs
prob += Nr * 78 + Nal * 20 + Nav * 9 >= 310

# At most 2600 calories
prob += Nr * 340 + Nc * 248 + Nal * 628 + Nav * 179 <= 2600

prob.solve()
for v in prob.variables():
    print(f'{v.name}={v.varValue}')
```

Let's run the script and get the solution

```
Result - Optimal solution found

Objective value:                28.00000000
Enumerated nodes:               0
Total iterations:               220
Time (CPU seconds):             0.01
Time (Wallclock seconds):       0.01

Option for printingOptions changed from normal to all
Total time (CPU seconds):       0.01   (Wallclock seconds):       0.01

Nal=0.0
Nav=4.0
Nc=2.0
Nr=4.0
```

As you can see, the program worked blazingly fast. Optimal solution was found in `0.01` seconds. The optimal cost is `30` and can be achieved by eating `4` avocados, `2` chicken breasts and `4` bags of rice, for the total of `2572` calories.

## Conclusion
Linear and Integer programming can be used to solve optimization problems. This article focused on practical aspects. I will describe the theory and algorithms in play in a different article.