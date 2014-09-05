#import sys
#sys.path.append('../pycoind')

# These are known correct values generated using vanitygen (https://github.com/samr7/vanitygen)
PubKeyA = '0454e6fd92033c4b268c68daafa9805c2722e8e51725e91129078f609fbf0d5f5c90a914b34603059795443cee94564df5569c95516a02eb4ed166d6d805681dba'.decode('hex')
PrivKeyA = 'FBDA14F04C744FE81979DCE6577DAE8BC85FCEBBFE8CDDAFA46291940FF87FA6'.decode('hex')
AddressA = '1NCzRaxNQKsxXHePcih9NkvzboSCvUu8Vd'
PrivKeyAWIF = '5KjCoLpx82UxshLYZzhaAjMsmjtvzXkWKz8Z5un9fR15V4urHw2'

AddressB = '1tEStoMLbigDH3BQzt4daGjCVVSn9RjJB'
PrivKeyBWIF = '5JGEPoC8GAhtAX6vFq29XnMCCWT5Dcunwb1a2gvqnWsdLmPPN6y'

PrivKeyOutput = '5JEQSE7xTJwdePUUt3epf9NFNQGGtLD8DqGDu8gfuh33vxqq7Av'


import pycoind

PrivKeyCWIF = pycoind.util.piecewise.combine_private_keys([PrivKeyAWIF, PrivKeyBWIF])

if PrivKeyOutput != PrivKeyCWIF:
    raise Exception('piecewise.combine_private_keys failed')

if AddressB != pycoind.util.piecewise.get_address(PubKeyA, PrivKeyBWIF):
    raise Exception('piecewise.get_address failed')



