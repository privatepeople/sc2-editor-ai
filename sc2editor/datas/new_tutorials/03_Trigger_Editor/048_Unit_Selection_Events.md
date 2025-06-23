# Unit Selection Events

The 'Unit Selection' category of events can be very useful when it comes to adding ways to interact with units. These events are triggered by changes in the state of a Unit that occur in response to the mouse actions of a Player. There are three types of change, which are broken down in the table below.

| Event                 | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit Selected       | Triggers the first time a Player clicks on the Unit, this selects the Unit. The Unit now enters its Selected state. Once the Unit is in this state, it cannot be selected again until it is deselected by the Player and returns to its Basic State. A unit may also be deselected when the Player selects any other game entity. A Player may select many units with a single action either by using a box select with the mouse or holding the CTRL key while clicking a unit.            |
| Unit Clicked        | Triggers every time the Unit is clicked with the mouse by a Player. Can occur indefinitely. The first click on a deselected Unit meets the criteria for both a Unit Clicked event and a Unit Selected event. A Player may only click on a single unit at a time.                                                                                                                                                                                                                            |
| Unit Highlighted/ | The highlighted and unhighlighted events trigger is based on the mouse position of the Player as it enters or leaves the area of the Unit respectively. When the mouse pointer first crosses the area of the Unit, the unit triggers its Unit Highlighted event and becomes Highlighted. When the mouse pointer leaves the area of the Highlighted unit, the unit triggers its Unit UnHighlighted event, returning to its Basic state. A Player can only highlight a single unit at a time. |
| UnHighlighted     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

## Selection States

StarCraft's UI offers some help with identifying selection states. Consider the following example. Here are four marines standing in a row. The first marine is not selected, and the mouse is not moved to the marine. The second marine is not selected, but the mouse is moved to the marine. The third marine is selected, and the mouse is moved to the marine. The fourth marine is selected, but the mouse is not moved to the marine.

The first marine here shows the unit in its Basic state, it is neither Selected nor Highlighted and there are no special alterations to its model as a result. In the second marine, the mouse has entered that unit's area, making the unit Highlighted. At this point, a Unit Highlighted event would trigger. Holding the cursor over a unit in the Highlighted state causes a pair of illustrative UI changes; the mouse pointer is altered to a targeting reticle and the unit is marked with a dashed circle. The color of the circle depends on the unit's owner, for a unit belonging to the player it is green, for an allied or neutral unit it is yellow, and for an enemy unit it is red.

In the third marine, the unit has been clicked for the first time, the unit is now Selected. This change results in the both the Unit Selected and Unit Clicked events triggering. A Selected unit's model is marked in the UI with an unbroken circle. This circle has the same alliance-based coloring as the Highlighted cursor. In this case, the cursor remains on top of the unit, making the unit both Highlighted and Selected. As a result, both sets of UI features are superimposed. The unit has both the selection circle and the highlighted circle, and the cursor remains the highlighting reticle.

In the fourth marine, the mouse has been moved from the area of the unit, resulting in the Unit Unhighlighted event. The unit is still selected and still marked with the unbroken selection circle. The cursor has returned to its basic pointer as the unit is no longer being highlighted.

## Selection Flags

Although each unit in the StarCraft engine can be clicked and highlighted, the data messages that trigger the events are not enabled by default. You'll have to edit some game data to enable these behaviors. Navigate to the Data Editor then to + ▶︎ Edit Game Data ▶︎ Units. Find the Unit type that is going to be monitored for selection events. In this Unit, navigate to the 'Unit: Flags' field and double click to launch an 'Object Values' window.

Scroll down through the unit flags until you reach 'No Click Event' and 'No Highlight Event'. These flags control the sending of the Unit Clicked and Unit Highlighted/UnHighlighted events respectively. Once these flags have been unchecked, the unit type will propagate any events of their respective type to the Trigger Editor, and should look as they do in the below.

-------------------------------------------------------------------------------

**Object Values**

**<u>Flags</u>**  
- [ ] Always Check Collision
- [x] Army Select
- [ ] Bounce
- [ ] Built On Optional
- [ ] Buried
- [x] Camera Follow
- [ ] Cannon Tower
- [ ] Clear Rally On Death
- [ ] Cloaked
- [ ] Core
- [ ] Create Visible
- [ ] Destructible
- [ ] Footprint Always Ignore Height
- [ ] Footprint Persist Rotate
- [ ] Gate
- [ ] Grant Level Kill XP
- [ ] Hero
- [ ] Hidden Cargo UI
- [ ] Hide From Harvesting Count
- [ ] Ignore Attack Alert
- [ ] Ignore Terrain Height
- [ ] Individual Subgroups
- [ ] Invulnerable
- [x] Keep Rally On TargetLost
- [x] Kill Credit
- [ ] Leech Behavior Shield Damage
- [ ] Missile
- [ ] Moonwell
- [x] Movable
- [ ] Never Think
- [ ] No Armor While Constructing
- [ ] **No Click Event**
- [ ] No Cursor
- [ ] No Death Event
- [ ] No Draw
- [ ] No Highlight Event
- [ ] No Portrait Talk

-------------------------------------------------------------------------------

## Examining Unit Selection Events

Open the demo map provided with this article, which provides a course where you can tinker with selection events. This will help to build an intuitive feel for how selection events arise from a player's actions. The course should appear as follows.

You'll see that the map contains several unit types that have been configured to accept both Unit Clicked and Unit Highlighted/UnHighlighted events via the Data Editor. Note that these units are also divided between the player, an allied player, an enemy player, and neutral. Move to the Trigger Editor to see how unit selection events will be used in this example. First, the Trigger List Panel is as follows:

- **Trigger**: Map init
- **Trigger**: Unit Highlighted
- **Trigger**: Unit UnHighlighted
- **Trigger**: Unit Selected
- **Trigger**: Unit Clicked

And here is the Trigger Content Panel:

-----------------------------------------------------------------------------------------------------

**Unit Highlighted**
- **Events**  
  - Unit Selection - Any Unit is Highlighted by Player Any Player

- **Local Variables**  
  (None shown)

- **Conditions**  
  (None shown)

- **Actions**
  - **UI - Display ((Name of (Unit type of (Triggering unit))) + \" is Highlighted\") for (All players) to Debug area**

-----------------------------------------------------------------------------------------------------

* **Text Message**
  * **Message**: Combine Text
    * **Text 1**: Name Of Unit Type
      * **Unit Type**: Unit Type Of Unit
        * **Unit**: Triggering Unit
    * **Text 2**: \" is Highlighted\"
  * **Players**: All Players
  * **Message Area**: Debug

-----------------------------------------------------------------------------------------------------

* Display <u>(</u><u>(</u>Name of <u>(</u>Unit type of (<u>Triggering Unit</u>))) + <u>\" is Highlighted\"</u>) for (<u>All players</u>) to <u>Debug</u> area

-----------------------------------------------------------------------------------------------------

The map has been set with some utility revealers, alliance controls, and invulnerability triggers within the 'Map Init' trigger. Beyond that, there is a trigger for each major unit selection event: Highlighted, UnHighlighted, Selected, and Clicked. Like the 'Unit Highlighted' example trigger shown above, these triggers respond to their events with a debug message sent to screen space. Using this setup, the map can give direct feedback for every possible selection action a player can make. You can explore it by hitting the 'Test Document' button in the Editor.

Some illustrative examples of unit selection events are shown below.

Here the enemy marauder has been moused over and then clicked. Doing so has produced a Unit Highlighted, Unit Clicked, and Unit Selected event in sequence. Note that the last two events happen at the same time in the Editor, but the clicked event will always occur first in any list. You can also see that the Marauder's UI alterations each display a red coloring, indicating its status as an enemy.

In this next case, a box selection has been made around the units. Despite the units being covered by the box overlay, this alone does not trigger any events.

Releasing the box selection results in all units belonging to the player being selected at once. Each unit individually triggers a Unit Selected event, then proceeds to a Selected state.

In this example, a neutral Lyote critter has been repeatedly clicked. This demonstrates that a Unit can accept an unlimited number of player clicks, with each triggering a Unit Clicked event.
