# Lighting

The Editor features a robust lighting system that you can use to create a wide palette of moods, looks, and feels for your project.

## Lighting Details

Lighting is actually accomplished in a number of different ways in the StarCraft engine. You may recall seeing light sources like street lamps props and mining lights attached to characters. Some spell and ability effects can even dynamically light a scene in interesting ways, but this article will focus on global lighting effects within a map.

The lighting in a map is set to one particular style at a time. It can then be dynamically altered to other styles during gameplay. You'll find these lighting styles in an extensive data type called Lights, which is handled directly through the Data Editor. Due to the number of options available when working with lighting, the Editor also features a special tool called the Lighting Window. This interface collects all of the lighting controls and puts them alongside the pre-built lighting styles within the Editor.

## Demoing Lighting

Open the demo map provided with this article. You'll see that it contains a scene in which a bar front is lit with a default lighting setting that looks like natural sunlight. First, you'll learn how to change the lighting from day to night, then how to use triggers to slowly reintroduce daytime lighting, simulating a sunrise.

The best place to start is in the Data Editor. Lighting is applied on the basis of the current Terrain Type. This is the designation in data for the landscape controlling the textures, style of doodads, and so forth. The demo map is set to the 'Agria (Jungle)' type. Open the 'Terrain Type Tab' by clicking on the 'New Tab' + button and navigating to Edit Terrain Data ▶︎ Terrain Types. Now, set the lighting by double clicking on the 'Lighting' property as shown below.

|                           |                                       |
|---------------------------|---------------------------------------|
| Height Flags              | Air Smoothing                         |
| Hidden in Editor          | Disabled                              |
| Hide Lowest Level         | Disabled                              |
| Lighting                  | Agria                                 |
| Loading Screen            | Assets\Textures\loading-agira.dds     |
| Minimap Background Color  | (255,0,0,0)                           |
| Minimap Brighten Factor   | 0.0000                                |
| Name                      | Agria (Jungle)                        |

If you're unsure what Terrain Type your map is using, you can see it by navigating to Map ▶︎ Map Textures. The field 'Current Texture Set' will provide the answer.

Clicking on the 'Lighting' field will launch the 'Object Values' window. Find the 'Mar Sara Night Test' lighting, select it, and click 'Ok'.

-------------------------------------------------------------------------------

**Object Values**

**<u>Lighting</u>**  
Selection: Mar Sara Night Test  
[(All - Light Group) ▼]  
Search: (None)  
- Main Menu Swarm
- MainMenuSwarm_Low
- Mar Sara
- Mar Sara Day Test
- **Mar Sara Night Test**
- Meinhoff
- Monlyth
- New Folsom
- No Light
- Planet View Agria
- Planet View Char

View: ◎ Tree ○ List  

-------------------------------------------------------------------------------

Confirm that you've successfully changed the terrain's lighting by opening the Terrain Editor and selecting Render ▶︎ Show Lighting ▶︎ Game Lighting. The main view should show a much darker, twilit scene.

Now go to the Trigger Editor and open the 'Initialization' trigger. This trigger uses some actions that remove the game's UI, reveal the map for view, and apply a standard camera. Add a new 'Wait' action by right-clicking under the 'Actions' heading and navigating to New ▶︎ New Action. Set the 'Time' field of this action to 2.0. Then add the 'Set Lighting' action, using the same procedure. Set the 'Light' field to 'Mar Sara Day Test' and change the 'Blend Time' to 6.0.

-----------------------------------------------------------------------------------------------------

**Initialization**
- **Events**  
  - Game - Map initialization

- **Local Variables**  
  (None shown)

- **Conditions**  
  (None shown)

- **Actions**
  - **UI - Hide game UI for (All players)**
  - Visibility - Reveal (Entire map) for player 1 for 0.0 seconds and Do Not check cliff level
  - Camera - Apply Game Camera for player 1 over 0.0 seconds with Existing Velocity% initial velocity, 10.0% deceleration, and Include Target
  - Camera - Lock camera input for player 1
  - General - Wait 2.0 Game Time seconds
  - Envionment - Set lighting to Mar Sara Day Test, blending over 6.0 seconds

-----------------------------------------------------------------------------------------------------

* **Show/Hide Game UI**
  * **Show/Hide**: Hide
  * **Players**: All Players

-----------------------------------------------------------------------------------------------------

* <u>Hide</u> game UI for (<u>All players</u>)

-----------------------------------------------------------------------------------------------------

Shows or hides the entire game UI. When shown, the UI will be set back to the visibility state of before it was hidden.

-----------------------------------------------------------------------------------------------------

The map is now complete. If you run a test, after a brief wait, the current lighting style, 'Mar Sara Night Test' will slowly change, blending into 'Mara Sara Day Test'. Giving a night-to-day lighting transition just like a sunrise. Launch the 'Test Map' function to see the result.
