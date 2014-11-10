''' Change some code!
'''


def usage():
    print ''' 
Credits: Marco Rocchetto (m.rocchetto@ucl.ac.uk)

Usage:   python reduce.py -m --master bias/dark/flat
                          -r --reduce [files]
                          -b --bias [file]
                          -d --dark [file]
                          -f --flat [file(s)]
                          -t --telescope telescopename

Typical use:
> cd /tmp/reduce
cd to the folder with the fits files to reduce

> python /path/to/reduce.py -t telescopename -m bias
create a master bias, called MasterBias.fits

> python /path/to/reduce.py -t telescopename -m dark [-b filename.fits]
create a master dark, called Masterdark.fits, using filename.fits
filename.fits is the bias frame to use. If it is not  specified, the default 
filename 'MasterBias.fits' is used

> python /path/to/reduce.py -t telescopename -m flat [-b filename.fits] [-d filename.fits]
create the master flats, called MasterFlat-filter.fits. 
Filters are automatically recognized. As before one can specify master 
dark and bias to use wth -b and -d, or just use the defaults.

> python /path/to/reduce.py -t telescopename -r [-b filename.fits] [-d filename.fits] \
            [-f filter1.fits filter2.fits ... ]
reduce all the Light frames. Specify the master bias, dark or flats to use
or use the default ones. 
''' 
    
''' Function round_base '''   
def round_base(x, base=5):
    return int(base * round(float(x)/base))

''' Function datenight 
     
     this function returns a date of the form DD-MM-YYYY from an observer point of view.
     i.e. the day is defined from the midday of the evening of observation until the
     midday of the following day. E.g. images aquired on 12-01-2012 at 4am will have
     date 11-01-2012.
'''
def datenight(timestamp):
    import datetime
    d = datetime.datetime.fromtimestamp(timestamp).strftime('%d')
    m = datetime.datetime.fromtimestamp(timestamp).strftime('%m')
    Y = datetime.datetime.fromtimestamp(timestamp).strftime('%Y')
    H = datetime.datetime.fromtimestamp(timestamp).strftime('%H')    
    if (int(H) < 12): 
        ts = timestamp - 86400
        d = datetime.datetime.fromtimestamp(ts).strftime('%d')
        m = datetime.datetime.fromtimestamp(ts).strftime('%m')
        Y = datetime.datetime.fromtimestamp(ts).strftime('%Y')
    if (d < 10): d = '0' + str(d)
    else: d = str(d)
    return Y + '-' + m + '-' + d

'''  Function list_frames 

Create a nested array, with frames divided by Image Type, Date, Temperature
and Bin. For each frame we have:
    
    validFrames[imagetyp][daten][ccdtemp][bin][nframe]
           { path, filter, ccdtemp, timestamp, datenight }

''' 
def list_frames(idir):
     
    import os, time, pyfits
    import param as p
    
    inFramesAll = os.listdir(idir)
    failedFrames = [] # @todo
    validFrames = {}    
    
    print 'Generating list of FITS files. Source: ' + idir
    
    for path, subdirs, files in os.walk(idir):
        for name in files:
            frame = os.path.join(path, name)
            if (frame[-4:].upper() == 'FITS' or frame[-3:].upper() == 'FIT'):
                
                # create nested array, with frames divided by Image type > Date > Temperature                                
                #try:
                header=pyfits.getheader(frame)    # Check header is readable                    
    
                if 'IMAGETYP' in header: 
                    imagetyp = header['IMAGETYP'].upper()   #determine imagetyp
                else: continue
                
                if imagetyp in p.biasTypes: imagetyp = 'Bias Frame'
                elif imagetyp in p.darkTypes: imagetyp = 'Dark Frame'
                elif imagetyp in p.flatTypes: imagetyp = 'Flat Field'
                else: imagetyp = 'Light Frame'
                if not imagetyp in validFrames.keys(): validFrames[imagetyp] = {}
 
                if imagetyp == 'Light Frame':
                    if not 'OBJCTRA' in header: continue
                    if not 'OBJCTDEC' in header: continue

                if 'DATE-OBS' in header:
                    obsdate = header["DATE-OBS"]
                    dtime = obsdate.split(".")
                    timestamp = time.mktime(time.strptime(dtime[0], "%Y-%m-%dT%H:%M:%S")) #convert DATEOBS in unix timestamp
                    daten = datenight(timestamp)  #convert obs-date in night of observation (see function datenight)
                else: continue
                
                if 'CCD-TEMP' in header:
                    ccdtemp = round_base(header['CCD-TEMP'], 5) #round ccdtemp, base 5
                else: continue
                
                  
                # create a dictionary for the frame
                frameD = {}                      
                frameD['path'] = frame 
                frameD['timestamp'] = timestamp
                frameD['datenight'] = daten
                frameD['ccdtemp'] = header['CCD-TEMP']
                
                # check if frame comes from ACP. Insert in array
                if 'TELESCOP' in header: 
                    if header['TELESCOP'] == 'ACP->TheSky':
                        frameD['ROBOTIC'] = True
                if not 'ROBOTIC' in frameD: frameD['ROBOTIC'] = False
                    

                if 'XBINNING' in header: xbin = header['XBINNING']
                if 'YBINNING' in header: ybin = header['YBINNING']
                if xbin and ybin and (xbin == ybin): bin = xbin
                else: print '*** ERROR Cannot determine binning'
                
                if imagetyp == 'Light Frame' or imagetyp == 'Flat Field':
                    frameD['filter'] = header['FILTER']
                    
                # declare dictionary for the date of observation if empty
                if not daten in validFrames[imagetyp].keys(): 
                    validFrames[imagetyp][daten] = {}
                
                # declare dictionary for the CCD temperature if empty
                if not ccdtemp in validFrames[imagetyp][daten].keys(): 
                    validFrames[imagetyp][daten][ccdtemp] = {}
                
                # declare dictionary for the binning  if empty
                if not bin in validFrames[imagetyp][daten][ccdtemp].keys(): 
                    validFrames[imagetyp][daten][ccdtemp][bin] = []
                
                #append frame
                validFrames[imagetyp][daten][ccdtemp][bin].append(frameD)
                
#                except:
#                    failedFrames.append(frame)
#                    print '*** ERROR occurred in frame ' + frame              
#                    continue
    return validFrames, failedFrames

''' Main '''
def main(argv):
    
    import getopt, os
    import param as p

    try:
        # accept options -h, -m, -t, -b, -d, -f, -r
        opts, argv = getopt.getopt(argv, 'hm:t:b:d:f:r', ['help', 'master=', 'telescope=', 'bias=', 'dark=', 'flat=', 'reduce'])
        
    except getopt.GetoptError:           
        usage()                         
        sys.exit(2)                     
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        
        # need to select the telescope, see param.py
        if opt in ('-r', '--reduce') or opt in ('-m', '--master'):
            for opt2, arg2 in opts:
                if opt2 in ('-t', '--telescope'):
                    telescope = p.telescopes[arg2]
                    
            try: telescope
            except:
                usage()
                sys.exit(2)
        
        # option -r, reduce frames
        if opt in ('-r', '--reduce'):
            
            from pyraf import iraf
            import pyfits

            # inizialise variables
            p = {}
            framelist = []
            filters = []
            
            if arg:
                # one can specify a list of frames, divided by a space 
                # @todo not tested!
                framelist.append(arg.split(' '))
                
            else:
                # get list of frames, using function list_frames
                frameType = 'Light Frame'
                frames = list_frames('.')[0]
                for date in frames[frameType]: # select just frameType
                    for temperature in frames[frameType][date]:
                        for bin in frames[frameType][date][temperature]:
                            framesProc = frames[frameType][date][temperature][bin]
                            for frameProc in framesProc:
                                # exclude master frames (shouldn't be necessary!)
                                if not os.path.basename(frameProc['path'])[0:6] == 'Master':   
                                    # add frame path to framelist                                 
                                    if not frameProc['filter'] in filters: filters.append(frameProc['filter'])
                                    f = {}
                                    f['path'] = os.path.abspath(frameProc['path'])
                                    f['filter'] = frameProc['filter']
                                    framelist.append(f)
            
            # set bias, dark and flats.
            # if nothing is specified, use default Master*.fits

            for opt1, arg1 in opts:
                if opt1 in ('-b', '--bias'):
                    if arg1: p['bias'] = arg1
                if opt1 in ('-d', '--dark'):
                    if arg1: p['dark'] = arg1
                if opt1 in ('-f', '--flat'):
                    if arg1: p['flat'] = arg1
        
            if not 'bias' in p: p['bias'] = 'MasterBias.fits'
            if not 'dark' in p: p['dark'] = 'MasterDark.fits'
            
            # set flat fields, divided by filter
            flatfiles = []
            if not 'flats' in p: 
                import glob
                for file in glob.glob('./MasterFlat*'):
                    f = {}
                    f['path'] = os.path.abspath(file)
                    header=pyfits.getheader(file)
                    f['filter'] = header['FILTER']
                    flatfiles.append(f)
            
            # check that files  exist
            try:
                with open(p['dark']): pass
            except IOError:
                print '%s not found' % p['dark']
            try:
                with open(p['bias']): pass
            except IOError:
                print '%s not found' % p['bias']

            # create copies of original files, with prefix CORR_
            import shutil
            for f in framelist:
                shutil.copy(f['path'], os.path.splitext(f['path'])[0]+'_reduced.fits')
                
            # reduce images by filter
            for filter in filters:
                
                
                # create text list of files for iraf
                tmplistcorr = open('tmplistcorr', 'w')        
                for frame in framelist:
                    if frame['filter'] == filter:
                        tmplistcorr.write("%s_reduced.fits\n" % (os.path.splitext(frame['path'])[0]))
                tmplistcorr.close()
                
                # select flat field
                for flat in flatfiles:
                    if flat['filter'] == filter: p['flat'] = flat['path']
                                
                # reduce frames
                print 'Calibrate images with %s filter' % filter
                iraf.ccdproc(images='@tmplistcorr',output='', ccdtype='', fixpix='no', \
                overscan='no', trim='No', zerocor='yes', zero=p['bias'],            \
                darkcor='Yes', dark=p['dark'], flatcor='yes', flat=p['flat'], readaxi='column', \
                biassec='',    trimsec='')
            
            
        # option -m type: create master frames                
        elif opt in ('-m', '--master'):
          
            from pyraf import iraf
            import pyfits
            
            p = {}
            framelist = []

            # select frame type
            if arg == 'bias' or arg == 'dark' or arg == 'flat':   
                if arg == 'bias': frameType = 'Bias Frame' # we need 'Bias Frame', not just 'bias'!
                elif arg == 'dark': frameType = 'Dark Frame' # same
                elif arg == 'flat': 
                    frameType = 'Flat Field' # same
                    frameflat = [] # frameflat is used to divide files by filter
                    filters = []
                    
                # use function list_frames from reduceall, to list all the frames
                # divided by frametype, date, temperature, bin
                # and add them to a single list
                frames = list_frames('.')[0]
                for date in frames[frameType]: # select just frameType
                    for temperature in frames[frameType][date]:
                        for bin in frames[frameType][date][temperature]:
                            framesProc = frames[frameType][date][temperature][bin]
                            for frameProc in framesProc:
                                # exclude master frames
                                if not os.path.basename(frameProc['path'])[0:6] == 'Master':   
                                    # add frame path to framelist                                 
                                    framelist.append(os.path.abspath(frameProc['path']))
                                    # for flat fields, create a second list (frameflat) 
                                    # that specifies the filter name
                                    if arg == 'flat':
                                        if not frameProc['filter'] in filters: filters.append(frameProc['filter'])
                                        flat = {}
                                        flat['path'] = os.path.abspath(frameProc['path'])
                                        flat['filter'] = frameProc['filter']
                                        frameflat.append(flat)
                
                # set bias frame and/or dark frame.
                # if nothing is specified, use default Master*.fits
                # check that files actually exist
                if arg == 'dark' or arg == 'flat':
                    for opt1, arg1 in opts:
                        if opt1 in ('-b', '--bias'):
                            if arg1: p['bias'] = arg1
                        if opt1 in ('-d', '--dark') and arg == 'flat':
                            if arg1: p['dark'] = arg1
                    
                    if not 'bias' in p: p['bias'] = 'MasterBias.fits'
                    if not 'dark' in p and arg == 'flat': p['dark'] = 'MasterDark.fits'
                    
                    if 'dark' in p:
                        try:
                            with open(p['dark']): pass
                        except IOError:
                            print '%s not found' % p['dark']
                    if 'bias' in p:
                        try:
                            with open(p['bias']): pass
                        except IOError:
                            print '%s not found' % p['bias']


                # create copies of original files, with prefix CORR_
                import shutil
                for f in framelist:
                    shutil.copy(f, os.path.join(os.path.dirname(f), 'CORR_'+os.path.basename(f)))
                
                # create text lists of original and copied files
                tmplistcorr = open('tmplistcorr', 'w')        
                tmplist = open('tmplist', 'w')        
                for f in framelist: 
                    tmplistcorr.write("%s/CORR_%s\n" % (os.path.dirname(f), os.path.basename(f)))
                    tmplist.write("%s\n" % f)
                tmplistcorr.close()
                tmplist.close()

                # create MasterBias
                if arg == 'bias':
                    
                        print 'Trim bias frames'
                        iraf.ccdproc (images='@tmplistcorr',output ='', ccdtype = '', fixpix='no', \
                        oversca = 'no', trim = 'yes', zerocor = 'no', zero = '',   \
                        flatcor = 'no', darkcor = 'no', readaxi = 'column',        \
                        biassec = '', trimsec=telescope.trimsection)
                    
                        print 'Creating MasterBias.fits'
                        iraf.zerocombine (PYinput='@tmplistcorr', output='MasterBias.fits', ccdtype='', \
                        combine='median', reject='none', rdnoise=telescope.rdnoise, gain=telescope.egain)

                # create MasterDark
                if arg == 'dark': 
                                            
                        print 'Bias subtract dark frames'
                        iraf.ccdproc(images='@tmplistcorr',output='', ccdtype='', fixpix='no', \
                        overscan='no', trim='yes', zerocor='yes', zero=p['bias'],            \
                        darkcor='No', flatcor='no', readaxi='column',        \
                        biassec='',    trimsec=telescope.trimsection)
                        
                        print 'Creating MasterDark.fits'
                        iraf.darkcombine (PYinput='@tmplistcorr', output='MasterDark.fits', ccdtype='', \
                        combine='median', reject='none', process='no', delete='no',      \
                        clobber='no', scale='exposure', statsec='', nlow='0', nhigh='1', \
                        nkeep='1', mclip='yes', lsigma='5.', hsigma='4.',rdnoise=telescope.rdnoise,\
                        gain=telescope.egain, snoise='0.', pclip='-0.5', blank='0.')
                
                # create FlatFields, divided by filter
                if arg == 'flat':
                    
                        print 'Bias and dark subtract flat fields'
                        iraf.ccdproc(images='@tmplistcorr',output='', ccdtype='', fixpix='no', \
                        overscan='no', trim='yes', zerocor='yes', zero=p['bias'],            \
                        darkcor='Yes', dark=p['dark'], flatcor='no', readaxi='column',        \
                        biassec='',    trimsec=telescope.trimsection)
                     
                        # divide images by filter and flat combine
                        for filter in filters:
                            print 'Combine flat fields - Filter %s' % filter
                            
                            # create text list for iraf
                            flatlist = open('flatlist', 'w')        
                            for frame in frameflat:
                                if frame['filter'] == filter:
                                    flatlist.write("%s\n" % frame['path'])
                            flatlist.close()
                            
                            iraf.flatcombine(PYinput = '@flatlist', output='MasterFlat-%s.fits' % filter, ccdtype='',   \
                            combine='median', reject='none', process='no', subsets='no',     \
                            delete='no', clobber='no', scale='mode', statsec=' ', nlow='1',  \
                            nhigh='1', nkeep='1', mclip='yes', lsigma='5.', hsigma='5.',     \
                            rdnoise=telescope.rdnoise, gain=telescope.egain, snoise='0.', pclip='-0.5',blank='1.')
                            
                            os.remove('flatlist')


                # remove working files & temp lists
                for f in framelist:
                    os.remove(os.path.join(os.path.dirname(f), 'CORR_'+os.path.basename(f)))
                os.remove('tmplist')
                os.remove('tmplistcorr')

                
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])