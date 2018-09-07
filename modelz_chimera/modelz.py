
# Copyright (c) 2018 Greg Pintilie - gregp@slac.stanford.edu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import chimera
import os
import os.path
import Tkinter
import tkFont
from CGLtk import Hybrid
import VolumeData
import _multiscale
import MultiScale.surface
import _surface
import numpy
import _contour
import Matrix
import Surface
import VolumeViewer
import FitMap
from sys import stderr
from time import clock

from axes import prAxes
import _multiscale
from CGLutil.AdaptiveTree import AdaptiveTree
import random
from VolumePath import Marker_Set, Marker, Link
from _contour import affine_transform_vertices as transform_vertices
from Matrix import xform_matrix, multiply_matrices, chimera_xform, identity_matrix, invert_matrix, shift_and_angle
import struct


from Rotamers import getRotamers
from chimera.resCode import protein1to3


OML = chimera.openModels.list



def umsg ( txt ) :
    print txt
    status ( txt )

def status ( txt ) :
    txt = txt.rstrip('\n')
    msg.configure(text = txt)
    msg.update_idletasks()


class ModelZ_Dialog ( chimera.baseDialog.ModelessDialog ):

    title = "ModelZ (v1.0)"
    name = "modelz"
    buttons = ( "Close" )
    help = 'https://cryoem.slac.stanford.edu/ncmi/resources/software/modelz'


    def fillInUI(self, parent):

        self.group_mouse_mode = None

        tw = parent.winfo_toplevel()
        self.toplevel_widget = tw
        tw.withdraw()

        parent.columnconfigure(0, weight = 1)

        row = 0

        menubar = Tkinter.Menu(parent, type = 'menubar', tearoff = False)
        tw.config(menu = menubar)

        f = Tkinter.Frame(parent)
        f.grid(column=0, row=row, sticky='ew')
        
        #l = Tkinter.Label(f, text='  ')
        #l.grid(column=0, row=row, sticky='w')

        

        # ---------------------------------------------------------------------------------

        self.InitVars()


        if 1 :
            #row += 1
            ff = Tkinter.Frame(f)
            ff.grid(column=0, row=row, sticky='nsew', pady=0, padx=0)

            Tkinter.Grid.columnconfigure(f, 0, weight=1)
            Tkinter.Grid.columnconfigure(ff, 0, weight=1)

            Tkinter.Grid.rowconfigure(f, row, weight=1)
            Tkinter.Grid.rowconfigure(ff, 0, weight=1)


            self.Canvas = Tkinter.Canvas(ff, height=80)
            self.Canvas.grid(column=0, row=0, sticky='nsew')

            self.modX = 10; self.modY = 10; self.modH = 30
            self.seqX = 10; self.seqY = 45; self.seqH = 30

            self.Canvas.bind("<ButtonPress-1>", lambda event : self.B1_Down ( event ) )
            self.Canvas.bind("<Control-ButtonPress-1>", lambda event : self.B1_Down_Ctrl ( event ) )
            self.Canvas.bind("<Shift-ButtonPress-1>", lambda event : self.B1_Down_Shift ( event ) )
            self.Canvas.bind("<Option-ButtonPress-1>", lambda event : self.B1_Down_Alt ( event ) )
            self.Canvas.bind("<Alt-ButtonPress-1>", lambda event : self.B1_Down_Alt ( event ) )
            self.Canvas.bind("<ButtonPress-2>", lambda event : self.B2_Down (event) )
            self.Canvas.bind("<ButtonPress-3>", lambda event : self.B3_Down (event) )
            self.Canvas.bind("<ButtonRelease-1>", lambda event : self.B1_Up ( event ) )
            self.Canvas.bind("<Control-ButtonRelease-1>", lambda event : self.B1_Up_Ctrl ( event ) )
            self.Canvas.bind("<Shift-ButtonRelease-1>", lambda event : self.B1_Up_Shift ( event ) )
            self.Canvas.bind("<Alt-ButtonRelease-1>", lambda event : self.B1_Up_Alt ( event ) )
            self.Canvas.bind("<Option-ButtonRelease-1>", lambda event : self.B1_Up_Alt ( event ) )

            self.Canvas.bind("<ButtonRelease-2>", lambda event : self.B2_Up (event) )
            self.Canvas.bind("<Option-ButtonRelease-2>", lambda event : self.B2_Up_Alt (event) )
            self.Canvas.bind("<Alt-ButtonRelease-2>", lambda event : self.B2_Up_Alt (event) )
            self.Canvas.bind("<Control-ButtonRelease-2>", lambda event : self.B2_Up_Ctrl (event) )
            self.Canvas.bind("<Command-ButtonRelease-2>", lambda event : self.B2_Up_Comm (event) )
            self.Canvas.bind("<Shift-ButtonRelease-2>", lambda event : self.B2_Up_Shift (event) )

            self.Canvas.bind("<ButtonRelease-3>", lambda event : self.B2_Up (event) )
            self.Canvas.bind("<Option-ButtonRelease-3>", lambda event : self.B2_Up_Alt (event) )
            self.Canvas.bind("<Alt-ButtonRelease-3>", lambda event : self.B2_Up_Alt (event) )
            self.Canvas.bind("<Control-ButtonRelease-3>", lambda event : self.B2_Up_Ctrl (event) )
            self.Canvas.bind("<Command-ButtonRelease-3>", lambda event : self.B2_Up_Comm (event) )
            self.Canvas.bind("<Shift-ButtonRelease-3>", lambda event : self.B2_Up_Shift (event) )

            self.Canvas.bind("<B1-Motion>", lambda event : self.B1_Drag ( event ) )
            self.Canvas.bind("<B2-Motion>", lambda event : self.B2_Drag ( event ) )
            self.Canvas.bind("<B3-Motion>", lambda event : self.B3_Drag ( event ) )
            self.Canvas.bind("<Motion>", lambda event : self.Mouse_Move ( event ) )
            self.Canvas.bind("<Configure>", lambda event : self.Canvas_Config (event) )
            self.Canvas.bind("<Leave>", lambda event : self.Canvas_Leave (event) )
            self.Canvas.bind("<MouseWheel>", lambda event : self.Canvas_Wheel (event) )


        row += 1
        ff = Tkinter.Frame(f)
        ff.grid(column=0, row=row, sticky='w', pady=0, padx=5)

        if 1 :
            ff = Tkinter.Frame(f)
            ff.grid(column=0, row=row, sticky='w', pady=5, padx=10)

            l = Tkinter.Label(ff, text='Map:', anchor=Tkinter.W)
            l.grid(column=0, row=0, sticky='w')

            self.dmap = Tkinter.StringVar(parent)
            self.dmapMB  = Tkinter.Menubutton ( ff, textvariable=self.dmap, relief=Tkinter.RAISED, width=15 )
            self.dmapMB.grid (column=1, row=0, sticky='we', padx=5)
            self.dmapMB.menu  =  Tkinter.Menu ( self.dmapMB, tearoff=0, postcommand=self.MapMenu )
            self.dmapMB["menu"]  =  self.dmapMB.menu

            self.cur_dmap = None
            self.SetVisMap ()


            l = Tkinter.Label(ff, text='Model:', anchor=Tkinter.W)
            l.grid(column=2, row=0, sticky='w')

            self.struc = Tkinter.StringVar(parent)
            self.strucMB  = Tkinter.Menubutton ( ff, textvariable=self.struc, relief=Tkinter.RAISED, width=15 )
            self.strucMB.grid (column=3, row=0, sticky='we', padx=5)
            self.strucMB.menu  =  Tkinter.Menu ( self.strucMB, tearoff=0, postcommand=self.StrucMenu )
            self.strucMB["menu"]  =  self.strucMB.menu

            self.cur_mol = None
            self.cur_chains = []
            self.SetVisMol ()


            l = Tkinter.Label(ff, text=" Chain:" )
            l.grid(column=4, row=0, sticky='w')

            self.chain = Tkinter.StringVar(parent)
            self.chainMB  = Tkinter.Menubutton ( ff, textvariable=self.chain, relief=Tkinter.RAISED, width=4 )
            self.chainMB.grid (column=5, row=0, sticky='we', padx=5)
            self.chainMB.menu  =  Tkinter.Menu ( self.chainMB, tearoff=0, postcommand=self.ChainMenu )
            self.chainMB["menu"]  =  self.chainMB.menu

            if len ( self.cur_chains ) > 0 :
                self.chain.set ( self.cur_chains[0] )
                self.ShowCh ( self.cur_chains[0] )
                self.GetSeq ()
                

            b = Tkinter.Button(ff, text="Show Chain", command=self.AllChain)
            b.grid (column=6, row=0, sticky='w', padx=5)

            b = Tkinter.Button(ff, text="Show All", command=self.AllChains)
            b.grid (column=7, row=0, sticky='w', padx=5)

            #b = Tkinter.Button(ff, text="RandColor", command=self.RandColorChains )
            #b.grid (column=7, row=0, sticky='w', padx=5)

            #l = Tkinter.Label(ff, text=' Z-Scores:', fg="#777")
            #l.grid(column=8, row=0, sticky='e')

            #b = Tkinter.Button(ff, text="SSE", command=self.SSE)
            #b.grid (column=9, row=0, sticky='w', padx=5)

            b = Tkinter.Button(ff, text="Calculate Z-Scores", command=self.CalcZScores)
            b.grid (column=10, row=0, sticky='w', padx=5)


            if 1 :
                oft = Hybrid.Checkbutton(ff, 'Ribbon', True)
                #oft.button.grid(column = 12, row = 0, sticky = 'w')
                self.showRibbon = oft.variable
                #self.showRibbon.set ( 1 )


            #oft = Hybrid.Checkbutton(ff_color, 'SSE', False)
            #oft.button.grid(column = 21, row = 0, sticky = 'w')
            #self.colorSSE = oft.variable
            #self.colorSSE.set ( 0 )

            #oft = Hybrid.Checkbutton(ff_color, 'SC', False)
            #oft.button.grid(column = 22, row = 0, sticky = 'w')
            #self.colorSC = oft.variable
            #self.colorSC.set ( 0 )

            #oft = Hybrid.Checkbutton(ff_color, 'Rand', False)
            #oft.button.grid(column = 23, row = 0, sticky = 'w')
            #self.colorRand = oft.variable
            #self.colorRand.set ( 0 )

            #oft = Hybrid.Checkbutton(ff_color, 'Map', False)
            #oft.button.grid(column = 24, row = 0, sticky = 'w')
            #self.colorMap = oft.variable
            #self.colorMap.set ( 1 )

            #b = Tkinter.Button(ff_color, text="Update", command=self.DoColor)
            #b.grid (column=25, row=0, sticky='w', padx=5)



            #b = Tkinter.Button(ff, text="Res-B", command=self.ResB)
            #b.grid (column=11, row=0, sticky='w', padx=5)

            #b = Tkinter.Button(ff, text="Mask", command=self.Mask)
            #b.grid (column=12, row=0, sticky='w', padx=5)


        if 1 :

            l = Tkinter.Label(ff, text='        Zoom:', fg="#777")
            l.grid(column=35, row=0, sticky='e')

            b = Tkinter.Button(ff, text="-", command=self.ZoomMinus)
            b.grid (column=36, row=0, sticky='w', padx=0)

            b = Tkinter.Button(ff, text="+", command=self.ZoomPlus)
            b.grid (column=37, row=0, sticky='w', padx=0)

            b = Tkinter.Button(ff, text="<", command=self.ZoomBegin)
            b.grid (column=38, row=0, sticky='w', padx=0)

            b = Tkinter.Button(ff, text=">", command=self.ZoomEnd)
            b.grid (column=39, row=0, sticky='w', padx=0)


        if 1 :

            row += 1
            ff = Tkinter.Frame(f)
            ff.grid(column=0, row=row, sticky='w', pady=0, padx=5)
            
            
            self.colorMod = Tkinter.StringVar()
            self.colorMod.set ( 'sc' )
            
            b = Tkinter.Button(ff, text="Color:", command=self.DoColor)
            b.grid (column=20, row=0, sticky='w', padx=5)
            
            c = Tkinter.Radiobutton(ff, text="SSE", variable=self.colorMod, value = 'sse')
            c.grid (column=21, row=0, sticky='w')
            
            c = Tkinter.Radiobutton(ff, text="SC", variable=self.colorMod, value = 'sc')
            c.grid (column=22, row=0, sticky='w')
            
            c = Tkinter.Radiobutton(ff, text="Random", variable=self.colorMod, value = 'rand')
            c.grid (column=23, row=0, sticky='w')



            ff = Tkinter.Frame(ff, borderwidth=1, padx=2, pady=2, relief=Tkinter.GROOVE)
            ff.grid(column=30, row=0, sticky='w', pady=0, padx=5)

            l = Tkinter.Label(ff, text='   Selection (Ctrl+Click+Drag on Sequence) - Show:', fg="#000")
            l.grid(column=35, row=0, sticky='ens')

            oft = Hybrid.Checkbutton(ff, 'Ribbon', True)
            oft.button.grid(column = 36, row = 0, sticky = 'w')
            self.showRibbon = oft.variable
            #self.showRibbon.set ( 1 )

            oft = Hybrid.Checkbutton(ff, 'Atoms', True)
            oft.button.grid(column = 37, row = 0, sticky = 'w')
            self.showAtoms = oft.variable
            #self.showRibbon.set ( 1 )

            oft = Hybrid.Checkbutton(ff, 'Mesh', True)
            oft.button.grid(column = 38, row = 0, sticky = 'w')
            self.showMesh = oft.variable
            #self.showRibbon.set ( 1 )

            #oft = Hybrid.Checkbutton(ff, 'Preserve', False, command=self.cb)
            #oft.button.grid(column = 39, row = 0, sticky = 'w')
            #self.preserveSel = oft.variable
            self.preserveSel = Tkinter.IntVar()
            oft = Tkinter.Checkbutton( ff, text="Preserve", variable=self.preserveSel, command=self.preserveSelCb)
            oft.grid(column = 39, row = 0, sticky = 'w')
            #self.showRibbon.set ( 1 )

            #b = Tkinter.Button(ff, text="Clear", command=self.ClearSel)
            #b.grid (column=40, row=0, sticky='w', padx=5)

            #self.keepExMap = Tkinter.IntVar()
            #self.keepExMap.set(0)
            #oft = Tkinter.Checkbutton( ff, text="Keep Extracted Maps", variable=self.keepExMap, command=self.keepExMapCb)
            #oft.grid(column = 40, row = 0, sticky = 'w')


        dummyFrame = Tkinter.Frame(parent, relief='groove', borderwidth=1)
        Tkinter.Frame(dummyFrame).pack()
        dummyFrame.grid(row=row,column=0,columnspan=7, pady=3, sticky='we')
        row += 1


        global msg
        msg = Tkinter.Label(parent, width = 60, anchor = 'w', justify = 'left', fg="red", pady=5, padx=10)
        msg.grid(column=0, row=row, sticky='ew')
        self.msg = msg

        #umsg ( 'Select one or more segmented regions then press "Place Points" to start' )

        
    def InitVars ( self ) :

        self.mag = 13
        self.seqt = []
        self.boldSeqT = None
        self.drag = ''

        #self.sheetBaseClr = numpy.array ( [50.0,205.0,50.0] )
        #self.sheetClr = numpy.array ( [204.0,255.0,204.0] )
        self.sheetBaseClr = numpy.array ( [55.0,55.0,150.0] )
        self.sheetClr = numpy.array ( [150.0,150.0,250.0] )
        self.sheetClrD = self.sheetClr - self.sheetBaseClr

        self.helixBaseClr = numpy.array ( [150.0,50.0,50.0] )
        self.helixClr = numpy.array ( [255.0,150.0,150.0] )
        self.helixClrD = self.helixClr - self.helixBaseClr
        
        c = self.helixBaseClr; self.helix1 = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
        c = self.helixClr;     self.helix2 = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
        
        self.switch = "#522"
        
        c = self.sheetBaseClr; self.strand1 = "#77F"
        c = self.sheetClr;     self.strand2 = "#77F"

        c = self.sheetBaseClr; self.sheet1 = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
        c = self.sheetClr;     self.sheet2 = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')

        self.loop1 = "#999"
        
        self.selColor = "#7e7"


        self.font = tkFont.Font(family='Courier', size=(self.mag), weight='normal')
        #self.boldFont = tkFont.Font(family='Courier', size=(self.mag+4), weight='bold')
        self.tw = self.font.measure ( "a" )
        
        self.seq = ""

        #self.OrderMods ()


    def SetVisMap ( self ) :
        dmap = None
        mlist = OML(modelTypes = [VolumeViewer.volume.Volume])
        for m in mlist :
            if m.display and not "sel_masked" in m.name :
                dmap = m
                break

        if dmap == None :
            if len(mlist) > 0 :
                dmap = mlist[0]
        
        if dmap != None :
            self.dmap.set ( dmap.name + " (%d)" % dmap.id )
            self.cur_dmap = dmap


    def MapMenu ( self ) :
        self.dmapMB.menu.delete ( 0, 'end' )   # Clear menu
        mlist = OML(modelTypes = [VolumeViewer.volume.Volume])
        for m in mlist :
            self.dmapMB.menu.add_radiobutton ( label=m.name+" (%d)"%m.id, variable=self.dmap,
                                command=lambda m=m: self.MapSelected(m) )


    def MapSelected ( self, dmap ) :

        self.cur_dmap = dmap    
        print "Selected " + dmap.name

        self.GetSeq ()
        self.ZoomBegin ()


    def GetChains ( self, mol ) :
        ct = {}
        for r in mol.residues: 
            ct[r.id.chainId] = 1
        clist = ct.keys()
        clist.sort()
        return clist
        

    def SetVisMol ( self ) :
        mol = None
        mlist = OML(modelTypes = [chimera.Molecule])
        for m in mlist :
            if m.display :
                mol = m
                break
        
        if mol == None :
            if len(mlist) > 0 :
                mol = mlist[0]
        
        if mol != None :
            self.struc.set ( mol.name + " (%d)" % mol.id )
            self.cur_mol = mol
            self.cur_chains = self.GetChains ( mol )


    def StrucSelected ( self, mol ) :

        self.cur_mol = mol
        print "Selected ", mol.name, " - ", mol.id
        if mol :

            mlist = OML(modelTypes = [chimera.Molecule])
            for m in mlist :
                m.display

            mol.display = True

            self.cur_chains = self.GetChains ( mol )

            if len(self.cur_chains) == 0 :
                self.chain.set ( "" )
            elif self.chain.get() in self.cur_chains :
                print " - ch " + self.chain.get() + " already sel"
                self.ShowCh ( self.chain.get() )
            else :
                self.chain.set ( self.cur_chains[0] )
                self.ShowCh ( self.chain.get() )
            
            self.GetSeq ()
            self.ZoomBegin ()


    
    def ChainSelected ( self, ch ) :
        print " - sel chain: ", ch, self.chain.get()
        self.ShowCh ( ch )
        self.GetSeq ()
        self.ZoomBegin ()


    def StrucMenu ( self ) :
        self.strucMB.menu.delete ( 0, 'end' )   # Clear menu
        mlist = OML(modelTypes = [chimera.Molecule])
        for m in mlist :
            self.strucMB.menu.add_radiobutton ( label=m.name+" (%d)"%m.id, variable=self.struc,
                                           command=lambda m=m: self.StrucSelected(m) )

    def ChainMenu ( self ) :
        self.chainMB.menu.delete ( 0, 'end' )   # Clear menu
        print " - chain menu"
        print self.cur_chains
        for ch in self.cur_chains :
            self.chainMB.menu.add_radiobutton ( label=ch, variable=self.chain, 
                                            command=lambda ch=ch: self.ChainSelected(ch) )

        
    
    def DoColor ( self ) :
        
        print "color...", self.colorMod.get()
        
        #colSC = self.colorSC.get()
        #colRand = self.colorRand.get()
        
        if self.colorMod.get() == "rand" :
            self.RandColorChains()
        else :
            self.UpdateModColor ()

        #if self.colorMap.get() :
        #    self.UpdateSurfColor ()



    def UpdateSurfColor ( self ) :

        print " - surf of %s, by %s" % ( self.cur_dmap.name, self.cur_mol.name )

        numAt = 0
        for r in self.cur_mol.residues :
            for at in r.atoms :
                if "H" in at.name :
                    pass
                else :
                    numAt += 1

        allAtPos = numpy.zeros ( (numAt, 3) )
        allAts = [None] * numAt

        numAt = 0
        for r in self.cur_mol.residues :
            for at in r.atoms :
                if "H" in at.name :
                    pass
                else :
                    allAtPos[numAt] = at.coord().data()
                    allAts[numAt] = at
                    at.allPtI = numAt
                    numAt += 1


        print " - tree with %d ats" % numAt
        allAtTree = AdaptiveTree ( allAtPos.tolist(), allAts, 4.0)
        print " - done"
        
        
        


    def UpdateModColor ( self ) :

        ress = []
        try :
            ress = self.seqRes
        except :
            pass

        if len ( ress ) == 0 :
            umsg ( "No molecule/chain selected?" )
            return

        if not hasattr (self, 'scores') :
            umsg ( "No scores - press 'Z-Scores' button first" )
            return

        foundScore = False            
        for sc in self.scores :
            if sc != None :
                foundScore = True
        
        if not foundScore :
            umsg ( "No scores - press 'Z-Scores' button first" )
            return


        ac = { 'O' : chimera.MaterialColor( .9, .2, .2, 1.0 ),
                'C' : chimera.MaterialColor( .7, .7, .7, 1.0 ),
                'N' : chimera.MaterialColor( .2, .2, .9, 1.0 ),
                'H' : chimera.MaterialColor( 1, 1, 1, 1.0 ),
                'S' : chimera.MaterialColor( .9, .9, 0, 1.0 ),
                ' ' : chimera.MaterialColor( .2, .2, .2, 1.0 ),
                 }

        minScore, maxScore = 0,0
        colorSC = self.colorMod.get() == "sc"
        if colorSC : 
            minScore, maxScore = self.minSCscore, self.maxSCscore
        else :
            minScore, maxScore = self.minSSEscore, self.maxSSEscore

        cH = numpy.array( [0.0,1.0,0.0] )
        cL = numpy.array( [1.0,0.0,0.0] )

        for ri, r in enumerate ( self.seqRes ) :
            sc = None
            #sc = self.scores[ri] if colorSC else self.scores2[ri]
            sc = r.scZ if colorSC else r.sseZ

            if sc == None  :
                r.ribbonColor = chimera.MaterialColor ( .7, .7, .7, 1.0 )
                for at in r.atoms :
                    #at.color = r.ribbonColor
                    try :
                        at.color = ac[at.name[0]]
                    except :
                        at.color = ac[' ']

            else :
                h = (sc - minScore) / (maxScore - minScore)
                if h > 1 : h = 1
                if h < 0 : h = 0
                c = h * cH + (1-h) * cL
                r.ribbonColor = chimera.MaterialColor ( c[0], c[1], c[2], 1.0 )
                for at in r.atoms :
                    #at.color = r.ribbonColor
                    try :
                        at.color = ac[at.name[0]]
                    except :
                        at.color = ac[' ']
            
                #ra = r.scZ, r.sseZ

        
        
    
    def RandColorChains ( self ) :
    
        if self.cur_mol == None :
            umsg ("Select a molecule first")
            return

        m = self.cur_mol

        from random import random as rand
    
        ct = {}
        for r in m.residues: ct[r.id.chainId] = 1
        clist = ct.keys()
        clist.sort()
        chains_clrs = {}
        cnames = ""
    
        for ci, cid in enumerate ( clist ) :
            clr = ( rand()*.8+.1, rand()*.8+.1, rand()*.8+.1 )
            chains_clrs[cid] = chimera.MaterialColor ( clr[0], clr[1], clr[2], 1.0 )
            cnames = cnames + cid
    
        print "%s - color ribbon for %d chains -" % ( m.name, len(cnames) ), cnames
    
        # color atoms
        for r in m.residues :
            clr = chains_clrs[r.id.chainId]
            r.ribbonColor = clr
            for at in r.atoms :
                at.color = clr
    
    
    def AllChain ( self ) :

        if self.cur_mol == None :
            umsg ("Select a molecule first")
            return

        chainId = self.chain.get()
        if len(chainId) == 0 :
            umsg ("Select a chain first")
            return
            
        umsg ( "Showing mol %s chain %s" % (self.cur_mol.name, chainId) )

        #ct = {}
        #for r in self.cur_mol.residues: ct[r.id.chainId] = 1
        #clist = ct.keys()
        #clist.sort()

        for r in self.cur_mol.residues :
            if r.id.chainId == chainId :
                if ("CA" in r.atomsMap and "N" in r.atomsMap and "C" in r.atomsMap) or ("O3'" in r.atomsMap and "O5'" in r.atomsMap)  :
                    r.ribbonDisplay = True
                    r.ribbonDrawMode = 2
                else :
                    r.ribbonDisplay = False
                    for at in r.atoms :
                        at.drawMode = at.Ball
                        at.display = True
            else :
                if ("CA" in r.atomsMap and "N" in r.atomsMap and "C" in r.atomsMap) or ("O3'" in r.atomsMap and "O5'" in r.atomsMap)  :
                    r.ribbonDisplay = False
                    r.ribbonDrawMode = 2
                else :
                    r.ribbonDisplay = False
                    for at in r.atoms :
                        at.drawMode = at.Ball
                        at.display = False


    def AllChains ( self ) :
        if self.cur_mol == None :
            umsg ("Select a molecule first")
            return

        m = self.cur_mol
        
        #ct = {}
        #for r in m.residues: ct[r.id.chainId] = 1
        #clist = ct.keys()
        #clist.sort()

        for r in m.residues :
            if ("CA" in r.atomsMap and "N" in r.atomsMap and "C" in r.atomsMap) or ("O3'" in r.atomsMap and "O5'" in r.atomsMap)  :
                r.ribbonDisplay = True
                r.ribbonDrawMode = 2
            else :
                r.ribbonDisplay = False
                for at in r.atoms :
                    at.drawMode = at.Ball
                    at.display = True
        
    
    def ShowCh ( self, ch ) :

        if self.cur_mol == None :
            umsg ("Select a molecule first")
            return
            
        print " - showing chain:", ch

        m = self.cur_mol
        print " - cur mol:", m.name

        ct = {}
        for r in m.residues: ct[r.id.chainId] = 1
        clist = ct.keys()
        clist.sort()

        for r in m.residues :
            show = True if r.id.chainId == ch else False
            if "CA" in r.atomsMap and "N" in r.atomsMap and "C" in r.atomsMap :
                r.ribbonDisplay = show
                #r.ribbonDrawMode = 2
                for at in r.atoms :
                    at.display = False
            else :
                r.ribbonDisplay = False
                for at in r.atoms :
                    at.drawMode = at.Ball
                    at.display = show
    

    def GetMod ( self, name ) :
        for m in chimera.openModels.list() :
            if name != None and len(name) > 0 :
                if m.name == name :
                    return m
            else :
                if m.display == True :
                    return m
        return None


        
    def GetSeq ( self ) :
        
        if self.cur_mol == None :
            umsg ( "No selected molecule" )
            return
        
        if len ( self.chain.get() ) == 0 :
            umsg ( "No selected chain" )
            return
            
        self.RemoveSeq ()

        try :
            print self.cur_mol.name
        except :
            print " - mol may have been closed"
            return

        self.GetSeqFromStruc ( self.cur_mol, self.chain.get() )
        
        if len(self.seq) > 0 :

            print "-- seq from open mol -- %d res" % len(self.seq)
            print self.seq
    
            self.seqt = []
            self.seqSheetR = [None] * len(self.seq)
            self.seqHelixR = [None] * len(self.seq)
            self.seqScoreR = [None] * len(self.seq)
            self.seqScoreR2 = [None] * len(self.seq)
            self.scores2 = [None] * len(self.seq)
            self.scores = [None] * len(self.seq)
            
            self.UpdateSeqFont ()
            
            return True
        
        return False




    def RemoveSeq  (self) :
        
        if self.seq == "" :
            return

        for si in range ( len(self.seq) ) :
            res = self.seq[si]
            pred = self.pred[si]
            conf = float ( self.conf[si] ) / 10.0

            if pred == 'E' :
                if self.seqSheetR[si] != None :
                    self.Canvas.delete ( self.seqSheetR[si] )

            elif pred == 'H' :
                if self.seqHelixR[si] != None :
                    self.Canvas.delete ( self.seqHelixR[si] )

            if self.seqScoreR[si] != None :
                self.Canvas.delete ( self.seqScoreR[si] )

            if self.seqScoreR2[si] != None :
                self.Canvas.delete ( self.seqScoreR2[si] )


        # box showing selected Residue
        if hasattr ( self, 'seqMouseR' ) :
            self.Canvas.delete ( self.seqMouseR )
            del self.seqMouseR

        if hasattr ( self, 'seqText' ) :
            self.Canvas.delete ( self.seqText )
            del self.seqText
            
        self.seqSel = None
        self.UpdateSeqSel ()



    def GetSeqFromStruc ( self, mol, chainId ) :

        self.conf = ""
        self.pred = ""
        self.seq = ""
        self.seqRes = []

        from chimera.resCode import protein3to1
        protein3to1['HSD'] = protein3to1['HIS']

        rids = {}
        for r in mol.residues :
            if r.id.chainId == chainId :
                if r.type in protein3to1 :
                    rids[r.id.position] = r


        ris = rids.keys()
        ris.sort()

        for ri in ris :
            r = rids[ri]
            if r.type in protein3to1 :
                self.seq = self.seq + protein3to1[r.type]
                self.conf = self.conf + "9"
                self.predi = "C"
                if r.isSheet : 
                    self.predi = "E"
                if r.isHelix :
                    self.predi = "H"
                self.pred = self.pred + self.predi
                self.seqRes.append ( r )


    
    


    def SSE ( self ) :

        print "sse"
        #self.GetFromMol ( mod, chainId )


    def CurRes ( self ) :

        #self.GetFromMol ( mod, chainId )
        
        if self.cur_mol == None :
            umsg ( "No selected molecule" )
            return []
        
        if self.cur_dmap == None :
            umsg ( "No selected map" )
            return []
            
        if len ( self.chain.get() ) == 0 :
            umsg ( "No selected chain" )
            return []
        
        from chimera.resCode import protein3to1
        protein3to1['HSD'] = protein3to1['HIS']
        
        rids = {}
        for r in self.cur_mol.residues :
            if r.id.chainId == self.chain.get() :
                if r.type in protein3to1 :
                    rids[r.id.position] = r
        
        print " - %d residues" % len(rids.values())
        return [ rids[6] ]
        #return rids.values ()
        


    def CalcZScores ( self ) :

        ress = []
        try :
            ress = self.seqRes
        except :
            pass
            
        if len ( ress ) == 0 :
            umsg ( "No molecule/chain selected?" )
            return

        self.scores2 = [None] * len(self.seqRes)
        scoreI = 0

        status ( "Getting secondary structure elements..." )

        resolution = 3.0 * self.cur_dmap.data.step[0]
        sses = SSEs ( self.seqRes )
        #print " - ",len(sses),"sse for ", len(ress), "res"

        status ( "Calculating SSE scores..." )
        atI = 1

        zscores2 = []
        for el in sses :
            si, ei, ss, elRess = el

            if atI % 10 == 0 :
                status ( "Calculating SSE scores: %d/%d" % (atI,len(sses) ) )
            atI += 1

            #if 1 or (startRes < 129 and endRes > 129) :
            zscore = evalSSE ( self.cur_mol, el, resolution, self.cur_dmap )
            #print ss, si, "-", ei, zscore
            if zscore != None :
                zscores2.append ( zscore )

            for r in elRess :
                r.sseZ = zscore
                self.scores2[scoreI] = zscore
                scoreI += 1
        

        print " - %d SSEs (%d res), min %.2f max %.2f, avg %.2f" % (len(sses), len(ress), min(zscores2), max(zscores2), numpy.average(zscores2) )
        self.avgScore2 = numpy.average ( zscores2 )

        doRes = []
        
        doAllResInMol = False
        
        if doAllResInMol :
            for res in self.cur_mol.residues :
                if "CA" in res.atomsMap and "N" in res.atomsMap and "C" in res.atomsMap :
                    doRes.append ( res )
            
            print "++++ added all %d res from %s ++++" % (len(doRes), self.cur_mol.name)
        
        else :
            for r in self.seqRes :
                try :
                    blah
                    ra = r.scZ
                except :
                    doRes.append ( r )
	


        #doRes = self.seqRes
        #doRes = self.CurRes()
        print " - need score for %d res" % len(doRes)

        status ( "Calculating side chain scores..." )

        if len(doRes) > 0 :
            evalSC ( self.cur_dmap, self.cur_mol, doRes, None )

        if not doAllResInMol :
            doRes = self.seqRes 

        self.selScore = "Res-A"

        self.scores = [None] * len(doRes)
        for ri, r in enumerate ( doRes ) :
            self.scores[ri] = r.scZ
            
        scores = [x for x in self.scores if x is not None]

        self.minScore = min ( scores )
        self.maxScore = max ( scores )
        self.avgScore = numpy.average ( scores )

        print " - %d res, min %.2f max %.2f, avg %.2f" % (len(doRes),self.minScore,self.maxScore, self.avgScore)

        self.minSCscore, self.maxSCscore = 0,2
        self.minSSEscore, self.maxSSEscore = 0,4

        sseRes = numpy.power ( numpy.e, (self.avgScore2 - 8.0334) / -4.128 ) # y = -4.128ln(x) + 8.0334 
        scRes = numpy.power ( numpy.e, (self.avgScore - 4.8261) / -3.097 ) # y = -3.097ln(x) + 4.8261
        #umsg ( "Average SSE Z-score: %.2f (%s - %.1fA), Average Side Chain Z-score: %.2f (%s - %.1fA)" % (self.avgScore2, sseRating, sseRes, self.avgScore, scRating, scRes) )
        umsg ( "Average SSE Z-score: %.2f (%.1fA), Average Side Chain Z-score: %.2f (%.1fA)" % (self.avgScore2, sseRes, self.avgScore, scRes) )

        self.UpdateSeq ()


        sByType = {}
        rByType = {}
        for r in doRes :
            if r.scZ != None :
                if not r.type in sByType :
                    rByType[r.type] = []
                    sByType[r.type] = []
                rByType[r.type].append ( [r.scZ, r] )
                sByType[r.type].append ( [r.scZ] )

        avgs = []
        for rtype, ra in sByType.iteritems () :
            avgs.append ( [numpy.average (ra), rtype] )

        from chimera.resCode import protein3to1
        avgs.sort ( reverse=True, key=lambda x: x[0] )
        for avgScore, rtype in avgs :

            rscores = rByType[rtype]
            rscores.sort ( reverse=True, key=lambda x: x[0] )
            hr = rscores[0]
            R = hr[1]
            highestScore = hr[0]
            numRes = len(rscores)

            print "%s\t%s\t%d\t%f\t%d\t.%s\t%f" % (rtype, protein3to1[rtype], numRes, avgScore, R.id.position, R.id.chainId, highestScore)
            
        
        


    def UpdateSeqFont ( self ) :
        # http://stackoverflow.com/questions/4296249/how-do-i-convert-a-hex-triplet-to-an-rgb-tuple-and-back

        if not hasattr ( self, 'seq' ) :
            print " - update seq font - no seq"
            return

        print "seq len %d, text w %d" % ( len(self.seq), self.tw )

        # boxes for SSEs
        x_at = self.seqX
        y_at = self.seqY + self.seqH/2

        y0 = self.seqY+5
        y1 = self.seqY+self.seqH-5

        for si in range ( len(self.seq) ) :
            res = self.seq[si]
            pred = self.pred[si]
            conf = float ( self.conf[si] ) / 10.0

            if pred == 'E' :
                x0 = self.seqX + si * self.tw
                x1 = x0 + self.tw
                #self.Canvas.coords ( self.seqMouseR, x0, y0, x1, y1 )
                #self.Canvas.itemconfigure ( self.seqMouseR, state=Tkinter.NORMAL )

                if self.seqSheetR[si] == None :
                    c = self.sheetBaseClr + self.sheetClrD * conf
                    clr = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
                    self.seqSheetR[si] = self.Canvas.create_rectangle(x0, y0, x1, y1, outline=clr, fill=clr)
                else :
                    self.Canvas.coords ( self.seqSheetR[si], x0, y0, x1, y1 )

            elif pred == 'H' :
                x0 = self.seqX + si * self.tw
                x1 = x0 + self.tw

                if self.seqHelixR[si] == None :
                    c = self.helixBaseClr + self.helixClrD * conf
                    clr = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
                    self.seqHelixR[si] = self.Canvas.create_rectangle(x0, y0, x1, y1, outline=clr, fill=clr)
                else :
                    self.Canvas.coords ( self.seqHelixR[si], x0, y0, x1, y1 )



        # box showing selected Residue
        if hasattr ( self, 'seqMouseR' ) :
            self.Canvas.coords ( self.seqMouseR, 0, 0, 0, 0 )
        else :
            self.seqMouseR = self.Canvas.create_rectangle(0, 0, 0, 0, outline="#aab", fill="#bbc", state=Tkinter.HIDDEN)



        x_at = self.seqX
        y_at = self.seqY + self.seqH/2

        if hasattr ( self, 'seqText' ) :
            self.Canvas.coords ( self.seqText, x_at, y_at )
            self.Canvas.itemconfigure ( self.seqText, font=self.font )
        else :
            self.seqText = self.Canvas.create_text( x_at, y_at, text=self.seq, font=self.font, anchor='w')


        #self.UpdateSeqSel ()




    def UpdateSeq ( self ) :
        
        if not hasattr ( self, 'seq' ) :
            print " - update seq - no seq"
            return

        x_at = self.seqX
        y_at = self.seqY + self.seqH/2
        
        if hasattr ( self, 'seqText' ) :
            self.Canvas.coords ( self.seqText, x_at, y_at )
        else :
            self.seqText = self.Canvas.create_text( x_at, y_at, text=self.seq, font=self.font, anchor='w')

        if 1 :
            y0 = self.seqY+5
            y1 = self.seqY+self.seqH-5
            
            cH = numpy.array( [50,200,50] )
            cL = numpy.array( [200,50,50] )
            
            for si in range ( len(self.seq) ) :
                #if i >= len ( self.seqt ) :
                #    t = self.Canvas.create_text( x_at, y_at, text=self.seq[i], font=self.font)
                #    self.seqt.append ( t )
                #else :
                #    t = self.seqt [ i ]
                #    self.Canvas.coords ( t, x_at, y_at )
                # x_at += self.tw
                    
                pred = self.pred[si]
                if pred == 'E' :
                    if self.seqSheetR[si] != None :
                        x0 = self.seqX + si * self.tw
                        x1 = x0 + self.tw
                        self.Canvas.coords ( self.seqSheetR[si], x0, y0, x1, y1 )

                elif pred == 'H' :
                    if self.seqHelixR[si] != None :
                        x0 = self.seqX + si * self.tw
                        x1 = x0 + self.tw
                        self.Canvas.coords ( self.seqHelixR[si], x0, y0, x1, y1 )

                sc = None
                try :
                    sc = self.scores[si]
                except :
                    #continue
                    pass
                
                if sc == None :
                    if self.seqScoreR[si] != None :
                        selv.Canvas.delete ( self.seqScoreR[si] )
                    self.seqScoreR[si] = None
                else :
                    xx0 = self.seqX + si * self.tw + 2
                    xx1 = xx0 + self.tw - 2
                    h = (sc - self.minSCscore) / (self.maxSCscore - self.minSCscore)
                    if h > 1 : h = 1
                    if h < 0 : h = 0
                    Y, H = self.modY, (self.modH/2 - 2)
                    yy0, yy1 = numpy.ceil(Y+H - H*h), numpy.floor(Y+H)
                    if self.seqScoreR[si] != None :
                        self.Canvas.coords ( self.seqScoreR[si], xx0, yy0, xx1, yy1 )
                    else :
                        #c = self.helixBaseClr + self.helixClrD * conf
                        c = h * cH + (1-h) * cL
                        clr = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
                        self.seqScoreR[si] = self.Canvas.create_rectangle(xx0, yy0, xx1, yy1, outline=clr, fill=clr)
                        
                sse = None
                try :
                    sse = self.scores2[si]
                except :
                    #continue
                    pass

                if sse == None :
                    if self.seqScoreR2[si] != None :
                        self.Canvas.delete ( self.seqScoreR2[si] )
                    self.seqScoreR2[si] = None
                else :
                    xx0 = self.seqX + si * self.tw + 2
                    xx1 = xx0 + self.tw - 2
                    h = (sse - self.minSSEscore) / (self.maxSSEscore - self.minSSEscore)
                    if h > 1 : h = 1
                    if h < 0 : h = 0
                    Y, H = self.modY, self.modH/2
                    #yy0, yy1 = Y+H, Y+H+H*h #upside down chart
                    yy0, yy1 = numpy.ceil(Y+H+H-H*h), numpy.floor(Y+H+H)
                    if self.seqScoreR2[si] != None :
                        self.Canvas.coords ( self.seqScoreR2[si], xx0, yy0, xx1, yy1 )
                    else :
                        #c = self.helixBaseClr + self.helixClrD * conf
                        cH = numpy.array( [50,200,50] )
                        cL = numpy.array( [200,50,50] )
                        c = h * cH + (1-h) * cL
                        clr = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
                        self.seqScoreR2[si] = self.Canvas.create_rectangle(xx0, yy0, xx1, yy1, outline=clr, fill=clr)


            self.UpdateSeqSel ()




    def SeqRec ( self, sel ) :
        y0 = self.seqY+5
        y1 = self.seqY+self.seqH-5

        x0 = self.seqX + sel[0] * self.tw
        x1 = self.seqX + (sel[1]+1) * self.tw
        
        return x0, y0, x1, y1


    def UpdateSeqSel ( self ) :
        
        if not hasattr ( self, 'seqSel' ) :
            return
        
        if self.seqSel == None :
            if hasattr(self, 'seqSelRect') :
                self.Canvas.delete ( self.seqSelRect )
                self.seqSelRect = None
            return

        x0, y0, x1, y1 = self.SeqRec ( self.seqSel )

        if hasattr(self, 'seqSelRect') and self.seqSelRect != None :
            self.Canvas.coords ( self.seqSelRect, x0, y0, x1, y1  )
        else :
            #c = self.helixBaseClr + self.helixClrD * conf
            #clr = "#" + struct.pack('BBB',c[0],c[1],c[2]).encode('hex')
            self.seqSelRect = self.Canvas.create_rectangle(x0, y0, x1, y1, outline=self.selColor,  width=3)





    def B1_Down (self, event):
        self.drag = ''

        #print "b1 _", event.x, event.y
        if self.isInSeq ( event.x, event.y ) :
            self.drag = 'seq'
        self.last_x = event.x
        self.last_y = event.y


    def B1_Down_Ctrl ( self, event ) :
        #print "b1 _ <ctrl>", event.x, event.y
        self.drag = ''
        
        if self.isInSeq ( event.x, event.y ) :
            self.drag = 'seqSel'

            if hasattr ( self, 'seqSel' ) and self.seqSel != None :
                self.prevSeqSel = self.seqSel
            else :
                self.prevSeqSel = None

            #print "sel seq..."
            seqI = ( event.x - self.seqX ) / self.tw
            status ( "Start sequence sel at %d" % (seqI+1) )
            self.seqSel = [seqI, seqI]
            self.UpdateSeqSel ()
            
        self.last_x = event.x
        self.last_y = event.y


    def B1_Down_Shift ( self, event ) :
        print "B1 down - shift"

        self.drag = ''

        if self.isInSeq ( event.x, event.y ) :
            if hasattr ( self, 'seqSel' ) and self.seqSel != None :
                seqI = ( event.x - self.seqX ) / self.tw
                if seqI >= self.seqSel[0] and seqI <= self.seqSel[1] :
                    self.drag = "con"
                    if not hasattr ( self, 'conLine' ) or self.conLine == None :
                        self.conLine = self.Canvas.create_line( event.x, event.y, event.x, event.y, fill="red", dash=(1, 1), width=2)
                    status ( "In selected sequence at %d" % seqI )


    def B1_Down_Alt ( self, event ) :
        print "B1 down - alt"

        self.drag = ''

        if self.isInMod ( event.x, event.y ) :
            self.dragMod = self.SelectedMod ( event.x, event.y )
            if self.dragMod != None :
                if self.dragMod.type == "Helix" :
                    self.drag = 'modRot'
                    self.dragStartX = event.x



    def B1_Up_Ctrl ( self, event ) :
        print "b1 up - ctrl - ", event.x, event.y
        self.B1_Up ( event )
        
        
    def B1_Up_Shift ( self, event ) :
        print "b1 up - shift - "
        self.B1_Up ( event )

    def B1_Up_Alt ( self, event ) :
        print "b1 up - alt - "
        self.B1_Up ( event )
        

    def B1_Up (self, event):
        print "b1 up - ", event.x, event.y

        if self.drag == 'seqSel' and hasattr ( self, 'seqSel' ) :
            status ( "Selected: %d-%d" % (self.seqSel[0], self.seqSel[1]) )
        
            if hasattr ( self, 'prevSeqSel' ) and self.prevSeqSel != None :
                if self.seqSel[0] == self.seqSel[1] :
                    self.seqSel = None
                    self.prevSeqSel = None
                    self.UpdateSeqSel ()
                    status ( "Cleared sequence selection" )
                    chimera.selection.clearCurrent ()

            if self.seqSel != None :
                m, cid = self.cur_mol, self.chain.get()
                if m != None :
                    startI = self.seqRes [ self.seqSel[0] ].id.position
                    endI = self.seqRes [ self.seqSel[1] ].id.position
                    selStr = "#%d:%d-%d.%s" % (m.id,startI,endI,cid)
                    
                    self.lastSelStr = "%d-%d.%s" % (startI,endI,cid)
                    
                    if hasattr ( self, 'prevSel' ) and self.preserveSel.get () :
                        for s in self.prevSel :
                            print " -s- adding to sel:", s
                            selStr = selStr + "," + s 
                    else :
                        self.prevSel = []

                    if self.preserveSel.get () :
                        self.prevSel.append ( "%d-%d.%s" % (startI,endI,cid) )
                        print " - added to selection list..."
                    
                    umsg ( "Selected: " + selStr )
                    sel = chimera.selection.OSLSelection ( selStr )
                    chimera.selection.setCurrent ( sel )
                    #chimera.selection.addCurrent ( sel )
                    self.ShowSel ()

                else :
                    status ( "no model visible" )

            #else :
            #    print "cleared past sel"
            #    self.prevSel = []


        elif self.drag == 'modSel' :
            status ( 'Selected %d mods' % len(self.selMods) )

        elif self.drag == 'con' :
            selMod = None
            if hasattr ( self, 'selModPiece' ) and self.selModPiece != None :
                selMod = self.selModPiece
                self.selModPiece = None
            else :
                return

            if hasattr ( self, 'conLine' ) and self.conLine != None :
                self.Canvas.delete ( self.conLine )
                self.conLine = None
    
            status ( "connected to %s" % selMod.type )

            selMod.seq = self.seqSel
            selMod.numRes = (self.seqSel[1] - self.seqSel[0] + 1)
            selMod.MakeMod ()

            self.UpdateMod ()
        
        self.drag = ''
        print "mod: ", self.modX, " seq:", self.seqX


    def preserveSelCb (self) :
        print "Preserve set to ", self.preserveSel.get()      
        if self.preserveSel.get() :
            print " - setting current selection to preserve..."  
            if hasattr ( self, 'lastSelStr' ) :
                self.prevSel = [ self.lastSelStr ]
        else :
            print " - clearing current"  
            self.prevSel = []
            
    #def keepExMapCb (self) :
    #    print "Kep ex map set to ", self.keepExMap.get()      


    def ClearSel ( self ) :
        self.prevSel = []
        self.seqSel = None
        self.prevSeqSel = None
        self.UpdateSeqSel ()
        status ( "Cleared sequence selection" )
        chimera.selection.clearCurrent ()


    def ShowSel ( self ) :
        
        #showRibbon = self.showRibbon.get()
        showRibbon = self.showRibbon.get()
        showAtoms = self.showAtoms.get()

        aColors = {'C' : chimera.MaterialColor (0.565,0.565,0.565),
                    'S' : chimera.MaterialColor (1.000,1.000,0.188),
                    'O' : chimera.MaterialColor (1.000,0.051,0.051),
                    'N' : chimera.MaterialColor (0.188,0.314,0.973),
                    'H' : chimera.MaterialColor (0.9,.9,.9) 
                    }

        atoms = []
        scores = []
        selResM = {}
        for r in chimera.selection.currentResidues () :
            rid = "%d.%s" % (r.id.position, r.id.chainId)
            selResM [rid] = 1
            
        if self.cur_mol == None :
            return

        for r in self.cur_mol.residues :
            rid = "%d.%s" % (r.id.position, r.id.chainId)
            if rid in selResM :

                if hasattr (r, 'scZ') and r.scZ != None :
                    scores.append(r.scZ)

                r.ribbonDisplay = showRibbon

                for at in r.atoms :
                    atoms.append ( at )
                    if showAtoms :
                        at.display = False if at.element.name == "H" else True
                        if at.element.name in aColors :
                            at.color = aColors[at.element.name]
                    else :
                        at.display = False

            else :
                r.ribbonDisplay = False
                for at in r.atoms :
                    at.display = False


        #for bond in self.seqRes[0].molecule.bonds :
        #    bond.display = bond.Smart
            #if bond.atoms[0] in atMap and bond.atoms[1] in atMap :
            #    #bond.display = bond.Smart
            #    bond.display = bond.Smart
            #else :
            #    #bond.display = bond.Never
            #    bond.display = bond.Smart
            

        if len(atoms) > 0 :

            from _multiscale import get_atom_coordinates
            points = get_atom_coordinates ( atoms, transformed = True )
            COM, U, S, V = prAxes ( points )
            
            p0 = numpy.array ( chimera.viewer.camera.center )
            p1 = numpy.array ( [ COM[0], COM[1], COM[2] ] )
            for i in range (10) :
                f = float(i) / 9.0
                f1, f2 = 2.0*f*f*f-3.0*f*f+1.0, 3*f*f-2*f*f*f
                P = p0 * f1 + p1 * f2
                chimera.viewer.camera.center = (P[0],P[1],P[2])
                print ".",
            print ""
    
    
            atomRad = 2.0 # float ( self.maskWithSelDist.get() )
            print " - %d selected atoms, mask at %.2f" % ( len(atoms), atomRad )
            dmap = self.cur_dmap
            
            mlist = OML(modelTypes = [VolumeViewer.volume.Volume])
    
            for m in mlist :
                if "sel_masked" in m.name :
                    chimera.openModels.close ( [m] )
    
            if len ( atoms ) > 0 and dmap != None :
                self.PtsToMap ( points, dmap, atomRad, dmap.name + " sel_masked", False )
                if self.showMesh.get () :
                    self.PtsToMap ( points, dmap, atomRad, dmap.name + " sel_masked_mesh", True )

            if len(scores) > 0 :
                umsg ( "%d residue scores, avg score %.1f" % ( len(scores), numpy.average(scores) ) )

        else :
            umsg ( "no atoms selected, try reselecting the model and chain..." )


    def PtsToMap0 ( self, points, dmap, atomRad, nname, neg = 1.0 ) :
        import _contour
        _contour.affine_transform_vertices ( points, Matrix.xform_matrix( dmap.openState.xform.inverse() ) )
        mdata = VolumeData.zone_masked_grid_data ( dmap.data, points, atomRad )

        gdata = VolumeData.Array_Grid_Data ( mdata.full_matrix()*neg, dmap.data.origin, dmap.data.step, dmap.data.cell_angles, name = "atom masked" )
        nv = VolumeViewer.volume.volume_from_grid_data ( gdata )
        nv.name = nname
        dmap.display = False
        nv.region = ( nv.region[0], nv.region[1], [1,1,1] )
        nv.surface_levels[0] = dmap.surface_levels[0]
        ro = VolumeViewer.volume.Rendering_Options()
        #ro.smoothing_factor = .5
        #ro.smoothing_iterations = 20
        #ro.surface_smoothing = True
        nv.update_surface ( False, ro )
        for sp in nv.surfacePieces :
            v, t = sp.geometry
            if len(v) == 8 and len(t) == 12 :
                sp.display = False
            else :
                sp.color = (0.7, 0.7, 0.7, 0.3)


    def PtsToMap ( self, points, dmap, atomRad, nname, showMesh = False ) :

        #_contour.affine_transform_vertices ( points, Matrix.xform_matrix( dmap.openState.xform.inverse() ) )
        #mdata = VolumeData.zone_masked_grid_data ( dmap.data, points, atomRad )

        import _contour
        points1 = numpy.copy ( points )
        _contour.affine_transform_vertices ( points1, Matrix.xform_matrix( dmap.openState.xform.inverse() ) )
        points0 = numpy.copy ( points1 )
        _contour.affine_transform_vertices ( points1, dmap.data.xyz_to_ijk_transform )

        bound = 5
        li,lj,lk = numpy.min ( points1, axis=0 ) - (bound, bound, bound)
        hi,hj,hk = numpy.max ( points1, axis=0 ) + (bound, bound, bound)

        n1 = hi - li + 1
        n2 = hj - lj + 1
        n3 = hk - lk + 1

        print " - bounds - %d %d %d --> %d %d %d --> %d %d %d" % ( li,lj,lk, hi,hj,hk, n1,n2,n3 )

        #nmat = numpy.zeros ( (n1,n2,n3), numpy.float32 )
        #dmat = dmap.full_matrix()

        nstep = (dmap.data.step[0], dmap.data.step[1], dmap.data.step[2] )
        #nstep = (fmap.data.step[0]/2.0, fmap.data.step[1]/2.0, fmap.data.step[2]/2.0 )

        nn1 = int ( round (dmap.data.step[0] * float(n1) / nstep[0]) )
        nn2 = int ( round (dmap.data.step[1] * float(n2) / nstep[1]) )
        nn3 = int ( round (dmap.data.step[2] * float(n3) / nstep[2]) )

        O = dmap.data.origin
        print " - %s origin:" % dmap.name, O
        nO = ( O[0] + float(li) * dmap.data.step[0],
               O[1] + float(lj) * dmap.data.step[1],
               O[2] + float(lk) * dmap.data.step[2] )

        print " - new map origin:", nO

        nmat = numpy.zeros ( (nn1,nn2,nn3), numpy.float32 )
        ndata = VolumeData.Array_Grid_Data ( nmat, nO, nstep, dmap.data.cell_angles )

        #print " - fmap grid dim: ", numpy.shape ( fmap.full_matrix() )
        #print " - new map grid dim: ", numpy.shape ( nmat )

        npoints = VolumeData.grid_indices ( (nn1, nn2, nn3), numpy.single)  # i,j,k indices
        _contour.affine_transform_vertices ( npoints, ndata.ijk_to_xyz_transform )

        dvals = dmap.interpolated_values ( npoints, dmap.openState.xform )
        #dvals = dmap.interpolated_values ( npoints, chimera.Xform.identity() )
        #dvals = dmap.interpolated_values ( npoints, dmap.openState.xform.inverse() )
        #dvals = numpy.where ( dvals > threshold, dvals, numpy.zeros_like(dvals) )
        #nze = numpy.nonzero ( dvals )

        nmat = dvals.reshape( (nn3,nn2,nn1) )
        #f_mat = fmap.data.full_matrix()
        #f_mask = numpy.where ( f_mat > fmap.surface_levels[0], numpy.ones_like(f_mat), numpy.zeros_like(f_mat) )
        #df_mat = df_mat * f_mask

        ndata = VolumeData.Array_Grid_Data ( nmat, nO, nstep, dmap.data.cell_angles )
        #try : nv = VolumeViewer.volume.add_data_set ( ndata, None )
        #except : nv = VolumeViewer.volume.volume_from_grid_data ( ndata )
        
        #nv.openState.xform = dmap.openState.xform

        mdata = VolumeData.zone_masked_grid_data ( ndata, points0, atomRad )
        gdata = VolumeData.Array_Grid_Data ( mdata.full_matrix(), nO, nstep, dmap.data.cell_angles, name = "atom masked" )
        nv = VolumeViewer.volume.volume_from_grid_data ( gdata )
        
        nv.name = nname
        dmap.display = False
        nv.region = ( nv.region[0], nv.region[1], [1,1,1] )
        nv.surface_levels[0] = dmap.surface_levels[0]
        ro = VolumeViewer.volume.Rendering_Options()
        ro.smoothing_factor = .3
        ro.smoothing_iterations = 2
        ro.surface_smoothing = True
        nv.update_surface ( False, ro )
        for sp in nv.surfacePieces :
            v, t = sp.geometry
            if len(v) == 8 and len(t) == 12 :
                sp.display = False
            else :
                if showMesh :
                    sp.color = (0.7, 0.7, 0.7, 1.0)
                    sp.displayStyle = sp.Mesh
                else :
                    sp.color = (0.7, 0.7, 0.7, 0.3)


    def B1_Drag (self, event):
        #print "b1m ", event.x, event.y

        if self.drag == 'seq' :
            d = event.x - self.last_x
            self.seqX += d
            #GetSegMod().seqX = self.seqX
            self.UpdateSeq ()
        elif self.drag == 'mod' :
            d = event.x - self.last_x
            self.modX += d
            #GetSegMod().modX = self.modX
            self.UpdateMod ()
        elif self.drag == 'seqSel' :
            if hasattr ( self, 'seqSel' ):
                seqI = ( event.x - self.seqX ) / self.tw
                if seqI > self.seqSel[0] :
                    self.seqSel[1] = seqI
                elif seqI < self.seqSel[1] :
                    self.seqSel[0] = seqI
                status ( "Sequence selected %d - %d" % (self.seqSel[0]+1, self.seqSel[1]+1) )
                self.UpdateSeqSel ()
        elif self.drag == 'con' :
            x1, y1, x2, y2 = self.Canvas.coords ( self.conLine )
            self.Canvas.coords ( self.conLine, x1, y1, event.x, event.y )
            self.SelectedModClr ( event.x, event.y )
        elif self.drag == "modRot" :
            dx = event.x - self.dragStartX
            self.dragStartX = event.x
            self.dragMod.Rotate ( dx )



        self.last_x = event.x
        self.last_y = event.y


    def B2_Down (self, event):
        print "b2 - down"



    
    def B2_Up (self, event):
        print "b2  - up", event.x, event.y
    
        if hasattr ( self, 'selModPiece' ) and self.selModPiece != None :
            
            if self.selModPiece.type == "Loop" :
                self.selModPiece.MakeMod ()
                
            else :
                self.selModPiece.switch = not self.selModPiece.switch
                self.selModPiece.MakeMod ()
                self.UpdateMod ()
    

    def B2_Up_Ctrl (self, event):
        print "b2  - up - control", event.x, event.y
        if hasattr ( self, 'selModPiece' ) and self.selModPiece != None :
            if self.selModPiece.type == "Loop" :
                MakeLoopMod1 ( self.selModPiece )
                #MakeLoopMod ( self.selModPiece )



    def B2_Up_Alt (self, event):
        print "b2  - up - alt", event.x, event.y
        if hasattr ( self, 'selModPiece' ) and self.selModPiece != None :
            if self.selModPiece.type == "Loop" :
                LoopPathOpt ( self.selModPiece, self.refUseMap.get() )
                

    def B2_Up_Shift (self, event):
        print "b2  - up - alt", event.x, event.y
        if hasattr ( self, 'selModPiece' ) and self.selModPiece != None :
            if self.selModPiece.type == "Loop" :
                LoopPathOpt ( self.selModPiece, self.refUseMap.get() )



    def B2_Up_Comm (self, event):
        print "b2  - up - command", event.x, event.y
    



    def B2_Drag (self, event):
        #print "b2m ", event.x, event.y
        pass



    def B3_Down (self, event):

        print "b3 _", event.x, event.y
        


    
    def B3_Up (self, event):
        print "b3 ^", event.x, event.y
        self.B2_Up ( event )


    def B3_Drag (self, event):
        #print "b3m ", event.x, event.y
        pass

    
    def isInSeq ( self, x, y ) :
        if y >= self.seqY and y <= self.seqY + self.seqH :
            return True
        else :
            return False
    
    def isInMod ( self, x, y ) :
        if y >= self.modY and y <= self.modY + self.modH :
            return True
        else :
            return False


    def Mouse_Move (self, event):
        #print "mod m ", event.x, event.y
        #self.Canvas.coords ( self.seqMouseLine, event.x,self.seqY,event.x,self.seqY+self.seqH )

        if self.isInSeq ( event.x, event.y ) and hasattr ( self, 'seq') and len(self.seq) > 0 :

            if hasattr ( self, 'seqRec' ) and hasattr ( self, 'tw' ) and hasattr ( self, 'seqMouseR' ) :
                self.Canvas.itemconfigure ( self.seqRec, state=Tkinter.NORMAL )

                si = ( event.x - self.seqX ) / self.tw
                if si < 0 :
                    si = 0
                if si < len ( self.seq ) :
                    res = self.seqRes [ si ]
                    resEnd = self.seqRes [ len(self.seqRes) - 1 ]
                    status ( "Sequence: %s/%s %d/%d" % ( self.seq[si], res.type, res.id.position, resEnd.id.position ) )
                    y0 = self.seqY+5
                    y1 = self.seqY+self.seqH-5
                    if event.y >= y0 and event.y <= y1 and hasattr ( self, 'seqMouseR' ) :
                        x0 = self.seqX + si * self.tw
                        x1 = x0 + self.tw
                        self.Canvas.coords ( self.seqMouseR, x0, y0, x1, y1 )
                        self.Canvas.itemconfigure ( self.seqMouseR, state=Tkinter.NORMAL )
                    else :
                        self.Canvas.itemconfigure ( self.seqMouseR, state=Tkinter.HIDDEN )

            else :
                self.Canvas.itemconfigure ( self.seqRec, state=Tkinter.HIDDEN )

                if hasattr ( self, 'seqMouseR' ) :
                    self.Canvas.itemconfigure ( self.seqMouseR, state=Tkinter.HIDDEN )


        self.last_x = event.x
        self.last_y = event.y


    def Canvas_Leave ( self, event ) :
        #self.Canvas.coords ( self.seqMouseLine, 0,0,0,0 )
        pass


    def Canvas_Config (self, event) :
        #print "mod cfg ", event.width, event.height
        self.W = event.width
        self.H = event.height

        #self.Canvas.delete("all")
        if 1 :
            if hasattr(self, 'backRec') :
                self.Canvas.coords (self.backRec, 0, 0, self.W, self.H)
            else :
                self.backRec = self.Canvas.create_rectangle(0, 0, self.W, self.H, outline="#eee", fill="#eee")
                #self.seqMouseLine = self.Canvas.create_line(0, 0, 0, 0, fill="#66a")

            if hasattr ( self, 'seqRec' ) :
                self.Canvas.coords ( self.seqRec, 0, self.seqY, self.W, self.seqY+self.seqH )
            else :
                self.seqRec = self.Canvas.create_rectangle(0, self.seqY, self.W, self.seqY+self.seqH, outline="#ddd", fill="#ddd" )

            self.Canvas.tag_lower(self.seqRec)
            self.Canvas.tag_lower(self.backRec)


    def Canvas_Wheel ( self, event ) :

        if self.isInSeq (self.last_x, self.last_y) :
            self.seqX += event.delta * 10
            #GetSegMod().seqX = self.seqX
            self.UpdateSeq ()



    def ZoomMinus ( self ) :
        self.mag = self.mag - 1
        if self.mag > 15 : self.mag = 15
        if self.mag < 2 : self.mag = 2
        #print "w ", event.delta, " mag: ", self.mag

        self.font = tkFont.Font(family='Courier', size=(self.mag), weight='normal')
        #self.boldFont = tkFont.Font(family='Courier', size=(self.mag+4), weight='bold')
        self.tw = self.font.measure ( "a" )

        self.UpdateSeqFont ()
        status ( "Magnification: %d" % self.mag )



    def ZoomPlus ( self ) :
        self.mag = self.mag + 1
        if self.mag > 15 : self.mag = 15
        if self.mag < 2 : self.mag = 2
        #print "w ", event.delta, " mag: ", self.mag

        self.font = tkFont.Font(family='Courier', size=(self.mag), weight='normal')
        #self.boldFont = tkFont.Font(family='Courier', size=(self.mag+4), weight='bold')
        self.tw = self.font.measure ( "a" )

        self.UpdateSeqFont ()
        status ( "Magnification: %d" % self.mag )


    def ZoomBegin ( self ) :        
        self.seqX = 10
        self.UpdateSeq ()

    def ZoomEnd ( self ) :
        self.seqX = - ( len(self.seq) - 50 ) * self.tw
        self.UpdateSeq ()




    def isSelected ( self, fmap ) :
        for sp in fmap.surfacePieces :
            if sp in Surface.selected_surface_pieces() :
                return True
        return False

    
    

def CurMolAndChain () :

    segModDialog = modelz_dialog ()
    if segModDialog != None :
        
        if segModDialog.cur_mol == None :
            segModDialog.cur_mol = chimera.Molecule()
            segModDialog.cur_mol.name = "Model"
            #chimera.openModels.add ( [mol], noprefs = True )
            chimera.openModels.add ( [segModDialog.cur_mol] )
            segModDialog.struc.set ( segModDialog.cur_mol.name )

            try :
                segModDialog.cur_mol.openState.xform = chimera.openModels.list()[0].openState.xform
            except :
                pass
        
        chainId = segModDialog.molChain.get()
        if len(chainId) == 0 :
            chainId = "A"
            segModDialog.molChain.set ( chainId )
        
        return segModDialog.cur_mol, chainId
    
    return None, ""






def SSEs ( allRess ) :

    if len(allRess) < 1 :
        return []

    sses, ss = [], ""

    res, rStart = allRess[0], allRess[0]
    #print "  - at first res / pos: %d " % res.id.position
    if res.isHelix :
        ss = "H"
    elif res.isSheet or res.isStrand :
        ss = "E"
    else :
        ss = "_"

    ress = [ res ]
    lastRes = rStart
    for res in allRess [1:] :

        if res.id.position > lastRes.id.position + 1 :
            print " - gap at", res.id.position
            sses.append ( [rStart.id.position, lastRes.id.position, ss, ress] )
            ress = []
            rStart = res
            if res.isHelix :
                ss = "H"
            elif res.isSheet or res.isStrand :
                ss = "E"
            else :
                ss = "_"

        if res.isHelix :
            if ss != "H" :
                #print "%s -> H - at %d rid %d | %d->%d, %d res" % (ss, i, res.id.position, rStart.id.position, lastRes.id.position, len(ress))
                sses.append ( [rStart.id.position, lastRes.id.position, ss, ress] )
                ress = []
                rStart = res
                ss = "H"
        elif res.isSheet or res.isStrand :
            if ss != "E" :
                #print "%s -> E - at %d rid %d | %d->%d, %d res" % (ss, i, res.id.position, rStart.id.position, lastRes.id.position, len(ress))
                sses.append ( [rStart.id.position, lastRes.id.position, ss, ress] )
                ress = []
                rStart = res
                ss = "E"
        else :
            if ss == "H" or ss == "E" :
                #print "%s -> _ at %d rid %d | %d->%d, %d res" % (ss, i, res.id.position, rStart.id.position, lastRes.id.position, len(ress))
                sses.append ( [rStart.id.position, lastRes.id.position, ss, ress] )
                ress = []
                rStart = res
                ss = "_"

        ress.append ( res )
        lastRes = res

    #print "Done at rid %d - %s | %d->%d, %d res" % ( res.id.position, ss, rStart.id.position, res.id.position, len(ress))
    sses.append ( [rStart.id.position, res.id.position, ss, ress] )
    return sses




def evalSC ( dmap, mol, ress, whichRes ) :

    resolution = 3.0 * dmap.data.step[0]
    umsg ( "Calculating Res-Z-scores - %d res - res %.1f" % (len(ress), resolution) )

    A, A_helix, A_strand, A_loop = [], [], [], []

    #AtomTree (mol)
    for ri, res in enumerate ( ress ) :

        #if res.id.position == 506 :
        #print " %d/%d %s " % (i+1,len(ris), res.type),
        if ri % 100 == 0 :
            umsg ( "Calculating Side Chain Z-scores - res %d/%d" % (ri,len(ress)) )

        #zs = ResRota ( mol, res, resolution, dmap )
        res.scZ = ResRinger ( mol, res, resolution, dmap )
        #res.scZ = ShakeSC ( mol, res, resolution, dmap, whichRes )

        #if res.type == "ILE" :
        #    print res.type, res.zA

        if res.scZ == None :
            pass
            #res.scZ = 0

        else :
            A.append ( res.scZ )
            if res.isHelix :
                A_helix.append ( res.scZ )
            elif res.isSheet or res.isStrand :
                A_strand.append ( res.scZ )
            else :
                A_loop.append ( res.scZ )

    #print ""
        #if i > 10 :
        #    break

    avgA, stdA = numpy.average ( A ), numpy.std ( A )
    umsg ( "Avg side chain Z-score: %.3f" % ( avgA ) )



def evalSSE ( mol, el, resolution, dmap ) :

    startResI, endResI, sseType, ress = el
    #print " : %d-%d, %s, %d res" % (startResI, endResI, sseType, len(ress))

    atoms = []
    for r in ress :
        #atoms.extend ( r.atoms )
        if 'C' in r.atomsMap : atoms.append ( r.atomsMap['C'][0] )
        if 'N' in r.atomsMap : atoms.append ( r.atomsMap['N'][0] )
        if 'CA' in r.atomsMap : atoms.append ( r.atomsMap['CA'][0] )
        if 'O' in r.atomsMap : atoms.append ( r.atomsMap['O'][0] )

    if len(atoms) < 5 :
        return None

    score0 = 0
    scores = []
    T = 1
    trange = [-T*2.0, 0.0, T*2.0]
    #trange = [-T*2.0, -T, 0.0, T, T*2.0]


    for xx in trange :
        for yy in trange :
            for zz in trange :

                v = chimera.Vector(xx,yy,zz)
                xfT = chimera.Xform.translation ( chimera.Vector(xx,yy,zz) )

                molg = MyMolMapX ( mol, atoms, resolution, dmap.data.step[0], xfT )

                fpoints, fpoint_weights = fit_points_g ( molg )
                map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
                olap, corr1, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )

                if numpy.fabs(xx) < .01 and numpy.fabs(yy) < .01 and numpy.fabs(zz) < .01 :
                    score0 = corr1
                else :
                    scores.append ( corr1 )

                #fout.write ( "%.0f,%.0f,%.0f\t%f\n" % (xx,yy,zz, corr1) )
                #nmol, cress = CopyRess ( ress )
                #for nr in cress :
                #    for nat in nr.atoms :
                #        try :
                #            nat.setCoord ( xfT.apply ( nat.coord() ) )
                #        except :
                #            pass
                #chimera.openModels.add ( [nmol] )
                #nmol.name = "T_%.0f_%.0f_%.0f" % (xx,yy,zz)


    if 0 :
        scores.sort ()
        scores.reverse ()

    #print ""
    avg = numpy.average ( scores )  #numpy.average ( scores[1:] )
    stdev = numpy.std ( scores ) #numpy.std ( scores[1:] )
    if stdev < 1e-8 :
        return None
    zscore = (score0 - avg) / stdev #(scores[0] - avg) / stdev
    #print " - scores: avg %.4f, std %.4f, z-score %.4f" % (avg, stdev, zscore )
    #fout.close()
    
    return zscore





def ShakeSC ( mol, r, resolution, dmap, whichRes ) :

    scTest = False
    
    if scTest :
        if r.id.position == 506 :
            print " %d/%d %s " % (r.id.position,len(r.molecule.residues), r.type),
        else :
            return None


    r.CA, r.CB, r.CG = None, None, None
    try :
        r.CA = r.atomsMap["CA"][0]
        r.CB = r.atomsMap["CB"][0]
        r.CG = r.atomsMap["CG"][0]
    except :
        pass


    if r.CA == None or r.CB == None or r.CG == None :
        #print r.type, " - no ats"
        return None


    atoms = []
    for at in r.atoms :
        if at.name == "C" or at.name == 'N' or at.name == 'CA' or at.name == 'O' :
            pass
        else :
            atoms.append ( at )

    if len(atoms) < 1 :
        return None


    resolution = 3.0 * dmap.data.step[0]

    X = r.CB.coord() - r.CA.coord(); X.normalize()
    Y = r.CG.coord() - r.CB.coord(); Y.normalize()

    #Y = chimera.Vector ( X[0], X[1], X[2] + 1.0 ); Y.normalize()
    Z = chimera.cross ( X, Y ); Z.normalize()
    Y = chimera.cross ( Z, X ); Y.normalize()


    fout = None
    if scTest :
        fout = open ( "sc_shake.txt", "w" )


    molg = MyMolMapX ( mol, atoms, resolution, dmap.data.step[0], chimera.Xform.identity() )
    fpoints, fpoint_weights = fit_points_g ( molg )
    map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
    olap, score0, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )
    #print "score0: ", score0
    if scTest :
        fout.write ( "%.0f,%.0f,%.0f\t%f\n" % (0,0,0, score0) )


    scores = []
    p1 = r.CB.coord()

    angs = [-45, 0, 45]
    #angs = [-60, -30, 30, 60]

    for xr in angs : # range ( -180, 180, 15 ) :

        for yr in angs : # range ( -180, 180, 15 ) :
            #yr = 0

            if numpy.abs(xr) < 0.1 and numpy.abs(yr) < 0.1 :
                continue

            xf = chimera.Xform.translation ( p1.toVector() )
            xf.multiply ( chimera.Xform.rotation ( X, xr ) )
            xf.multiply ( chimera.Xform.rotation ( Z, yr ) )
            xf.multiply ( chimera.Xform.translation ( p1.toVector() * -1.0 ) )
        
            molg = MyMolMapX ( mol, atoms, resolution, dmap.data.step[0], xf )
            fpoints, fpoint_weights = fit_points_g ( molg )
            #xfMol = mol.openState.xform
            #xfMol.premultiply ( xf.inverse() )
            #transform_vertices ( fpoints, Matrix.xform_matrix( xf.inverse() ) )
    
            map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
            olap, corr1, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )
            scores.append ( corr1 )
    
            #transform_vertices ( fpoints, Matrix.xform_matrix( xf ) )
    
            if scTest :
                fout.write ( "%.0f,%.0f,%.0f\t%f\n" % (xr,yr,0, corr1) )
                nmol, cress = CopyRess ( [r] )
                for nr in cress :
                    for at in nr.atoms :
                        try :
                            at.setCoord ( xf.apply ( at.coord() ) )
                        except :
                            pass
                chimera.openModels.add ( [nmol] )
                for at in nmol.atoms :
                    if at.name == "C" or at.name == 'N' or at.name == 'CA' or at.name == 'O' :
                        at.display = False
                        #at.setCoord ( xfT.apply ( nr.atomsMap['CA'][0].coord() ) )
                nmol.name = "SC_%.0f_%.0f" % (xr,yr)

    if 0 :
        for yr in angs :
    
            xf = chimera.Xform.translation ( p1.toVector() )
            xf.multiply ( chimera.Xform.rotation ( Y, yr ) )
            xf.multiply ( chimera.Xform.translation ( p1.toVector() * -1.0 ) )
        
            molg = MyMolMapX ( mol, atoms, resolution, dmap.data.step[0], xf )
    
            fpoints, fpoint_weights = fit_points_g ( molg )
            map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
            olap, corr1, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )
            scores.append ( corr1 )
    
            if scTest :
                fout.write ( "%.0f,%.0f,%.0f\t%f\n" % (yr,0,0, corr1) )
                nmol, cress = CopyRess ( [r] )
                for nr in cress :
                    for at in nr.atoms :
                        try :
                            at.setCoord ( xf.apply ( at.coord() ) )
                        except :
                            pass
                chimera.openModels.add ( [nmol] )
                for at in nmol.atoms :
                    if at.name == "C" or at.name == 'N' or at.name == 'CA' or at.name == 'O' :
                        at.display = False
                        #at.setCoord ( xfT.apply ( nr.atomsMap['CA'][0].coord() ) )
                nmol.name = "SC_Y_%.0f" % (yr)

    if 0 :
        for zr in angs :

            xf = chimera.Xform.translation ( p1.toVector() )
            xf.multiply ( chimera.Xform.rotation ( Z, zr ) )
            xf.multiply ( chimera.Xform.translation ( p1.toVector() * -1.0 ) )

            molg = MyMolMapX ( mol, atoms, resolution, dmap.data.step[0], xf )

            fpoints, fpoint_weights = fit_points_g ( molg )
            map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
            olap, corr1, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )
            scores.append ( corr1 )

            if scTest :
                fout.write ( "%.0f,%.0f,%.0f\t%f\n" % (zr,0,0, corr1) )
                nmol, cress = CopyRess ( [r] )
                for nr in cress :
                    for at in nr.atoms :
                        try :
                            at.setCoord ( xf.apply ( at.coord() ) )
                        except :
                            pass
                chimera.openModels.add ( [nmol] )
                for at in nmol.atoms :
                    if at.name == "C" or at.name == 'N' or at.name == 'CA' or at.name == 'O' :
                        at.display = False
                        #at.setCoord ( xfT.apply ( nr.atomsMap['CA'][0].coord() ) )
                nmol.name = "SC_Z_%.0f" % (zr)
    

    if 0 :
        scores.sort ()
        scores.reverse ()

    #print ""
    avg = numpy.average ( scores )  #numpy.average ( scores[1:] )
    stdev = numpy.std ( scores ) #numpy.std ( scores[1:] )
    if stdev < 1e-7 :
        return None
    zscore = (score0 - avg) / stdev #(scores[0] - avg) / stdev

    if scTest :
        print " - scores: avg %.4f, std %.4f, z-score %.4f" % (avg, stdev, zscore )
        fout.close ()
    
    
    return zscore





def ResRinger ( mol, r, resolution, dmap ) :

    r.CA, r.CB, r.CG = None, None, None
    try :
        r.CA = r.atomsMap["CA"][0]
        r.CB = r.atomsMap["CB"][0]
    except :
        pass

    if "CG" in r.atomsMap :
        r.CG = r.atomsMap["CG"][0]
    elif "CG1" in r.atomsMap :
        r.CG = r.atomsMap["CG1"][0]
    elif "CG2" in r.atomsMap :
        r.CG = r.atomsMap["CG2"][0]
    elif "OG" in r.atomsMap :
        r.CG = r.atomsMap["OG"][0]

    if r.CA == None or r.CB == None or r.CG == None :
        #print r.type, " - no ats"
        return None

    resolution = 3.0 * dmap.data.step[0]

    scores1, scores2 = [], []

    molg = MyMolMap ( mol, r.atoms, resolution, dmap.data.step[0] )
    fpoints, fpoint_weights = fit_points_g ( molg )
    map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
    olap_0, corr1_0, corr2_0 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )

    for at in r.atoms :
        at.p0 = at.coord()

    rats = []
    for at in r.atoms :
        if at.name == 'C' or at.name == 'N' or at.name == 'O' :  # or at.name == 'CB' or at.name == 'CA'
            continue
        rats.append ( at )

    #print ""

    #for ri, rmol in enumerate ( rmols[0:10] ) :
    for deg in range (0, 360, 36) :

        #nmol, cress = CopyRess ( [r] )
        #chimera.openModels.add ( [nmol] )
        #nmol.name = "ringer CA %d %.0f" % (r.id.position, deg)
        #r = nmol.residues[0]

        RotAts ( rats, r.CA, r.CB, deg )
        corr = ResCC ( mol, rats, resolution, dmap )
        scores1.append ( corr )

        for at in rats :
            at.setCoord ( at.p0 )
    
    zscore1 = None
    if len(scores1) > 3 :
        avg = numpy.average ( scores1[1:] )
        stdev = numpy.std ( scores1[1:] )
        zscore1 = ( (scores1[0] - avg) / stdev ) if stdev > 1e-5 else 0
        #print " -1- avg %.4f, std %.4f, z-score %.4f" % (avg, stdev, zscore1 )

    
    #for sc in scores1 :
    #    print "%f" % sc
    #print ""
    
    if 0 :
        if r.CG == None or len(rats) < 2 :
            return (zscore1,0)
    
        for deg2 in range (0, 360, 36) :
            #nmol, cress = CopyRess ( [r] )
            #chimera.openModels.add ( [nmol] )
            #nmol.name = "ringer CB %d %.0f" % (r.id.position, deg)
            #nres2 = nmol.residues[0]
            #RotAts ( nres2.atoms, nres2.atomsMap['CB'][0], nres2.atomsMap['CG'][0], deg2 )
            #corr = ResCC ( nmol, nres2.atoms, resolution, dmap )
    
            RotAts ( rats, r.CB, r.CG, deg2 )
            corr = ResCC ( mol, rats, resolution, dmap )
    
            scores2.append ( corr )
        
            for at in rats :
                at.setCoord ( at.p0 )
                    
    
        zscore2 = 0
        if len(scores2) > 3 :
            avg = numpy.average ( scores2[1:] )
            stdev = numpy.std ( scores2[1:] )
            zscore2 = (scores2[0] - avg) / stdev if stdev > 1e-5 else 0
            #print " -2- avg %.4f, std %.4f, z-score %.4f" % (avg, stdev, zscore2 )

    return zscore1



def CopyRess ( res ) :

    nmol = chimera.Molecule()
    ress = [None] * len ( res )

    aMap = dict()
    for ri, r in enumerate ( res ) :
        nres = nmol.newResidue (r.type, chimera.MolResId(r.id.chainId, r.id.position))
        ress[ri] = nres
        for at in r.atoms :
            nat = nmol.newAtom (at.name, chimera.Element(at.element.number))
            aMap[at] = nat
            nres.addAtom( nat )
            nat.setCoord ( at.coord() )
            if at.name == "C" or at.name == 'CA' or at.name == 'O' or at.name == "N" :
                at.display = False
            
    for bond in res[0].molecule.bonds :
        try :
            nb = nmol.newBond ( aMap[bond.atoms[0]], aMap[bond.atoms[1]] )
            nb.display = nb.Smart
        except :
            pass
        
    for r in ress :
        r.CA, r.CB, r.CG = None, None, None
        try :
            r.CA = r.atomsMap["CA"][0]
            r.CB = r.atomsMap["CB"][0]
            r.CG = r.atomsMap["CG"][0]
        except :
            pass
    
    #SetBBAts ( ress )
    return nmol, ress



def RotAts (rats, a1, a2, deg) :
    
    # phi: N -> CA
    p1, p2 = a1.coord(), a2.coord()
    v = p2 - p1; v.normalize()

    xf = chimera.Xform.translation ( p1.toVector() )
    xf.multiply ( chimera.Xform.rotation ( v, deg ) )
    xf.multiply ( chimera.Xform.translation ( p1.toVector() * -1.0 ) )

    #for at in res.atoms :
    #    if at.name != 'C' and at.name != 'CA' and at.name != 'N' and at.name != 'CB' and at.name != 'O' :
    for at in rats :
            at.setCoord ( xf.apply (at.coord()) )
            




def molecule_grid_dataX (m0, atoms, resolution, step, pad, xfT, cutoff_range, sigma_factor, transforms = [], csys = None):

    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms, transformed = True)

    # Transform coordinates to local coordinates of the molecule containing
    # the first atom.  This handles multiple unaligned molecules.
    # Or if on_grid is specified transform to grid coordinates.
    #m0 = atoms[0].molecule
    xf = m0.openState.xform
    xf.multiply ( xfT )
    import Matrix as M
    M.transform_points(xyz, M.xform_matrix(xf.inverse()))
    if csys:
        xf.premultiply(csys.xform.inverse())
    tflist = M.coordinate_transform_list(transforms, M.xform_matrix(xf))

    anum = [a.element.number for a in atoms]

    molecules = set([a.molecule for a in atoms])
    if len(molecules) > 1:
        name = 'molmap res %.3g' % (resolution,)
    else:
        name = 'molmap %s res %.3g' % (m0.name, resolution)

    grid = bounding_grid(xyz, step, pad, tflist)
    grid.name = name

    sdev = resolution * sigma_factor
    add_gaussians(grid, xyz, anum, sdev, cutoff_range, tflist)

    #return grid, molecules
    return grid
        

def MyMolMapX ( m0, atoms, resolution, step, xf ) :

    #from MoleculeMap import molecule_grid_data
    from math import sqrt, pi
    from chimera import openModels as om
    from VolumeViewer import volume_from_grid_data

    atoms = tuple(atoms)

    pad = 3*resolution
    cutoff_range = 5 # in standard deviations
    sigma_factor = 1/(pi*sqrt(2)) # standard deviation / resolution
    transforms,csys = [], None
    display_threshold = 0.95
    
    return molecule_grid_dataX (m0, atoms, resolution, step, pad, xf, cutoff_range, sigma_factor, transforms, csys)



def MyMolMap ( m0, atoms, resolution, step ) :

    #from MoleculeMap import molecule_grid_data
    from math import sqrt, pi
    from chimera import openModels as om
    from VolumeViewer import volume_from_grid_data

    atoms = tuple(atoms)

    pad = 3*resolution
    cutoff_range = 5 # in standard deviations
    sigma_factor = 1/(pi*sqrt(2)) # standard deviation / resolution
    transforms,csys = [], None
    display_threshold = 0.95
    
    return molecule_grid_data(m0, atoms, resolution, step, pad, None, cutoff_range, sigma_factor, transforms, csys)




def molecule_grid_data(m0, atoms, resolution, step, pad, on_grid,
                       cutoff_range, sigma_factor,
                       transforms = [], csys = None):



    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms, transformed = True)

    # Transform coordinates to local coordinates of the molecule containing
    # the first atom.  This handles multiple unaligned molecules.
    # Or if on_grid is specified transform to grid coordinates.
    #m0 = atoms[0].molecule
    xf = on_grid.openState.xform if on_grid else m0.openState.xform
    import Matrix as M
    M.transform_points(xyz, M.xform_matrix(xf.inverse()))
    if csys:
        xf.premultiply(csys.xform.inverse())
    tflist = M.coordinate_transform_list(transforms, M.xform_matrix(xf))

    anum = [a.element.number for a in atoms]

    molecules = set([a.molecule for a in atoms])
    if len(molecules) > 1:
        name = 'molmap res %.3g' % (resolution,)
    else:
        name = 'molmap %s res %.3g' % (m0.name, resolution)

    if on_grid:
        from numpy import float32
        grid = on_grid.region_grid(on_grid.region, float32)
    else:
        grid = bounding_grid(xyz, step, pad, tflist)
    grid.name = name

    sdev = resolution * sigma_factor
    add_gaussians(grid, xyz, anum, sdev, cutoff_range, tflist)

    #return grid, molecules
    return grid




def ResCC ( mol, rats, resolution, dmap ) :

    molg = MyMolMap ( mol, rats, resolution, dmap.data.step[0] )
    
    #if 0 :
    #    fmap = VolumeViewer.volume.volume_from_grid_data ( molg )
    #    fmap.name = "res molmap!"
    #    fpoints, fpoint_weights = fit_points(fmap, False)
    #    map_values = dmap.interpolated_values ( fpoints, fmap.openState.xform )
    #    olap, corr1, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )
    #    scores.append ( corr1 )
    #    chimera.openModels.close ( [fmap] )
    #else :

    fpoints, fpoint_weights = fit_points_g ( molg )
    map_values = dmap.interpolated_values ( fpoints, mol.openState.xform )
    olap, corr1, corr2 = FitMap.overlap_and_correlation ( fpoint_weights, map_values )
    return corr1



def fit_points_g (fdata, threshold = 1e-5):

    mat = fdata.full_matrix()

    import _volume
    points = _volume.high_indices(mat, threshold)
    fpoints = points.astype(numpy.single)
    fpoint_weights = mat[points[:,2],points[:,1],points[:,0]]

    nz = numpy.nonzero( fpoint_weights )[0]
    if len(nz) < len (fpoint_weights) :
        fpoints = numpy.take( fpoints, nz, axis=0 )
        fpoint_weights = numpy.take(fpoint_weights, nz, axis=0)

    transform_vertices( fpoints, fdata.ijk_to_xyz_transform )

    if 0 : print "FitPoints from %s with threshold %.4f, %d nonzero" % (
        fmap.name, threshold, len(nz) )

    return fpoints, fpoint_weights






# -----------------------------------------------------------------------------
#
def bounding_grid(xyz, step, pad, transforms):

    xyz_min, xyz_max = point_bounds(xyz, transforms)
    origin = [x-pad for x in xyz_min]
    from math import ceil
    shape = [int(ceil((xyz_max[a] - xyz_min[a] + 2*pad) / step)) for a in (2,1,0)]
    from numpy import zeros, float32
    matrix = zeros(shape, float32)
    from VolumeData import Array_Grid_Data
    grid = Array_Grid_Data(matrix, origin, (step,step,step))
    return grid


# -----------------------------------------------------------------------------
#
def add_gaussians(grid, xyz, weights, sdev, cutoff_range, transforms = []):

    from numpy import zeros, float32, empty
    sdevs = zeros((len(xyz),3), float32)
    for a in (0,1,2):
        sdevs[:,a] = sdev / grid.step[a]

    import Matrix as M
    if len(transforms) == 0:
        transforms = [M.identity_matrix()]
    from _gaussian import sum_of_gaussians
    ijk = empty(xyz.shape, float32)
    matrix = grid.matrix()
    for tf in transforms:
        ijk[:] = xyz
        M.transform_points(ijk, M.multiply_matrices(grid.xyz_to_ijk_transform, tf))
        sum_of_gaussians(ijk, weights, sdevs, cutoff_range, matrix)

    from math import pow, pi
    normalization = pow(2*pi,-1.5)*pow(sdev,-3)
    matrix *= normalization



# -----------------------------------------------------------------------------
#
def point_bounds(xyz, transforms = []):

    from _multiscale import bounding_box
    if transforms :
        from numpy import empty, float32
        xyz0 = empty((len(transforms),3), float32)
        xyz1 = empty((len(transforms),3), float32)
        txyz = empty(xyz.shape, float32)
        import Matrix as M
        for i, tf in enumerate(transforms) :
            txyz[:] = xyz
            M.transform_points(txyz, tf)
            xyz0[i,:], xyz1[i,:] = bounding_box(txyz)
        xyz_min, xyz_max = xyz0.min(axis = 0), xyz1.max(axis = 0)
    else:
        xyz_min, xyz_max = bounding_box(xyz)

    return xyz_min, xyz_max
    





# ---------------------------------------------------

def modelz_dialog ( create=False ) :

    from chimera import dialogs
    d = dialogs.find ( "modelz", create=False )
    return d



def close_dialog () :

    from chimera import dialogs



def show_dialog () :

    from chimera import dialogs

    d = dialogs.find ( "modelz", create=False )
    if d :
        print " - found old diag"
        d.toplevel_widget.update_idletasks ()
        d.Close()
        d.toplevel_widget.update_idletasks ()

    dialogs.register (ModelZ_Dialog.name, ModelZ_Dialog, replace = True)

    d = dialogs.find ( "modelz", create=True )
    # Avoid transient dialog resizing when created and mapped for first time.
    d.toplevel_widget.update_idletasks ()
    d.enter()

    return d



def GetMod ( name ) :
    for m in chimera.openModels.list() :
        if m.name == name :
            return m
    return None


#def GetVisibleMol () :
#    for m in chimera.openModels.list() :
#        if m.display == True and type(m) == chimera.Molecule :
#            return m
#    return None















