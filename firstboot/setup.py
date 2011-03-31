#!/usr/bin/python2

from distutils.core import setup
from glob import *

setup(name='firstboot', version='1.110',
      description='Post-installation configuration utility',
      author='Chris Lumens', author_email='clumens@redhat.com',
      url='http://fedoraproject.org/wiki/FirstBoot',
      data_files=[('/usr/sbin', ['progs/firstboot']),
                  ('/etc/rc.d/init.d', ['init/firstboot']),
                  ('/usr/share/firstboot/themes/default', glob('themes/default/*.png')),
                  ('/usr/share/firstboot/modules', glob('modules/*.py')),
                 ],
      packages=['firstboot'])
