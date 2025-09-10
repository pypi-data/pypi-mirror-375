# beepr
simple, cli tool to make beeps in intervals

to install clone this repo and use pip
```bash
git clone https://github.com/nazariinyzhnyk/beepr.git
cd beepr
pip install .
```

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
