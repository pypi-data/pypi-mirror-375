from padocc.core.utils import BypassSwitch
from padocc.phases import KerchunkDS, ScanOperation

WORKDIR = '/home/users/dwest77/cedadev/padocc/padocc/tests/auto_testdata_dir'


sco = ScanOperation('1DAgg', workdir=WORKDIR, groupID = 'padocc-test-suite', verbose=1)
sco.run(forceful=True)

com = KerchunkDS('1DAgg', workdir=WORKDIR, groupID = 'padocc-test-suite', verbose=1)
com.run(forceful=True)