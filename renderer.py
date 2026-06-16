# Custom injection of scripts and behavior into reviewer cards

import os
import re
from aqt import mw, gui_hooks

def get_payload_and_resources(card=None):
    addon_dir = os.path.dirname(__file__)
    
    # Load Javascript logic
    js_path = os.path.join(addon_dir, "js", "cloze.js")
    js_content = ""
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
            
    # Load CSS styling
    css_path = os.path.join(addon_dir, "styles", "sequential.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
    # Load configuration
    config = mw.addonManager.getConfig(__name__) or {}
    show_info = "true" if config.get("show_info_by_default", False) else "false"
    click_rev = "true" if config.get("enable_click_reveal", True) else "false"
    center_mode = "true" if config.get("center_mode", True) else "false"
    mitcent_mode = "true" if config.get("mitcent_mode", True) else "false"
    reveal_speed = str(config.get("reveal_speed", 120))
    dark_compat = "true" if config.get("enable_dark_compatibility", True) else "false"
    auto_reveal = "true" if config.get("auto_reveal_back", True) else "false"
    cloze_revealed_custom = "true" if config.get("cloze_revealed_custom", False) else "false"
    cloze_revealed_color = f'"{config.get("cloze_revealed_color", "#c00000")}"'
    cloze_hidden_custom = "true" if config.get("cloze_hidden_custom", False) else "false"
    cloze_hidden_color = f'"{config.get("cloze_hidden_color", "#0284c7")}"'
    active_cloze_idx = str(card.ord + 1) if card is not None else "0"
    
    # Build payload config script content
    payload_config = f"""
    window.MINIMAL_CLOZE_CONFIG = {{
        showInfoByDefault: {show_info},
        enableClickReveal: {click_rev},
        centerMode: {center_mode},
        mitcentMode: {mitcent_mode},
        revealSpeed: {reveal_speed},
        darkCompatibility: {dark_compat},
        autoRevealBack: {auto_reveal},
        clozeRevealedCustom: {cloze_revealed_custom},
        clozeRevealedColor: {cloze_revealed_color},
        clozeHiddenCustom: {cloze_hidden_custom},
        clozeHiddenColor: {cloze_hidden_color},
        activeClozeIdx: {active_cloze_idx}
    }};
    """
    return css_content, js_content, payload_config

def enrich_html_clozes(html, matches, active_ord):
    # Filter matches to only include clozes that are active on this card (cl_num == active_ord)
    card_active_matches = [m for m in matches if m[0] == active_ord]
    
    counter = [0]
    def repl(match):
        idx = counter[0]
        counter[0] += 1
        tag_open = match.group(0)
        
        # If there's a match corresponding to this active cloze, embed its answer & hint
        if idx < len(card_active_matches):
            cl_num, answer, hint = card_active_matches[idx]
            safe_answer = answer.replace('"', '&quot;')
            safe_hint = hint.replace('"', '&quot;')
            return re.sub(r'(?i)<span', f'<span data-answer="{safe_answer}" data-hint="{safe_hint}" data-cloze-idx="{cl_num}"', tag_open, count=1)
        else:
            # Fallback if mismatch
            return re.sub(r'(?i)<span', f'<span data-cloze-idx="{active_ord}"', tag_open, count=1)
            
    return re.sub(r'(?i)<span\b[^>]*\bclass\s*=\s*["\']?[^"\'>]*\bcloze\b[^"\'>]*["\']?[^>]*>', repl, html)

def on_card_will_render(output, card, kind) -> None:
    try:
        model = card.note().model()
        if model['name'] != "Sequential Cloze v1":
            return
    except Exception:
        pass
        
    note = card.note()
    
    # We want to find all cloze deletions across all note fields and preserve their order.
    # We use a general regex to extract all clozes {{c(d+)::(.*?)}}
    pattern = re.compile(r'{{c(d+)::(.*?)}}', re.IGNORECASE | re.DOTALL)
    matches = []
    
    for key in note.keys():
        val = note[key] or ""
        raw_matches = pattern.findall(val)
        for cl_num_str, content in raw_matches:
            cl_num = int(cl_num_str)
            parts = content.split("::")
            if len(parts) > 1:
                hint = parts[-1]
                answer = "::".join(parts[:-1])
            else:
                answer = content
                hint = ""
            matches.append((cl_num, answer, hint))
    
    css_content, js_content, payload_config = get_payload_and_resources(card)
    
    active_ord = card.ord + 1
    enriched_q = enrich_html_clozes(output.question_text, matches, active_ord)
    enriched_a = enrich_html_clozes(output.answer_text, matches, active_ord)
    
    style_tag = f"<style>{css_content}</style>"
    script_tag = f"<script>{payload_config}\n{js_content}</script>"
    
    output.question_text = enriched_q + style_tag + script_tag
    output.answer_text = enriched_a + style_tag + script_tag

def on_webview_will_set_content(web_content, context) -> None:
    class_name = context.__class__.__name__.lower()
    if not any(x in class_name for x in ("reviewer", "previewer", "card", "browser", "editor")):
        return
        
    css_content, js_content, payload_config = get_payload_and_resources()
    
    # Inject directly into head of webview
    web_content.head += f"<style>{css_content}</style>"
    web_content.head += f"<script>{payload_config}\n{js_content}</script>"

def on_reviewer_did_show_question(*args, **kwargs) -> None:
    if mw.reviewer and mw.reviewer.web:
        mw.reviewer.web.eval("if (typeof setupClozeInteractions === 'function') { setupClozeInteractions(); }")

def on_reviewer_did_show_answer(*args, **kwargs) -> None:
    if mw.reviewer and mw.reviewer.web:
        mw.reviewer.web.eval("if (typeof setupClozeInteractions === 'function') { setupClozeInteractions(); }")

# Register standard card rendering hooks
try:
    gui_hooks.card_will_render.append(on_card_will_render)
except Exception as e:
    try:
        from anki.hooks import card_will_render
        card_will_render.append(on_card_will_render)
    except Exception as e:
        pass

# Register supporting webview and show hooks
try:
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
    gui_hooks.reviewer_did_show_answer.append(on_reviewer_did_show_answer)
except Exception as e:
    pass
