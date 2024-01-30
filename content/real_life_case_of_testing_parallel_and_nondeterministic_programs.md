Title: Testing parallel, non-deterministic code
Date: 01-24-2024
Category: Python
Tags: python, pytest, testing, software-engineering, programming, unit-tests
Slug: real_life_case_of_testing_parallel_and_nondeterministic_programs
Author: eryktr
Summary: Hands-on practice on testing multiple processes. Also, a refresher on Calculus :)

# Introduction
This is the next article from my testing series. The previous one introduced [monkeypatching]({filename}/monkeypatching.md) as
a way to abstract away some complexity. This article will also use monkeypatching, to solve a more complex problem.
Most developers are familiar with testing synchronous code. Techniques such as mocking and stubbing, as well as the 'pure-fabrication' principle (more on that coming later) make up a pretty robust framework for covering regular code. However, sometimes we have to deal with highly concurrent programs which are also non-deterministic. In this article, I will analyze and cover one such scenario.

# Problem statement
Consider the problem of finding the definite integral of the function `f` on the closed integral `[a, b]`. Then, denote the value as S.

$$
S = \int_{a}^{b} f(x) \, dx
$$

We want to implement a function which evaluates the integral.


# Math recap
The definite integral of a function can be visualized as the area under the function's curve.
Therefore, to get a numerical estimation, we only need to calculate the area below the curve and above the X axis.

# Solution
We can implement the function using a **Monte Carlo** simulation. This is a simplified overview of the algorithm

1. Enclose the function's graph in the area to be integrated in a rectangle.
2. Specify the number of tests.
3. In each test, we 'throw' a point in the rectangle.
4. If the point lands below the curve, we increment the `hit` counter.
5. Finally, we get the integral as `num_hit / num_tests * rect_area`


From programming perspective, we want to implement such function
```python
def mc_integrate(f, a, b, y_min, y_max):
    """
    Calculates the definite integral of the function 'f' on
    interval [a, b] using a MonteCarlo simulation
    with y = y_min being the lower and y = y_max the upper
    bound of the rectangle.
    """
    ...
```

Which can then be called like this

```python
i = integrate(math.sin, 0, math.pi/2, -1, 1)
```

In this case, `i` would be a numerical approximation of the integral - a value close to `2`.

# Synchronous implementation
Let's implement the function in a naive way, step by step

```python
import random
def mc_integrate(f, a, b, y_min, y_max):
    num_tests = 100_000
    rect_area = (b-a) * (y_max - y_min)
    points = ((random.uniform(a, b), random.uniform(y_min, y_max)) for _ in range(num_tests))
    num_under_curve = sum(y <= f(x) for x, y in points)
    return num_under_curve / num_tests * rect_area
```

Now, we have to come up with a reasonable value for `num_tests`.
I have considered several possible values and benchmarked them.
Data in the below table comes from the average of `100` runs.

| num_tests   | average performance (ms)   | average error  |
|-------------|----------------------------|----------------|
| $10,000$    | $20$                       | $2\%$          |
| $100,000$   | $60$                       | $1\%$          |
| $1,000,000$ | $500$                      | $0.1\%$        |
| $10,000,000$| $5,000$                    | $0.01\%$       |
| $50,000,000$| $30,000$                   | $0.001\%$      | 

As you can see, the value of `50,000,000` tests yields accurate results, however, execution time is significant.
We can fix that.

# Parallellism kicks in
Let's use all CPU cores that our machine has. We can get this number by calling
```
>> import multiprocessing
>> multiprocessing.cpu_count()
24
```

So, we have this code

```python
import random
import multiprocessing

def mc_integrate(f, a, b, y_min, y_max):
    num_tests = 50_000_000
    num_cpus = multiprocessing.cpu_count()
    tests_per_process = num_tests // num_cpus
    rect_area = (b-a) * (y_max - y_min)
    
    with multiprocessing.Pool(num_cpus) as pool:
        num_under_curve_per_thread = pool.starmap(
            perform_tests,
            [(tests_per_process, f, a, b, y_min, y_max)] * num_cpus
        )
    
    total_num_under_curve = sum(num_under_curve_per_thread)
    return total_num_under_curve / num_tests * rect_area

def perform_tests(num_tests, f, a, b, y_min, y_max):
    points = ((random.uniform(a, b), random.uniform(y_min, y_max)) for _ in range(num_tests))
    num_under_curve = sum(y <= f(x) for x, y in points)
    return num_under_curve
```

And now, the code executes - on average - in 100 milliseconds.

# Testing
Now, we might want to cover the code with unit tests. We encounter two problems
that make it harder

1. The code is not deterministic - several runs of the same function with the same
parameters yield different results.
2. The code spawns new processes and executes some code in them.

Let's cover the problems one by one

## Non-determinism
Since the Monte Carlo simulation only approximates the integral, we cannot be sure of the value it will return,
so we cannot just easily come up with some constant `C` to satisfy assertion like

```python
assert mc_integrate(f, a, b, y_min, y_max) == C
```

Why?

The function uses randomly generated points for the simuation. For example, let's try calculating

$$
S = \int_{0}^{1} x^2 \, dx
$$

The exact answer is 

$$
S = \frac{1}{3}
$$

```python
def f(x):
    return x*x

S1 = mc_integrate(f, 0, 1, 0, 1)
S2 = mc_integrate(f, 0, 1, 0, 1)
```

```
S1 = 0.33325338
S2 = 0.33324428
```

However, we can validate the correctness of the calculation by always forcing the random generator to return the same series of numbers - this is called `seeding`.

Let's have a look at this piece of code:
```
import random
random.seed(42)
print([random.randint(0, 100) for _ in range(10)])
```

And let's run it twice

```
[81, 14, 3, 94, 35, 31, 28, 17, 94, 13]
[81, 14, 3, 94, 35, 31, 28, 17, 94, 13]
```
As you can see, the seed forced the generator to return the same sequence of random numbers.
Let's try doing the same with the Monte Carlo simulation

```
import random
random.seed(42)
S1 = mc_integrate(f, 0, 1, 0, 1)
S2 = mc_integrate(f, 0, 1, 0, 1)
```

And let's check
```
S1 = 0.33346894
S2 = 0.33283536
```

It did not work. Why?

Because the code is **parallel**. We are generating the same sequence of numbers, but we might never be sure at which point certain number is generated - and on which process. The random generator just yields a sequence of numbers. Let's say we only want to generate four numbers. With our seed, they are as follows: `1, 2, 3, 4`. We want to create two points from these numbers. We might get `(1,2)` and `(3,4)` as well as `(1,4)` and `(2, 3)`. Sequence is the same, but the place at which they land - different. We need to inject a separate seed for each process.

## Solution
Let's say we are running our simulation on $N$ processes. Then, we need a deterministic set of $N$ seeds.
Of course, we could use one seed and set it for all subprocesses, but then all processes would perform the same calculations - we would be compromising on the testing of the way they cooperate towards the final solution.

Let me share the updated code:

```python
import random
import os
import multiprocessing

def _get_seed(i, start_seed):
    if start_seed is None:
        return os.urandom(16)
    return start_seed + i
    
def mc_integrate(f, a, b, y_min, y_max, start_seed=None):
    num_tests = 50_000_000
    num_cpus = multiprocessing.cpu_count()
    tests_per_process = num_tests // num_cpus
    rect_area = (b-a) * (y_max - y_min)
    
    with multiprocessing.Pool(num_cpus) as pool:
        params = [
            (tests_per_process, f, a, b, y_min, y_max, _get_seed(i, start_seed))
            for i in range(num_cpus)
        ]
        num_under_curve_per_thread = pool.starmap(perform_tests, params)
    
    total_num_under_curve = sum(num_under_curve_per_thread)
    return total_num_under_curve / num_tests * rect_area

def perform_tests(num_tests, f, a, b, y_min, y_max, seed):
    random.seed(seed)
    points = ((random.uniform(a, b), random.uniform(y_min, y_max)) for _ in range(num_tests))
    num_under_curve = sum(y <= f(x) for x, y in points)
    return num_under_curve
```

Now, specifying no `start_seed` will cause the function to behave as previously. However, once we specify the `start_seed`, we will be getting deterministic results.

```
0.33339372
0.33339372
```

## Parallellism
Old school developers would argue that unit tests should not spawn subprocesses because they are hard to debug
and can cause events like deadlocks that can carry over into subsequent tests, causing failure of unrelated parts
of the test suite.
Common approaches include:

1. Mocking out the `threading` module and only verifying that correct functions were called
2. Substituting the concurrent implementation with a synchronous one for testing

Both of these allow us to attain necessary code coverage, however, neither of them tests the actual cooperation between processes.

I can suggest a different approach - let's just run the concurrent code in the unit tests, it doesn't really cause
too much harm, as long as we understnad the problems. Let's consider the problems

## Deadlocks
Parallel code can block out completely if two processes or threads are waiting on each other. However, we do not have this problem in our case as the processes are completely independent

## Resource usage
Processes are heavy both on memory and CPU. We need to understand that the machine on which the unit tests are executed (the CI/CD runner, most likely) is usually way less powerful than your working station. We might cause problems like out of memory error or CPU throttling by spawning too many processes

## Performance issues
As described before, the test runner is probably significantly less capable in terms of computational power than our working machine. In our case, $50,000,000$ monte carlo tests might be good enough for the production deployment on a machine with many CPUs, but it might be too heavy for the test runner

## Solution
Let's rework the original code to get the value of `num_tests` and `num_cpus` from a function call.

```python
def _get_seed(i, start_seed):
    if start_seed is None:
        return os.urandom(16)
    return start_seed + i
    
def _get_num_cpus():
    return multiprocessing.cpu_count()

def _get_num_tests():
    return 50_000_000

def mc_integrate(f, a, b, y_min, y_max, start_seed=None):
    num_tests = _get_num_tests()
    num_cpus = _get_num_cpus()
    tests_per_process = num_tests // num_cpus
    rect_area = (b-a) * (y_max - y_min)
    
    with multiprocessing.Pool(num_cpus) as pool:
        params = [
            (tests_per_process, f, a, b, y_min, y_max, _get_seed(i, start_seed))
            for i in range(num_cpus)
        ]
        num_under_curve_per_thread = pool.starmap(perform_tests, params)
    
    total_num_under_curve = sum(num_under_curve_per_thread)
    return total_num_under_curve / num_tests * rect_area

def perform_tests(num_tests, f, a, b, y_min, y_max, seed):
    random.seed(seed)
    points = ((random.uniform(a, b), random.uniform(y_min, y_max)) for _ in range(num_tests))
    num_under_curve = sum(y <= f(x) for x, y in points)
    return num_under_curve
```

Now, given that our code is already deterministic, we can run a minimal test that actually tests the complete Monte Carlo
simulation with minimal performance overhead

```python
from montecarlo import mc_integrate

def f(x):
    return x*x

def stub_get_num_cpus():
    return 2

def stub_get_num_tests():
    return 10_000

def test_mc_integrate(mocker):
    mocker.patch('montecarlo._get_num_cpus', stub_get_num_cpus)
    mocker.patch('montecarlo._get_num_tests', stub_get_num_tests)
    mc_integrate(f, 0, 1, 0, 1, start_seed=10) == 0.3297

```

That's it. Now, the test is blazingly fast, efficient in terms of memory usage and deterministic - it will pass all the time,
as long as the algorithm remains in tact.

# Summary
Testing of concurrent and non deterministic code is often complex and requires creativity. 
However, taking time and coming up with a good solution will benefit you in the long run.
Having clear and deterministic tests enable you to put higher confidence in your code and serve as a good documentation.
Not mocking out multithreading completely ensures that your code is tested end to end.