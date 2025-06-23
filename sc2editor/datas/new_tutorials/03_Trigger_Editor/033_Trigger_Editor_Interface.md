# Trigger Editor Interface

The Trigger Editor is a construction-site for triggers, actions, events, and all the other elements that make up the logic of the trigger system. The moment you start working in the Trigger Editor, the logic you build will be made active in the map immedaitely, enforcing rules, building mechanics, and creating gameplay.

## The Interface

The Trigger Editor offers a clean, ordered representation of all the logic elements active in a project. Any developers with programming experience will note the resemblance to a standard text editor. The lynchpin of this interface is the Trigger List Panel, shown below example.

- **Map Triggers**
  - **Folder**: ====== MAIN ======
    - **Folder**: Global Variables
    - **Folder**: Initialization
    - **Folder**: Debug
      - **Trigger**: DEBUG - S2
      - **Trigger**: DEBUG - S3
  - **Folder**: ====== GAMEPLAY ======
    - **Folder**: General Scripts
    - **Folder**: Environment
    - **Folder**: Section 1
    - **Folder**: Section 2
    - **Folder**: Section 3
    - **Folder**: Particle Cannons (Bonus Objective)
    - **Folder**: Achievements
    - **Folder**: Victory/Defeat
      - **Trigger**: Defeat - Zeratul Dies
      - **Trigger**: Defeat - Escape Failed
      - **Trigger**: Victory - Escape Complete
      - **Trigger**: Victory Sequence
      - **Trigger**: Victory
      - **Trigger**: Defeat
      - **Trigger**: Victory Cheat
      - **Trigger**: Defeat Cheat
    - **Folder**: Tips
  - **Folder**: ====== OBJECTIVES ======
    - **Folder**: Main Objective - Investigate Temple
    - **Folder**: Main Objective - Destroy Void Catalyst
    - **Folder**: Main Objective - Escape
    - **Folder**: Main Objective - Zeratul Must Survive
    - **Folder**: Bonus Objective - Destroy Particle Cannons
  - **Folder**: ====== CINEMATIC ======
    - **Folder**: Cinematic Variables
    - **Folder**: Intro Cinematic
    - **Folder**: Mid - Antechamber
    - **Folder**: Mid - Void Catalyst Destroyed
    - **Folder**: Victory Cinematic

Inside the Trigger List Panel you'll find a list of all the active trigger elements in a project. As well as providing an overview, this will be your primary means of navigating your project. Selecting an element in this panel will display its information in the middle of your screen, inside the Trigger Content Panel, shown below example.

-----------------------------------------------------------------------------------------------------

**Defeat - Zeratul Dies**
- **Events**  
  - Unit - Zeratul dies

- **Local Variables**  
  (None shown)

- **Conditions**  
  - GameOver == False

- **Actions**
  - Trigger - Turn (Current trigger) Off
  - Variable - Set GameOver = True
  - -------- Prevent new scenes, cinematics, etc. from being queued up.
  - Trigger - Pause the action queue
  - Trigger - Clear the action queue (Clear the active action)
  - -------- Wait a few seconds to let death anims and sounds play
  - General - Wait 2.0 Real Time seconds
  - Trigger - Run Objective - Zeratul Must Survive - Failed (Check Conditions. Don't Wait until it finishes)
  - Campaign - Display to (All players) the Mission Failed message: \"Zeratul has been slain.\" (Format Message)
  - **Trigger - Run Defeat (Check Conditions. Don't Wait until it finishes)**

-----------------------------------------------------------------------------------------------------

Depending on the type of element you've selected, this panel can take on a number of different layouts.

When the Use Subviews option is enabled, this view will also introduce a Trigger Content Panel Subview, which shows the fields of an element alongside any available tooltips, shown below example.

-----------------------------------------------------------------------------------------------------

* **Run Trigger**
  * **Trigger**: Defeat
  * **Check**: Check Conditions
  * **Wait**: Don't Wait

-----------------------------------------------------------------------------------------------------

* Run <u>Defeat</u> (<u>Check Conditions</u>, <u>Don't Wait</u> until it finishes)

-----------------------------------------------------------------------------------------------------

its actions, or reaches a \"Wait\" action. If Trigger B has a \"Wait\" action, and the Wait parameter of \"Run Trigger\" was set to Don't Wait, then Trigger A will resume execution. If the Wait parameter was set to Wait, then Trigger A will not resume execution until Trigger B has completed or returned.

-----------------------------------------------------------------------------------------------------

As your project grows, you'll find another manageability option available in the form of the Trigger Explorer. Enabling this will append a viewer to the Trigger List Panel showing a breakdown of the components inside the currently selected element. You can use this to scan through a larger project's components as quickly as possible, shown below example.

- **Trigger**: Defeat - Zeratul Dies
  - **Trigger**: Defeat
  - **Global Variable**: GameOver = False \<Boolean\>
  - **Trigger**: Objective - Zeratul Must Survive - Failed
  - **Global Variable**: Zeratul = No Unit \<Unit\>

Projects can grow to include libraries, which are collections of trigger elements shared between multiple maps. All of the standard, pre-made elements are also included in a map via libraries. You can find a list of all the libraries currently in a map in the Libraries Panel.

The segment of the Main Toolbar available from this module is the Trigger Bar.

All of the Trigger Editor's viewing and creation options are made available here for your convenience. Below you'll find a table that breaks down the options available from the Trigger Bar.

| Action                   | Effect                                                                                                                                                                |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Back                     | Reverts commands backward through the Trigger Editor history.                                                                                                         |
| Forward                  | Reverts commands forwards through the Trigger Editor history.                                                                                                         |
| View Raw Data            | Changes the view from plain-language to raw script identifiers and Galaxy function calls.                                                                             |
| Show Libraries           | Toggles the Libraries Panel on or off.                                                                                                                                |
| Use Subviews             | Toggles the Trigger Content Panel Subview on or off.                                                                                                                  |
| New Element              | Creates a new element of the type that is currently selected.                                                                                                         |
| New Folder               | Creates a folder in the Trigger List Panel.                                                                                                                               |
| New Comment              | Creates a comment at the current cursor location.                                                                                                                     |
| New Trigger              | Creates a trigger in the Trigger List Panel.                                                                                                                              |
| New Event                | Creates an event in the Trigger Content Panel.                                                                                                                        |
| New Condition            | Creates a condition in the Trigger Content Panel.                                                                                                                     |
| New Action               | Creates an action in the Trigger Content Panel.                                                                                                                       |
| New Condition Definition | Creates a condition definition in the Trigger List Panel.                                                                                                                 |
| New Action Definition    | Creates an action definition in the Trigger List Panel.                                                                                                                   |
| New Function             | Creates a function in the Trigger List Panel.                                                                                                                             |
| New Parameter            | Creates a parameter in an active definition within the Trigger Content Panel.                                                                                         |
| New Preset Type          | Creates a preset in the Trigger List Panel.                                                                                                                               |
| New Preset Value         | Creates a value in an active preset within the Trigger Content Panel.                                                                                                 |
| New Record               | Creates a record in the Trigger List Panel.                                                                                                                               |
| New Sub-function type    | Creates a sub-function in a currently active function within the Trigger Content Panel. For this, you must have the Sub-functions flag checked in 'Function Options'. |
| New Variable             | Creates a Global Variable in the Trigger List Panel or a Local Variable in the Trigger Content Panel depending on cursor position.                                        |

## Viewing Options

Using the View Raw Data option will translate the plain-language statements of the Trigger Editor into the Galaxy function calls.

This can be useful if you'd like to move into script editing. Moreover, you can use the View Script option to look at the actual game scripts. Selecting this option will launch the Script Test window.
