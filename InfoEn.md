# Introduction #

# Details #

Hi there.

This is a pre-release of a Python-to-C translator.

It compiles Python 2.6 code to C code, thus allowing to translate a single Python module to a binary .dll or .so file .

Handles all the the language constructs, although there are some incompatibilities:

  * Python standard profiling and debugging tools won't work for compiled modules -- use the C code instruments instead ;
  * the `type()` for the compiled functions and the code objects won't be the same as for the interpreted functions and code objects with same attributes and methods ;
  * The `.copy()` method for a compiled function is not supported; this means neither `deepcopy` nor `pickle`-ing do not work for binary functions ;
  * `threading` is not supported ( it is just not implemented yet ) ;
  * Certainly there are some bugs.

Usage:
```

```
	python 2c.py [options] filename.py
```
```


After a successful compilation there would be a `_c_filename.dll` or `_c_filename.so` file in the `site-packages` directory. ( We use the `_c_` prefix because of the fact that if both the binary file and the .py file have the same base name (without extension), then the .py file will be used. ) So to import the compiled modules one has to use the form
```

```
import _c_filename as filename
```
```


That's an arguable solution, and the ones who do not fancy it should look into the definition of the `compile_c` function (there are no comments, sorry for that). I understand that the import system is incomplete ( so that in the case if the binary file is newer than the python file the binary file should be imported ), but there is a number of other things to do, and the import thing would take too much time.

There are no warnings. Also, if at compile time we discover that some Python code produces an error -- we just make code that dynamically issues that error.

There are no detailed messages about syntactic errors. To understand what's wrong, run it from Python.
In fact, this is just an additional binary code generator for CPython.


Using the generated binary code gives a speed boost from 2 to 4.5 times ☺.
If you want to get speed -- don't forget the -O3 option ( -O0 -- -O1 -- -O2 -- -O options are available as well ). These options are passed directly to the C compiler ( I have tried GCC only, so the ones who feel adventurous might try this with Python built with some other compiler )