# Create Wasd Keyboard Controls

Using the keyboard to control a game character's movement is a classic control scheme. The best known example of this is the WASD keyboard controls, in which the W, A, S, and D keys are bound to the directions up, left, right, and down. This is often used as an ergonomic, universally available option that can be operated one hand while the other uses the mouse.

Although StarCraft uses a mouse and keyboard control scheme, it does not tie any keyboard controls directly to movement. Still, this is possible for custom projects made using the Editor. Learning to implement the WASD keyboard controls can be very educational and has many practical applications in action, adventure, and simulation games.

## Keypress UI Events

A keyboard control system requires some way of getting between player inputs and the game. UI events usually suit this requirement and in this case you'll make use of the Key Pressed event. The triggers 'KeyPressDOWN' and 'KeyPressUP' create events that respond to the four keys of the WASD controls. 'KeyPressDOWN' runs when any of these keys is pushed down, while 'KeyPressUP' runs when any of these keys are released. You can see the composition of these triggers in the below.

First, configure the Trigger List Panel as follows:

- **Trigger**: Melee Initialization
- **Action**: KeyPress Detect
- **Action**: Execute Move
- **Trigger**: KeyPressDOWN
- **Trigger**: KeyPressUP
- **Global Variable**: WASD Unit = No Unit \<Unit\>
- **Global Variable**: KEYPRESS = False \<Boolean[3]\>

And the Trigger Content Panels for the 'KeyPressDOWN' and 'KeyPressUP' triggers are as follows.

-----------------------------------------------------------------------------------------------------

**KeyPressDOWN**
- **Events**  
  - UI - Player Any Player presses W key Down with shift Allow, control Allow, alt Allow
  - UI - Player Any Player presses A key Down with shift Allow, control Allow, alt Allow
  - UI - Player Any Player presses S key Down with shift Allow, control Allow, alt Allow
  - UI - Player Any Player presses D key Down with shift Allow, control Allow, alt Allow

- **Local Variables**  
  (None shown)

- **Conditions**  
  (None shown)

- **Actions**
  - General - Switch (Actions) depending on (Key Pressed)
    - Cases
      - General - If (W)
        - Actions
          - Variable - Set KEYPRESS[0] = True
      - General - If (A)
        - Actions
          - Variable - Set KEYPRESS[1] = True
      - General - If (S)
        - Actions
          - Variable - Set KEYPRESS[2] = True
      - General - If (D)
        - Actions
          - Variable - Set KEYPRESS[3] = True
    - Default

-----------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------------------------------------

**KeyPressUP**
- **Events**  
  - UI - Player Any Player presses W key Up with shift Allow, control Allow, alt Allow
  - UI - Player Any Player presses A key Up with shift Allow, control Allow, alt Allow
  - UI - Player Any Player presses S key Up with shift Allow, control Allow, alt Allow
  - UI - Player Any Player presses D key Up with shift Allow, control Allow, alt Allow

- **Local Variables**  
  (None shown)

- **Conditions**  
  (None shown)

- **Actions**
  - General - Switch (Actions) depending on (Key Pressed)
    - Cases
      - General - If (W)
        - Actions
          - Variable - Set KEYPRESS[0] = False
      - General - If (A)
        - Actions
          - Variable - Set KEYPRESS[1] = False
      - General - If (S)
        - Actions
          - Variable - Set KEYPRESS[2] = False
      - General - If (D)
        - Actions
          - Variable - Set KEYPRESS[3] = False
    - Default

-----------------------------------------------------------------------------------------------------

By separating the keys out individually, this system supports combinations of keys being pressed and released in any way the hardware supports. As a result, combinations like pressing the W and A keys together will give the proper response of moving the character both up and left at the same time.

## Key Storage Array

In order to track all concurrent key presses, this design requires an array for storage. The 'KEYPRESS' array is of the Boolean type and sized to a value of 3. Considering that arrays begin at a zero index, the total storage available here is 4 keys, enough for the entire WASD control system. Using a Boolean array allows each array value to represent whether or not a certain key is currently pressed. The keys will use the following mapping.

W == Index 0

A == Index 1

S == Index 2

D == Index 3

A True value represents pressed, while a False value represents not being pressed. All the spots in the array are set to False by default. The array itself is shown below.

-----------------------------------------------------------------------------------------------------

<table style="border-collapse: collapse; border: none;">
  <tr>
    <td style="border: none;">KEYPRESS</td>
  </tr>
  <tr>
    <td style="border: none;">Script Identifier</td>
    <td style="border: none;"><input type="checkbox" disabled checked> Based On Name</td>
  </tr>
  <tr>
    <td style="border: none;">kEYPRESS</td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;">gv_kEYPRESS</td>
    <td style="border: none;"></td>
  </tr>
</table>
<table>
  <tr>
    <td style="border: none;">Type:</td>
    <td style="border: none;"></td>
    <td style="border: none;">[Boolean ▼]</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;"></td>
    <td style="border: none;">[ ▼]</td>
  </tr>
  <tr>
    <td style="border: none;"><input type="checkbox" disabled></td>
    <td style="border: none;">Constant</td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;"><input type="checkbox" disabled checked></td>
    <td style="border: none;">Array</td>
    <td style="border: none;"></td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">Dimension:</td>
    <td style="border: none;">[1 ▼]</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;">Size:</td>
    <td style="border: none;">◎ Value: 3</td>
  </tr>
  <tr>
    <td style="border: none;"></td>
    <td style="border: none;"></td>
    <td style="border: none;">○ Constant: [(No constant integer variable found) ▼]</td>
  </tr>
  <tr>
    <td style="border: none;"><input type="checkbox" disabled></td>
    <td style="border: none;">Defines Default Value</td>
    <td style="border: none;"></td>
  </tr>
</table>

-----------------------------------------------------------------------------------------------------

Initial Value:  
- Initial Value: False

-----------------------------------------------------------------------------------------------------

<u>**False**</u>

-----------------------------------------------------------------------------------------------------

## Switch Actions

As you've already seen, the two keypress triggers will each respond to any of the four WASD keys. This saves the design from having to rely on eight separate events to monitor keyboard inputs. However, this creates a need for some control statements to properly parse the input. You can use a switch statement to solve this by providing a case for each of the four Key values. The switch statement used for the 'KeyPressUP' trigger is shown in the below.

-----------------------------------------------------------------------------------------------------

  - General - Switch (Actions) depending on (Key Pressed)
    - Cases
      - General - If (W)
        - Actions
          - Variable - Set KEYPRESS[0] = False
      - General - If (A)
        - Actions
          - Variable - Set KEYPRESS[1] = False
      - General - If (S)
        - Actions
          - Variable - Set KEYPRESS[2] = False
      - General - If (D)
        - Actions
          - Variable - Set KEYPRESS[3] = False
    - Default

-----------------------------------------------------------------------------------------------------

For each trigger, the switch statement contains a 'Set Variable' action that sets the index of the array associated with that case's Key. For the 'KeyPressUP' trigger the values are set to False, indicating that the key has been released. Conversely, for 'KeyPressDOWN' trigger the values are set to True, indicating that the key is now down.

## Keypress Detection Loop

To create a constant a feed of keypress inputs into movement logic, a loop 'KeyPress Detect' is used. The loop itself is quite extensive and has been reproduced below, annotated with comments.

-----------------------------------------------------------------------------------------------------

**KeyPress Detect**
  - **Options**: Action 

  - **Return Type**: (None)

  - **Parameters**  
    (None shown)

  - **Grammar Text**: KeyPress Detect() 

  - **Hint Text**: (None)

  - **Custom Script Code**  
    (None shown)

  - **Local Variables**  
    (None shown)

  - **Actions**
    - General - While (Conditions) are true, do (Actions)
      - Conditions
        - (WASD Unit is alive) == True
      - Actions
        - General - If (Conditions) then do multiple (Actions)
          - If Then Else
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[0] == False
                - KEYPRESS[1] == False
                - KEYPRESS[2] == False
                - KEYPRESS[3] == False
              - Then
                - Unit - Order WASD Unit to (Stop) (Replace Existing Orders)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[0] == True
                - KEYPRESS[1] == True
              - Then
                - Execute Move(145.0, 1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[0] == True
                - KEYPRESS[3] == True
              - Then
                - Execute Move(45.0, 1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[2] == True
                - KEYPRESS[1] == True
              - Then
                - Execute Move(45.0, -1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[2] == True
                - KEYPRESS[3] == True
              - Then
                - Execute Move(145.0, -1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[0] == True
              - Then
                - Execute Move(90.0, 1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[1] == True
              - Then
                - Execute Move(180.0, 1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[2] == True
              - Then
                - Execute Move(90.0, -1.0)
            - General - Else if (Conditions) then do (Actions)
              - Else If
                - KEYPRESS[3] == True
              - Then
                - Execute Move(0.0, 1.0)
        - General - Wait 0.0 Real Time seconds

-----------------------------------------------------------------------------------------------------

## Moving The Unit

'KeyPress Detect' pushes a set of instructions to the 'Execute Move' action, which handles moving the controlled unit. These instructions include an Angle and Offset that are sent to an 'Order Targeting Point' command. This command makes use of the 'Move' ability, sending the unit to a 'Point with a Polar Offset'. By sending the unit to its current position altered by the Offset, the command effectively moves the unit in the direction of the Angle by the offset magnitude.

When the Offset is set to a negative value, this actually represents moving the unit in the opposite direction. So an Angle of 145.0 with an Offset of -1.0, which occurs when the S and D keys are pressed, will send the unit in the southwest direction. When the values are an Angle of 145.0 and an Offset of 1.0, as is the case when the W and A keys are pressed, the unit is sent in the northeast direction. The 'Execute Move' action definition can be seen in the below.

-----------------------------------------------------------------------------------------------------

**Execute Move**
  - **Options**: Action 

  - **Return Type**: (None)

  - **Parameters**  
    - Angle = 0.0 \<Real\>
    - Offset = 0.0 \<Real\>

  - **Grammar Text**: Execute Move(Angle, Offset)

  - **Hint Text**: (None)

  - **Custom Script Code**  
    (None shown)

  - **Local Variables**  
    (None shown)

  - **Actions**
    - Unit - Order WASD Unit to (Move targeting ((Position of WASD Unit) offset by Offset towards Angle degrees)) (Replace Existing Orders)
  
-----------------------------------------------------------------------------------------------------

## Connecting It Together

For this demonstration, the movement system is initiated on map start. This isn't necessary, but it is the most likely scenario. Control schemes seldom change within the body of a game, but shifting the initialization actions elsewhere is still an option. The 'Melee Initialization' trigger is shown below.

-----------------------------------------------------------------------------------------------------

**Melee Initialization**
- **Events**  
  - Game - Map initialization

- **Local Variables**  
  (None shown)

- **Conditions**  
  (None shown)

- **Actions**
  - Variable - Set WASD Unit = Marine [62.87, 63.70]
  - KeyPress Detect()

-----------------------------------------------------------------------------------------------------

This trigger sets a pre-placed unit to the 'WASD Unit' variable. This makes it the controlled unit for the movement system. Additionally, the 'KeyPress Detect' loop begins, at which point it immediately starts searching for player inputs. Whenever you're working with a constantly running UI events system, you should monitor the large quantity of loop and event checks closely for performance. When designing a system like this for online use, be sure to do careful testing to ensure latency doesn't become a problem.

## Testing The Controls

Launching the map will allow you to control the marine with the WASD keys.
