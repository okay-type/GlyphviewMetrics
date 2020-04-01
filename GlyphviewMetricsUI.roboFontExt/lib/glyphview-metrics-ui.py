from AppKit import NSApp, NSColor, NSTextAlignmentCenter, NSTextAlignmentRight, NSTextAlignmentLeft
from vanilla import Window, Button, EditText, Group
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup
from mojo.UI import CurrentWindow, CurrentGlyphWindow, getGlyphViewDisplaySettings
from mojo.drawingTools import rect, fill
import re
import time

# setup
debug = False

# sizes
height = 16
width = height*4/3
s = height*3
margin = 5
unit = 5
gap = 3
dfltLwidth = dfltRwidth = dfltCwidth = width*7

# buttons
buttstyle = 11
iconminus = '➖'
iconplus = '➕'
iconround = '▞'
iconcenter = '↔︎'
iconcopyR = '→'
iconcopyL = '←'

# window view manager
windowViewManger = {}
lll = {}
ccc = {}
rrr = {}

class GlyphMetricsUI(object):

    def __init__(self):
        # debug
        windowname = 'Debug Glyph Metrics UI'
        windows = [w for w in NSApp().orderedWindows() if w.isVisible()]
        for window in windows:
            print(window.title())
            if window.title() == windowname:
                window.close()
        if debug == True:
            self.debug = Window((333, 33), windowname)
            self.debug.bind('close', self.windowSideuiClose)
            self.debug.open()
        # setup
        self.showButtons = False
        self.sbui = None
        # add interface
        addObserver(self, 'addInterface', 'glyphWindowWillOpen')
        addObserver(self, 'updateSelfWindow', 'currentGlyphChanged')
        # toggle visibility of tool ui
        addObserver(self, 'showSideUIonDraw', 'draw')
        addObserver(self, 'hideSideUIonPreview', 'drawPreview')
        # remove UI and window manager when glyph window closes
        # addObserver(self, "observerGlyphWindowWillClose", "glyphWindowWillClose")
        # subscribe to glyph changes
        addObserver(self, "viewDidChangeGlyph", "viewDidChangeGlyph")


    # def observerGlyphWindowWillClose(self, notification):
    #     self.window = notification['window']
    #     self.cleanup(self.window)
    #     del windowViewManger[notification['window']]
    #     del lll[notification['window']]
    #     del ccc[notification['window']]
    #     del rrr[notification['window']]


    def windowSideuiClose(self, sender):
        self.window.removeGlyphEditorSubview(self.sbui)
        removeObserver(self, 'glyphWindowWillOpen')
        removeObserver(self, 'glyphWindowWillClose')
        removeObserver(self, 'glyphWindowWillClose')
        removeObserver(self, 'currentGlyphChanged')
        removeObserver(self, 'draw')
        removeObserver(self, 'drawPreview')
        removeObserver(self, 'viewDidChangeGlyph')


    def cleanup(self, w):
        try:
            w.removeGlyphEditorSubview(self.sbui)
        except:
            return


    def addInterface(self, notification):
        self.window = notification['window']
        # self.cleanup(self.window)


        # CONTAINER
        xywh = (margin, -55, -margin, height)
        self.sbui = CanvasGroup(xywh, delegate=CanvasStuff(self.window))

        # LEFT
        x, y, w, h = xywh = (0, -height, dfltLwidth, height) 
        this = self.sbui.L = Group(xywh)

        # text input
        xywh = (x, y+3, width*1.5, height*.75)
        this.Ltext = EditText(xywh, placeholder='angledLeftMargin', sizeStyle='mini', continuous=False, callback=self.setSB)
        # quick mod buttons
        xywh = (x+width*1.5+(gap*1), y, width, height)
        this.Lminus = Button(xywh, iconminus, sizeStyle='mini', callback=self.setLminus)
        this.Lminus.getNSButton().setToolTip_('Adjust LSB -'+str(unit))
        xywh = (x+width*2.5+(gap*2), y, width, height)
        this.Lplus = Button(xywh, iconplus, sizeStyle='mini', callback=self.setLplus)
        this.Lplus.getNSButton().setToolTip_('Adjust LSB +'+str(unit))
        xywh = (x+width*3.5+(gap*3), y, width, height)
        this.Lround = Button(xywh, iconround, sizeStyle='mini', callback=self.setLround)
        this.Lround.getNSButton().setToolTip_('Round LSB to '+str(unit))
        xywh = (x+width*4.5+(gap*4), y, width, height)
        this.Lright = Button(xywh, iconcopyR, sizeStyle='mini', callback=self.setLright)
        this.Lright.getNSButton().setToolTip_('Copy Right Value')
        # stylize
        this.Ltext.getNSTextField().setBezeled_(False)
        this.Ltext.getNSTextField().setBackgroundColor_(NSColor.clearColor())
        self.flatButt(this.Lminus)
        self.flatButt(this.Lplus)
        self.flatButt(this.Lround)
        self.flatButt(this.Lright)

        # RIGHT
        x, y, w, h = xywh = (-dfltRwidth, y, dfltRwidth, h)
        this = self.sbui.R = Group(xywh)
        # text input
        xywh = (-x-width*1.5, y+3, width*1.5, height*.75)
        this.Rtext = EditText(xywh, placeholder='angledRightMargin', sizeStyle='mini', continuous=False, callback=self.setSB)
        # quick mod buttons
        xywh = (-x-width*5.5-(gap*4), y, width, height)
        this.Rleft = Button(xywh, iconcopyL, sizeStyle='mini', callback=self.setRleft)
        this.Rleft.getNSButton().setToolTip_('Copy Left Value')
        xywh = (-x-width*4.5-(gap*3), y, width, height)
        this.Rround = Button(xywh, iconround, sizeStyle='mini', callback=self.setRround)
        this.Rround.getNSButton().setToolTip_('Round RSB to '+str(unit))
        xywh = (-x-width*3.5-(gap*2), y, width, height)
        this.Rminus = Button(xywh, iconminus, sizeStyle='mini', callback=self.setRminus)
        this.Rminus.getNSButton().setToolTip_('Adjust RSB -'+str(unit))
        xywh = (-x-width*2.5-(gap*1), y, width, height)
        this.Rplus = Button(xywh, iconplus, sizeStyle='mini', callback=self.setRplus)
        this.Rplus.getNSButton().setToolTip_('Adjust RSB +'+str(unit))
        # stylize
        this.Rtext.getNSTextField().setBezeled_(False)
        this.Rtext.getNSTextField().setBackgroundColor_(NSColor.clearColor())
        this.Rtext.getNSTextField().setAlignment_(NSTextAlignmentRight)
        self.flatButt(this.Rminus)
        self.flatButt(this.Rplus)
        self.flatButt(this.Rround)
        self.flatButt(this.Rleft)

        # CENTER
        winX, winY, winW, winH = self.window.getVisibleRect()
        winW = winW - margin*5
        x, y, w, h = xywh = ((winW/2)-(dfltCwidth/2), y, dfltCwidth, h)
        this = self.sbui.C = Group(xywh)
        x = 0

        # text input
        c = (dfltCwidth/2)
        xywh = (c-(width*.75), y+3, width*1.5, height*.75)
        this.Ctext = EditText(xywh, placeholder='width', sizeStyle='mini', continuous=False, callback=self.setSB)
        # quick mod buttons
        xywh = (c-(width*.75)-width*2-(gap*2), y, width, height)
        this.Ccenter = Button(xywh, iconcenter, sizeStyle='mini', callback=self.setCcenter)
        this.Ccenter.getNSButton().setToolTip_('Center on Width')
        xywh = (c-(width*.75)-width-(gap*1), y, width, height)
        this.Cround = Button(xywh, iconround, sizeStyle='mini', callback=self.setCround)
        this.Cround.getNSButton().setToolTip_('Round Width to '+str(unit))
        xywh = (c+(width*.75)+(gap*1), y, width, height)
        this.Cminus = Button(xywh, iconminus, sizeStyle='mini', callback=self.setCminus)
        this.Cminus.getNSButton().setToolTip_('Adjust Width -'+str(2*unit))
        xywh = (c+(width*.75)+width+(gap*2), y, width, height)
        this.Cplus = Button(xywh, iconplus, sizeStyle='mini', callback=self.setCplus)
        this.Cplus.getNSButton().setToolTip_('Adjust Width +'+str(2*unit))
        # stylize
        this.Ctext.getNSTextField().setBezeled_(False)
        this.Ctext.getNSTextField().setBackgroundColor_(NSColor.clearColor())
        this.Ctext.getNSTextField().setAlignment_(NSTextAlignmentCenter)
        self.flatButt(this.Cminus)
        self.flatButt(this.Cplus)
        self.flatButt(this.Cround)
        self.flatButt(this.Ccenter)

        # hide
        self.sbui.L.Lminus.show(False)
        self.sbui.L.Lround.show(False)
        self.sbui.L.Lplus.show(False)
        self.sbui.L.Lright.show(False)
        self.sbui.R.Rminus.show(False)
        self.sbui.R.Rround.show(False)
        self.sbui.R.Rplus.show(False)
        self.sbui.R.Rleft.show(False)
        self.sbui.C.Cminus.show(False)
        self.sbui.C.Cround.show(False)
        self.sbui.C.Ccenter.show(False)
        self.sbui.C.Cplus .show(False)

        # make it real
        self.sbWatcherInitialize()
        self.window.addGlyphEditorSubview(self.sbui)
        self.updateValues()
        self.buildMatchBase()
        windowViewManger[self.window] = self.sbui


    def updateSelfWindow(self, notification):
        self.window = CurrentGlyphWindow()
        self.buildMatchBase()
        self.updateValues()


    def showSideUIonDraw(self, notification):
        self.sbWatcher()
        sbui = windowViewManger.get(self.window)
        if sbui is not None:
            sbui.show(True)


    def hideSideUIonPreview(self, notification):
        sbui = windowViewManger.get(self.window)
        if sbui is not None:
            sbui.show(False)


    def updateValues(self, notification=None):
        try:
            g = self.window.getGlyph()
            f = g.font
            sbui = windowViewManger.get(self.window)
            sbui.L.Ltext.set(str(g.angledLeftMargin))
            sbui.R.Rtext.set(str(g.angledRightMargin))
            sbui.C.Ctext.set(str(g.width))
        except Exception as e: 
            # if debug == True:
            #     print('Exception updateValues', e)
            return


    # hack sidebearings changed observer 
    # used when things redraw
    def sbWatcherInitialize(self):
        g = self.window.getGlyph()
        f = g.font
        if g is not None:
            lll[self.window] = g.angledLeftMargin
            ccc[self.window] = g.width
            rrr[self.window] = g.angledRightMargin

    def sbWatcher(self):
        g = CurrentGlyph()
        if g is not None:
            f = g.font
            if lll[self.window] != None and ccc[self.window] != None and rrr[self.window] != None:
                if lll[self.window] != g.angledLeftMargin or ccc[self.window] != g.width or rrr[self.window] != g.angledRightMargin:
                    lll[self.window] = g.angledLeftMargin
                    ccc[self.window] = g.width
                    rrr[self.window] = g.angledRightMargin
                    self.updateValues()
                    self.buildMatchBase()



    def setSB(self, sender):
        changeAttribute = sender.getPlaceholder()
        g = self.window.getGlyph()
        f = g.font
        v = sender.get()
        if is_number(v):
            if debug == True:
                print('value is a number')
            g.prepareUndo('Change '+changeAttribute+' SB')
            setattr(g, changeAttribute, float(v))
            g.performUndo()
            self.updateValues()
        elif v in f:
            if debug == True:
                print('value is a glyph')
            g.prepareUndo('Change '+changeAttribute+' SB')
            sb = getattr(f[v], changeAttribute)
            setattr(g, changeAttribute, sb)
            g.performUndo()
            self.updateValues()
        else:
            if debug == True:
                print('value is not a number or a glyph')
            return

    def setLminus(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('➖ Left SB')
        g.angledLeftMargin += -1*unit
        g.performUndo()
        self.updateValues()


    def setLround(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Round Left SB')
        g.angledLeftMargin = int(unit * round(float(g.angledLeftMargin)/unit))
        g.performUndo()
        self.updateValues()


    def setLplus(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('➕ Left SB')
        g.angledLeftMargin += unit
        g.performUndo()
        self.updateValues()


    def setLright(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Copy Right SB')
        g.angledLeftMargin = g.angledRightMargin
        g.performUndo()
        self.updateValues()


    def setLmatch(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Match Left SB')
        f = g.font
        gmatch = sender.getTitle()
        if f[gmatch] is not None:
            g.angledLeftMargin = f[gmatch].angledLeftMargin
        g.performUndo()
        self.updateValues()


    def setRminus(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('➖ Right SB')
        g.angledRightMargin += -1*unit
        g.performUndo()
        self.updateValues()


    def setRround(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Round Right SB')
        g.angledRightMargin = int(unit * round(float(g.angledRightMargin)/unit))
        g.performUndo()
        self.updateValues()


    def setRplus(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('➕ Right SB')
        g.angledRightMargin += unit
        g.performUndo()
        self.updateValues()


    def setRmatch(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Match Right SB')
        gmatch = sender.getTitle()
        f = g.font
        if f[gmatch] is not None:
            g.angledRightMargin = f[gmatch].angledRightMargin
        g.performUndo()
        self.updateValues()

    def setRleft(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Copy Left SB')
        g.angledRightMargin = g.angledLeftMargin
        g.performUndo()
        self.updateValues()


    def setCminus(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('➖ Width')
        # use whole units, not floats
        oldwidth = g.width
        leftby = unit
        g.angledLeftMargin += -1*leftby
        g.width = oldwidth - unit*2
        g.performUndo()
        self.updateValues()


    def setCround(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Round Width')
        g.width = int(unit * round(float(g.width)/unit))
        g.performUndo()
        self.updateValues()


    def setCcenter(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Center on Width')
        # use whole units, not floats
        padding = g.angledLeftMargin + g.angledRightMargin
        gwidth = g.width
        g.angledLeftMargin = int(padding/2)
        g.width = gwidth
        g.performUndo()
        self.updateValues()


    def setCplus(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('➕ Width')
        # use whole units, not floats
        oldwidth = g.width
        leftby = unit
        g.angledLeftMargin += leftby
        g.width = oldwidth + unit*2
        g.performUndo()
        self.updateValues()


    def setCmatch(self, sender):
        g = self.window.getGlyph()
        if g is None:
            return
        g.prepareUndo('Match Width')
        f = g.font
        gmatch = sender.getTitle()
        if f[gmatch] is not None:
            g.width = f[gmatch].width
        g.performUndo()
        self.updateValues()


    def flatButt(self, this, match=False):
        this = this.getNSButton()
        this.setBezelStyle_(buttstyle)
        this.setBordered_(False)
        this.setWantsLayer_(True)
        this.setBackgroundColor_(NSColor.whiteColor())
        if match == True:      
            this.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(.9, 1, .85, 1))


    def buildMatchBase(self, notification=None):
        self.newheight = height
        try:
            g = self.window.getGlyph()
            f = g.font
            # remove old buttons
            for i in range(10):
                if hasattr(self.sbui.L, 'buttobj_%s' % i):
                    delattr(self.sbui.L, 'buttobj_%s' % i)
                    delattr(self.sbui.R, 'buttobj_%s' % i)
                    delattr(self.sbui.C, 'buttobj_%s' % i)

            # add button for each component
            self.uniquecomponents = []
            for c in g.components:
                if c.baseGlyph not in self.uniquecomponents:
                    self.uniquecomponents.append(c.baseGlyph)

            for i, c in enumerate(self.uniquecomponents):
                row = i+1
                yy = -height*(row+1)-3

                xywh = (0, yy, width*5.5+(gap*4), height)
                buttobj = Button(xywh, c, sizeStyle='mini', callback=self.setLmatch)
                setattr(self.sbui.L, 'buttobj_%s' % i, buttobj)
                this = getattr(self.sbui.L, 'buttobj_%s' % i)
                this.getNSButton().setAlignment_(NSTextAlignmentLeft)
                this.getNSButton().setToolTip_('Match LSB of '+c)

                xywh = (-width*5.5-(gap*4), yy, width*5.5+(gap*4), height)
                buttobj = Button(xywh, c, sizeStyle='mini', callback=self.setRmatch)
                setattr(self.sbui.R, 'buttobj_%s' % i, buttobj)
                this = getattr(self.sbui.R, 'buttobj_%s' % i)
                this.getNSButton().setAlignment_(NSTextAlignmentRight)
                this.getNSButton().setToolTip_('Match RSB of '+c)

                xywh = ((dfltLwidth/2)-(width*2.75+(gap*2)), yy, width*5.5+(gap*4), height)
                buttobj = Button(xywh, c, sizeStyle='mini', callback=self.setCmatch)
                setattr(self.sbui.C, 'buttobj_%s' % i, buttobj)
                this = getattr(self.sbui.C, 'buttobj_%s' % i)
                this.getNSButton().setToolTip_('Match Width of '+c)


            for i, c in enumerate(self.uniquecomponents):
                try:
                    this = getattr(self.sbui.L, 'buttobj_%s' % i)
                    # hide if hidden
                    if self.showButtons == False:
                        this.show(False)
                    # check if metrics match base glyphs
                    if int(f[c].angledLeftMargin) == int(g.angledLeftMargin):
                        self.flatButt(this, True)
                    else:
                        self.flatButt(this)

                    this = getattr(self.sbui.R, 'buttobj_%s' % i)
                    if self.showButtons == False:
                        this.show(False)
                    if int(f[c].angledRightMargin) == int(g.angledRightMargin):
                        self.flatButt(this, True)
                    else:
                        self.flatButt(this)
                    
                    this = getattr(self.sbui.C, 'buttobj_%s' % i)
                    if self.showButtons == False:
                        this.show(False)
                    if f[c].width == g.width:
                        self.flatButt(this, True)
                    else:
                        self.flatButt(this)

                except Exception as e: 
                    return

            # change height of canvas to fit buttons
            self.newheight = height*(len(self.uniquecomponents)+2)
            newy = -55-height*(len(self.uniquecomponents))
            self.sbui.setPosSize((margin, newy, -margin, self.newheight))
            self.sbui.L.setPosSize((0, 0, dfltLwidth, self.newheight))
            self.sbui.R.setPosSize((-dfltRwidth, 0, dfltRwidth, self.newheight))
            winX, winY, winW, winH = self.window.getVisibleRect()
            winW = winW - margin*5
            offsetcenter = (winW/2)-(width*2.25)
            self.sbui.C.setPosSize((offsetcenter, 0, width*5+12, self.newheight))

        except Exception as e: 
            return


    #############################################
    # watch for glyph changes
    #############################################

    def viewDidChangeGlyph(self, notification):
        self.glyph = CurrentGlyph()
        self.unsubscribeGlyph()
        self.subscribeGlyph()
        self.glyphChanged()


    def subscribeGlyph(self):
        self.glyph.addObserver(self, 'glyphChanged', 'Glyph.Changed')


    def unsubscribeGlyph(self):
        if self.glyph is None:
            return
        self.glyph.removeObserver(self, 'Glyph.Changed')


    def glyphChanged(self, notification=None):
        self.updateValues()



class CanvasStuff(object):

    def __init__(self, window):
        self.w = window

    def opaque(self):
        return False
    def acceptsFirstResponder(self):
        return False
    def acceptsMouseMoved(self):
        return False
    def becomeFirstResponder(self):
        return False
    def resignFirstResponder(self):
        return False
    def shouldDrawBackground(self):
        return False

    def draw(self):
        # ruler fix
        x = 0
        if getGlyphViewDisplaySettings()['Rulers']:
            x = 17
        sbui = windowViewManger.get(self.w)
        g = self.w.getGlyph()
        f = g.font
        uniquecomponents = []
        for c in g.components:
            if c.baseGlyph not in uniquecomponents:
                uniquecomponents.append(c.baseGlyph)
        newheight = height*(len(uniquecomponents)+2)
        sbui.L.setPosSize((x, 0, dfltLwidth, newheight))
        # center center
        winX, winY, winW, winH = self.w.getVisibleRect()
        winW = winW - margin*2
        offsetcenter = (winW/2)-(dfltCwidth/2)+x
        xywh = (offsetcenter, 0, dfltCwidth, newheight) 
        sbui.C.setPosSize(xywh)
        # self.sbWatcher()

    def mouseEntered(self, event):
        g = self.w.getGlyph()
        if g is None:
            return
        f = g.font
        if f is None:
            return
        self.showButtons = True
        sbui = windowViewManger.get(self.w)
        sbui.L.Lminus.show(True)
        sbui.L.Lround.show(True)
        sbui.L.Lplus.show(True)
        sbui.L.Lright.show(True)
        sbui.R.Rminus.show(True)
        sbui.R.Rround.show(True)
        sbui.R.Rplus.show(True)
        sbui.R.Rleft.show(True)
        sbui.C.Cminus.show(True)
        sbui.C.Cround.show(True)
        sbui.C.Ccenter.show(True)
        sbui.C.Cplus .show(True)

        sbui.L.Ltext.getNSTextField().setBackgroundColor_(NSColor.whiteColor())
        sbui.R.Rtext.getNSTextField().setBackgroundColor_(NSColor.whiteColor())
        sbui.C.Ctext.getNSTextField().setBackgroundColor_(NSColor.whiteColor())

        uniquecomponents = []
        for c in g.components:
            if c.baseGlyph not in uniquecomponents:
                uniquecomponents.append(c.baseGlyph)
        for i, c in enumerate(uniquecomponents):
            try:
                this = getattr(sbui.L, 'buttobj_%s' % i)
                this.show(True)
                this = getattr(sbui.R, 'buttobj_%s' % i)
                this.show(True)
                this = getattr(sbui.C, 'buttobj_%s' % i)
                this.show(True)
            except:
                return

        sbui.update()


    def mouseExited(self, event):
        g = self.w.getGlyph()
        if g is None:
            return
        f = g.font
        if f is None:
            return
        self.showButtons = False
        sbui = windowViewManger.get(self.w)
        sbui.L.Lminus.show(False)
        sbui.L.Lround.show(False)
        sbui.L.Lplus.show(False)
        sbui.L.Lright.show(False)
        sbui.R.Rminus.show(False)
        sbui.R.Rround.show(False)
        sbui.R.Rplus.show(False)
        sbui.R.Rleft.show(False)
        sbui.C.Cminus.show(False)
        sbui.C.Cround.show(False)
        sbui.C.Ccenter.show(False)
        sbui.C.Cplus .show(False)

        sbui.L.Ltext.getNSTextField().setBackgroundColor_(NSColor.clearColor())
        sbui.R.Rtext.getNSTextField().setBackgroundColor_(NSColor.clearColor())
        sbui.C.Ctext.getNSTextField().setBackgroundColor_(NSColor.clearColor())

        uniquecomponents = []
        for c in g.components:
            if c.baseGlyph not in uniquecomponents:
                uniquecomponents.append(c.baseGlyph)
        for i, c in enumerate(uniquecomponents):
            try:
                this = getattr(sbui.L, 'buttobj_%s' % i)
                this.show(False)
                this = getattr(sbui.R, 'buttobj_%s' % i)
                this.show(False)
                this = getattr(sbui.C, 'buttobj_%s' % i)
                this.show(False)
            except:
                return

        sbui.update()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


GlyphMetricsUI()