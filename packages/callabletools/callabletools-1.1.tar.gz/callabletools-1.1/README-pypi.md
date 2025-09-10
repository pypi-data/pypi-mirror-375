<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]







<!-- About -->
<div align="center">

<h3 align="center">Python Callabletools</h3>

<p align="center">

Advanced tools for callable objects in Python.

[Changelog][changelog-url] · [Report Bug][issues-url] · [Request Feature][issues-url]
 
</p>

</div>



<!-- ABOUT THE PROJECT -->

##  About The Project

Provides advanced tools for callable objects in Python 3.x.


###  Built With

* [![python-shield][python-shield]][pypi-project-url]

<br>


<!-- GETTING STARTED -->

##  Getting Started

To get a local copy up and running follow these simple example steps.

###  Prerequisites

Does not require any prerequisites.

###  Installation

1. Clone the repo
```sh
git clone https://github.com/TahsinCr/python-callabletools.git
```

2. Install PIP packages
```sh
pip install callabletools
```


<br>



<!-- USAGE EXAMPLES -->

##  Usage

Let's try to retrieve a callable object's arguments, argument count, return result, and the arguments with their given values.
```python
from callabletools import (
    get_arguments, get_argument_length, get_return_argument, get_argument_values
)

def item_to_string(key1:str, key2, start:str='-', *keys, sep:str=', ', **items:int) -> str:
    items = [f'{k}:{v}' for k, v in items]
    return start + sep.join([key1, key2, *keys, items])

func_args = ['test1', 'test2', '--', 'test3']
func_kwargs = {
    'ex' : 'test4'
}

arguments = get_arguments(item_to_string)
print("FuncArgs:", *arguments, sep='\n', end='\n\n')

print("FuncArgLength: {}".format(get_argument_length(item_to_string)), end='\n\n')

print("FuncReturnArg: \n{}".format(get_return_argument(item_to_string)), end='\n\n')

print(
    "FuncArgValues:", 
    *get_argument_values(arguments, func_args, func_kwargs), 
    sep='\n', end='\n\n'
)

```
Output
```
FuncArgs:
Argument(name: key1, type: <class 'str'>, default: Ellipsis, argtype: ARG)
Argument(name: key2, type: typing.Any, default: Ellipsis, argtype: ARG)
Argument(name: start, type: <class 'str'>, default: Ellipsis, argtype: ARG)
Argument(name: keys, type: typing.Any, default: Ellipsis, argtype: ARGS)
Argument(name: sep, type: <class 'str'>, default: ', ', argtype: ARG)
Argument(name: items, type: <class 'int'>, default: Ellipsis, argtype: KWARGS)

FuncArgLength: 6

FuncReturnArg: 
Argument(name: return, type: <class 'str'>, default: Ellipsis, argtype: RETURN)

FuncArgValues:
ArgumentValue(name: key1, type: <class 'str'>, default: Ellipsis, argtype: ARG, value: 'test1')
ArgumentValue(name: key2, type: typing.Any, default: Ellipsis, argtype: ARG, value: 'test2')
ArgumentValue(name: start, type: <class 'str'>, default: Ellipsis, argtype: ARG, value: '--')
ArgumentValue(name: keys, type: typing.Any, default: Ellipsis, argtype: ARGS, value: ['test3'])
ArgumentValue(name: sep, type: <class 'str'>, default: ', ', argtype: ARG, value: ', ')
ArgumentValue(name: items, type: <class 'int'>, default: Ellipsis, argtype: KWARGS, value: {'ex': 'test4'})
```

_For more examples, please refer to the [Documentation][wiki-url]_

<br>





<!-- LICENSE -->

##  License

Distributed under the MIT License. See [LICENSE][license-url] for more information.


<br>





<!-- CONTACT -->

##  Contact

Tahsin Çirkin - [@TahsinCrs][x-url] - TahsinCr@outlook.com

Project: [TahsinCr/python-callabletools][project-url]







<!-- IMAGES URL -->

[python-shield]: https://img.shields.io/pypi/pyversions/callabletools?style=flat-square

[contributors-shield]: https://img.shields.io/github/contributors/TahsinCr/python-callabletools.svg?style=for-the-badge

[forks-shield]: https://img.shields.io/github/forks/TahsinCr/python-callabletools.svg?style=for-the-badge

[stars-shield]: https://img.shields.io/github/stars/TahsinCr/python-callabletools.svg?style=for-the-badge

[issues-shield]: https://img.shields.io/github/issues/TahsinCr/python-callabletools.svg?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/TahsinCr/python-callabletools.svg?style=for-the-badge

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555



<!-- Github Project URL -->

[project-url]: https://github.com/TahsinCr/python-callabletools

[pypi-project-url]: https://pypi.org/project/callabletools

[contributors-url]: https://github.com/TahsinCr/python-callabletools/graphs/contributors

[stars-url]: https://github.com/TahsinCr/python-callabletools/stargazers

[forks-url]: https://github.com/TahsinCr/python-callabletools/network/members

[issues-url]: https://github.com/TahsinCr/python-callabletools/issues

[wiki-url]: https://github.com/TahsinCr/python-callabletools/wiki

[license-url]: https://github.com/TahsinCr/python-callabletools/blob/master/LICENSE

[changelog-url]:https://github.com/TahsinCr/python-callabletools/blob/master/CHANGELOG.md



<!-- Contacts URL -->

[linkedin-url]: https://linkedin.com/in/TahsinCr

[x-url]: https://twitter.com/TahsinCrs
