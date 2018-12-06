# Picofamily flexx with OpenNI2 + libroyale-3.20.0

### Feasibility Study Conditions

- [pmdtec picofamily flexx](https://pmdtec.com/picofamily/flexx/)
- RaspberryPi-3 Model B+
- Raspbian stretch
- ubuntu package libopenni2-0
- ubuntu package libopenni2-dev 
- [PyPI package primesense](https://pypi.org/project/primesense/#description)
- From flexx royale SDK libroyaleONI2.so (Sh!2BCpf) 

### Test via OpenNI2-utils package

```
# apt install openni2-utils
$ NiViewer2 --help
-devices
-depth=<on|off|try>
-color=<on|off|try>
-ir=<on|off|try>
$ NiViewer2 -depth=on
```
