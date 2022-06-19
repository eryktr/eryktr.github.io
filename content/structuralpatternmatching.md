Title: Modern Python - Structural Pattern Matching
Date: 06-19-2022
Category: Python
Tags: python, modern-python
Slug: structuralpatternmatching
Author: eryktr
Summary: Bored of mundane if-else statements and sanity checks against your data format? The advent of Python 3.10 brought a tool allowing one to  solve such 
    problems elegantly, compactly and declaratively - Structural Pattern Matching.

# Introduction
[Structural Pattern Matching](https://peps.python.org/pep-0634/) is a relatively new feature, introduced with Python 3.10.
For those of you who programmed in languages like C or Java, the new feature resembles the **switch** statement,
yet it is more powerful and flexible.

The feature incorporates itself in the code by the following syntax:

```python
match expression:
    case condition_1:
        # do something
    case condition_2:
        # do something else
    ...
    case condition_N:
        # do something yet else
```

Let's take a look at a simple example.

## Commandline tool
Let's create a simple program which calculates the frequency of used characters in a piece of text.
For example, for the text
```
one, two, three
```
The output should be

```
e: 0.2317
o: 0.1548
,: 0.1548
t: 0.1548
n: 0.0779
w: 0.0779
h: 0.0779
r: 0.0779
```

The program can be started in two ways:

1. With free text
        
        freqcount [the text to analyze goes here]

1. With a file flag

        freqcount -f [path/to/file]

Here's the code:

```python
#!/usr/bin/env python3

from collections import Counter
import sys

FrequencyByChar = dict[str, float]


def freqcount(text: str) -> FrequencyByChar:
    # Here, a 'word' denotes a contiguous piece of text. For example: 'one,' (with the comma)
    # is treated as one word.
    text_without_whitespace = ''.join(text.lower().split())
    num_chars = len(text_without_whitespace)
    return {
        char: num_occurences / num_chars
        for char, num_occurences 
        in Counter(text_without_whitespace).items()
    }


def output_result(freqs: FrequencyByChar) -> None:
    """
    We need to sort the output by frequency before printing.
    A dictionary is an unorded data structure.
    """

    sorted_items = sorted(
        freqs.items(),
        # "Items" are tuples: (character, frequency)
        key=lambda item: item[1],
        reverse=True
    )
    for char, freq in sorted_items:
        print(f'{char}: {freq:.4}')


def report_frequency(text: str) -> None:
    freqs = freqcount(text)
    output_result(freqs)


def main() -> None:
    args = sys.argv[1:] # The first entry is always the name of the program
    match args:
        case ['-f', filename]:
            with open(filename) as f:
                text = f.read()
        case [*words]:
            text = ''.join(words)    
    report_frequency(text)

if __name__ == '__main__':
    main()
```

The interesting part happens in the **main** function.
Instead of running a series of "if" statements to determine the length of the input,
whether it starts with '-f' or to handle edge cases like 

    freqcount -f words to count here

In the example, the entire process of args-parsing is fully declarative and has no nested logic.
Also, notice that the input array got 'decomposed' - in the first case, the filename given by user got 
assigned to the 'filename' variable. In the second case - all entered words got stored inside the 'words'
array. Doing that with if-statements clearly requires more code.

# What can be matched?
As shown in the previous example, **match** is a powerful feature capabla to handle complex data types.
You can use structural pattern matching on many different data types. Let me enumerate a few.

## OR Patterns
You can use the pipe (|) operator to allow any of these two patterns. 
For example:
```python
match status_code:
    case 400 | 404:
        print('bad')
    case 200 | 201 | 202:
        print('ok')
    case 500:
        print('error')
```

You can also assign the result of the conditional matching to a variable. 
This will be presented in the next example.

## Wildcard Pattern
You can use a pattern that will match anything that hasn't been matched before
(by any previous pattern)

Example:

```python
cmd = input()
match cmd.split():
    case ['quit']:
        print('bye')
    # 'as' keyword causes the matched value to be stored in the 'direction' variable.
    case ['go', ('up' | 'down' | 'left' | 'right') as direction]:
        print(f'going {direction}')
    # _ is the wildcard pattern - it will match anything that hasn't been matched yet.
    case _:
        print("I don't understand.") 
```

## Classes
It is possible to match against classes. You can even match against certain attributes.

Let's define a bunch of classes (dataclasses would work as well):

```python
class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Circle:
    r: int

    def __init__(self, r: int) -> None:
        self.r = r
```


We can use those classes in `case` clauses. 
Notice that the matching expression doesn't have to be a proper instance of the class.
Cases like `Point(x=0)` denote **any Point instance having x=0**

```python
match shape:
    case Point(x=0, y=0):
        print('The origin')
    case Point(x=0):
        print('A point on the X axis')
    case Point(y=0):
        print('A point on the Y axis')
    case Circle(r=r):
        print(f'A circle with radius {r}')
    case _:
        print('Invalid data type.')
```

## Dictionaries
You can also use dictionaries in 'case' clauses.
**It will match ALL dictionaries that meet all requirements**

For example:

```python
case {'firstname': firstname}
```
will match all dictionaries having the key 'firstname'.

```python
case {'firstname': 'Chris', 'age': age}
```
will match all dictionaries having the key 'firstname' assigned with the value of *Chris* AND 
having the key *age*.


In below example, 'person' can either be a list of two elements or a dictionary with keys: *firstname* and *lastname*.
```python
match person:
    case [firstname, lastname]:
        ...
    case {'firstname': firstname, 'lastname': lastname}:
        ...
```

## Built-in types
Finally, it is possible to add additional constraints on the primitive type of the matched data.
For example, let's assume that our program parses a list of arguments to form a command. One possible command is:

    sleep [number of seconds]

To automatically handle cases where *number of seconds* is a string instead of an integer, we can handle it as follows:

```python
match command:
    case ['sleep', int(t)]:
        time.sleep(t)
    case ['sleep', str(t)]:
        time.sleep(int(t))
```

This syntax might be difficult to understand at first. But let's break it down.
The expression

```python
case ['sleep', int(t)]
```

simply matches two-element lists, whose first element it the string literal `'sleep'` and the second element
is an integer. In addition, the integer gets assigned to the variable `t`.

# Plausible applications
# Examples
# Summary