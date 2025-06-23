# Units

A Unit is an interactive game object. Despite the term being thrown around in a lot of contexts, in the Data Editor the term 'unit' refers very specifically to a data type placed directly into the game to be manipulated by players. Selecting a unit in the Data Editor will give you a breakdown like the one shown below.

-------------------------------------------------------------------------------

- Archon
  - Abilities
    - Attack
    - High Templar - Mergeable
    - Move
    - Progress Rally
    - Stop
  - Actors
    - Archon
    - Archon Attack
    - Archon Attack Beam
    - Archon_Death
    - Generic Attack Damage Model
    - Generic Attack Damage Sound
    - Generic Attack Impact Model
    - Generic Attack Impact Sound
    - Generic Attack Launch Model
    - Generic Attack Launch Sound
  - Behaviors
    - Massive Void Ray Vulnerability
  - Buttons
    - Attack
    - Hold Position
    - Move
    - Patrol
    - Set Rally Point
    - Stop
  - Effects
    - Archon - Psionic Shockwave (Damage)
  - Models
    - Archon
    - Archon Attack Beam
    - Archon Death
    - Hallucination Death
    - Invisible
    - Portrait - Archon
    - Protoss Medium Unit Death
    - Protoss Small Unit Death Low
    - Terran Small Unit Death Low
    - Zerg Small Unit Death Low
  - Movers
    - Ground
  - Sounds
    - Archon_Attack
    - Archon_AttackImpact
    - Archon_AttackLaunch
    - Archon_Death
    - Archon_Explode
    - Archon_Help
    - Archon_Pissed
    - Archon_Ready
    - Archon_What
    - Archon_Yes
    - Sentry_HallucinationDeathLarge
  - Upgrades
    - Protoss Ground Armor Level 1
    - Protoss Ground Armor Level 2
    - Protoss Ground Armor Level 3
    - Protoss Ground Armors
    - Protoss Ground Weapons
    - Protoss Ground Weapons Level 1
    - Protoss Ground Weapons Level 2
    - Protoss Ground Weapons Level 3
    - Protoss Shields
    - Protoss Shields Level 1
    - Protoss Shields Level 2
    - Protoss Shields Level 3
  - Weapons
    - Archon - Psionic Shockwave

-------------------------------------------------------------------------------

The unit shown above is the Archon, as displayed on the top of its fairly extensive data hierarchy. The length of the list shown here should give you an impression of the unit data type's main purpose, to serve as a container for various other types of Game Data, Art and Sound Data, and Actors. You can investigate units in the Data Editor by navigating to them via + ▶︎ Edit Game Data ▶︎ Units.

The unit data type is distinguished from other data types by the fact that it can be placed into the game and receive inputs, things like player commands, interactions with other units, and orders from an AI. Communicating these interactions to its connected data types makes the unit one of the primary ways in which data is turned into gameplay.

As you can see, much of the data in the Editor ends up leading to a unit. The direct contributors are Abilities, Actors, Behavior, Movers, and Weapons. The relationship between these categories and the Units type is described below.

## Abilities

A unit has space for up to 32 abilities. These abilities determine much of its functionality. Common abilities present in a unit include attack, move, stop, hold position, and patrol. These abilities are primarily added to a unit through the 'Abilities' field shown below.

-------------------------------------------------------------------------------

**Object Values**

**<u>Abilities</u>**

| Index | Ability             | **+**
|-------|---------------------| :-:
| 0     | Stop                | **-**
| 1     | Attack              | **↑**
| 2     | Move                | **↓**
| 3     | Queen - Build       |
| 4     | Queen - Burrow      |
| 5     | Queen - Larva Swarm |
| 6     | Stalker - Blink     |

**<u>Ability</u>** 

Selection: Stalker - Blink  
[(All - Race) ▼] [(All - Ability Type) ▼]  
Search: (None)
- Shatter
- Single Recall
- Snipe DoT
- Spawn Changeling Target
- Spectre Shield
- **Stalker - Blink**
- Taunt
- Temporal Rift
- Test Zerg
- Thor - 250mm Strike Cannons

View: ◎ Tree ○ List  

-------------------------------------------------------------------------------

Once added, the abilities are tied into gameplay using the 'Command Card' field. Adding a button to the command card portion of the unit's UI allows player inputs to trigger abilities.

## Actors

Actors mainly add art and sound assets into a unit. More specifically, each unit is home to an Actor that shares its name. These hook in the unit's 3D model, portrait, death animation, and operational sounds. Many units also have an attack actor that handles the visual and audio components of their weapons. These actors are linked to the unit in their actor messages.

## Behaviors

Behaviors can exist in the scope of a unit, giving it passive abilities such as auras or timed life. Behaviors are added to a unit using the 'Behaviors' field, as shown below.

-------------------------------------------------------------------------------

**Object Values**

**<u>Behaviors</u>**

| Index | Behavior                               | **+**
|-------|----------------------------------------| :-:
| 0     | Mothership - Cloak Field               | **-**
| 1     | Massive Void Ray Vulnerability         | **↑**
| 2     | Mothership Reset Energy                | **↓**

**<u>Behavior</u>** 

Selection: Mothership - Cloak Field  
[(All - Race) ▼] [(All - Behavior Type) ▼]  
Search: (None)
- Massive Void Ray Vulnerability
- Maximum Thrust
- Mercenary Cyclone Missiles
- Mercenary Sensor Dish
- Mercenary Shield
- Mine Drone
- Mineral Shield
- Mineral Shield
- Mothership - Recalled (Post Recall)
- **Mothership - Cloak Field**

View: ◎ Tree ○ List  

-------------------------------------------------------------------------------

## Movers

A unit will have a mover that that dictates its basic movement. Any unit without a mover cannot use move commands. Common movers for units include Ground, Fly, Burrowed, and Cliff Jumper. Projectiles also contain movers, typically more complex ones that simulate dynamic movement. You can customize a unit's movement further within the unit's movement fields, allowing you to set things like Speed, Turning Rate, and Acceleration. Movers are set up within a unit's 'Movers' field.

-------------------------------------------------------------------------------

**Object Values**

**<u>Mover^</u>**  
Selection: Punisher Grenades Weapon  
[(All - Mover Type) ▼]  
Search: (None)
- Mothership Core Weapon Weapon
- Mothership Core Weapon Weapon Close
- Needle Spines Weapon
- Noxious Turret
- Photon Cannon Weapon
- **Punisher Grenades Weapon**
- Reaper Jump Down
- Reaper Jump Up
- Release Auto Turret Weapon
- Seeker Missile
- Spine Crawler Tentacle Extend Long
- Spine Crawler Tentacle Extend Short

View: ◎ Tree ○ List  

-------------------------------------------------------------------------------

## Weapons And Turrets

Weapons grant a unit the ability to attack. Without a weapon, attack commands are unavailable. They operate in a relatively straightforward manner. It begins with a unit being targeted, either by a player or the AI. The weapon will then create an effect at the target. If the target unit is in range and the weapon's cooldown period has expired, the weapon will fire, playing an animation, applying its effects, and launching a missile if appropriate. Weapons can also be stacked, giving a unit multiple attacks that each have their own effects, range, cooldowns, and so forth.

Each weapon can also be configured with a turret. Turrets are a special data type responsible for aiming at their attack targets. This aiming creates a timed rotation of the turret before firing, which provides both a visual and gameplay element. Weapons and turrets are added to a unit using their respective fields, 'Weapons' and 'Turrets'.
