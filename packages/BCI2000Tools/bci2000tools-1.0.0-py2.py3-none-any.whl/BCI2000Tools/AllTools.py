__all__ = [
	'ForgetBCI2000Tools',
]
import os
import sys
import glob

thisSubmoduleName = os.path.splitext( os.path.basename( __file__ ) )[ 0 ]
parentDir = os.path.realpath( os.path.dirname( __file__ ) )
parentModuleName = os.path.basename( parentDir )
submodulePaths = sorted( glob.glob( os.path.join( parentDir, '*.py' ) ) )
iskosher = lambda x: x.replace( '/', '' ).replace( '\\', '' ).replace( '_', '' ).replace( '.', '' ).isalnum()
submodulePaths = [ submodulePath for submodulePath in submodulePaths if iskosher( submodulePath[ len( parentDir ): ] ) ]
sub = None
allItems = {}
provenance = {}
print( '# The path to %s is %s' % ( parentModuleName, parentDir.replace( '\\', '/' ) ) )
from . import Bootstrapping; from .Bootstrapping import bci2000path, bci2000_exe_extension
for submodulePath in submodulePaths:
	submoduleName = os.path.splitext( os.path.basename( submodulePath ) )[ 0 ] # NB: this assumes no sub-sub-modules (flat structure inside BCI2000Tools directory)
	if submoduleName in ( '__init__', '__main__', thisSubmoduleName ): continue
	msg = 'from %s.%s import *' % ( parentModuleName, submoduleName )
	canaries = []
	if submoduleName in [ 'Remote' ]:
		canaries.append( 'prog/BCI2000Remote.py' )
	if submoduleName in [ 'Chain'  ]:
		exeExtension = bci2000_exe_extension('tools/cmdline')
		canaries.append( 'tools/cmdline/bci_dat2stream' + exeExtension )
		canaries.append( 'tools/cmdline/bci_stream2hybrid' + exeExtension )
	deadCanaries = [ canary for canary in canaries if not os.path.exists( bci2000path( canary ) ) ]
	if deadCanaries:
		print( '#%s    # skipped (no %s)' % ( msg, deadCanaries[ 0 ] ) )
		continue
	print( msg )
	exec( 'import %s.%s as sub' % ( parentModuleName, submoduleName ) )
	for name in sub.__all__:
		item = getattr( sub, name )
		if item is not allItems.get( name, item ): print( '# WARNING: %s from %s.%s overwrites %s from %s.%s' % ( name, parentModuleName, submoduleName, name, parentModuleName, provenance[ name ] ) )
		allItems[ name ] = item
		provenance[ name ] = submoduleName

__all__ += allItems.keys()
locals().update( allItems )

def ForgetBCI2000Tools():
	for k in list( sys.modules ):
		if k.startswith( parentModuleName + '.' ): del sys.modules[ k ]

