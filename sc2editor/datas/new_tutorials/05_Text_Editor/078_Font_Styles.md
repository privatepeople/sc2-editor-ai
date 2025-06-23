# Font Styles

Font Styles allow you to change the basic presentation of your text. Font styles don't need to be particularly elaborate or exotic. They represent any distinction made to a font from the default text used by the game.

## Creating A Font Style

Creating font styles lets you use font assets from outside the standard dependencies. You can set up styles with any choice of existing or imported fonts, but for this exercise you'll use a free font sample of OpenSans. First, import the font using the Importer. You can get there via Module ▶︎ Import. There, right-click inside the white box and select 'Import Files', then locate the font file, either a .ttf or .otf, and click 'Ok'. Saving your project after the import.

Font styles themselves are created from the Text Editor. To build a font style, navigate there via Modules ▶︎ Text. Move to the 'Font Styles' heading and right-click in the main listing. Select 'Add Style' to begin.

In the 'Style Properties' pop up, set the 'Name' to 'OpenSans18'. This denotes the font type and its intended size.

-------------------------------------------------------------------------------

**Style Properties**  

Name: OpenSans18  
Template: [(None) ▼]  

-------------------------------------------------------------------------------

Once the font style has been created, you can configure it using the panel on the right-hand side of the Text Editor. In this case, set Font Height to 18, Horizontal Justify to Left, and Vertical Justify to Middle. Set the text's color to white. The set fields should look as follows.

-------------------------------------------------------------------------------

Basic  
- Font: OpenSans-ExtraBold.ttf
- Font Height: 18
- Horizontal Justify: [Left ▼]
- Vertical Justify: [Middle ▼]
- Shadow Offset: 0
- Outline Width: 0

Colors  
- Text: (255,255,255), (255,255,255)
- Disabled: (0,0,0), (0,0,0)
- Highlight: (0,0,0), (0,0,0)
- Hotkey: (0,0,0), (0,0,0)
- Hyperlink: (0,0,0), (0,0,0)
- Glow: (0,0,0), (0,0,0)

Flags  
- [ ] Bold
- [ ] Glow
- [ ] Hint Style LCD
- [ ] Hint Style LCD Vertical
- [ ] Hint Style Light
- [ ] Hint Style Normal
- [ ] Hinting Auto
- [ ] Hinting Default
- [ ] Hinting Off
- [ ] Inline Justification
- [ ] Italic
- [ ] Outline
- [ ] Shadow
- [ ] Tight Gradient
- [ ] Uppercase

-------------------------------------------------------------------------------

Turn your attention to the 'Text Preview' to get a feel for the style.

## Create Font Style From Template

From here you can create more font styles using the 'OpenSans18' style as a template. This will set all fields of the child style to that of its parent. This option is a useful timesaver, you can use it to build out a family of styles that has a degree of consistency.

Create a new font style from a template by navigating to 'Add Font Style' in the Text Editor. Name the style 'OpenSans48' then set its 'Template' to 'OpenSans18', as shown below.

-------------------------------------------------------------------------------

**Style Properties**  

Name: OpenSans48  
Template: [OpenSans18 ▼]  

-------------------------------------------------------------------------------

Configure this style's Font Height to 48, then check the Shadow flag and set a Shadow Offset of 2. Add an Outline Width of 4 then set the two color choices to (R175, G237, B230) and (R133, G220, B139). Alternately, you can choose to experiment with how the font looks now. This should leave you with a style panel that looks as shown in the below.

-------------------------------------------------------------------------------

Basic  
- Font: OpenSans-ExtraBold.ttf
- Font Height: 48
- Horizontal Justify: [Left ▼]
- Vertical Justify: [Middle ▼]
- Shadow Offset: 2
- Outline Width: 4

Colors  
- Text: (175,237,230), (133,220,139)
- Disabled: (0,0,0), (0,0,0)
- Highlight: (0,0,0), (0,0,0)
- Hotkey: (0,0,0), (0,0,0)
- Hyperlink: (0,0,0), (0,0,0)
- Glow: (0,0,0), (0,0,0)

Flags  
- [ ] Bold
- [ ] Glow
- [ ] Hint Style LCD
- [ ] Hint Style LCD Vertical
- [ ] Hint Style Light
- [ ] Hint Style Normal
- [ ] Hinting Auto
- [ ] Hinting Default
- [ ] Hinting Off
- [ ] Inline Justification
- [ ] Italic
- [ ] Outline
- [x] Shadow
- [ ] Tight Gradient
- [ ] Uppercase

-------------------------------------------------------------------------------

The preview will now show a more substantial typeface.

## Applying A Font Style

Once created, you can apply font styles from anywhere in the Editor that you can edit text. The Text Editor is a top-down solution for changing the content or font styles of any text within a project. Navigating to the 'Text' tab will display a list of all the project text.

Highlighting an instance of text will push its details to the right-hand side of the screen, which consists of three sub-panels, Text Entry, Text Controls, and Text Preview.

You can apply a style to a highlighted piece of text by selecting it from the 'Apply Style' dropdown.

-------------------------------------------------------------------------------

Text Entry:  
**Just Another StarCraft II Map**

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">[Apply Style: ]</td>
    <td style="border: none;">[OpenSans48 ▼]</td>
    <td style="border: none;"></td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;">Color: </td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">[Apply Color]</td>
    <td style="border: none;">[Apply Gradient]</td>
    <td style="border: none;">[Apply Color]</td>
  </tr>
  <tr>
    <td style="border: none;">[Insert:]</td>
    <td style="border: none;">[Data Reference ▼]</td>
    <td style="border: none;">(None) [Choose Field...]</td>
    <td style="border: none;">[Create Formula...]</td>
  </tr>
</table>

-------------------------------------------------------------------------------

Clicking the 'Apply Style' button will finish the operation by appending a style tag around the text entry. A style tag will precede the raw text with \<s val ='Style Name"\> and follow it with \</s\>. These elements instruct the game to change the contained text's style at run-time. For now, you can preview the text output from the Text Preview panel.

-------------------------------------------------------------------------------

Text Entry:  
\<s val="OpenSans48"\>Just Another StarCraft II Map\</s\>  

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">[Apply Style: ]</td>
    <td style="border: none;">[OpenSans48 ▼]</td>
    <td style="border: none;"></td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;">Color: </td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">[Apply Color]</td>
    <td style="border: none;">[Apply Gradient]</td>
    <td style="border: none;">[Apply Color]</td>
  </tr>
  <tr>
    <td style="border: none;">[Insert:]</td>
    <td style="border: none;">[Data Reference ▼]</td>
    <td style="border: none;">(None) [Choose Field...]</td>
    <td style="border: none;">[Create Formula...]</td>
  </tr>
</table>

-------------------------------------------------------------------------------

Alternately, you can style text while you fill any text field in the Trigger Editor. Selecting a text field and navigating to the 'Value' source should bring up another editor reminiscent of the Text Editor.

-------------------------------------------------------------------------------

**Text**

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">Type:</td>
    <td style="border: none;">[Text ▼]</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">[ ▼]</td>
  </tr>
</table>

Source: ○ Function ○ Preset ○ Variable ◎ Value ○ Expression ○ Custom Script  

Text:  
<br>

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">[Apply Style: ]</td>
    <td style="border: none;">[(None) ▼]</td>
    <td style="border: none;"></td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;">Color: </td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">[Apply Color]</td>
    <td style="border: none;">[Apply Gradient]</td>
    <td style="border: none;">[Apply Color]</td>
  </tr>
  <tr>
    <td style="border: none;">[Insert:]</td>
    <td style="border: none;">[Data Reference ▼]</td>
    <td style="border: none;">(None) [Choose Field...]</td>
    <td style="border: none;">[Create Formula...]</td>
  </tr>
</table>

[Edit] <input type="checkbox" disabled checked> Show Style Controls <input type="checkbox" disabled> Show Preview

-------------------------------------------------------------------------------

As before, highlight any inputted text to unlock the Text Controls. Select a style with the 'Apply Style' dropdown and click the button itself to style the text. The results of this process are shown below.

-------------------------------------------------------------------------------

**Text**

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">Type:</td>
    <td style="border: none;">[Text ▼]</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">[ ▼]</td>
  </tr>
</table>

Source: ○ Function ○ Preset ○ Variable ◎ Value ○ Expression ○ Custom Script  

Text:  
**\<s val="OpenSans48">Demo Styled Text</s\>**

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">[<b>Apply Style:</b>]</td>
    <td style="border: none;">[OpenSans48 ▼]</td>
    <td style="border: none;"></td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;">Color: </td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
    <td style="border: none;">(0,0,0)</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">[Apply Color]</td>
    <td style="border: none;">[Apply Gradient]</td>
    <td style="border: none;">[Apply Color]</td>
  </tr>
  <tr>
    <td style="border: none;">[Insert:]</td>
    <td style="border: none;">[Data Reference ▼]</td>
    <td style="border: none;">(None) [Choose Field...]</td>
    <td style="border: none;">[Create Formula...]</td>
  </tr>
</table>

[Edit] <input type="checkbox" disabled checked> Show Style Controls <input type="checkbox" disabled> Show Preview

-------------------------------------------------------------------------------

In this case, you can test the updated text by launching the map.
