// Sequential Cloze Revealer - Reviewer Frontend Script

// Explicitly bind functions to window/global scope for reliable access from python .eval()
window.toggleInfo = function(event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    const info = document.getElementById("info-content");
    if (info) {
        info.classList.toggle("hidden");
    }
};

window.setupClozeInteractions = function() {
    // Only apply interaction logic if the custom .anki-card-container is present
    const container = document.querySelector(".anki-card-container");
    if (!container) {
        if (!window._setupClozeRetryCount) window._setupClozeRetryCount = 0;
        if (window._setupClozeRetryCount < 10) {
            window._setupClozeRetryCount++;
            setTimeout(window.setupClozeInteractions, 50);
        }
        return;
    }
    window._setupClozeRetryCount = 0; // reset
    
    const config = window.MINIMAL_CLOZE_CONFIG || {
        showInfoByDefault: false,
        enableClickReveal: true,
        centerMode: true,
        revealSpeed: 120,
        autoRevealBack: true,
        clozeRevealedCustom: false,
        clozeRevealedColor: "#c00000",
        clozeHiddenCustom: false,
        clozeHiddenColor: "#0284c7",
        activeClozeIdx: "1"
    };
    
    // Apply default styles or timing from configuration
    document.documentElement.style.setProperty('--reveal-speed', config.revealSpeed + "ms");
    
    if (config.clozeRevealedCustom && config.clozeRevealedColor) {
        document.documentElement.style.setProperty('--cloze-revealed-color', config.clozeRevealedColor);
    } else {
        document.documentElement.style.setProperty('--cloze-revealed-color', 'inherit');
    }
    
    if (config.clozeHiddenCustom && config.clozeHiddenColor) {
        document.documentElement.style.setProperty('--cloze-hidden-color', config.clozeHiddenColor);
    } else {
        document.documentElement.style.setProperty('--cloze-hidden-color', 'inherit');
    }
    
    // Dynamically apply Center / Left layout
    const applyCentering = function() {
        const containers = [
            document.body,
            document.querySelector(".card"),
            document.querySelector(".anki-card-container")
        ];
        containers.forEach(function(el) {
            if (el) {
                if (config.mitcentMode) {
                    el.classList.add("center-mode", "mitcent-mode");
                    el.classList.remove("left-mode");
                } else if (config.centerMode) {
                    el.classList.add("center-mode");
                    el.classList.remove("left-mode", "mitcent-mode");
                } else {
                    el.classList.add("left-mode");
                    el.classList.remove("center-mode", "mitcent-mode");
                }
            }
        });
    };
    applyCentering();
    setTimeout(applyCentering, 0);
    setTimeout(applyCentering, 100);

    // Initial info field visibility state
    const infoContent = document.getElementById("info-content");
    if (infoContent) {
        if (config.showInfoByDefault) {
            infoContent.classList.remove("hidden");
        } else {
            infoContent.classList.add("hidden");
        }
    }
    
    const isBackCard = document.getElementById("answer-splitter") !== null || document.querySelector(".minimal-back") !== null;
    const rawEl = document.getElementById("raw-front");
    const frontContentEl = document.querySelector(".minimal-front");
    
    // Multi-platform enrichment: Parse raw Front if available and not yet marked
    if (rawEl && frontContentEl && !frontContentEl.hasAttribute("data-interactive-rendered")) {
        frontContentEl.setAttribute("data-interactive-rendered", "true");
        let rawText = rawEl.innerHTML || rawEl.textContent || "";
        
        // Find raw clozes to determine active index
        const clozPattern = /\{\{c(\d+)::(.*?)\}\}/gi;
        const rawClozes = [];
        let match;
        while ((match = clozPattern.exec(rawText)) !== null) {
            const clNum = parseInt(match[1], 10);
            const content = match[2];
            const parts = content.split("::");
            let hint = "";
            let answer = content;
            if (parts.length > 1) {
                hint = parts[parts.length - 1];
                answer = parts.slice(0, -1).join("::");
            }
            rawClozes.push({ num: clNum, answer: answer.trim(), hint: hint.trim() });
        }
        
        // Detect active cloze index
        let activeIdx = 1;
        if (config.activeClozeIdx && config.activeClozeIdx !== "0") {
            activeIdx = parseInt(config.activeClozeIdx, 10);
        } else {
            const nativeClozeSpan = frontContentEl.querySelector(".cloze");
            if (nativeClozeSpan) {
                const natText = (nativeClozeSpan.textContent || nativeClozeSpan.innerText || "").trim();
                const plainNativeText = frontContentEl.innerText || frontContentEl.textContent || "";
                for (let i = 0; i < rawClozes.length; i++) {
                    const rc = rawClozes[i];
                    if (rc.hint && natText.includes(rc.hint)) {
                        activeIdx = rc.num;
                        break;
                    }
                }
                if (activeIdx === 1) {
                    for (let i = 0; i < rawClozes.length; i++) {
                        const rc = rawClozes[i];
                        if (!plainNativeText.includes(rc.answer)) {
                            activeIdx = rc.num;
                            break;
                        }
                    }
                }
            }
        }
        
        // Rebuild HTML with interactive span elements
        const enrichedHtml = rawText.replace(/\{\{c(\d+)::(.*?)\}\}/gi, function(match, clNumStr, content) {
            const clNum = parseInt(clNumStr, 10);
            const parts = content.split("::");
            let hint = "";
            let answer = content;
            if (parts.length > 1) {
                hint = parts[parts.length - 1];
                answer = parts.slice(0, -1).join("::");
            }
            const isActive = (clNum === activeIdx);
            
            const safeAnswer = answer.replace(/"/g, "&quot;");
            const safeHint = hint.replace(/"/g, "&quot;");
            const originalText = hint ? "[" + hint + "]" : "[...]";
            
            if (isActive) {
                if (isBackCard) {
                    return '<span class="cloze active" data-cloze-idx="' + clNum + '" data-answer="' + safeAnswer + '" data-hint="' + safeHint + '" data-state="revealed" data-original-text="' + originalText + '" style="pointer-events: auto !important; cursor: pointer !important;">' + answer + '</span>';
                } else {
                    return '<span class="cloze active" data-cloze-idx="' + clNum + '" data-answer="' + safeAnswer + '" data-hint="' + safeHint + '" data-state="hidden" data-original-text="' + originalText + '" style="pointer-events: auto !important; cursor: pointer !important;">' + originalText + '</span>';
                }
            } else {
                return '<span class="cloze passive" data-cloze-idx="' + clNum + '" data-answer="' + safeAnswer + '" data-hint="' + safeHint + '" data-state="revealed" data-original-text="' + originalText + '" style="pointer-events: auto !important; cursor: pointer !important;">' + answer + '</span>';
            }
        });
        
        frontContentEl.innerHTML = enrichedHtml;
    }
    
    // Select all clozes (native or reconstructed)
    const clozes = document.querySelectorAll(".cloze");
    
    clozes.forEach(function(cloze) {
        const text = (cloze.innerText || cloze.textContent || "").trim();
        const isBlank = cloze.hasAttribute("data-answer") || text.includes("...") || (text.startsWith("[") && text.endsWith("]"));
        
        const clozeIdxAttr = cloze.getAttribute("data-cloze-idx");
        let isActive = false;
        if (clozeIdxAttr && config.activeClozeIdx && config.activeClozeIdx !== "0") {
            isActive = (clozeIdxAttr === config.activeClozeIdx);
        } else {
            isActive = isBlank || cloze.classList.contains("active");
        }
        
        const hint = cloze.getAttribute("data-hint") || "";
        
        if (isActive) {
            cloze.classList.add("active");
            cloze.classList.remove("passive");
            
            if (isBackCard) {
                cloze.setAttribute("data-state", "revealed");
                if (!cloze.getAttribute("data-answer")) {
                    cloze.setAttribute("data-answer", cloze.innerHTML);
                }
                if (!cloze.getAttribute("data-original-text")) {
                    cloze.setAttribute("data-original-text", hint ? "[" + hint + "]" : "[...]");
                }
            } else {
                cloze.setAttribute("data-state", "hidden");
                if (!cloze.getAttribute("data-original-text")) {
                    cloze.setAttribute("data-original-text", cloze.innerHTML);
                }
            }
        } else {
            cloze.classList.add("passive");
            cloze.classList.remove("active");
            cloze.setAttribute("data-state", "revealed");
        }
        
        // Setup click/touchend handlers
        if (config.enableClickReveal) {
            if (!cloze.hasAttribute("data-has-listener")) {
                cloze.setAttribute("data-has-listener", "true");
                
                const handleInteract = function(e) {
                    e.stopPropagation();
                    e.preventDefault(); // Critically prevent card flipping on click
                    
                    if (cloze.classList.contains("active")) {
                        if (cloze.getAttribute("data-state") === "hidden") {
                            window.revealCloze(cloze);
                        } else {
                            window.hideCloze(cloze);
                        }
                    } else if (cloze.classList.contains("passive")) {
                        window.togglePassiveCloze(cloze);
                    }
                };
                
                cloze.addEventListener("click", handleInteract);
                cloze.addEventListener("touchend", handleInteract, { passive: false });
                
                cloze.addEventListener("dblclick", function(e) {
                    e.stopPropagation();
                    e.preventDefault();
                    if (cloze.classList.contains("active")) {
                        window.hideCloze(cloze);
                    }
                });
            }
        }
    });
    
    window.updateClozeSequencing();
    
    // Set up Keyboard Shortcuts
    document.onkeydown = function(e) {
        const key = e.key.toLowerCase();
        
        if (e.code === "Space" || e.key === " ") {
            const hiddenCloze = document.querySelector(".cloze.active[data-state='hidden']");
            if (hiddenCloze) {
                e.preventDefault();
                window.revealCloze(hiddenCloze);
                return;
            }
            if (window.pycmd) {
                window.pycmd("ans");
            }
        }
        
        if ((e.code === "Space" || e.key === " ") && e.shiftKey) {
            e.preventDefault();
            const activeClozes = document.querySelectorAll(".cloze.active[data-state='hidden']");
            activeClozes.forEach(function(c) { window.revealCloze(c); });
            return;
        }
        
        if (key === "a") {
            e.preventDefault();
            if (window.pycmd) {
                window.pycmd("ans");
            }
        }
        
        if (key === "i") {
            e.preventDefault();
            window.toggleInfo();
        }
    };
};

window.updateClozeSequencing = function() {
    const hiddenActive = document.querySelectorAll(".cloze.active[data-state='hidden']");
    document.querySelectorAll(".cloze").forEach(function(el) {
        el.classList.remove("current-cloze");
    });
    if (hiddenActive.length > 0) {
        hiddenActive[0].classList.add("current-cloze");
    }
};

window.revealCloze = function(el) {
    if (el.getAttribute("data-state") === "hidden") {
        el.style.opacity = "0";
        setTimeout(function() {
            const actualAnswer = el.getAttribute("data-answer");
            if (actualAnswer) {
                el.innerHTML = actualAnswer;
            } else {
                el.innerHTML = el.innerHTML.replace(/[[]]/g, '');
            }
            el.setAttribute("data-state", "revealed");
            el.style.opacity = "1";
            window.updateClozeSequencing();
            
            // Auto open the back card if this was the last hidden active cloze
            const remainingHidden = document.querySelectorAll(".cloze.active[data-state='hidden']");
            const conf = window.MINIMAL_CLOZE_CONFIG || { autoRevealBack: true };
            if (remainingHidden.length === 0 && window.pycmd && conf.autoRevealBack) {
                window.pycmd("ans");
            }
        }, 65);
    }
};

window.hideCloze = function(el) {
    if (el.getAttribute("data-state") === "revealed" && el.classList.contains("active")) {
        el.style.opacity = "0";
        setTimeout(function() {
            const originalText = el.getAttribute("data-original-text") || "[...]";
            el.innerHTML = originalText;
            el.setAttribute("data-state", "hidden");
            el.style.opacity = "1";
            window.updateClozeSequencing();
        }, 65);
    }
};

window.togglePassiveCloze = function(el) {
    if (el.style.opacity === "0.3" || el.classList.contains("hidden-passive")) {
        el.classList.remove("hidden-passive");
        el.style.opacity = "1";
    } else {
        el.classList.add("hidden-passive");
        el.style.opacity = "0.3";
    }
};
