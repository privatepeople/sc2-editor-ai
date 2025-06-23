# Trigger Organization

As your project grows and incorporates more and more elements, it's probably going to trend toward some degree of disorder. This can be pretty hazardous. In programming, the quality of work often depends on how easily the developer is able to understand how the whole system works together. A big mess of elements is directly opposed to this sort of clear understanding, so developing a system for organizing your project is a must. To support this, there are several tools in the Trigger Editor to help you clean up.

For example, our current Trigger List Panel looks like this:

- **Trigger**: Untitled Trigger 007
- **Condition**: Untitled Condition 005
- **Event**: Untitled Event 007
- **Global Variable**: Untitled Variable 004 = No Actor \<Actor\>
- **Trigger**: Untitled Trigger 003
- **Event**: Untitled Event 005
- **Condition**: Untitled Condition 002
- **Trigger**: Untitled Trigger 002
- **Function**: Untitled Function 001
- **Action**: Untitled Action 003
- **Condition**: Untitled Condition 001
- **Function**: Untitled Function 004
- **Trigger**: Melee Initialization
- **Global Variable**: Untitled Variable 005 = No Actor \<Actor\>
- **Event**: Untitled Event 006
- **Function**: Untitled Function 002
- **Function**: Untitled Function 003
- **Action**: Untitled Action 001
- **Action**: Untitled Action 002
- **Condition**: Untitled Condition 006
- **Global Variable**: Untitled Variable 001 = 0 \<Integer\>
- **Event**: Untitled Event 004
- **Function**: Untitled Function 005
- **Condition**: Untitled Condition 004
- **Event**: Untitled Event 002
- **Condition**: Untitled Condition 003
- **Trigger**: Untitled Trigger 001
- **Event**: Untitled Event 001
- **Global Variable**: Untitled Variable 006 = No Actor \<Actor\>
- **Global Variable**: Untitled Variable 003 = 0 \<Integer\>
- **Event**: Untitled Event 003
- **Action**: Untitled Action 004

Events, Conditions, Actions, Functions, Triggers, Global Variables, etc. are all mixed together, making them difficult to see. This can be neatly organized as follows:

- **Library**: Trigger Organization
  - **Event Label Folder**: Events
    - **Event**: Event Definition #1
    - **Event**: Event Definition #2
    - **Event**: Event Definition #3
  - **Condition Label Folder**: Conditions
    - **Comment**: Listing of Condition Definitions
    - **Condition**: Condition Definition #1
    - **Condition**: Condition Definition #2
    - **Condition**: Condition Definition #3
  - **Action Label Folder**: Actions
    - **Comment**: Listing of Action Definitions
    - **Action**: Action Definition #1
    - **Action**: Action Definition #2
    - **Action**: Action Definition #3
  - **Function Label Folder**: Functions
    - **Comment**: Listing of Function Definitions
    - **Function**: Function #1
    - **Function**: Function #2
    - **Function**: Function #3
  - **Trigger**: Melee Initialization
  - **Trigger Label Folder**: Triggers
    - **Trigger**: Trigger #1
    - **Trigger**: Trigger #2
    - **Trigger**: Trigger #3
  - **Variable Label Folder**: Variables
    - **Actor Label Folder**: Actors
      - **Record**: Actor Variables
      - **Global Variable**: Actor Variables \<Actor Variables\>
    - **Math Label Folder**: Math
      - **Record**: Math Variables
      - **Global Variable**: Math Variables \<Math Variables\>

## Folders

Folders are a fundamental element of organizing work on a computer, so they likely need little explanation. They work pretty much as you'd expect them to within the Editor. A Trigger Editor folder offers the ability to group items into a container object that can be opened or collapsed through its left-side + or - control.

Create a folder by right-clicking inside the Trigger List Panel and navigating to New ▶︎ New Folder, or by using the New Folder button found in the Trigger Bar.

Moving or creating a folder inside another folder will create a subfolder. You can repeat this process to create a hierarchy for your project. While you should avoid getting too carried away with this, a couple of layers of hierarchy can be a strong first step for organization. The following Trigger List Panel shows the means by which the official StarCraft campaign maps are organized, first broken into folders by their general type (MAIN, GAMEPLAY, OBJECTIVES, and CINEMATIC), then by their specific purposes, such as 'Global Variables', 'AI', or 'Victory Cinematic'.

- **Map Triggers**
  - **Folder**: ======= MAIN =======
    - **Folder**: Global Variables
    - **Folder**: Initialization
    - **Folder**: Debug
  - **Folder**: ======= GAMEPLAY =======
    - **Folder**: Starting Sequence
    - **Folder**: Create Leaderboard
    - **Folder**: Scripted Events
    - **Folder**: AI
    - **Folder**: Transmissions
    - **Folder**: Stats and Achievements
    - **Folder**: Victory/Defeat
  - **Folder**: ======= OBJECTIVES =======
    - **Folder**: Primary Objective - Kill 1500/2000/2500 Zerg
    - **Folder**: Lab Research - Protect the Protoss Archive
  - **Folder**: ======= CINEMATIC =======
    - **Folder**: Briefing Cinematic
    - **Folder**: Intro Cinematic
    - **Folder**: Midgame Cinematic
    - **Folder**: Victory Cinematic

## Comments

Comments are a tool for project documentation. They add a text element that is written directly into the Editor. These elements have no effect on gameplay and stay inside the Editor, where they provide a useful communication tool for describing how a section of a project works. You can make comments for personal use or for other users who may see your map, whether teammates or the community at large. Extended comment sections can also be used for many utility purposes, including manuals, release histories, lists of debugs codes, and to-do lists.

You can create comments from either the Trigger List Panel or the Trigger Content Panel. Do so by right-clicking in either location then navigating to New ▶︎ New Comment. Alternatively, you can also do so using the New Comment button in the Trigger Bar, which will create a comment at the cursor's current location.

Adding comments within the Trigger List Panel is considered less useful, as it tends to be messy. Still, the option is available for small notes that describe things like folder contents.

## Libraries

Libraries allow you to organize elements of the Trigger Editor into collections that you can share between projects using their import and export functions. You can see which libraries are active in a project in the Libraries Panel, which will typically include Built-In, Liberty, Swarm, Void, and so forth. These are trigger libraries from the standard dependencies, and they are the source of all pre-made actions, conditions, functions, and events in the Editor.

## Labels

Next to every Trigger Editor element is a small illustrative icon, known as a Label. Each label categorizes its element via the icon, and may also change the element's description to a color associated with the label. Whenever you create an element from the standard library in the Trigger Content Panel, it is assigned a pre-determined label.

These label presets are made available through the standard dependency libraries and may be repurposed for use in any project. An element's label is set by selecting it, right-clicking, and navigating to Label.

Setting a label for a definition will add both the icon and the chosen label to any elements of that definition. If you choose a label for an element that exists only in the Trigger List Panel such as a trigger, variable, or record, the label will only change the color of the element. Labels are also useful when searching for elements using the 'Find' function of the Trigger Editor.

If you find yourself looking for more customization, you may want to add custom labels. You can create a custom label by navigating to Data ▶︎ Modify Labels. This will launch the 'Trigger Labels' window.

Here you can set the color and label. You can set any image sized 16 x 16 px as a label icon through the Archive Browser.

## Records

Records present layouts of variables that are typically useful for templating objects. This makes them a natural organizing tool as well.

## Groups

The main Trigger Content Panel is actually composed of organizers called Trigger Groups. Each group allows you to browse a separate element of the Trigger Editor in a division of the main content panel. The Editor supports up to three groups in a given project. Opening an additional group will divide the panel space.

Viewing things in parallel, as in the above, can be an effective way of comparing different parts of your project. Overall, it offers versatility in the ways that users can configure their Editor. You can enable additional groups in the Trigger Editor view by going to View ▶︎ Show Groups. There you'll find four options for configuration.

  - Smart -- Trigger groups will be continually added or removed, depending on the current needs.
  - 1 -- Allows a single trigger group. This is the default setting.
  - 2 -- Allows two trigger groups.
  - 3 -- Allows three trigger groups.

## Tabs

Tabs are sub-panels that exist within a certain trigger group. Tabs allow you to view any number of elements and quickly navigate between them using the tab headers at the top of the Trigger Content Panel.

You can open tabs to the currently active group by selecting multiple elements in the Trigger List Panel, then hitting Enter. Once opened, you can close tabs by right-clicking the tab header and navigating to either Close Tab (CTRL+Shift+A) or Close All Tabs (CTRL+Alt+A). The combination of tabs and groups offers a significant amount of customization in how you organize the Trigger Editor.
