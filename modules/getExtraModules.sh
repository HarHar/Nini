#!/usr/bin/sh
git clone git://github.com/HarHar/NiNiModules.git
mv NiNiModules/*.py .
rm -f -R NiNiModules
echo "Note: Addition dependcies will probably need to be installed through pip to load all modules"
