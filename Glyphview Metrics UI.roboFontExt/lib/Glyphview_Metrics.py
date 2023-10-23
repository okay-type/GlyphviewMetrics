from vanilla import *
from AppKit import NSColor, NSAttributedString, NSForegroundColorAttributeName, NSFontAttributeName, NSFont, NSTextAlignmentLeft, NSTextAlignmentRight, NSTextAlignmentCenter, NSBaselineOffsetAttributeName, NSParagraphStyleAttributeName, NSParagraphStyle, NSMutableParagraphStyle, NSEvent, NSShiftKeyMask
from mojo.subscriber import listRegisteredSubscribers

import merz
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber, registerSubscriberEvent
from lib.UI.glyphMetricsEditText import GlyphMetricsEditText

unit = 5
h = 15
size = h

iconminus = '-'
iconplus = '+'
iconround = '⚪︎'
iconcenter = '＝'
iconcopyR = '→'
iconcopyL = '←'

uibackground = NSColor.colorWithCalibratedRed_green_blue_alpha_(.8, 1, 1, .4)


'''


valid values
---
100             set a value numerically
glyphname       match a value from another glyph using it's name
?               shortcut to use the current glyph name

add-ons
---
glyphname.      lazy suffix completion, uses the suffix of the current glyph
glyphname@l     get the value of the left side
glyphname@left
glyphname@r     get the value of the right side
glyphname@right
~glyphname      distribute the left-right margins using the same proportion as the glyphname glyph

examples
---
69              set the value to 69
thorn           get the corresponding value from the thorn
thorn.          same, but will autocomplete the suffix of the currentglyph
                for example, using 'thorn.' in /p.sc will get /thorn.sc
thorn@left      same as above, but gets the value of the leftmargin
thorn@l         same as above, but lazier
thorn.@l        the things above things stack, useful if you can remember
~thorn          months later and i cant remember what this is for...

latest updates
- text fields are now GlyphMetricsEditText fields, so you can use up/down arrows to adjust values
- modifier + set component left/right margin -> keep width
- shift+click on the center component button will set both the left margin and the width to match the component
- run this script to install the tool, rerun this script to uninstall the tool

older updates
- in the width: field
    prefix a glyphname with ~ to proportioanlly match it's left and right margins
    so a if glyphname 'x' has 50-500-25, typing ~x in a 600upm wide glyph will give 60-600-30 (left-width-right)
- you can tab through the fields but changing a value will exit back to the glyph edit view
    - hopefully fixes accidental double changes and annoying drag-to-change accidents
- added buttons to match the metrics for *left and *right glyphs (i.e. parenleft-parenright)
- repositions center group on window resize (currently needs a glyph change to trigger)
- round displayed values to one decimals (works better for italics)
- right-align text fields for tighter layout
- lazy suffix completion with "."
    - entering '.' in a field will try to match the current glyph suffix
    - using 'R.' in a 'Racute.suffix' glyph will automatically use 'R.suffix'
    - this works with the @ syntax 'h.@l' will get the left margin of 'h.suffix'
- oops, broke the center in width button (=). fixed
- target which glyph metrics using glyphname@left shorthand
    - values are @left @right @width or @l @r @w if you're in a hurry
- even lazier, using '?' will use the current glyph name
    - good for nonalpha glyphs like numbers: '?@r' in a six will use the right side of 'six'
- color purple if component sidebearings equal the opposite side
- tweak icons' sizepos
- added textShouldEndEditing_ to EditText fields so I stop accidently changing things
- can we unset focus after pressing return (needs testing)
'''

class GlyphViewMetricsUI(Subscriber):

    # debug = True
    debug = False

    def build(self):
        self.added = []
        self.w = self.getGlyphEditor()

        self.xywh = [0, -size, -0, -unit]
        self.m = merz.MerzView(self.xywh, delegate=self)
        self.merzContainer = self.m.getMerzContainer()

        self.addMetricsUI()
        self.w.addGlyphEditorSubview(self.m)

    def destroy(self):
        self.w.removeGlyphEditorSubview(self.m)

    def terminateThis(self, info):
        unregisterGlyphEditorSubscriber(self)

    def glyphEditorDidSetGlyph(self, info):
        self.glyph = info['glyph']
        if self.glyph == None:
            return
        self.updateUI()

    def glyphDidChangeMetrics(self, info):
        self.glyph = info['glyph']
        if self.glyph == None:
            return
        self.updateUI()

    def glyphDidChangeOutline(self, info):
        self.glyph = info['glyph']
        if self.glyph == None:
            return
        self.updateUI()

    def updateUI(self):
        self.m.center.text.set(str(round(self.glyph.width, 1)))
        if self.glyph.angledLeftMargin is not None:
            self.m.left.text.set(str(round(self.glyph.angledLeftMargin, 1)))
        else:
            self.m.left.text.set('X')
        if self.glyph.angledRightMargin is not None:
            self.m.right.text.set(str(round(self.glyph.angledRightMargin, 1)))
        else:
            self.m.right.text.set('X')
        self.componentsUI()
        self.widthGroupPos()

    def addMetricsUI(self):

        self.width = 112

        this = self.m.left = Group((2, -h, self.width, -0))
        # this.getNSView().setBackgroundColor_(NSColor.yellowColor())
        x = 0
        w = 40
        b = 15
        this.text = mEditText((x, -h, w, -0), placeholder='X', sizeStyle='small', side='left', continuous=False, callback=self.setSB)
        x += w+5
        this.plus = mButton((x, -h-6, b, -0), iconplus, sizeStyle='mini', side='left', action='plus', callback=self.set)
        x += b+2
        this.minus = mButton((x, -h-6, b, -0), iconminus, sizeStyle='mini', side='left', action='minus', callback=self.set)
        x += b+2
        this.round = mButton((x, -h-4, b, -0), iconround, sizeStyle='mini', side='left', action='round', callback=self.set)
        x += b+2
        this.copy = mButton((x, -h-4, b, -0), iconcopyR, sizeStyle='mini', side='left', action='copy', callback=self.set)
        this.plus.getNSButton().setToolTip_('Increase Left Margin +'+str(unit))
        this.minus.getNSButton().setToolTip_('Decrease Left Margin -'+str(unit))
        this.round.getNSButton().setToolTip_('Round Left Margin to '+str(unit))
        this.copy.getNSButton().setToolTip_('Copy Right Margin')
        self.flatText(this.text)
        self.flatButt(this.minus)
        self.flatButt(this.plus)
        self.flatButt(this.round)
        self.flatButt(this.copy)
        textLeft = this.text.getNSTextField()
        textLeft.setAlignment_(NSTextAlignmentRight)

        this = self.m.right = Group((-self.width, -h, -2, -0))
        # this.getNSView().setBackgroundColor_(NSColor.yellowColor())
        x = 0
        this.text = mEditText((x, -h, w, -0), placeholder='X', sizeStyle='small', side='right', continuous=False, callback=self.setSB)
        x += w+5
        this.plus = mButton((x, -h-6, b, -0), iconplus, sizeStyle='mini', side='right', action='plus', callback=self.set)
        x += b+2
        this.minus = mButton((x, -h-6, b, -0), iconminus, sizeStyle='mini', side='right', action='minus', callback=self.set)
        x += b+2
        this.round = mButton((x, -h-4, b, -0), iconround, sizeStyle='mini', side='right', action='round', callback=self.set)
        x += b+2
        this.copy = mButton((x, -h-4, b, -0), iconcopyL, sizeStyle='mini', side='right', action='copy', callback=self.set)
        this.plus.getNSButton().setToolTip_('Increase Right Margin +'+str(unit))
        this.minus.getNSButton().setToolTip_('Decrease Right Margin -'+str(unit))
        this.round.getNSButton().setToolTip_('Round Right Margin to '+str(unit))
        this.copy.getNSButton().setToolTip_('Copy Left Margin')
        self.flatText(this.text)
        self.flatButt(this.minus)
        self.flatButt(this.plus)
        self.flatButt(this.round)
        self.flatButt(this.copy)
        textRight = this.text.getNSTextField()
        textRight.setAlignment_(NSTextAlignmentRight)

        winW = self.w.getVisibleRect()[2]
        x = winW/2 - self.width/2

        this = self.m.center = Group((x, -h, -x, -0))
        # this.getNSView().setBackgroundColor_(NSColor.yellowColor())
        x = 0
        this.text = mEditText((x, -h, w, -0), placeholder='X', sizeStyle='small', side='width', continuous=False, callback=self.setSB)
        x += w+5
        this.plus = mButton((x, -h-6, b, -0), iconplus, sizeStyle='mini', side='width', action='plus', callback=self.set)
        x += b+2
        this.minus = mButton((x, -h-6, b, -0), iconminus, sizeStyle='mini', side='width', action='minus', callback=self.set)
        x += b+2
        this.round = mButton((x, -h-4, b, -0), iconround, sizeStyle='mini', side='width', action='round', callback=self.set)
        x += b+2
        this.center = mButton((x, -h-4, b, -0), iconcenter, sizeStyle='mini', side='width', action='center', callback=self.set)
        this.plus.getNSButton().setToolTip_('Increase Width +'+str(unit*2))
        this.minus.getNSButton().setToolTip_('Decrease Width -'+str(unit*2))
        this.center.getNSButton().setToolTip_('Center Glyph In Width')
        this.round.getNSButton().setToolTip_('Round Width to '+str(unit))
        self.flatText(this.text)
        self.flatButt(this.minus)
        self.flatButt(this.plus)
        self.flatButt(this.round)
        self.flatButt(this.center)
        textWidth = this.text.getNSTextField()
        textWidth.setAlignment_(NSTextAlignmentRight)

        textLeft.setNextKeyView_(textWidth)
        textWidth.setNextKeyView_(textRight)
        textRight.setNextKeyView_(textLeft)

    def widthGroupPos(self):
        winW = self.w.getVisibleRect()[2]
        x = winW/2 - self.width/2
        self.m.center.setPosSize((x, -h, -x, -0))

    def sizeChanged(self, event):
        self.widthGroupPos()

    def setSB(self, sender):
        side = sender.side
        no = sender.get()
        nexttarget = sender.getNSTextField().nextKeyView()
        before = [self.glyph.angledLeftMargin, self.glyph.width, self.glyph.angledRightMargin]
        if side == 'left':
            with self.glyph.undo('Set Left Margin To '+ str(no)):
                if is_number(no):
                    self.glyph.angledLeftMargin = float(no)
                    self.glyph.changed()
                else:
                    v = self.setSBfromGlyph(no, side)
                    if type(v) == int or type(v) == float:
                        self.glyph.angledLeftMargin = self.setSBfromGlyph(no, side)
                        self.glyph.changed()
                sender.set(round(self.glyph.angledLeftMargin, 1))
        if side == 'right':
            with self.glyph.undo('Set Right Margin To '+ str(no)):
                if is_number(no):
                    self.glyph.angledRightMargin = float(no)
                    self.glyph.changed()
                else:
                    v = self.setSBfromGlyph(no, side)
                    if type(v) == int or type(v) == float:
                        self.glyph.angledRightMargin = self.setSBfromGlyph(no, side)
                        self.glyph.changed()
                sender.set(round(self.glyph.angledRightMargin, 1))
        if side == 'width':
            with self.glyph.undo('Set Width To '+ str(no)):
                if '~' == no[0]:
                    self.setProportional(no, side)
                elif is_number(no):
                    self.glyph.width = float(no)
                    self.glyph.changed()
                else:
                    v = self.setSBfromGlyph(no, side)
                    if type(v) == int or type(v) == float:
                        self.glyph.width = v
                        self.glyph.changed()
                sender.set(round(self.glyph.width, 1))
        # if changed, direct focus back to outlines
        if before != [self.glyph.angledLeftMargin, self.glyph.width, self.glyph.angledRightMargin]:
            sender.getNSTextField().setNextKeyView_(self.w.w)

    def setSBfromGlyph(self, no, side):
        font = self.glyph.font
        sourceG = no
        sourceSide = side
        if '.' == sourceG[-1] and '.' in self.glyph.name:
            suffix = '.'+self.glyph.name.split('.')[-1]
            sourceG = sourceG.replace('.', suffix)
        if '@' in sourceG:
            sourceG, sourceSide = sourceG.split('@')
        if '?' in sourceG:
            sourceG = sourceG.replace('?', self.glyph.name)
        if sourceG not in font.glyphOrder:
            print('sourceG not in font.glyphOrder', no, sourceG, sourceSide)
            return None
        if sourceSide == 'left' or sourceSide == 'l':
            metric = font[sourceG].angledLeftMargin
        if sourceSide == 'right' or sourceSide == 'r':
            metric = font[sourceG].angledRightMargin
        if sourceSide == 'width' or sourceSide == 'w':
            metric = font[sourceG].width
        if metric == None:
            metric = 0
        return metric

    def setProportional(self, no, side):
        font = self.glyph.font
        sourceG = no.replace('~', '')
        sourceSide = side

        sourceLeft = self.setSBfromGlyph(sourceG, 'left')
        sourceRight = self.setSBfromGlyph(sourceG, 'right')
        sourceWidth = self.setSBfromGlyph(sourceG, 'width')

        sourceTotalSpace = sourceLeft+sourceRight
        sourcePercentLeft = sourceLeft/sourceTotalSpace

        targetLeft = self.glyph.angledLeftMargin
        targetRight = self.glyph.angledRightMargin
        targetWidth = self.glyph.width
        targetTotalSpace = targetLeft+targetRight
        newLeft = targetTotalSpace*sourcePercentLeft

        self.glyph.angledLeftMargin = float(newLeft)
        self.glyph.width = targetWidth
        self.glyph.changed()

    def set(self, sender):
        side, action = sender.side, sender.action

        # component buttons
        if action == 'component':
            f = self.glyph.font
            baseGlyph = f[sender.getTitle()]
            if baseGlyph is not None:
                if side == 'left':
                    if NSEvent.modifierFlags() & NSShiftKeyMask:
                        with self.glyph.undo('Match Left Margin of ' + baseGlyph.name + ' and maintain width'):
                            w1 = self.glyph.width
                            self.glyph.angledLeftMargin = baseGlyph.angledLeftMargin
                            self.glyph.width = w1
                    else:
                        with self.glyph.undo('Match Left Margin of ' + baseGlyph.name):
                            self.glyph.angledLeftMargin = baseGlyph.angledLeftMargin
                if side == 'right':
                    if NSEvent.modifierFlags() & NSShiftKeyMask:
                        with self.glyph.undo('Match Right Margin of ' + baseGlyph.name + ' and maintain width'):
                            w1 = self.glyph.width
                            right_diff = baseGlyph.angledRightMargin - self.glyph.angledRightMargin
                            self.glyph.angledLeftMargin += -1 * right_diff
                            self.glyph.angledRightMargin += right_diff
                            if self.glyph.width != w1:
                                self.glyph.width = w1
                    else:
                        with self.glyph.undo('Match Right Margin of ' + baseGlyph.name):
                            self.glyph.angledRightMargin = baseGlyph.angledRightMargin
                if side == 'width':
                    with self.glyph.undo('Match Width of ' + baseGlyph.name):
                        if NSEvent.modifierFlags() & NSShiftKeyMask:
                            self.glyph.angledLeftMargin = baseGlyph.angledLeftMargin
                            self.glyph.width = baseGlyph.width
                        else:
                            self.glyph.width = baseGlyph.width

        # leftright glyph buttons
        if action == 'leftright':
            f = self.glyph.font
            baseGlyph = sender.getTitle().replace(iconcopyR+' ', '').replace(' '+iconcopyL, '')
            baseGlyph = f[baseGlyph]
            if baseGlyph is not None:
                if side == 'left':
                    with self.glyph.undo('Match Left Margin of ' + baseGlyph.name):
                        self.glyph.angledLeftMargin = baseGlyph.angledRightMargin
                if side == 'right':
                    with self.glyph.undo('Match Right Margin of ' + baseGlyph.name):
                        self.glyph.angledRightMargin = baseGlyph.angledLeftMargin
                if side == 'width':
                    with self.glyph.undo('Match Width of ' + baseGlyph.name):
                        self.glyph.width = baseGlyph.width

        # left side buttons
        elif side == 'left':
            if action == 'plus':
                with self.glyph.undo('Increase Left Margin +' + str(unit)):
                    self.glyph.angledLeftMargin += unit
            if action == 'minus':
                with self.glyph.undo('Decrease Left Margin +' + str(unit)):
                    self.glyph.angledLeftMargin -= unit
            if action == 'round':
                with self.glyph.undo('Round Left Margin to ' + str(unit)):
                    self.glyph.angledLeftMargin = int(unit * round(float(self.glyph.angledLeftMargin)/unit))
            if action == 'copy':
                with self.glyph.undo('Copy Right Margin to Left'):
                    self.glyph.angledLeftMargin = self.glyph.angledRightMargin

        # right side buttons
        elif side == 'right':
            if action == 'plus':
                with self.glyph.undo('Increase Right Margin +' + str(unit)):
                    self.glyph.angledRightMargin += unit
            if action == 'minus':
                with self.glyph.undo('Decrease Right Margin +' + str(unit)):
                    self.glyph.angledRightMargin -= unit
            if action == 'round':
                with self.glyph.undo('Round Right Margin to ' + str(unit)):
                    self.glyph.angledRightMargin = int(unit * round(float(self.glyph.angledRightMargin)/unit))
            if action == 'copy':
                with self.glyph.undo('Copy Right Margin to Left'):
                    self.glyph.angledRightMargin = self.glyph.angledLeftMargin

        # width buttons
        elif side == 'width':
            if action == 'plus':
                with self.glyph.undo('Increase Both Margins +' + str(unit)):
                    self.glyph.angledLeftMargin += unit
                    self.glyph.angledRightMargin += unit
            if action == 'minus':
                with self.glyph.undo('Decrease Both Margins +' + str(unit)):
                    self.glyph.angledLeftMargin -= unit
                    self.glyph.angledRightMargin -= unit
            if action == 'round':
                with self.glyph.undo('Round Width to ' + str(unit)):
                    oldwidth = self.glyph.width
                    newwidth = int(unit * round(float(oldwidth)/unit))
                    self.glyph.width = newwidth
            if action == 'center':
                with self.glyph.undo('Center Glyph On Width'):
                    padding = self.glyph.angledLeftMargin + self.glyph.angledRightMargin
                    gwidth = self.glyph.width
                    self.glyph.angledLeftMargin = int(padding/2)
                    self.glyph.width = gwidth

        self.glyph.changed()


    def componentsUI(self):
        f = self.glyph.font

        self.uniquecomponents = []
        for c in self.glyph.components:
            if c.baseGlyph not in self.uniquecomponents:
                self.uniquecomponents.append(c.baseGlyph)

        leftrightGlyph = 0
        if 'left' in self.glyph.name or 'right' in self.glyph.name:
            if 'left' in self.glyph.name:
                flippedname = self.glyph.name.replace('left', 'right')
            if 'right' in self.glyph.name:
                flippedname = self.glyph.name.replace('right', 'left')
            if flippedname in f.glyphOrder:
                leftrightGlyph = 1

        newy = self.xywh[1] - (h * (len(self.uniquecomponents) + leftrightGlyph + 1))
        xywh = [self.xywh[0], newy, self.xywh[2], self.xywh[3]]

        self.m.setPosSize(xywh)

        # remove old buttons
        for added in self.added:
            if hasattr(self.m, added):
                delattr(self.m, added)

        i = -1
        self.added = []
        for i, c in enumerate(self.uniquecomponents):

            thisy = -(h+1)*(i+2)-4
            thish = h-1

            size = (5, thisy, self.width, thish)
            this = mButton(size, c, sizeStyle='mini', side='left', action='component', callback=self.set)
            this.getNSButton().setToolTip_('Match Left Margin of /'+c)
            match = False
            if int(f[c].angledLeftMargin) == int(self.glyph.angledLeftMargin):
                match = True
            elif int(f[c].angledRightMargin) == int(self.glyph.angledLeftMargin):
                match = 'Opposite'
            self.flatButt(this, match)
            name = 'ButtonComponentLeft_%s' % i
            setattr(self.m, name, this)
            self.added.append(name)

            size = (-self.width+1, thisy, -3, thish)
            this = mButton(size, c, sizeStyle='mini', side='right', action='component', callback=self.set)
            this.getNSButton().setToolTip_('Match Right Margin of /'+c)
            match = False
            if int(f[c].angledRightMargin) == int(self.glyph.angledRightMargin):
                match = True
            elif int(f[c].angledLeftMargin) == int(self.glyph.angledRightMargin):
                match = 'Opposite'
            self.flatButt(this, match)
            name = 'ButtonComponentRight_%s' % i
            setattr(self.m, name, this)
            self.added.append(name)

            winW = self.w.getVisibleRect()[2]
            x = winW/2 - self.width/2
            size = (x+1, thisy, -x, thish)
            this = mButton(size, c, sizeStyle='mini', side='width', action='component', callback=self.set)
            this.getNSButton().setToolTip_('Match Width of /'+c)
            self.flatButt(this, bool(int(f[c].width) == int(self.glyph.width)))
            name = 'ButtonComponentWidth_%s' % i
            setattr(self.m, name, this)
            self.added.append(name)

        if leftrightGlyph == 1:
            leftrightGlyph = self.glyph.name.replace('left', 'RRRRRRRRRRRRR').replace('right', 'left').replace('RRRRRRRRRRRRR', 'right')

            i += 1
            thisy = -(h+1)*(i+2)-8
            thish = h-1

            size = (5, thisy, self.width, thish)
            this = mButton(size, iconcopyR+' '+leftrightGlyph, sizeStyle='mini', side='left', action='leftright', callback=self.set)
            this.getNSButton().setToolTip_('Match Right Margin of /'+leftrightGlyph)
            match = 'LeftRightFalse'
            if int(f[leftrightGlyph].angledRightMargin) == int(self.glyph.angledLeftMargin):
                match = 'LeftRightTrue'
            self.flatButt(this, match)
            name = 'ButtonLEFTRIGHTLeft_%s' % i
            setattr(self.m, name, this)
            self.added.append(name)

            size = (-self.width+1, thisy, -3, thish)
            this = mButton(size, leftrightGlyph+' '+iconcopyL, sizeStyle='mini', side='right', action='leftright', callback=self.set)
            this.getNSButton().setToolTip_('Match Left Margin of /'+leftrightGlyph)
            match = 'LeftRightFalse'
            if int(f[leftrightGlyph].angledLeftMargin) == int(self.glyph.angledRightMargin):
                match = 'LeftRightTrue'
            self.flatButt(this, match)
            name = 'ButtonLEFTRIGHTRight_%s' % i
            setattr(self.m, name, this)
            self.added.append(name)

            winW = self.w.getVisibleRect()[2]
            x = winW/2 - self.width/2
            size = (x+1, thisy, -x, thish)
            this = mButton(size, leftrightGlyph, sizeStyle='mini', side='width', action='leftright', callback=self.set)
            this.getNSButton().setToolTip_('Match Width of /'+leftrightGlyph)
            match = 'LeftRightFalse'
            if int(f[leftrightGlyph].width) == int(self.glyph.width):
                match = 'LeftRightTrue'
            self.flatButt(this, match)
            name = 'ButtonLEFTRIGHTWidth_%s' % i
            setattr(self.m, name, this)
            self.added.append(name)


    def flatText(self, this):
        ns = this.getNSTextField()
        # ns.setBezeled_(False)
        ns.setBordered_(False)
        # ns.setBackgroundColor_(NSColor.clearColor())
        ns.setBackgroundColor_(uibackground)
        # ns.setTextColor_(NSColor.blackColor())
        ns.setFocusRingType_(1)


    def flatButt(self, this, match=None):
        ns = this.getNSButton()
        ns.setBordered_(False)
        # ns.setBackgroundColor_(NSColor.redColor())
        ns.setBackgroundColor_(uibackground)
        fontSize = 14
        if this.action == 'component' or this.action == 'leftright':
            fontSize = 11

        textcolor = NSColor.blackColor()
        customFont = NSFont.menuBarFontOfSize_(fontSize)
        # customFont = NSFont.fontWithName_size_('SFMono-Regular', fontSize)

        if match == False:
            textcolor = NSColor.redColor()
            ns.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1, .7, .7, .4))
        if match == True:
            textcolor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, .8, 0, 1)
            ns.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(.7, 1, .7, .4))
        if match == 'Opposite':
            textcolor = NSColor.colorWithCalibratedRed_green_blue_alpha_(.8, .1, 1, 1)
            ns.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(.9, .8, 1, .4))
        if match == 'LeftRightTrue':
            textcolor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, .8, .8, .9)
            ns.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(.6, 1, 1, .4))
            # customFont = NSFont.fontWithName_size_('SFMono-RegularItalic', fontSize)
        if match == 'LeftRightFalse':
            textcolor = NSColor.colorWithCalibratedRed_green_blue_alpha_(.8, 0, 0, .6)
            # customFont = NSFont.fontWithName_size_('SFMono-RegularItalic', fontSize)

        alignment = 2  ## 0=left, 1=right, 2=center, 3=justified
        if this.action == 'component' or this.action == 'leftright':
            if this.side == 'left':
                alignment = 0
            if this.side == 'right':
                alignment = 1

        paragraphStyle = NSMutableParagraphStyle.alloc().init()
        paragraphStyle.setAlignment_(alignment)

        attributes = {}
        attributes[NSFontAttributeName] = customFont
        attributes[NSForegroundColorAttributeName] = textcolor
        attributes[NSParagraphStyleAttributeName] = paragraphStyle
        # attributes[NSBaselineOffsetAttributeName] = 10

        attributedText = NSAttributedString.alloc().initWithString_attributes_(
            ns.title(),
            attributes
        )
        ns.setAttributedTitle_(attributedText)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class mButton(Button):
    def __init__(self, *args, **kwargs):
        self.side = kwargs['side']
        self.action = kwargs['action']
        del kwargs['side']
        del kwargs['action']
        super(mButton, self).__init__(*args, **kwargs)


class mEditText(GlyphMetricsEditText):
    def __init__(self, *args, **kwargs):
        self.side = kwargs['side']
        del kwargs['side']
        super(mEditText, self).__init__(*args, **kwargs)



if __name__ == '__main__':
    registered_subscribers = listRegisteredSubscribers(subscriberClassName='GlyphViewMetricsUI')
    if len(registered_subscribers) > 0:
        for target_subscriber in registered_subscribers:
            unregisterGlyphEditorSubscriber(target_subscriber)
        print('Glyph Edit View Metrics UI Uninstalled')
    else:
        registerGlyphEditorSubscriber(GlyphViewMetricsUI)
        print('Glyph Edit View Metrics UI Installed')


