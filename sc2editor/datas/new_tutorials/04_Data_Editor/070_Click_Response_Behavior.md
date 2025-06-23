# Click Response Behavior

The Click Response Behavior applies an effect in response to a player's clicks on its hosting unit. This is an esoteric behavior that is used in StarCraft's data dependencies just once, inside each map tileset's local wildlife, the critters. If you weren't aware, critters in StarCraft, and in the lineage of --Craft games, exhibit some spontaneous behavior after being clicked repeatedly. If you haven't had the pleasure, there are far worse ways to spend your time than testing this behavior now.

Despite its lack of traditional use, the click response behavior shows an interesting direct relationship between player input and a data effect. It's worth investigating.

## Demoing Click Response Behavior

Open the demo map provided with this article. There you'll find a small Zerg base with a flock of mutalisks drifting outside.

This course has been configured to allow the player to spawn mutalisks from the hatcheries for free and at an accelerated pace. You'll take advantage of this by adding a custom click response behavior that destroys mutalisks after a series of clicks.

Start assembling the behavior by moving to the Data Editor and navigating to the behaviors tab. If the tab is not already open you can launch it by navigating to + ▶︎ Edit Game Data ▶︎ Behaviors. Right-click inside the main behaviors window and select 'Add Behavior'.

In the behavior creation window, enter 'Mutalisk Destroy' as the name, then click 'Suggest' to generate an ID. Now set the 'Behavior Type' to 'Click Response'. The finished creation window should like this.

-------------------------------------------------------------------------------

**Behavior Properties**

- Object Type: [Behavior ▼]
- Name: Mutalisk Destroy 
- ID: MutaliskDestroy [Suggest]
- Behavior Type: [Click Response ▼]
  - [ ] Defines Default Values
- Parent: [CBehaviorClickResponse ▼]
  - [ ] Show Non-Default
- Editor Prefix: (None)
- Editor Suffix: (None)
- Race: [(None) ▼]
- Field Values:
  - ○ Do Not Change
  - ◎ Set To Parent Value
  - ○ Copy From:
    - (None) [-] [Choose]

-------------------------------------------------------------------------------

Click 'Ok' to finish the creation and return to the main Data Editor screen.

## Setting The Behavior'S Fields

Once you've created the behavior, select it to edit its fields. First, move to the 'Count' field, where you will set the number of clicks required to apply the behavior. Double click the field to launch a 'Object Values' window and set the 'Count' value to 5.

-------------------------------------------------------------------------------

**Object Values**

**<u>Count^</u>**  
5

-------------------------------------------------------------------------------

Next, move to the 'Count Delay' field. Double click the field to launch another 'Object Values' window and set its value to 0.5. This will set a timer that runs between clicks. If this value is exceeded, the click count will be reset. This can be useful if the behavior needs some sort of protection against being set off accidentally during normal use.

-------------------------------------------------------------------------------

**Object Values**

**<u>Count Delay^</u>**  
0.5 \<0 .. xx\>

-------------------------------------------------------------------------------

Now move to the 'Count Effect' field, select it, and double click to launch its editing window. This field will set the effect to be triggered in response to the clicks. This is a good location to come back to later for experimentation, but for now select 'Suicide'. This will command to unit to be removed on repeated clicking.

-------------------------------------------------------------------------------

**Object Values**

**<u>Count Effect^</u>**  
Selection: Suicide  
[(All - Race) ▼] [(All - Effect Type) ▼]  
Search: (None)
- Sheep - Sheep
- Siege Tank - Arclite Cannon (Damage)
- Spine Crawler - Spine Crawler (Damage)
- Splash Damage
- Spore Crawler - Spore Crawler (Damage)
- Stalker - Entropy Lance (Damage)
- **Suicide**
- Suicide Remove
- Talons Missile Damage
- Tempest Damage
- Thermal Lances Friendly Damage
- Thor - 250mm Strike Cannons (Damage)
- Thor - 250mm Strike Cannons (Dummy)
- Thor - Anti Air (Damage)
- Thor Hand Gun Splash Damage Target

View: ◎ Tree ○ List  

-------------------------------------------------------------------------------

Now select 'Ok' to finish the behavior's construction. The finished fields should look as they do in the below.

| Field               | Mutalisk Destroy          |
|---------------------|---------------------------|
| Count               | 5                         |
| Count Delay         | 0.5000                    |
| Count Effect        | Suicide                   |
| Editor Categories   | AbilityorEffectType:Units |
| Name                | Mutalisk Destroy          |
| Alignment           | Neutral                   |

## Applying The Click Response Behavior

The behavior is now completely prepared and ready to be hooked into gameplay. One nice attribute of this behavior type is that you can slot it directly into a unit, making it quite easy to set up. This is sensible, as the behavior grants an effect that responds directly to player input, so the behavior's most natural location is within the unit itself. You can make this connection by navigating to the units tab or opening it via + ▶︎ Edit Game Data ▶︎ Units. From here, select the 'Mutalisk' and move to its 'Behaviors' field.

Double click the 'Behaviors' field to launch the 'Object Values' window. Right-click inside the 'Behaviors' box and select 'Add Value'. This will add a blank behavior to the unit, as shown below.

Once created, highlight the new value and find the 'Mutalisk Destroy' behavior with either the window's search feature or the scroll bar.

-------------------------------------------------------------------------------

**Object Values**

**<u>Behaviors</u>**

| Index | Behavior                       | **+**
|-------|--------------------------------| :-:
| 0     | Mutalisk Destroy               | **-**
|       |                                | **↑**
|       |                                | **↓**

**<u>Behavior</u>** 

Selection: Mutalisk Destroy  
[(All - Race) ▼] [(All - Behavior Type) ▼]  
Search: Mutalisk
- Click Response
  - **Mutalisk Destroy**

View: ◎ Tree ○ List  

-------------------------------------------------------------------------------

Click 'Ok' to select the behavior. At this point, you have one last change to make to the unit. By default, units do not respond to player clicks as a data event. They may be clickable and useable within the gameplay view, but as a signal they produce no event on the data side of things. To correct this, highlight the 'Mutalisk' and navigate to its 'Flags' field. Double click the field to launch it, then move to the 'No Click Event' flag and deselect it.

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
- [x] No Highlight Event
- [ ] No Portrait Talk

-------------------------------------------------------------------------------

Click 'Ok' to return to the main Data Editor view. The map is now complete and you can run the 'Test Document' feature. If you inspect a mutalisk inside the map, you'll find that they're now tagged with a behavior status.

Clicking on this mutalisk five times will reveal the design of this behavior.
