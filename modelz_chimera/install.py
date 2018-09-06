import sys, os, shutil

#li = sys.argv.index ( "install.py" )
#print li


if len(sys.argv) != 2 :
    print ""
    print "Please add the path where Chimera is installed, e.g.:"
    print "   python install.py /home/greg/applications/Chimera"
    print ""

    exit()
    

print ""

opath = os.path.join ( sys.argv[1], "Contents" )
opath = os.path.join ( opath, "Resources" )
opath = os.path.join ( opath, "share" )

if os.path.isdir( opath ) :
    opath = os.path.join ( opath, "modelz" )

    if os.path.isdir( opath ) :
        print " - removing previous ModelZ:", opath
        shutil.rmtree(opath)
    
    print " - copying from:", os.getcwd()
    print " - copying to:", opath

    try :
        shutil.copytree ( os.getcwd(), opath )  
    except :
        print "Could not copy to:", opath
        print " 1. please check if you have write access"
        print " 2. try with sudo python install.py <path to Chimera>"
        print ""
        
    
    print ""
    print "Installation complete."
    print ""
    print "To use:"
    print " 1. Please restart Chimera."
    print " 2. Select Tools -> Volume Data -> ModelZ"
    print ' 3. Please note that on Mac OS, you may see the message "Chimera is damaged and cannot be opened." Please see the following link for the solution: https://www.santoshsrinivas.com/disable-gatekeeper-in-macos-sierra/'
    print ' 4. More info: https://cryoem.slac.stanford.edu/ncmi/resources/software/modelz'
    print ' 5. Tutorial: https://github.com/gregdp/modelz/blob/master/tutorials/Tutorial-ModelZ.pdf'
    print " 6. Let us know about yourself and if we can contact you for updates and other related information: https://cryoem.slac.stanford.edu/ncmi/content/modelz-registration"
    print ' 7. For other questions/comments/suggestions, please contact gregp@slac.stanford.edu'
    print ""
    
    #wh = os.path.join ( os.getcwd(), "install.html" )
    #import webbrowser
    #webbrowser.open( 'file://' + wh, new=2)


else :
    print ""
    print 'Chimera not found in "' + sys.argv[1] + '"'
    print " 1. please check the path"
    print " 2. remember you can auto-complete while typing the path with <tab>"
    print " 3. if issue persists, please report to gregp@slac.stanford.edu"
    print ""


