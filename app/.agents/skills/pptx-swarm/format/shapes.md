## Parameter Value Conventions

* adjustments parameters are described following the parameter order and count defined by OOXML
* Value range is generally [0, 100000], representing percentage (100000 = 100%)
* Angle parameter unit is OOXML 1/60000 of a degree, conversion formula: `OOXML value = angle x 60000` (e.g., `16200000` = 270 degrees)
* The parameter array must be complete (intermediate values cannot be omitted), or entirely absent to use default values
* `-` indicates the shape has no adjustable parameters

---

## Basic Shapes

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| rect | Rectangle | - | - |
| roundRect | Rounded rectangle | [corner radius] | [16667] |
| ellipse | Ellipse | - | - |
| triangle | Triangle | [apex horizontal position] | [50000] |
| rtTriangle | Right triangle | - | - |
| parallelogram | Parallelogram | [skew offset] | [25000] |
| trapezoid | Trapezoid | [top edge inset] | [25000] |
| nonIsoscelesTrapezoid | Non-isosceles trapezoid | [left offset, right offset] | [25000, 25000] |
| diamond | Diamond | - | - |
| pentagon | Regular pentagon | [horizontal factor, vertical factor] | [105146, 110557] |
| hexagon | Hexagon | [inset offset, vertical factor] | [25000, 115470] |
| heptagon | Heptagon | [horizontal factor, vertical factor] | [102572, 105210] |
| octagon | Octagon | [chamfer size] | [29289] |
| decagon | Decagon | [vertical factor] | [105146] |
| dodecagon | Dodecagon | - | - |
| plus | Plus sign | [arm width ratio] | [25000] |
| homePlate | Pentagon arrow | [arrow tip offset] | [50000] |
| chevron | Chevron | [V tip offset] | [50000] |
| pie | Pie | [start angle, end angle] | [0, 16200000] |
| pieWedge | Pie wedge | - | - |
| arc | Arc | [start angle, end angle] | [16200000, 0] |
| chord | Chord | [start angle, end angle] | [2700000, 16200000] |
| blockArc | Block arc | [start angle, end angle, thickness] | [10800000, 0, 25000] |
| teardrop | Teardrop | [tail extension ratio] | [100000] |
| frame | Frame | [border thickness] | [12500] |
| halfFrame | Half frame | [horizontal thickness, vertical thickness] | [33333, 33333] |
| corner | Corner | [horizontal thickness, vertical thickness] | [50000, 50000] |
| diagStripe | Diagonal stripe | [stripe width] | [50000] |
| foldedCorner | Folded corner | - | - |
| donut | Donut | [ring width ratio] | [25000] |
| noSmoking | No symbol | [slash width] | [18750] |
| heart | Heart | - | - |
| lightningBolt | Lightning bolt | - | - |
| sun | Sun | [ray inner radius ratio] | [25000] |
| moon | Moon | [crescent width] | [50000] |
| cloud | Cloud | - | - |
| smileyFace | Smiley face | [mouth curvature] | [4653] |
| bevel | Bevel | [bevel width] | [12500] |
| can | Cylinder | [elliptical cap height] | [25000] |
| cube | Cube | [perspective depth] | [25000] |
| funnel | Funnel | - | - |
| gear6 | 6-tooth gear | [tooth height, tooth width] | [15000, 3526] |
| gear9 | 9-tooth gear | [tooth height, tooth width] | [10000, 1763] |
| plaque | Plaque | [corner radius] | [16667] |
| doubleWave | Double wave | [wave amplitude, horizontal offset] | [6250, 0] |
| wave | Wave | [wave amplitude, horizontal offset] | [12500, 0] |
| lineInv | Inverse line | - | - |

## Rectangle Variants

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| round1Rect | Single rounded corner rectangle | [corner radius] | [16667] |
| round2DiagRect | Diagonal double rounded corner rectangle | [corner 1 radius, corner 2 radius] | [16667, 0] |
| round2SameRect | Same-side double rounded corner rectangle | [top corner radius, bottom corner radius] | [16667, 0] |
| snip1Rect | Single snipped corner rectangle | [snip size] | [16667] |
| snip2DiagRect | Diagonal double snipped corner rectangle | [snip 1 size, snip 2 size] | [0, 16667] |
| snip2SameRect | Same-side double snipped corner rectangle | [top snip size, bottom snip size] | [16667, 0] |
| snipRoundRect | Snipped and rounded corner rectangle | [corner radius, snip size] | [16667, 16667] |

## Stars and Bursts

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| star4 | 4-point star | [inner radius ratio] | [12500] |
| star5 | 5-point star | [inner radius ratio, horizontal factor, vertical factor] | [19098, 105146, 110557] |
| star6 | 6-point star | [inner radius ratio, horizontal factor] | [28868, 115470] |
| star7 | 7-point star | [inner radius ratio, horizontal factor, vertical factor] | [34601, 102572, 105210] |
| star8 | 8-point star | [inner radius ratio] | [37500] |
| star10 | 10-point star | [inner radius ratio, horizontal factor] | [42533, 105146] |
| star12 | 12-point star | [inner radius ratio] | [37500] |
| star16 | 16-point star | [inner radius ratio] | [37500] |
| star24 | 24-point star | [inner radius ratio] | [37500] |
| star32 | 32-point star | [inner radius ratio] | [37500] |
| irregularSeal1 | Burst 1 | - | - |
| irregularSeal2 | Burst 2 | - | - |

## Arrow Shapes

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| rightArrow | Right arrow | [shaft width, head length] | [50000, 50000] |
| leftArrow | Left arrow | [shaft width, head length] | [50000, 50000] |
| upArrow | Up arrow | [shaft width, head length] | [50000, 50000] |
| downArrow | Down arrow | [shaft width, head length] | [50000, 50000] |
| leftRightArrow | Left-right arrow | [shaft width, head length] | [50000, 50000] |
| upDownArrow | Up-down arrow | [shaft width, up head length, shaft width, down head length] | [50000, 50000, 50000, 50000] |
| quadArrow | Quad arrow | [shaft width, head width, head length] | [22500, 22500, 22500] |
| leftRightUpArrow | Left-right-up arrow | [shaft width, head width, head length] | [25000, 25000, 25000] |
| leftUpArrow | Left-up arrow | [shaft width, head width, head length] | [25000, 25000, 25000] |
| bentArrow | Bent arrow | [shaft width, head width, head length, bend position] | [25000, 25000, 25000, 43750] |
| bentUpArrow | Bent up arrow | [shaft width, head width, head length] | [25000, 25000, 25000] |
| uturnArrow | U-turn arrow | [shaft width, head width, head length, bend radius, shaft length] | [25000, 25000, 25000, 43750, 75000] |
| circularArrow | Circular arrow | [head width, start angle, end angle, arc angle, tip width] | [12500, 1142319, 20457681, 10800000, 12500] |
| leftCircularArrow | Left circular arrow | [head width, start angle, end angle, arc angle, tip width] | [12500, -1142319, 1142319, 10800000, 12500] |
| leftRightCircularArrow | Left-right circular arrow | [head width, start angle, end angle, arc angle, tip width] | [12500, 1142319, 20457681, 11942319, 12500] |
| curvedRightArrow | Curved right arrow | [head width, arc degree, head length] | [25000, 50000, 25000] |
| curvedLeftArrow | Curved left arrow | [head width, arc degree, head length] | [25000, 50000, 25000] |
| curvedUpArrow | Curved up arrow | [head width, arc degree, head length] | [25000, 50000, 25000] |
| curvedDownArrow | Curved down arrow | [head width, arc degree, head length] | [25000, 50000, 25000] |
| stripedRightArrow | Striped right arrow | [shaft width, head length] | [50000, 50000] |
| notchedRightArrow | Notched right arrow | [shaft width, head length] | [50000, 50000] |
| swooshArrow | Swoosh arrow | [tail width, head length] | [25000, 16667] |

## Arrow Callouts

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| rightArrowCallout | Right arrow callout | [shaft width, head width, head length, box width] | [25000, 25000, 25000, 64977] |
| leftArrowCallout | Left arrow callout | [shaft width, head width, head length, box width] | [25000, 25000, 25000, 64977] |
| upArrowCallout | Up arrow callout | [shaft width, head width, head length, box height] | [25000, 25000, 25000, 64977] |
| downArrowCallout | Down arrow callout | [shaft width, head width, head length, box height] | [25000, 25000, 25000, 64977] |
| leftRightArrowCallout | Left-right arrow callout | [shaft width, head width, head length, box width] | [25000, 25000, 25000, 48123] |
| upDownArrowCallout | Up-down arrow callout | [shaft width, head width, head length, box height] | [25000, 25000, 25000, 48123] |
| quadArrowCallout | Quad arrow callout | [shaft width, head width, head length, box size] | [18515, 18515, 18515, 48123] |

## Callouts

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| wedgeRectCallout | Rectangular callout | [tip X offset, tip Y offset] | [-20833, 62500] |
| wedgeRoundRectCallout | Rounded rectangular callout | [tip X offset, tip Y offset, corner radius] | [-20833, 62500, 16667] |
| wedgeEllipseCallout | Elliptical callout | [tip X offset, tip Y offset] | [-20833, 62500] |
| cloudCallout | Cloud callout | [tip X offset, tip Y offset] | [-20833, 62500] |
| borderCallout1 | Line callout 1 | [callout line Y1, X1, Y2, X2] | [18750, -8333, 112500, -38333] |
| borderCallout2 | Line callout 2 | [line Y1, X1, bend Y, X, end Y, X] | [18750, -8333, 18750, -16667, 112500, -46667] |
| borderCallout3 | Line callout 3 | [line Y1, X1, bend1 Y, X, bend2 Y, X, end Y, X] | [18750, -8333, 18750, -16667, 100000, -16667, 112963, -8333] |
| accentCallout1 | Accent callout 1 | Same as borderCallout1 | [18750, -8333, 112500, -38333] |
| accentCallout2 | Accent callout 2 | Same as borderCallout2 | [18750, -8333, 18750, -16667, 112500, -46667] |
| accentCallout3 | Accent callout 3 | Same as borderCallout3 | [18750, -8333, 18750, -16667, 100000, -16667, 112963, -8333] |
| accentBorderCallout1 | Accent border callout 1 | Same as borderCallout1 | [18750, -8333, 112500, -38333] |
| accentBorderCallout2 | Accent border callout 2 | Same as borderCallout2 | [18750, -8333, 18750, -16667, 112500, -46667] |
| accentBorderCallout3 | Accent border callout 3 | Same as borderCallout3 | [18750, -8333, 18750, -16667, 100000, -16667, 112963, -8333] |
| callout1 | Borderless callout 1 | Same as borderCallout1 | [18750, -8333, 112500, -38333] |
| callout2 | Borderless callout 2 | Same as borderCallout2 | [18750, -8333, 18750, -16667, 112500, -46667] |
| callout3 | Borderless callout 3 | Same as borderCallout3 | [18750, -8333, 18750, -16667, 100000, -16667, 112963, -8333] |

> **Callout tip offset note**: The X/Y offset values for callout shapes use the shape center as the origin, with units in percentage of shape width/height. Negative values indicate the tip is to the left of/above the shape.

## Brackets and Braces

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| leftBrace | Left brace | [curvature, midpoint position] | [8333, 50000] |
| rightBrace | Right brace | [curvature, midpoint position] | [8333, 50000] |
| leftBracket | Left bracket | [curvature] | [8333] |
| rightBracket | Right bracket | [curvature] | [8333] |
| bracePair | Brace pair | [curvature] | [8333] |
| bracketPair | Bracket pair | [curvature] | [16667] |

## Ribbons

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| ribbon | Down-curved ribbon | [fold height, ribbon curvature] | [16667, 50000] |
| ribbon2 | Up-curved ribbon | [fold height, ribbon curvature] | [16667, 50000] |
| ellipseRibbon | Curved down ribbon | [arc degree, center height, fold height] | [25000, 50000, 12500] |
| ellipseRibbon2 | Curved up ribbon | [arc degree, center height, fold height] | [25000, 50000, 12500] |
| leftRightRibbon | Left-right ribbon | [fold height, ribbon curvature, fold width] | [50000, 50000, 16667] |

## Scrolls

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| horizontalScroll | Horizontal scroll | [scroll size] | [12500] |
| verticalScroll | Vertical scroll | [scroll size] | [12500] |

## Math Symbols

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| mathPlus | Plus sign | [line thickness] | [23520] |
| mathMinus | Minus sign | [line thickness] | [23520] |
| mathMultiply | Multiply sign | [line thickness] | [23520] |
| mathDivide | Divide sign | [line thickness, dot spacing, dot size] | [23520, 5880, 11760] |
| mathEqual | Equal sign | [line thickness, line spacing] | [23520, 11760] |
| mathNotEqual | Not equal sign | [line thickness, slash angle, line spacing] | [23520, 6600000, 11760] |

## Chart Shapes

| shapeName | Description |
| --------- | --- |
| chartPlus | Chart plus |
| chartStar | Chart star |
| chartX | Chart X |

## Tab Shapes

| shapeName | Description |
| --------- | --- |
| cornerTabs | Corner tabs |
| squareTabs | Square tabs |
| plaqueTabs | Plaque tabs |

## Action Buttons

| shapeName | Description |
| --------- | --- |
| actionButtonBackPrevious | Back/previous button |
| actionButtonBeginning | Beginning button |
| actionButtonBlank | Blank button |
| actionButtonDocument | Document button |
| actionButtonEnd | End button |
| actionButtonForwardNext | Forward/next button |
| actionButtonHelp | Help button |
| actionButtonHome | Home button |
| actionButtonInformation | Information button |
| actionButtonMovie | Movie button |
| actionButtonReturn | Return button |
| actionButtonSound | Sound button |

## Flowchart Shapes

| shapeName | Description |
| --------- | --- |
| flowChartProcess | Flowchart: Process |
| flowChartAlternateProcess | Flowchart: Alternate process |
| flowChartDecision | Flowchart: Decision |
| flowChartDocument | Flowchart: Document |
| flowChartMultidocument | Flowchart: Multidocument |
| flowChartInputOutput | Flowchart: Data |
| flowChartPredefinedProcess | Flowchart: Predefined process |
| flowChartInternalStorage | Flowchart: Internal storage |
| flowChartManualInput | Flowchart: Manual input |
| flowChartManualOperation | Flowchart: Manual operation |
| flowChartPreparation | Flowchart: Preparation |
| flowChartDelay | Flowchart: Delay |
| flowChartTerminator | Flowchart: Terminator |
| flowChartConnector | Flowchart: Connector |
| flowChartOffpageConnector | Flowchart: Off-page connector |
| flowChartPunchedCard | Flowchart: Card |
| flowChartPunchedTape | Flowchart: Tape |
| flowChartCollate | Flowchart: Collate |
| flowChartSort | Flowchart: Sort |
| flowChartExtract | Flowchart: Extract |
| flowChartMerge | Flowchart: Merge |
| flowChartOr | Flowchart: Or |
| flowChartSummingJunction | Flowchart: Summing junction |
| flowChartOnlineStorage | Flowchart: Online storage |
| flowChartMagneticDisk | Flowchart: Magnetic disk |
| flowChartMagneticDrum | Flowchart: Magnetic drum |
| flowChartMagneticTape | Flowchart: Magnetic tape |
| flowChartOfflineStorage | Flowchart: Offline storage |
| flowChartDisplay | Flowchart: Display |

## Line Shapes

> Line shapes are used through the connector-type shapeName of Shape elements.

| shapeName | Description | adjustments Parameters | Default Values |
| --------- | --- | -------------- | ---- |
| line | Straight line (alias for straightConnector1) | - | - |
| straightConnector1 | Straight line | - | - |
| bentConnector2 | L-shaped connector (1 bend point) | - | - |
| bentConnector3 | Z-shaped connector (2 bend points) | [midpoint position] | [50000] |
| bentConnector4 | Z-shaped connector (3 bend points) | [X offset, Y offset] | [50000, 50000] |
| curvedConnector2 | Simple arc | - | - |
| curvedConnector3 | S-shaped curve (1 inflection point) | [control point position] | [50000] |
| curvedConnector4 | Spiral curve (2 inflection points) | [X offset, Y offset] | [50000, 50000] |
