# Create and registers the "Sequential Cloze v1" Note Type

import os
from aqt import mw

NOTE_TYPE_NAME = "Sequential Cloze v1"

def setup_note_type() -> None:
    models = mw.col.models
    existing = models.by_name(NOTE_TYPE_NAME)
    if existing:
        return existing
    
    # Create a Cloze-typed Note Type
    m = models.new(NOTE_TYPE_NAME)
    m['type'] = 1 # Cloze notes type in Anki
    
    # Fields requirements
    fields = ["Front", "Back", "Image", "Front Sound", "Back Sound", "Info"]
    for f_name in fields:
        fld = models.new_field(f_name)
        models.add_field(m, fld)
        
    t = models.new_template("Card 1")
    
    # Front Template HTML
    t['qfmt'] = """
<div class="anki-card-container">
  <div class="minimal-front">
    {{cloze:Front}}
  </div>
  
  {{#Image}}
  <div class="minimal-image">
    {{Image}}
  </div>
  {{/Image}}
  
  {{#Front Sound}}
  <div class="minimal-sound front-sound">
    {{Front Sound}}
  </div>
  {{/Front Sound}}
  
  <div id="raw-front" style="display:none !important;">{{Front}}</div>
</div>
"""
    
    # Back Template HTML
    t['afmt'] = """
<div class="anki-card-container">
  <div class="minimal-front">
    {{cloze:Front}}
  </div>
  
  {{#Image}}
  <div class="minimal-image">
    {{Image}}
  </div>
  {{/Image}}
  
  <hr id="answer-splitter">
  
  <div class="minimal-back">
    {{Back}}
  </div>
  
  {{#Back Sound}}
  <div class="minimal-sound back-sound">
    {{Back Sound}}
  </div>
  {{/Back Sound}}
  
  {{#Info}}
  <button class="minimal-info-toggle" id="info-toggle-btn" onclick="toggleInfo(event)" aria-label="Toggle Information">
    <svg viewBox="0 0 24 24" class="info-icon">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="16" x2="12" y2="12"></line>
      <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>
  </button>
  <div class="minimal-info hidden" id="info-content">
    {{Info}}
  </div>
  {{/Info}}
  
  <div id="raw-front" style="display:none !important;">{{Front}}</div>
</div>
"""
    
    # Read embedded styles — CSS belongs on the model (m), not the template (t)
    addon_dir = os.path.dirname(__file__)
    css_path = os.path.join(addon_dir, "styles", "sequential.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            m['css'] = f.read()
    else:
        m['css'] = "/* Sequential Cloze CSS */"
        
    models.add_template(m, t)
    models.add(m)
    mw.col.models.save(m)
    return m
