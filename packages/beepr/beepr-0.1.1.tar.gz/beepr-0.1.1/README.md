# beepr
simple, cli tool to make beeps in intervals

use it for your pomodoro, gym sessions or whatever - not my business really 😅

<b>Zero deps!</b>

[![PyPI version](https://img.shields.io/pypi/v/beepr.svg)](https://pypi.org/project/beepr/)

## installation

the easiest way is to install from pypi

```bash
pip install beepr
```

to install clone this repo and use pip
```bash
git clone https://github.com/nazariinyzhnyk/beepr.git
cd beepr
pip install .
```

## usage

to use it for a single beep just run
```bash
beepr
```

Actual usecase work for 5 seconds, pause for 3 seconds and repeat it 2 times:
```bash
beepr 5 3 2 'work time' 'pause time'
```

or with default values
```bash
beepr 5 3 2
```

Output will be:
```
CMD >>> beepr 5 3 2

beepr is running with the following parameters:
Action: 5
Pause: 3
Repeat: 2
Action Message: 💻 Work
Pause Message: 🌴 Pause

session started!
 💻 Work for 5s. 1 of 2.
 🌴 Pause. Rest for 3s.
++++++++++ Rest is over! ++++++++++



 💻 Work for 5s. 2 of 2.
 🌴 Pause. Rest for 3s.
++++++++++ Rest is over! ++++++++++



 session is over!
```


## instead of farewell

the main reason I build this tool it to have free, ad-free, simple tool to track time intervals. this tool was designed and developed just as I needed it to be. simple DIY to suit my needs.

have fun using it 🤗
