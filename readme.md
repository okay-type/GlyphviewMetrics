# Glyphview Metrics UI
---

This Robofont extension adds a small UI to the bottom of the Glyphview window that helps you adjust the current glyph's left margin, right margin, and width. Updated for Robofont 4.

This extension still needs a better name. It adds a UI to the bottom of the glyphview window to adjust the metrics.


<img src="/resources/ScreenShot.png" width="666" alt="Glyphview Metrics HUD ScreenShot">


## There are buttons to make quick adjustments:


| Button | Effect |
|--------|--------|
| \+ | Increase the left or right margin by 5, or both by 5 |
| \- | Decrease the left or right margin by 5, or both by 5 |
| ⚪︎ | Rounds the current value to a threashold of 5 |
| ＝ | Center the glyph on the current width |
| → | Copy the right margin to the left margin |
| ← | Copy the left margin to the right margin |


## There is also a text field to enter values directly, or with a useful (but cryptic) shorthand:


**Base Values**

| Value | Effect |
|--------|--------|
| "100" | set a value numerically |
| "glyphname" | match a value from another glyph using it's name |
| "?" | shortcut to use the current glyph name |


**Other Useful Values**

| Button | Result |
|--------|--------|
| "glyphname." | lazy suffix completion, adds the suffix of the current glyph to the glyphname you enter |
| "glyphname@l"  | copy the value of /glyphname's left side |
| "glyphname@left" | same as above, in case it's easier to remember |
| "glyphname@r"  | copy the value of /glyphname's right side |
| "glyphname@right" | same as above, in case it's easier to remember |
| "~glyphname" | distribute the left-right margins using the same proportion as the /glyphname without changing the current glyphs width |


**Examples**

| Button | Result |
|--------|--------|
| "69" | set the corresponding value to 69 |
| "thorn" | get the corresponding value from the font's /thorn glyph |
| "thorn." | same, but will autocomplete the suffix of the currentglyph, so if you're editing /p.sc and enter "thorn." you will get the value from /thorn.sc |
| "thorn@left" | get the corresponding value of /thorn's the leftmargin (useful if you wante to copy a glyph's left margin to something else's right margin)  |
| "thorn@l" | same as above, but lazier  |
| "thorn.@l" | the things above things stack, useful if you can remember how everything |
| "~thorn " | will copy the metrics of /thorn proportional to the current glyph's width, somewhat useful for things like smallcaps |

## Last, there are buttons that pop up if a glyph contains a component or has an obvious left/right mirror pair

You'll see these and they'll make more sense. These are superuseful for checking if metrics match baseglyph, but it's also useful to get a rough idea of the glyph's component order.
- Clicking the button will apply the that component's base glyph value
- If a value doesn't match the component's base glyph, the button will be red
- If a value matches the component's base glyph, the button will be green
- If current glyph and component's base glyph are part of a left/right mirror pair, and a value matches the component's base glyph opposite value, the button will be purple
- If current glyph and component's base glyph are part of a left/right mirror pair an additional button will appear with an → or ← to copy the mirror value
- Holding shift while clicking the set component's right margin button will apply the right margin by shifting the glyph's position (instead of changing the width)



### needs to be fixed
- resizing the window scrambles the ui until the glyph changes

### latest update
- holding shift while clicking the set component's left or right margin button will apply the left or right margin but maintain the current width

### older updates
- shift+click on the center component button will set both the left margin and the width to match the component
- run this script to install the tool, rerun this script to uninstall the tool
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





