# Sequential Cloze Revealer - Anki Add-on
# Keeps Anki's native feeling while optimizing focus for cloze deletions.

from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo, qconnect
import os

from . import note_type
from . import reviewer
from . import renderer

def init_addon() -> None:
    # Set up and register our custom note type
    note_type.setup_note_type()
    # Initialize the reviewer enhancements
    reviewer.setup_reviewer()
    # Setup configuration menus
    setup_menu()

def setup_menu() -> None:
    # Setup Action
    action_settings = QAction("Sequential Cloze Revealer Settings...", mw)
    qconnect(action_settings.triggered, reviewer.show_settings_dialog)
    mw.form.menuTools.addAction(action_settings)

# Register addon when the profile is opened
gui_hooks.profile_did_open.append(init_addon)
