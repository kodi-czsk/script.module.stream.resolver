#/bin/sh
# do NOT use this script from Kodi addons directory, it is intented for development only
DESTDIR=~/.kodi/addons/script.module.stream.resolver

rm -rf ${DESTDIR}
mkdir -p ${DESTDIR}
cp -a * ${DESTDIR}
