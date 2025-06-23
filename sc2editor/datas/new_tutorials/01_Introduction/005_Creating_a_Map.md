# Creating A Map

The first step in any project is the creation of a new document, either a map or a mod. When you are creating a document, you'll be presented with options to help you configure your project quickly. Any of these initial configurations can be changed later within the Editor itself.

## Map Creation Options

With the Editor launched, navigate to the file tab in the top left corner of any Editor screen. The menu items in the file tab are as follows:

| Action                  | Hotkey                |
|-------------------------|-----------------------|
| New...                  | Ctrl+N                |
| Open...                 | Ctrl+O                |
| Close                   |                       |
| Save                    | Ctrl+S                |
| Save As...              |                       |
| Dependencies...         |                       |
| Publish...              |                       |
| Manage Published...     |                       |
| Convert Legacy Map...   |                       |
| Export Balance Data...  |                       |
| Test Document           | Ctrl+F9               |
| Preferences...          | Ctrl+Shift+Alt+P      |
| Configure Controls...   | Ctrl+Shift+Alt+C      |

Clicking on the New menu item in the File Tab above will take you to the 'New Document' window, where you can select the type of document you want to create. The Document Types you can select are as follows:

- **Melee Map**  
  Standard multiplayer melee map

- **Training Map**  
  Map that uses standard melee gameplay, but includes additional functionality for training, practing, or testing

- **Arcade Map**  
  Custom map with non-melee gameplay

- **Dependent Mod**  
  File containing custom data and trigger libraries which can be shared by multiple maps

- **Extension Mod**  
  Mod which may be seen and added by players as an extension on Battle.net

For this scenario, select 'Arcade Map' by clicking the button to its left, then hit 'Next' to proceed. You will be brought to the dependency section. The dependency section is structured as follows:

- **Standard**  
  - Wings of Liberty 
  - Heart of the Swarm 
  - Legacy of the Void  
  - [ ] Include Campaign Data

- **Custom**

Dependencies describe which mod files will provide assets to a project. For Standard Dependencies, you can choose whether to include Campaign Data or not via **'Include Campaign Data'**. Custom can  select from the Standard Dependencies above, as well as Warcraft III (Art Mod), Nova Covert Ops (Art Mod), Co-op Mission, etc. You can also import and select Dependencies created by other users. Or, You can proceed by navigating to the 'Custom' heading, then selecting nothing. This would provide an entirely blank project, with no mod file dependencies. In this example, you'll use the substantial archive of StarCraft assets, typically known as the 'standard dependencies'. Access to the standard dependencies is one of the primary strengths of working with the Editor.

To import the most recent iteration of StarCraft's assets, select the 'Heart of the Swarm' standard dependency, then proceed by selecting 'Next'. This will bring you to the map configuration section.

## Map Configuration

The map configuration screen is where you'll make some basic decisions about the initial look of your terrain. The effects of each option are broken down in the following table.

| Property                    | Effect                                                                                                                                                                                                                        |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dimensions (Width x Height) | Sets the initial full size of the map. You can change this later from the Map Bounds options. Dimensions range from 32 to 256 units, in increments of 8.                                                                      |
| Playable Size               | The actual area of a map in which units can path, the correction is made based on a hard-coded variable buffer on each side of the map. At some extremely small sizes this buffer is avoided.                                 |
| Size Description            | A basic description of map sizes. Options include Tiny, Small, Medium, Huge, and Epic.                                                                                                                                        |
| Use Terrain                 | Unchecking this cancels terrain generation. While you may want a terrainless map in some cases, it is functionally similar to a mod.                                                                                          |
| Texture Set                 | Selects the 'Terrain Type' for a map, this is the palette of eight textures that will be used to build the ground in your environment. This also applies to creep visuals, cliff types, lighting, and atmospheric sound sets. |
| Initial Texture             | On generation, the entire terrain will be painted this single type of the terrain set.                                                                                                                                        |
| Base Height                 | All terrain is generated at this default height. If the Add Random Height option is unchecked, the terrain will be produced as a smooth surface.                                                                              |
| Add Random Height           | Creates random distortions in the Base Height at a magnitude determined by the Strength and Variability option sliders. This is useful in producing a more naturalistic base for terrain.                                     |

Following the guidelines should give you a map. At this time, it's usually wise to save your file.
