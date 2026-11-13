# Where Is It: art asset specification

Every piece of art the book draws lives in `Media/` as a 32-bit TGA. Replace a file
with one of the same name and the addon picks it up with no code change. This
document lists each file, how large it is, how the game uses it, and what it must
contain for the layout to keep working.

## Rules that apply to every file

* **Format:** 32-bit uncompressed TGA (RGB + 8-bit alpha, "straight" alpha, not
  premultiplied). The game also reads BLP, but TGA is the simplest to author.
* **Name:** exactly as listed, in `Media/`. The lookup is `Interface\AddOns\WhereIsIt\Media\<Name>` with no extension, so `Page.tga` must stay `Page.tga`.
* **Dimensions:** every side a power of two (16, 32, 64, 128, 256, 512, 1024). Sides
  need not be equal. You may double a texture for more detail (for example `Page`
  at 1024x1024, `Corner` at 128x128) as long as the aspect ratio stays the same;
  the game stretches it to the render size given below.
* **Stretching:** textures are stretched to the on-screen size listed for each
  asset, so keep the aspect ratio of the current file. Where only part of a file is
  shown ("portion used") the rest is cropped and can hold anything.
* **Tinting:** assets marked **tinted** are multiplied by a colour in code. Paint
  them pure white (255,255,255) with the shape in the alpha channel; any grey or
  colour you paint will only darken the result. Assets marked **full colour** are
  shown exactly as painted.
* **Mirroring:** some assets are drawn once and flipped for the other side or
  corners. Design the orientation named below; the flips are automatic.
* **Seeing a change:** the client caches textures. After replacing files, exit the
  game fully and relaunch. `/reload` is not enough.
* **Previewing without the game:** `python -I tools/make_media.py` regenerates the
  current procedural set, which also serves as a reference for proportions.

## Palette used by the code (RGB 0-255)

| Name | Colour | Where it appears |
| --- | --- | --- |
| Ink | 59, 41, 26 | body text, Lens icon, drop-cap tint base |
| Faded ink | 107, 87, 64 | Flourish, Rule, Vine, Compass tints; captions |
| Rubric red | 140, 46, 31 | section headings on the Scroll banners |
| Gold | 122, 79, 18 | Diamond bullets, row highlight gradient |
| Gilt | 242, 204, 107 | the letter on illuminated initials |
| Alliance | 46, 87, 158 | faction ribbon, drop-cap field |
| Horde | 168, 41, 36 | faction ribbon, drop-cap field |
| Settings gold | 199, 148, 41 | the Settings ribbon |
| Cream | 255, 242, 217 | ribbon labels, Gear icon, legend text |
| Spine gutter | 18, 9, 4 | the dark strip between the pages |

Paint full-colour assets (parchment, leather, brass, scroll banners, drop-cap frame,
map rim, straps, lace, corners) to sit well with these.

## Layout reference

The book frame is 960 x 640. Each page is 451 x 588, inset 26 px from the cover's
outer edge and 3 px from the centre line. Text starts 38 px inside each page. The
spine gutter is 10 px wide. The faction ribbon hangs from the bottom edge 150 px left of centre; the
Settings ribbon hangs from the top edge 112 px in from the right.

## The assets

### Page.tga — parchment
* **Size:** 512 x 512. **Render size:** 451 x 588 (stretched, not tiled). **Full colour.**
* **Used for:** both pages. The right page is the same file mirrored horizontally
  (left-right flip), so a toasted left edge becomes the right page's outer edge.
* **Must have:** fully opaque alpha everywhere. Any transparent pixel shows the
  leather cover through the page. Darkened or toasted edges should run around all
  four sides; the inner edge (toward the spine) gets a shadow gradient from code.
* **Keep it quiet:** text, maps and ornaments are drawn over the whole surface, so
  stains and fibres should stay low contrast.

### Leather.tga — cover
* **Size:** 256 x 256. **Render:** tiled at native size across the 960 x 640 cover
  and the controller-legend tab under the bottom-right corner (tinted there to
  0.55, 0.45, 0.35, so it reads lighter). **Full colour.**
* **Must have:** seamless tiling on both axes, fully opaque.

### Corner.tga — gilt corner guards
* **Size:** 64 x 64. **Render size:** 72 x 72, one per corner, 1 px inside the cover
  edge. **Full colour** with alpha.
* **Orientation:** design the top-left guard; the other three are mirrored.
* **Must have:** transparent where the parchment or leather should show. Anything
  in the inner 50 px square toward the centre of the book covers the page edge.

### Stitch.tga and StitchV.tga — cover thread
* **Size:** 32 x 8 and 8 x 32 (the same design rotated). **Render:** 8 px thick lines
  8 px inside the cover edge, repeating at native size along the full edge, drawn
  at 75% alpha. **Full colour** with alpha.
* **Must have:** seamless repeat along the long axis.

### Lace.tga — cord lacing the spine
* **Size:** 32 x 32. **Render:** a 26 px wide strip down the centre of the book,
  36 px short of the top and bottom, repeating vertically at native size, 90%
  alpha. **Full colour** with alpha. It is drawn over the inner edges of both pages.
* **Must have:** seamless vertical repeat.

### Strap.tga — spare
* **Size:** 128 x 32. A buckled leather strap, no longer drawn; kept for anyone who wants
  to put straps back on the cover.

### Vine.tga — inked corner vines
* **Size:** 128 x 128. **Render size:** 130 x 130, in the two outer corners of each
  page, 10 px in from the page edge. **Tinted** faded ink at 60% alpha.
* **Orientation:** design the top-left corner (vines running along the top and left
  edges); other corners are mirrored. White with alpha only.
* **Keep clear:** the region more than ~60 px from both edges, which text runs through.

### Compass.tga — compass rose watermark
* **Size:** 256 x 256. **Render:** 210 x 210 in the bottom-right of the left page at
  14% alpha, and 140 x 140 in the centre of the map area at 35% when no chart is
  available. **Tinted** faded ink. White with alpha only.

### Brass.tga — close stud
* **Size:** 64 x 64. **Render size:** 32 x 32 at the top-right of the cover.
  **Full colour** with alpha; brightened ~15% on hover.

### Cross.tga — close glyph
* **Size:** 32 x 32. **Render size:** 18 x 18 centred on the stud. **Tinted** dark
  brown (64, 38, 13). White with alpha only.

### Ribbon.tga — cloth bookmark
* **Size:** 64 x 128. **Portion used:** rows 0 to 112 of 128 (the bottom 16 rows are
  cropped). **Render size:** 66 x 100 for the Settings ribbon hanging from the top
  edge, 60 x 96 for the faction ribbon hanging from the bottom edge. **Tinted**
  Settings gold, Alliance blue or Horde red; brightened 25% on hover. White with
  alpha only: weave, folds and fraying go in the alpha and in grey values below
  white (which darken the tint).
* **Orientation:** hangs downward; the notched tail is at the bottom. Content on the
  ribbon: a label at 26 px from the top and a 22 px icon at 46 px from the top
  (Settings), or a 34 px crest at 36 px from the top (faction). Keep that band free
  of strong texture.

### RibbonShadow.tga — ribbon drop shadow
* **Size:** 64 x 128, same crop and render sizes as Ribbon, drawn 3 px right and
  4 px down behind it. **Full colour:** a black, blurred silhouette with alpha.

### Gear.tga — settings icon
* **Size:** 32 x 32. **Render size:** 22 x 22 on the Settings ribbon. **Tinted** cream.
  White with alpha only.

### Lens.tga — search icon
* **Size:** 32 x 32. **Render size:** 18 x 18 at the right end of the search box.
  **Tinted** ink. White with alpha only.

### Scroll.tga — heading banner
* **Size:** 256 x 64. **Portion used:** rows 8 to 56 of 64. **Render size:** 38 px tall
  for section headings, stretched horizontally to the heading's width plus 70 px
  (roughly 120 to 190 px); 240 x 40 for the title banner. **Full colour** with alpha.
* **Orientation:** a horizontal strip. The heading text sits 24 px from the left edge,
  vertically centred, in rubric red, so the banner must stay pale across the middle.
  The ends get compressed when the banner is narrow; keep end details simple.

### DropCapField.tga — illuminated initial, field
* **Size:** 64 x 64. **Render size:** 42 x 42 and 44 x 44. **Tinted** Alliance blue or
  Horde red. White with alpha only; a lighter centre reads as inner glow.
* **Keep inside** the frame below: the field is drawn under DropCapFrame.

### DropCapFrame.tga — gilt frame
* **Size:** 64 x 64. **Render size:** 42 x 42 and 44 x 44 around the initials, and
  54 x 54 around the item icon. **Full colour** with alpha.
* **Must have:** a fully transparent centre. The item icon shows through from 5 px
  inside each edge (at 54 px), so the opaque frame must be at most ~6 of 64 texels
  wide, plus corner ornaments that may intrude a little further.

### Flourish.tga — ornamental divider
* **Size:** 256 x 32. **Render size:** 300 x 38 under the item title, 280 x 30 under
  "Where to look". **Tinted** faded ink. White with alpha only.
* **Orientation:** horizontal, symmetrical about the centre, with the ornament
  vertically centred.

### Rule.tga — tapering rule
* **Size:** 256 x 16. **Render size:** 12 px tall, stretched from roughly 100 to 330 px
  wide, running from the end of "Recently consulted" to the page margin. **Tinted**
  faded ink. White with alpha only.
* **Orientation:** anchored on the left, fading out toward the right.

### Diamond.tga — list bullet
* **Size:** 16 x 16. **Render size:** 9 x 9 beside each provenance line. **Tinted** gold.
  White with alpha only.

### MapEdge.tga — the chart's toasted rim
* **Size:** 512 x 256. **Render size:** 324 x 225, overlapping the 296 x 197 map by
  14 px on every side. **Full colour** with alpha.
* **Must have:** a transparent centre. The map tiles sit 14 px (about 22 texels
  horizontally, 16 vertically) inside the texture's edge; the rim may feather
  inward over the map, but anything opaque further in hides the map.

### Arrow.tga — page-turn arrow
* **Size:** 32 x 32. **Render size:** 18 x 18, beside the "Next Page" / "Previous Page"
  label centred above the left page's number. **Tinted** faded ink, ink on hover. White
  with alpha only.
* **Orientation:** as drawn it reads as pointing right in the client; the Previous Page arrow is the same file flipped horizontally.

## Art that is not in Media

* **Faction crests** on the ribbon and above the title come from the game client
  (`UI-PVP-Alliance` / `UI-PVP-Horde` or the equivalent atlases). To supply your own,
  add `Media/CrestAlliance.tga` and `Media/CrestHorde.tga` (64 x 64, full colour,
  transparent background, emblem filling the square) and change the `CREST` table
  near the top of `WhereIsIt_Book.lua` to point `file` at them with texcoords 0..1.
  The one above the title is drawn desaturated at 55% alpha; the one on the ribbon
  is drawn as painted at 34 x 34.
* **Item icons** are the game's own.
* **Map tiles** are the game's own map art, drawn desaturated and tinted olive sepia.
* **Minimap button** uses the game's `INV_Misc_Book_11` icon and standard minimap
  button ring. The addon list icon in `WhereIsIt.toc` is the same book icon.
* **Controller glyphs** in the legend are the game's gamepad atlases.
