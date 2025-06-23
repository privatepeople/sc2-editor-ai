# Dynamic Pathing Blockers

Dynamic Pathing Blockers let you build pathing zones that can be switched on and off during gameplay. This ability is based on the fact that they are actually units, meaning that they can be shown or hidden through trigger actions. Hiding a unit suspends its footprint, removing its pathing accordingly. When the blocker is shown again, its pathing will be restored.

There are a number of uses for pathing on the fly like this. Most notably, you can restrict access to certain portions of the map until a condition or quest-type action is met. Dynamic pathing blockers will also show their footprints in the Terrain Editor, making them easier to work with than any other solutions for creating temporary blockages.

## Creating Dynamic Pathing Blockers

You can find pre-made dynamic pathing blockers in the Units Palette by searching for the term 'Dynamic'.

The name of each blocker typically notes its footprint size and shape, as well as the type of pathing it blocks. Dynamic pathing blockers are not to be confused with the dynamic pathing fill option in the Pathing Layer. The former is a pathing zone that can be altered during game-time, while the latter fills an area in the Editor with a 'No Pathing' zone.

You can also build dynamic pathing blockers from scratch using the template PATHINGBLOCKER during unit creation, as shown in the below.

-------------------------------------------------------------------------------

**Unit Properties**

- Object Type: [Unit ▼]
- Name: Dynamic Pathing Blocker
- ID: DynamicPathingBlocker [Suggest]
- Unit Type: [Generic ▼]
  - [ ] Defines Default Values
- Parent: [PATHINGBLOCKER ▼]
  - [ ] Show Non-Default
- Editor Prefix: (None)
- Editor Suffix: (None)
- Object Family: [(None) ▼]
- Race: [Zerg ▼]
- Object Type: [(None) ▼]
- Field Values:
  - ○ Do Not Change
  - ◎ Set To Parent Value
  - ○ Copy From:
    - (None) [-] [Choose]

-------------------------------------------------------------------------------

Once you've created it, you'll need to set the pathing blocker's 'Footprint' field to the desired Footprint object. It also needs to be connected to a unit actor in order to connect it to its standard models. The blueprint for a common blocker is shown below.

-----------------------------------------------------------------------------------------------------

- Dynamic Pathing Blocker 3x3 (Diagonal)
  - Actors
    - Pathing Blocker 3x3 Diagonal
  - Footprints
    - Footprint 3x3 Diagonal
  - Models
    - Invisible
    - Pathing Blocker 1x1
    - Pathing Blocker 3x3
    - Pathing Blocker Helper
    - Protoss Small Unit Death Low
    - Static Portrait
    - Terran Small Unit Death Low
    - Zerg Small Unit Death Low
  - Movers
    - Ground

-----------------------------------------------------------------------------------------------------

## Placing Dynamic Pathing Blockers

The placement grid is particularly useful when placing dynamic pathing blockers. You can enable it by navigating to View ▶︎ Show Placement Grid, then checking all of its options.

For this demo map, the dynamic placement blockers are used to simulate a sort of energy gate. This map uses a 'Protoss Energy Line (Blue)' doodad along with some cliff faces to give the placement blocker a visual element.

Due to the construction of the map, there is only an eight unit-wide area where the marines can pass through the gate. This is the ideal scenario to use dynamic pathing blockers, and the map has been fitted with four 'Dynamic Pathing Blocker 2x2' in order to fill the gap.

Since the path is closed off by the dynamic blockers, you can turn them on and off to give the functionality of a doorway or gate.

## Using Dynamic Pathing Blockers

Because dynamic pathing blockers are units, they will only apply their footprints when they are active on the map. You can use the trigger action 'Show/Hide Unit' to change the blocker's status, effectively switching them on and off as needed. Any other actions that can target units can be used with dynamic pathing blockers to varying effect, useful choices include 'Kill Unit', 'Create Units', and 'Move Unit Instantly'.

In the demo exercise, the dynamic pathing blockers have been added to a group during map initialization. Next, add a trigger related to Dynamic Pathing.

The Trigger List Panel of this demo map is structured as follows:

- **Trigger**: Melee Initialization
- **Trigger**: Dynamic Pathing
- **Global Variable**: Line Hidden = False \<Boolean\>
- **Global Variable**: Pathing Blockers = (Empty unit group) \<Unit Group\>

And the Dynamic Pathing Trigger is configured as follows:

-----------------------------------------------------------------------------------------------------

**Dynamic Pathing**
- **Events**  
  - Timer - Every 5.0 seconds of Real Time

- **Local Variables**  
  (None shown)

- **Conditions**  
  (None shown)

- **Actions**
  - General - If (Conditions) then do (Actions) else do (Actions)
    - If
      - Line Hidden == False
    - Then
      - Variable - Set Line Hidden = True
      - Actor - Send message \"SetOpacity 0.000000 1.000000\" to actor (Actor for Protoss Energy Line (Blue) [15.92, 16.15])
      - Unit Group - Pick each unit in Pathing Blockers and do (Actions)
        - Actions
          - Unit - Hide (Picked unit)
    - Else
      - Variable - Set Line Hidden = False
      - Actor - Send message \"SetOpacity 1.000000 1.000000\" to actor (Actor for Protoss Energy Line (Blue) [15.92, 16.15])
      - Unit Group - Pick each unit in Pathing Blockers and do (Actions)
        - Actions
          - Unit - Show (Picked unit)

-----------------------------------------------------------------------------------------------------

This trigger alters the dynamic pathing blocker's status every five seconds. When the 'Line Hidden' variable is set to False, the gate is faded in using the SetOpacity actor message. This same statement block also activates the dynamic pathing blocker with the 'Show Unit' action.

When the variable is switched to True, the opacity and blocker status are toggled with SetOpacity and 'Hide Unit' respectively. This eliminates the gate and blocker from the map, allowing units to pass through.
