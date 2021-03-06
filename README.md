# modelz

To Install:

1. First, <a href="https://www.cgl.ucsf.edu/chimera/download.html">download</a> and install UCSF Chimera. 
* Run it once before installing the plugin; on some platforms, e.g. MacOS, you may see a warning message on first run which you have to accept. This may prevent further issues after adding the plugin.
* On Windows, install to your home folder rather than to "Program Files". In the latter, the OS may not allow further modifications at a user level, i.e. adding this plugin.
2. <a href="https://github.com/gregdp/modelz/tree/master/download">Download</a> latest version of ModelZ.
3. In a terminal, navigate to where the file was downloaded, then execute the following commands:
* unzip modelz_chimera_1_2.zip
* cd modelz_chimera_1_2
* python install.py [path to Chimera]

e.g.:
* python install.py ~/Desktop/Chimera.app/


Note that on Windows, you may use the python bundled with Chimera itself, so the third command would be
* [path to Chimera]\bin\python install.py [path to Chimera]

To Run:
1. (Re)start Chimera
* On Mac OS, an error message may be shown on first run after installing, see [here](https://www.santoshsrinivas.com/disable-gatekeeper-in-macos-sierra/) for solution.
2. Start ModelZ: Tools -> Volume Data -> ModelZ
3. See [more details and tutorials](https://cryoem.slac.stanford.edu/ncmi/resources/software/modelz)

