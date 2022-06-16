Title: Deterministic tests - introduction to monkeypatching
Date: 06-16-2022
Category: Python
Tags: python, pytest, testing, software-engineering, programming, unit-tests
Slug: monkeypatching
Author: eryktr
Summary: Some parts of your code are hard to test - API calls, randomized or long-running calculations
    cannot be tested effectively. Luckily, there are a bunch of tools to help us bypass such limitations.
    This article describes one of them - **monkeypatching**.

# Introduction
It's important to keep your code properly covered with unit tests. However, when working on a complex system,
certain parts of it are harder to cover on unit level.

Examples of such relucant cases include:

- API calls (Unit tests shouldn't send any requests - they need to be runnable without any external dependencies)
- Non deterministic functions (e.g. *random*, *datetime*)
- Long running calculations (Unit tests should run as quickly as possible)
- Operations on the file system (Reading from / writing to a file / stderr)
- Network operations (Reading to / writing from a socket)
- Interacting with the user (Logging, reading input)

If some part of your system depends on any of the above mentioned actions - which is highly probable - you can still
achieve full coverage. You just need to sport a trifle bit extra creativity when writing your test and make sure your toolbox 
is complete.

There are a bunch of tools to help covering such scenarios. Probably the most common one is **monkeypatching**.

# Monkeypatching - meaning?
Let's start with a simple definition from [Wikipedia](https://en.wikipedia.org/wiki/Monkey_patch)

> A monkey patch is a way for a program to extend or modify supporting system software locally (affecting only the running instance of the program).

In other words, when we *monkeypatch* an object (a module, a function, a class), we replace it with a different one 
**in runtime**.

Let's see a few possible applications that would enable unit testing:

- A function calling an external API could be replaced with a function sending no requests,
just returning a value of the same structure as would have been returned by the original function.
- A long running function could be replaced with one that returns a hardcoded value immediately.
- Sockets and other file-like objects could be replaced with an in-memory equivalents, storing information
about all performed reads and writes

# Monkeypatching vs mocking
Having read the examples, a different word might spring to your mind: **mocking**.
Monkeypatching and mocking are tightly related, yet they aren't the same thing. 

- A mock is a **simulated object** that mimics the behavior of the original object in a **controlled way**. 
It can replace its attributes, cause certain side effects (e.g. raise an exception) or keep track of the object's calls
(e.g. how many times was the function called? With what arguments?)
- Monkeypatching is **replacing** one object with a different one in runtime
- Mocking is **monkeypatching** an object with a **mock**.

As you see, these definitions work together, not against each other.
Therefore, the question *Which is better - mocking or monkeypatching?*
is like asking *Which is better - the car or the engine?*.

# Example: An orc slayer
Imagine a video game you have implemented. All characters have the following statistics:

- HP (health points)
- Strength Points
- Armor points

In addition, they yield a weapon.
Each weapon has a range of damage it can deal.

```python
from dataclasses import dataclass

@dataclass
class Weapon:
    min_dmg: int
    max_dmg: int


@dataclass
class Character:
    hp: int
    armor: int
    strength: int
    weapon: Weapon
```

Now, let's make a few assumptions how our system works:

- The more strength a character has, the harder it hits (deals more damage)
- The better the weapon (damage range), the harder it hits.
- The more armor a character has, the less damage it takes.

So, the algorithm to calculate the amount of damage dealt by Attacker to Target runs as follows:

```python
def calculate_attack_strength(attacker: Character) -> int:
    """
    Returns the amount of damage that would be dealt
    if target had no armor.

    Algorithm:
        Return the sum of character's strength and a random value 
        from the range (minimal_weapon_dmg, maximal_weapon_dmg)
    """
    min_dmg = attacker.weapon.min_dmg
    max_dmg = attacker.weapon.max_dmg
    return attacker.strength + random.randint(min_dmg, max_dmg)


def reduce_dmg(attack_strength: int, target: Character) -> int:
    """
    Returns the net amount of damage
    (the value by which target's HP will be decreased)
    """
    # At least one damage point will always be dealt
    if (armor := target.armor) > attack_strength:
        return 1
    return attack_strength - armor

def attack(attacker: Character, target: Character) -> None:
    attack_strength = calculate_attack_strength(attacker)
    reduced_dmg = reduce_dmg(attack_strength, target)
    target.hp -= reduced_dmg
```

Now, take a look at line *12* - A random number from the range (minimum weapon damage, maximum weapon damage) is drawn to 
increase the attack strength. What does it mean?
**The function *attack* is not deterministic!**

To prove that, let's run this snippet of code a few times and log the output.

```python
rusty_sword = Weapon(min_dmg=20, max_dmg=50)
large_axe = Weapon(min_dmg=40, max_dmg=60)
knight = Character(hp=100, armor=50, strength=20, weapon=rusty_sword)
orc = Character(hp=100, armor=10, strength=30, weapon=rusty_sword)

attack(knight, orc)
print(orc.hp)
```

My results:

```
50
64
52
65
60
66
```

How do we test this function?

There are a few solutions that might come to your mind at first:

- **Let's assert that the target's HP has decreased** - The test would pass but you are only verifying that *some* damage is applied.
You are not testing the actual calculation.
- **Let's only test weapons with minimum_damage equal to maximum_damage** - The test would work, but that's only an edge case - you need to test that anyway.

## Solution
We will monkeypatch the `random.randint(a, b)` function to always return the mean average of its arguments.

I will use the [**monkeypatch**](https://docs.pytest.org/en/6.2.x/monkeypatch.html) fixture, from pytest's standard library.
```python
def test_attack(monkeypatch):
    """
    Verifies that damage is correctly propagated
    to target.
    """
    def fake_randint(a, b):
        return (a + b) // 2

    monkeypatch.setattr(random, 'randint', fake_randint)
    attacker = Character(
        hp=100,
        armor=100,
        strength=50,
        weapon=Weapon(min_dmg=10, max_dmg=100)
    )
    target = Character(
        hp=100,
        armor=50,
        strength=100,
        weapon=Weapon(min_dmg=10, max_dmg=100)
    )
    
    attack(attacker, target)

    assert target.hp == 45
```

Since we know that our patched **random.randint(10, 100)** will always return **(10 + 100) // 2 = 55**, we are able
to calculate expected target't HP - it should be **45**. 
The test is green.

# Summary
Monkeymatching stands for 'replacing an object with a different one at runtime'.
It's commonly confused with mocking, but these two concepts are supplementary.
Monkeypatching allows you to test otherwise non-unit-testable parts of your code.
Can you think of any advantages of monkeypatching with traditional functions (as we did in this article)
over mocking?