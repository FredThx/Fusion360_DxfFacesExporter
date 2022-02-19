import adsk.core
import os
from pathlib import Path
from ...lib import fusion360utils as futil
from ...lib import my_utils

from ... import config
import gettext

my_fusion = my_utils.MyFusion360()

locale_dir = Path(__file__).resolve().parent.parent.parent/'locale'
try:
    traduction = gettext.translation("base", localedir=locale_dir, languages=[my_fusion.get_language()])
    traduction.install("base")
except:
    gettext.install("base")


app = adsk.core.Application.get()
ui = app.userInterface


CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = _('Export to DXF')
CMD_Description = _('Export faces to DXF files.')

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')
    
    inputs = args.command.commandInputs
    # Selection faces
    faces_input = inputs.addSelectionInput('faces_input', _('Faces to export'), _('Select planes faces to export'))
    faces_input.setSelectionLimits(0)
    faces_input.addSelectionFilter('Faces')
    
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    #futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    #futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    #futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    '''When user click OK button
    '''
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')
    inputs = args.command.commandInputs
    faces_input = inputs.itemById('faces_input')
    faces = []
    for i in range(faces_input.selectionCount):
        faces.append(faces_input.selection(i).entity)
    futil.log(f'faces : {faces}')
    if faces:
        #Ask for a path to export dxf files
        folderdlg = ui.createFolderDialog()
        folderdlg.title = _('Please select a folder to save dxf files:')
        reponse = folderdlg.showDialog()
        if reponse == adsk.core.DialogResults.DialogOK:
            folder = folderdlg.folder
            design = app.activeProduct # Active Design
            rootComp = design.rootComponent #Root component
            sketches = rootComp.sketches #Sketches collection
            #create one sketch by face, export it in dxf and delete it
            names = {}
            files_exported = []
            for face in faces:
                try:
                    dxf_sketch = sketches.add(face)
                except:
                    ui.messageBox(_("Error on selection : not a plane face. This face is ignored."))
                else:
                    if face.body.name in names:
                        names[face.body.name]+=1
                        name = f"{face.body.name} ({names[face.body.name]})"
                    else:
                        names[face.body.name]=0
                        name = face.body.name
                    fullpath = os.path.join(folder, name) + '.dxf'
                    dxf_sketch.saveAsDXF(fullpath)
                    dxf_sketch.deleteMe()
                    futil.log(f'DXF file created : {fullpath}')
                    files_exported.append(fullpath)
            msg = str(len(files_exported)) + ' ' + _("file(s) created.") + "\n"
            for file in files_exported:
                msg+= f"\t{file}\n"
            ui.messageBox(msg)


'''
# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        inputs.areInputsValid = True
    else:
        inputs.areInputsValid = False
'''        


def command_destroy(args: adsk.core.CommandEventArgs):
    '''This event handler is called when the command terminates.
    '''
    global local_handlers
    local_handlers = []
