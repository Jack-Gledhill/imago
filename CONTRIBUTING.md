# Contribution Guidelines

So, you're interested in helping this project succeed? If you are - then I love you - please make sure to join our [Discord server](https://invite.gg/mila).

## Coding Conventions

If you need an example, just check through the code, you'll get the idea. For simplicity, here is the majority of them:
* Indents are always with 4 spaces (not tabs)
* When passing arguments into methods, we always specify the keyword for it (if at all possible). The only exceptions are builtin methods that refuse any kwargs and functions that take non-sensical kwargs (e.g: x in int()).

:heavy_check_mark: This is correct.
```python
open(file="/path/to/file")
```
:x: This is not correct.
```python
int(x="123")
```

* When two kwargs are being passed to a method call, we put the two kwargs on their one line and inline with each other (if syntax allows), individual spaces may be used to achieve lining if necessary.

:heavy_check_mark: This is correct.
```python
app.run(host="127.0.0.1",
        port=1234)
```
:x: This is not correct.
```python
app.run(host="127.0.0.1", port=1234)
```
:x: This is not correct.
```python
app.run(host="127.0.0.1",
port=1234)
```

* Spaces **always** put spaces after list items (including Tuples, Lists, Sets and Dicts), method parameters and around operators. The exception to this is around the = operator when parsing kwargs.

:heavy_check_mark: This is correct.
```python
my_list = [1, 2, 3]
```
:x: This is not correct.
```python
my_list = [1,2,3]
```

* When we need to define a variable and run a condition (i.e: if statement) on it, we always use the Walrus operator in the condition.

:heavy_check_mark: This is correct.
```python
if (my_int := 5) > 3:
    print(my_int)
```
:x: This is not correct.
```python
my_int = 5

if my_int > 3:
    print(my_int)
```

* When defining methods, the require arguments must have typing annotations. If an argumet could be anything, pass Any as it's typing annotation. If the function returns None, do not add the returned value typing annotation.

:heavy_check_mark: This is correct.
```python
def return_x(x: int,
             y: Optional[int]=None,
             z: Any) -> Union[int, bool]:
    """Returns x."""

    pass
```
:x: This is not correct.
```python
def return_x(x,
             y,
             z) -> None:
    """Does smth."""

    pass
```

* We _always_ create a docstring for public methods. The one exception to this is the __init__ method for classes.

:heavy_check_mark: This is correct.
```python
def do_smth():
    """Does smth
    
    Very magical, right?"""

    pass
```
:x: This is not correct.
```python
def do_smth():
    pass
```

* A line should separate docstrings, nested statements, method definitions, separate statements (might want to look at the code for this one). But, the first line within a nested statement of any kind must come directly after the nesting statement's beginning.

:heavy_check_mark: This is correct.
```python
def some_function(x: int) -> int:
    """A cool docstring.
    
    Does stuff."""

    if x > 2:
        print(x)

        return 0

    while True:
        y = 1
        z = 2

        return x, y
```
:x: This is not correct.
```python
def some_function(x: int) -> int:
    """A cool docstring.
    
    Does stuff."""
    if x > 2:
        print(x)
        return 0
    while True:
        y = 1
        z = 2
        return x, y
```

* Comments should be placed directly above groups of code lines that do a particular thing. They should have a line of commented = signs above and below the comment. This also applies to comments that explain the code, rather than summarise it.

:heavy_check_mark: This is correct.
```python
# =======================
# Starts the Flask server
# =======================
try:
    pass

except RuntimeError:
    pass

# =====================================================
# this does lorem, it is ipsum and will never do dolor.
# we should use sit if amet
# =====================================================
pass
```
:x: This is not correct.
```python
# Starts the Flask server
try:
    pass

except RuntimeError:
    pass

# this does lorem, it is ipsum and will never do dolor.
# we should use sit if amet
pass
```

* We always use f-strings wherever possible, we **_NEVER_** - under any circumstances - use the %s syntax. If an f-string references the same root variable several times, the "{0.\*}".format() or "{var.\*}".format() may be used.

:heavy_check_mark: This is correct.
```python
# In order of preference, top is most preferred, bottom is least preferred
my_str_1 = f"{config.xyz} - {x}: {y} = {z}"

my_str_2 = "{0.xyz} - {0.x}: {0.y} = {0.z}".format(config)

my_str_3 = "{cf.xyz} - {cf.x}: {cf.y} = {cf.z}".format(cf=config)
```

* If possible, try to focus on using `from x import y` instead of `import y`. Never use `from x import *`, this is inefficient and unnecessary. Using the `import y` syntax is fine if loads of different parts of the module are referenced. Any packages that are depended on must be marked as so. Any locally imported materials will have their own comment. If multiple packages are being imported with `import y`, then they must be comma separated, not imported on their own line with their own import statement.

:heavy_check_mark: This is correct.
```python
# ===================
# Import dependencies
# ===================
import os, sys, builtins

from random import choice

# ==========================
# Import extension libraries
# ==========================
from util import prepare
```

:x: This is not correct.
```python
import os
import sys
import builtins
from random import *
from util import prepare
```