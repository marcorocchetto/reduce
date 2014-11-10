# FrameTypes 
lightTypes = [ "LIGHT", "LIGHT FRAME" ]
biasTypes = [ "BIAS", "BIAS FRAME" ]
darkTypes = [ "DARK", "DARK FRAME" ]
flatTypes = [ "FLAT", "FLAT FIELD", "FLAT FRAME" ]    

# Telescopes
class telescope: 
    name = ''
    fullname = ''    
    aperture = 0
    rdnoise= 0        # readout noise
    egain =  0        # electron gain
    aperture = 0
    # approximate matrix for plate solution
    pmat = {}
    pmat['CD1_1'] = '' 
    pmat['CD1_2'] = ''
    pmat['CD2_1'] = ''
    pmat['CD2_2'] = ''
    
telescopes = {}

#here you can add new telescopes
telescopes['lp50'] = telescope()
telescopes['lp50'].name = 'lp50'
telescopes['lp50'].fullname = 'lp50'
telescopes['lp50'].rdnoise = 14.0
telescopes['lp50'].egain = 1.22
telescopes['lp50'].aperture = 50.0
telescopes['lp50'].pmat['CD1_1'] = ' 2.37780000000E-004'
telescopes['lp50'].pmat['CD1_2'] = ' 6.73650000000E-006' 
telescopes['lp50'].pmat['CD2_1'] = '-6.73040000000E-006'
telescopes['lp50'].pmat['CD2_2'] =  '2.37999000000E-004'

telescopes['kuiper61'] = telescope()
telescopes['kuiper61'].name = 'kuiper61'
telescopes['kuiper61'].fullname = 'Kuiper 61inch'
telescopes['kuiper61'].rdnoise = 5.0
telescopes['kuiper61'].egain = 3.1
telescopes['kuiper61'].aperture = 154.0
telescopes['kuiper61'].pmat['CD1_1'] = ' 2.37780000000E-004'
telescopes['kuiper61'].pmat['CD1_2'] = ' 6.73650000000E-006' 
telescopes['kuiper61'].pmat['CD2_1'] = '-6.73040000000E-006'
telescopes['kuiper61'].pmat['CD2_2'] =  '2.37999000000E-004'

telescopes['c14w'] = telescope()
telescopes['c14w'].name = 'c14w'
telescopes['c14w'].fullname = 'C14 West'
telescopes['c14w'].rdnoise = 10
telescopes['c14w'].egain = 2.53
telescopes['c14w'].aperture = 35
telescopes['c14w'].trimsection = '[2:1535,7:1023]'
telescopes['c14w'].pmat['CD1_1'] = ' 2.37780000000E-004'
telescopes['c14w'].pmat['CD1_2'] = ' 6.73650000000E-006' 
telescopes['c14w'].pmat['CD2_1'] = '-6.73040000000E-006'
telescopes['c14w'].pmat['CD2_2'] =  '2.37999000000E-004'

telescopes['c14e'] = telescope()
telescopes['c14e'].name = 'c14e'
telescopes['c14e'].fullname = 'C14 East'
telescopes['c14e'].rdnoise = 10
telescopes['c14e'].egain = 2.53
telescopes['c14e'].aperture = 35
telescopes['c14e'].trimsection = ''
telescopes['c14e'].pmat['CD1_1'] = ' 2.36760000000E-004'
telescopes['c14e'].pmat['CD1_2'] = ' 2.52240000000E-006' 
telescopes['c14e'].pmat['CD2_1'] = '-2.48240000000E-006'
telescopes['c14e'].pmat['CD2_2'] = ' 2.36480000000E-004'
