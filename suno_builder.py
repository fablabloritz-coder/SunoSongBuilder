#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suno Song Builder — Outil de structuration de chansons pour Suno AI
Gère la structure, les metatags, les multi-voix et la phonétique.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import uuid
from copy import deepcopy

# ─────────────────────────────────────────────
# Constantes & Données de référence
# ─────────────────────────────────────────────

SECTION_TYPES = [
    "INTRO",
    "VERSE",
    "PRE-CHORUS",
    "CHORUS",
    "POST-CHORUS",
    "BRIDGE",
    "HOOK",
    "INSTRUMENTAL",
    "INTERLUDE",
    "BREAK",
    "DROP",
    "OUTRO",
    "END",
    "ROUND FINAL",
]

VOICE_TYPES = ["male", "female"]

MOOD_TAGS = [
    "Explosion sonore",
    "Montée en puissance",
    "Chute brutale du rythme",
    "Changement de rythme",
    "Tempo survitaminé",
    "Ambiance oppressante",
    "Plus intimiste",
    "Doux et mélodique",
    "Crescendo dramatique",
    "Basse vrombissante",
    "Mur de guitares",
    "Batterie martelante",
    "Synthé grave",
    "Piano mélancolique",
    "Acoustique, calme",
    "Fade Out",
    "Building intensity",
    "Soft and gentle",
    "Energetic",
    "Aggressive",
    "Slow Down",
    "Epic orchestral swell",
]

PERFORMANCE_TAGS = [
    "Spoken Word",
    "Whisper",
    "Rap",
    "Harmony",
    "Choir",
    "Background Vocals",
    "Ad-lib",
    "Call and Response",
    "Duet",
    "A cappella",
    "Belting",
    "Falsetto",
    "Growl",
    "Scream",
    "Humming",
]

SONG_TEMPLATES = {
    # ── Structures classiques ──
    "Pop — Verse/Chorus standard": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("PRE-CHORUS", None, "solo", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("PRE-CHORUS", None, "solo", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "solo", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("OUTRO", None, "instrumental", "", ["Fade Out"], ""),
    ],
    "Pop — avec Post-Chorus": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("PRE-CHORUS", None, "solo", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("POST-CHORUS", None, "all", "", [], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("PRE-CHORUS", None, "solo", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("POST-CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "solo", "", ["Plus intimiste"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("OUTRO", None, "instrumental", "", ["Fade Out"], ""),
    ],
    "Rock — Énergie crescendo": [
        ("INTRO", None, "instrumental", "", ["Batterie martelante"], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("CHORUS", None, "all", "", ["Mur de guitares"], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("CHORUS", None, "all", "", ["Mur de guitares"], ""),
        ("BRIDGE", None, "solo", "", ["Chute brutale du rythme"], ""),
        ("INSTRUMENTAL", None, "instrumental", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("OUTRO", None, "all", "", [], ""),
    ],
    "Ballade — Lente et émotive": [
        ("INTRO", None, "instrumental", "", ["Piano mélancolique"], ""),
        ("VERSE", 1, "solo", "", ["Doux et mélodique"], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("CHORUS", None, "all", "", ["Montée en puissance"], ""),
        ("INTERLUDE", None, "instrumental", "", ["Plus intimiste"], ""),
        ("VERSE", 3, "solo", "", [], ""),
        ("CHORUS", None, "all", "", ["Crescendo dramatique"], ""),
        ("BRIDGE", None, "solo", "", ["Plus intimiste"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("OUTRO", None, "all", "", ["Fade Out"], ""),
    ],
    "Rap / Hip-Hop — 3 couplets": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "singer_0", "", [], "Rap"),
        ("HOOK", None, "all", "", [], ""),
        ("VERSE", 2, "singer_1", "", [], "Rap"),
        ("HOOK", None, "all", "", [], ""),
        ("BRIDGE", None, "solo", "", ["Changement de rythme"], ""),
        ("VERSE", 3, "singer_2", "", [], "Rap"),
        ("HOOK", None, "all", "", [], ""),
        ("OUTRO", None, "instrumental", "", ["Fade Out"], ""),
    ],
    "R&B — Smooth & groovy": [
        ("INTRO", None, "instrumental", "", ["Doux et mélodique"], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("PRE-CHORUS", None, "solo", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("PRE-CHORUS", None, "solo", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "solo", "", ["Plus intimiste"], "Falsetto"),
        ("CHORUS", None, "all", "", ["Crescendo dramatique"], ""),
        ("OUTRO", None, "all", "", ["Fade Out"], ""),
    ],
    "EDM / Électro — Drop": [
        ("INTRO", None, "instrumental", "", ["Synthé grave"], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("PRE-CHORUS", None, "all", "", ["Building intensity"], ""),
        ("DROP", None, "instrumental", "", ["Explosion sonore", "Tempo survitaminé"], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("PRE-CHORUS", None, "all", "", ["Building intensity"], ""),
        ("DROP", None, "instrumental", "", ["Explosion sonore", "Tempo survitaminé"], ""),
        ("BRIDGE", None, "solo", "", ["Chute brutale du rythme", "Plus intimiste"], ""),
        ("DROP", None, "instrumental", "", ["Explosion sonore"], ""),
        ("OUTRO", None, "instrumental", "", ["Fade Out"], ""),
    ],
    "Metal — Agressif": [
        ("INTRO", None, "instrumental", "", ["Batterie martelante", "Mur de guitares"], ""),
        ("VERSE", 1, "solo", "", ["Aggressive"], "Growl"),
        ("PRE-CHORUS", None, "solo", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("VERSE", 2, "solo", "", ["Aggressive"], "Growl"),
        ("PRE-CHORUS", None, "solo", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("BRIDGE", None, "instrumental", "", ["Chute brutale du rythme"], ""),
        ("INSTRUMENTAL", None, "instrumental", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], "Scream"),
        ("OUTRO", None, "instrumental", "", [], ""),
    ],
    "Country / Folk — Storytelling": [
        ("INTRO", None, "instrumental", "", ["Acoustique, calme"], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 3, "solo", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "solo", "", ["Plus intimiste"], "Spoken Word"),
        ("CHORUS", None, "all", "", ["Montée en puissance"], ""),
        ("OUTRO", None, "instrumental", "", ["Acoustique, calme", "Fade Out"], ""),
    ],
    # ── Multi-voix ──
    "Multi-Chanteurs — Duo (homme/femme)": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "singer_0", "", [], ""),
        ("PRE-CHORUS", None, "all", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", [], "Duet"),
        ("VERSE", 2, "singer_1", "", [], ""),
        ("PRE-CHORUS", None, "all", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", [], "Duet"),
        ("BRIDGE", None, "singer_0", "", ["Plus intimiste"], ""),
        ("BRIDGE", None, "singer_1", "", ["Montée en puissance"], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], "Duet"),
        ("OUTRO", None, "all", "", ["Fade Out"], "Harmony"),
    ],
    "Multi-Chanteurs — Rotation 3 voix": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "singer_0", "", [], ""),
        ("PRE-CHORUS", None, "all", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 2, "singer_1", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "all", "", ["Changement de rythme"], ""),
        ("VERSE", 3, "singer_2", "", [], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("ROUND FINAL", None, "all", "", ["Montée en puissance"], ""),
        ("OUTRO", None, "instrumental", "", [], ""),
    ],
    "Multi-Chanteurs — Rotation 4 voix": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "singer_0", "", [], ""),
        ("PRE-CHORUS", None, "all", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 2, "singer_1", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 3, "singer_2", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "all", "", ["Chute brutale du rythme"], ""),
        ("VERSE", 4, "singer_3", "", [], ""),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("ROUND FINAL", None, "all", "", ["Montée en puissance"], ""),
        ("OUTRO", None, "instrumental", "", [], ""),
    ],
    "Multi-Chanteurs — Call & Response": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "singer_0", "", [], ""),
        ("VERSE", 2, "singer_1", "", [], "Call and Response"),
        ("CHORUS", None, "all", "", [], ""),
        ("VERSE", 3, "singer_0", "", [], ""),
        ("VERSE", 4, "singer_1", "", [], "Call and Response"),
        ("CHORUS", None, "all", "", [], ""),
        ("BRIDGE", None, "all", "", ["Plus intimiste"], "Harmony"),
        ("CHORUS", None, "all", "", ["Explosion sonore"], ""),
        ("OUTRO", None, "all", "", ["Fade Out"], ""),
    ],
    # ── Formats courts ──
    "Courte — Couplet unique + Refrain": [
        ("INTRO", None, "instrumental", "", [], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("CHORUS", None, "all", "", [], ""),
        ("OUTRO", None, "instrumental", "", [], ""),
    ],
    "Courte — Hook repeat (TikTok style)": [
        ("HOOK", None, "all", "", ["Energetic"], ""),
        ("VERSE", 1, "solo", "", [], ""),
        ("HOOK", None, "all", "", [], ""),
        ("VERSE", 2, "solo", "", [], ""),
        ("HOOK", None, "all", "", ["Explosion sonore"], ""),
    ],
    "Spoken Word / Slam": [
        ("INTRO", None, "instrumental", "", ["Plus intimiste"], ""),
        ("VERSE", 1, "solo", "", [], "Spoken Word"),
        ("INTERLUDE", None, "instrumental", "", [], ""),
        ("VERSE", 2, "solo", "", [], "Spoken Word"),
        ("CHORUS", None, "all", "", ["Montée en puissance"], ""),
        ("VERSE", 3, "solo", "", [], "Spoken Word"),
        ("OUTRO", None, "all", "", ["Fade Out"], ""),
    ],
    # ── Vide ──
    "Vide (personnalisé)": [],
}


# ─────────────────────────────────────────────
# Modèle de données
# ─────────────────────────────────────────────

class Singer:
    def __init__(self, name="", voice_type="male", phonetic="", description=""):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.voice_type = voice_type
        self.phonetic = phonetic
        self.description = description

    def suno_display(self):
        return self.phonetic if self.phonetic else self.name

    def suno_voice_tag(self):
        parts = []
        parts.append("Male Voice" if self.voice_type == "male" else "Female Voice")
        if self.description:
            parts.append(self.description)
        return ", ".join(parts)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "voice_type": self.voice_type,
                "phonetic": self.phonetic, "description": self.description}

    @classmethod
    def from_dict(cls, d):
        s = cls(d["name"], d["voice_type"], d.get("phonetic", ""), d.get("description", ""))
        s.id = d["id"]
        return s


class Section:
    def __init__(self, section_type="VERSE", number=None, assignment="all",
                 lyrics="", mood_tags=None, performance_tag="", spoken_line=""):
        self.id = str(uuid.uuid4())[:8]
        self.section_type = section_type
        self.number = number
        self.assignment = assignment
        self.lyrics = lyrics
        self.mood_tags = mood_tags or []
        self.performance_tag = performance_tag
        self.spoken_line = spoken_line

    def header_label(self):
        label = self.section_type
        if self.number:
            label += f" {self.number}"
        return label

    def to_dict(self):
        return {"id": self.id, "section_type": self.section_type,
                "number": self.number, "assignment": self.assignment,
                "lyrics": self.lyrics, "mood_tags": self.mood_tags,
                "performance_tag": self.performance_tag,
                "spoken_line": self.spoken_line}

    @classmethod
    def from_dict(cls, d):
        s = cls(d["section_type"], d.get("number"), d["assignment"],
                d.get("lyrics", ""), d.get("mood_tags", []),
                d.get("performance_tag", ""), d.get("spoken_line", ""))
        s.id = d["id"]
        return s


class SongProject:
    def __init__(self):
        self.title = "Ma Chanson"
        self.style = ""
        self.singers: list[Singer] = []
        self.sections: list[Section] = []
        self.global_note = ""

    def singer_by_id(self, sid):
        for s in self.singers:
            if s.id == sid:
                return s
        return None

    def to_dict(self):
        return {"title": self.title, "style": self.style,
                "global_note": self.global_note,
                "singers": [s.to_dict() for s in self.singers],
                "sections": [s.to_dict() for s in self.sections]}

    @classmethod
    def from_dict(cls, d):
        p = cls()
        p.title = d.get("title", "")
        p.style = d.get("style", "")
        p.global_note = d.get("global_note", "")
        p.singers = [Singer.from_dict(s) for s in d.get("singers", [])]
        p.sections = [Section.from_dict(s) for s in d.get("sections", [])]
        return p

    def generate_global_note(self):
        males = sum(1 for s in self.singers if s.voice_type == "male")
        females = sum(1 for s in self.singers if s.voice_type == "female")
        total = len(self.singers)
        if total == 0:
            return ""
        parts = [f"{total} singers"]
        if males:
            parts.append(f"{males} male{'s' if males > 1 else ''}")
        if females:
            parts.append(f"{females} female{'s' if females > 1 else ''}")
        return "[" + ", ".join(parts) + "]"

    def render_suno(self):
        lines = []
        note = self.global_note or self.generate_global_note()
        if note:
            lines.append(note)
            lines.append("")

        for sec in self.sections:
            for tag in sec.mood_tags:
                lines.append(f"[{tag}]")

            header = self._build_header(sec)
            lines.append(header)

            if sec.spoken_line:
                lines.append(f'[Voix : "{sec.spoken_line}"]')
                lines.append("")

            if sec.performance_tag and sec.assignment != "instrumental":
                lines.append(f"[{sec.performance_tag}]")

            if sec.lyrics.strip():
                lines.append(sec.lyrics.strip())

            lines.append("")

        return "\n".join(lines).strip()

    def _build_header(self, sec: 'Section'):
        label = sec.section_type
        if sec.number:
            label += f" {sec.number}"

        if sec.assignment in ("instrumental", "all", "mixed"):
            return f"[{label}]"
        elif sec.assignment == "public":
            return f"[{label} - PUBLIC]"
        else:
            singer = self.singer_by_id(sec.assignment)
            if singer:
                disp = singer.suno_display()
                vtype = singer.voice_type
                return f"[{label} - {disp} ({vtype})]"
            return f"[{label}]"


# ─────────────────────────────────────────────
# Interface graphique
# ─────────────────────────────────────────────

class SunoBuilderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Suno Song Builder")
        self.root.geometry("1450x920")
        self.root.minsize(1100, 700)

        self.project = SongProject()
        self._selected_section_idx = None
        self._singer_selection_idx = None  # track singer selection separately
        self._inhibit_singer_select = False  # prevent re-entrant selection events

        style = ttk.Style()
        style.configure("Status.TLabel", background="#2b2b3c", foreground="#a6adc8", padding=4)
        style.configure("Save.TButton", foreground="#1e1e2e")

        self._build_menu()
        self._build_ui()
        self._refresh_all()

    # ── Menu ──────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouveau projet", command=self._new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir projet (.json)", command=self._open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder projet (.json)", command=self._save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exporter pour Suno (.txt)", command=self._export_suno, accelerator="Ctrl+E")
        file_menu.add_command(label="Importer depuis .txt", command=self._import_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        tpl_menu = tk.Menu(menubar, tearoff=0)

        # Sous-menus par catégorie
        cat_classic = tk.Menu(tpl_menu, tearoff=0)
        cat_multi = tk.Menu(tpl_menu, tearoff=0)
        cat_short = tk.Menu(tpl_menu, tearoff=0)
        cat_empty = tk.Menu(tpl_menu, tearoff=0)

        for name in SONG_TEMPLATES:
            if "Multi-Chanteurs" in name:
                cat_multi.add_command(label=name, command=lambda n=name: self._apply_template(n))
            elif "Courte" in name or "Spoken" in name:
                cat_short.add_command(label=name, command=lambda n=name: self._apply_template(n))
            elif "Vide" in name:
                cat_empty.add_command(label=name, command=lambda n=name: self._apply_template(n))
            else:
                cat_classic.add_command(label=name, command=lambda n=name: self._apply_template(n))

        tpl_menu.add_cascade(label="Genres classiques", menu=cat_classic)
        tpl_menu.add_cascade(label="Multi-Chanteurs", menu=cat_multi)
        tpl_menu.add_cascade(label="Formats courts / Spéciaux", menu=cat_short)
        tpl_menu.add_separator()
        tpl_menu.add_cascade(label="Vide", menu=cat_empty)
        menubar.add_cascade(label="Templates", menu=tpl_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guide des Metatags Suno", command=self._show_metatags_help)
        help_menu.add_command(label="Conseils Multi-Voix", command=self._show_multivoice_help)
        help_menu.add_command(label="A propos", command=self._show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)

        self.root.config(menu=menubar)

        self.root.bind("<Control-n>", lambda e: self._new_project())
        self.root.bind("<Control-o>", lambda e: self._open_project())
        self.root.bind("<Control-s>", lambda e: self._save_project())
        self.root.bind("<Control-e>", lambda e: self._export_suno())

    # ── UI principale ─────────────────────────
    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Titre :").pack(side=tk.LEFT)
        self.title_var = tk.StringVar(value=self.project.title)
        self.title_var.trace_add("write", lambda *_: self._on_title_change())
        ttk.Entry(top, textvariable=self.title_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(top, text="Style de musique :").pack(side=tk.LEFT, padx=(20, 0))
        self.style_var = tk.StringVar(value=self.project.style)
        self.style_var.trace_add("write", lambda *_: self._on_style_change())
        ttk.Entry(top, textvariable=self.style_var, width=50).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Pret")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel",
                                anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Paned window 3 colonnes
        pw = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._build_singers_panel(pw)
        self._build_sections_panel(pw)
        self._build_preview_panel(pw)

    # ── Panneau Chanteurs ─────────────────────
    def _build_singers_panel(self, pw):
        left = ttk.LabelFrame(pw, text="Chanteurs / Voix", padding=5)
        pw.add(left, weight=1)

        # Liste
        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.singers_list = tk.Listbox(list_frame, height=6, font=("Consolas", 10),
                                        selectmode=tk.SINGLE, exportselection=False)
        self.singers_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.singers_list.bind("<<ListboxSelect>>", self._on_singer_select)

        slb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.singers_list.yview)
        slb.pack(side=tk.RIGHT, fill=tk.Y)
        self.singers_list.configure(yscrollcommand=slb.set)

        # Boutons
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="+ Ajouter", command=self._add_singer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Supprimer", command=self._del_singer).pack(side=tk.LEFT, padx=2)

        # Formulaire de détails — toujours visible
        det = ttk.LabelFrame(left, text="Edition du chanteur", padding=8)
        det.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(det, text="Nom :").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.singer_name_var = tk.StringVar()
        self.singer_name_entry = ttk.Entry(det, textvariable=self.singer_name_var, width=22)
        self.singer_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=3, pady=2)

        ttk.Label(det, text="Type :").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.singer_type_var = tk.StringVar(value="male")
        type_frame = ttk.Frame(det)
        type_frame.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Radiobutton(type_frame, text="Homme", variable=self.singer_type_var, value="male").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Femme", variable=self.singer_type_var, value="female").pack(side=tk.LEFT)

        ttk.Label(det, text="Phonetique Suno :").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.singer_phonetic_var = tk.StringVar()
        ttk.Entry(det, textvariable=self.singer_phonetic_var, width=22).grid(row=2, column=1, sticky=tk.EW, padx=3, pady=2)

        ttk.Label(det, text="Description voix :").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.singer_desc_var = tk.StringVar()
        ttk.Entry(det, textvariable=self.singer_desc_var, width=22).grid(row=3, column=1, sticky=tk.EW, padx=3, pady=2)

        det.columnconfigure(1, weight=1)

        save_btn = ttk.Button(det, text="Enregistrer le chanteur",
                               command=self._save_singer_details)
        save_btn.grid(row=4, column=0, columnspan=2, pady=(8, 2), sticky=tk.EW)

        # Indication
        hint = ttk.Label(left, text="Phonetique : nom tel que Suno doit le prononcer\n"
                                     "Ex: 'Fènrice' au lieu de 'Fenrice'",
                          foreground="gray", wraplength=250, justify=tk.LEFT)
        hint.pack(fill=tk.X, pady=(5, 0))

    # ── Panneau Sections ──────────────────────
    def _build_sections_panel(self, pw):
        center = ttk.LabelFrame(pw, text="Structure de la chanson", padding=5)
        pw.add(center, weight=2)

        # Treeview
        sec_top = ttk.Frame(center)
        sec_top.pack(fill=tk.BOTH, expand=True)

        cols = ("type", "num", "assign", "mood", "preview")
        self.sections_tree = ttk.Treeview(sec_top, columns=cols, show="headings", height=10)
        self.sections_tree.heading("type", text="Section")
        self.sections_tree.heading("num", text="#")
        self.sections_tree.heading("assign", text="Assigne a")
        self.sections_tree.heading("mood", text="Ambiance")
        self.sections_tree.heading("preview", text="Apercu paroles")
        self.sections_tree.column("type", width=95, minwidth=70)
        self.sections_tree.column("num", width=30, minwidth=25)
        self.sections_tree.column("assign", width=110, minwidth=80)
        self.sections_tree.column("mood", width=130, minwidth=80)
        self.sections_tree.column("preview", width=200)
        self.sections_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sections_tree.bind("<<TreeviewSelect>>", self._on_section_select)

        sb = ttk.Scrollbar(sec_top, orient=tk.VERTICAL, command=self.sections_tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.sections_tree.configure(yscrollcommand=sb.set)

        # Boutons
        sec_btns = ttk.Frame(center)
        sec_btns.pack(fill=tk.X, pady=4)
        for text, cmd in [("+ Section", self._add_section),
                          ("Dupliquer", self._dup_section),
                          ("Supprimer", self._del_section),
                          ("Monter", self._move_section_up),
                          ("Descendre", self._move_section_down)]:
            ttk.Button(sec_btns, text=text, command=cmd).pack(side=tk.LEFT, padx=2)

        # Editeur de section
        editor = ttk.LabelFrame(center, text="Editeur de section", padding=5)
        editor.pack(fill=tk.BOTH, expand=True)

        # Ligne 1 : type, numéro, assignation
        row0 = ttk.Frame(editor)
        row0.pack(fill=tk.X, pady=2)

        ttk.Label(row0, text="Type :").pack(side=tk.LEFT)
        self.sec_type_var = tk.StringVar()
        self.sec_type_combo = ttk.Combobox(row0, textvariable=self.sec_type_var,
                                            values=SECTION_TYPES, width=15, state="readonly")
        self.sec_type_combo.pack(side=tk.LEFT, padx=3)

        ttk.Label(row0, text="N :").pack(side=tk.LEFT, padx=(10, 0))
        self.sec_num_var = tk.StringVar()
        ttk.Entry(row0, textvariable=self.sec_num_var, width=5).pack(side=tk.LEFT, padx=3)

        ttk.Label(row0, text="Assigne a :").pack(side=tk.LEFT, padx=(10, 0))
        self.sec_assign_var = tk.StringVar()
        self.sec_assign_combo = ttk.Combobox(row0, textvariable=self.sec_assign_var, width=25,
                                              state="readonly")
        self.sec_assign_combo.pack(side=tk.LEFT, padx=3)

        # Ligne 2 : ambiance
        row1 = ttk.Frame(editor)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Ambiance :").pack(side=tk.LEFT)
        self.sec_mood_var = tk.StringVar()
        self.sec_mood_combo = ttk.Combobox(row1, textvariable=self.sec_mood_var,
                                            values=MOOD_TAGS, width=28)
        self.sec_mood_combo.pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="+ Ajouter", command=self._add_mood_tag).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Retirer dernier", command=self._remove_last_mood_tag).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="Vider", command=self._clear_mood_tags).pack(side=tk.LEFT, padx=2)

        self.mood_display = ttk.Label(row1, text="(aucun)", foreground="#4488cc", wraplength=350)
        self.mood_display.pack(side=tk.LEFT, padx=5)

        # Ligne 3 : performance, parlé
        row1b = ttk.Frame(editor)
        row1b.pack(fill=tk.X, pady=2)

        ttk.Label(row1b, text="Performance :").pack(side=tk.LEFT)
        self.sec_perf_var = tk.StringVar()
        ttk.Combobox(row1b, textvariable=self.sec_perf_var,
                      values=["(aucun)"] + PERFORMANCE_TAGS, width=20, state="readonly").pack(side=tk.LEFT, padx=3)

        ttk.Label(row1b, text="Ligne parlee :").pack(side=tk.LEFT, padx=(10, 0))
        self.sec_spoken_var = tk.StringVar()
        ttk.Entry(row1b, textvariable=self.sec_spoken_var, width=30).pack(side=tk.LEFT, padx=3)

        # Paroles
        ttk.Label(editor, text="Paroles :").pack(anchor=tk.W, pady=(4, 0))
        self.lyrics_text = scrolledtext.ScrolledText(editor, height=5, font=("Consolas", 10), wrap=tk.WORD)
        self.lyrics_text.pack(fill=tk.BOTH, expand=True)

        save_btn_frame = ttk.Frame(editor)
        save_btn_frame.pack(fill=tk.X, pady=4)
        ttk.Button(save_btn_frame, text="Appliquer les modifications",
                    command=self._save_section_details).pack(side=tk.LEFT, padx=2)
        ttk.Button(save_btn_frame, text="Appliquer + Suivante",
                    command=self._save_and_next_section).pack(side=tk.LEFT, padx=2)

    # ── Panneau Aperçu ────────────────────────
    def _build_preview_panel(self, pw):
        right = ttk.LabelFrame(pw, text="Apercu Suno (sortie finale)", padding=5)
        pw.add(right, weight=2)

        preview_btns = ttk.Frame(right)
        preview_btns.pack(fill=tk.X, pady=2)
        ttk.Button(preview_btns, text="Rafraichir", command=self._refresh_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_btns, text="Copier dans le presse-papiers", command=self._copy_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_btns, text="Exporter .txt", command=self._export_suno).pack(side=tk.LEFT, padx=2)

        self.preview_text = scrolledtext.ScrolledText(right, font=("Consolas", 10),
                                                       wrap=tk.WORD, state=tk.DISABLED,
                                                       bg="#1e1e2e", fg="#cdd6f4",
                                                       insertbackground="#cdd6f4")
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        self.preview_text.tag_configure("tag", foreground="#f9e2af", font=("Consolas", 10, "bold"))
        self.preview_text.tag_configure("singer", foreground="#89b4fa")
        self.preview_text.tag_configure("mood", foreground="#a6e3a1", font=("Consolas", 10, "italic"))

    # ══════════════════════════════════════════
    # GESTION DES CHANTEURS (corrigée)
    # ══════════════════════════════════════════

    def _refresh_singers_list(self, restore_idx=None):
        """Rafraîchit la liste des chanteurs et restaure la sélection."""
        self._inhibit_singer_select = True
        self.singers_list.delete(0, tk.END)
        for s in self.project.singers:
            icon = "M" if s.voice_type == "male" else "F"
            phon = f"  [{s.phonetic}]" if s.phonetic else ""
            desc = f"  ({s.description})" if s.description else ""
            self.singers_list.insert(tk.END, f"[{icon}] {s.name}{phon}{desc}")
        self._update_assign_combo()

        # Restaurer la sélection
        idx = restore_idx if restore_idx is not None else self._singer_selection_idx
        if idx is not None and 0 <= idx < len(self.project.singers):
            self.singers_list.selection_set(idx)
            self.singers_list.see(idx)
            self._singer_selection_idx = idx
        else:
            self._singer_selection_idx = None
        self._inhibit_singer_select = False

    def _update_assign_combo(self):
        choices = ["Tous (all)", "Instrumental", "Public", "Mixte"]
        for s in self.project.singers:
            icon = "M" if s.voice_type == "male" else "F"
            choices.append(f"[{icon}] {s.name}")
        self.sec_assign_combo["values"] = choices

    def _on_singer_select(self, event=None):
        if self._inhibit_singer_select:
            return
        sel = self.singers_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self._singer_selection_idx = idx
        singer = self.project.singers[idx]
        self.singer_name_var.set(singer.name)
        self.singer_type_var.set(singer.voice_type)
        self.singer_phonetic_var.set(singer.phonetic)
        self.singer_desc_var.set(singer.description)
        self._set_status(f"Chanteur selectionne : {singer.name}")

    def _add_singer(self):
        count = len(self.project.singers) + 1
        vtype = "female" if count % 3 == 0 else "male"
        s = Singer(f"Chanteur {count}", vtype)
        self.project.singers.append(s)
        new_idx = len(self.project.singers) - 1
        self._refresh_singers_list(restore_idx=new_idx)
        self._load_singer_to_form(s)
        self._set_status(f"Chanteur '{s.name}' ajoute — modifiez les details puis cliquez Enregistrer")
        # Focus sur le champ nom pour édition rapide
        self.singer_name_entry.focus_set()
        self.singer_name_entry.select_range(0, tk.END)

    def _load_singer_to_form(self, singer: Singer):
        self.singer_name_var.set(singer.name)
        self.singer_type_var.set(singer.voice_type)
        self.singer_phonetic_var.set(singer.phonetic)
        self.singer_desc_var.set(singer.description)

    def _save_singer_details(self):
        idx = self._singer_selection_idx
        if idx is None or idx < 0 or idx >= len(self.project.singers):
            messagebox.showwarning("Aucune selection",
                "Selectionnez un chanteur dans la liste, puis modifiez et enregistrez.")
            return

        singer = self.project.singers[idx]
        new_name = self.singer_name_var.get().strip()
        if not new_name:
            messagebox.showwarning("Nom vide", "Le nom du chanteur ne peut pas etre vide.")
            return

        # Vérifier doublons
        for i, s in enumerate(self.project.singers):
            if i != idx and s.name.lower() == new_name.lower():
                messagebox.showwarning("Doublon", f"Un chanteur nomme '{new_name}' existe deja.")
                return

        singer.name = new_name
        singer.voice_type = self.singer_type_var.get()
        singer.phonetic = self.singer_phonetic_var.get().strip()
        singer.description = self.singer_desc_var.get().strip()

        self._refresh_singers_list(restore_idx=idx)
        self._refresh_sections_tree()
        self._refresh_preview()
        self._set_status(f"Chanteur '{singer.name}' enregistre avec succes")

    def _del_singer(self):
        idx = self._singer_selection_idx
        if idx is None or idx < 0 or idx >= len(self.project.singers):
            messagebox.showinfo("Info", "Selectionnez un chanteur a supprimer.")
            return

        singer = self.project.singers[idx]
        if not messagebox.askyesno("Supprimer ?",
                f"Supprimer le chanteur '{singer.name}' ?\n"
                "Les sections assignees a ce chanteur seront remises a 'Tous'."):
            return

        for sec in self.project.sections:
            if sec.assignment == singer.id:
                sec.assignment = "all"
        del self.project.singers[idx]

        # Ajuster la sélection
        new_idx = min(idx, len(self.project.singers) - 1) if self.project.singers else None
        self._singer_selection_idx = new_idx
        self._refresh_singers_list(restore_idx=new_idx)

        # Vider le formulaire si plus aucun chanteur
        if new_idx is not None:
            self._load_singer_to_form(self.project.singers[new_idx])
        else:
            self.singer_name_var.set("")
            self.singer_phonetic_var.set("")
            self.singer_desc_var.set("")
            self.singer_type_var.set("male")

        self._refresh_sections_tree()
        self._refresh_preview()
        self._set_status(f"Chanteur '{singer.name}' supprime")

    # ══════════════════════════════════════════
    # GESTION DES SECTIONS
    # ══════════════════════════════════════════

    def _refresh_sections_tree(self):
        sel_id = None
        if self._selected_section_idx is not None and \
           0 <= self._selected_section_idx < len(self.project.sections):
            sel_id = self.project.sections[self._selected_section_idx].id

        self.sections_tree.delete(*self.sections_tree.get_children())
        for sec in self.project.sections:
            assign_label = self._assignment_label(sec.assignment)
            mood_label = " + ".join(sec.mood_tags[:2]) + ("..." if len(sec.mood_tags) > 2 else "") \
                         if sec.mood_tags else ""
            preview = sec.lyrics[:50].replace("\n", " ") + ("..." if len(sec.lyrics) > 50 else "")
            num = str(sec.number) if sec.number else ""
            self.sections_tree.insert("", tk.END, iid=sec.id,
                                       values=(sec.section_type, num, assign_label, mood_label, preview))

        # Restaurer sélection
        if sel_id:
            try:
                self.sections_tree.selection_set(sel_id)
                self.sections_tree.see(sel_id)
            except tk.TclError:
                pass

    def _assignment_label(self, assignment):
        if assignment == "all":
            return "Tous"
        elif assignment == "instrumental":
            return "Instrumental"
        elif assignment == "public":
            return "Public"
        elif assignment == "mixed":
            return "Mixte"
        else:
            singer = self.project.singer_by_id(assignment)
            if singer:
                icon = "M" if singer.voice_type == "male" else "F"
                return f"[{icon}] {singer.name}"
            return "Tous"

    def _on_section_select(self, event=None):
        sel = self.sections_tree.selection()
        if not sel:
            self._selected_section_idx = None
            return
        sid = sel[0]
        for i, sec in enumerate(self.project.sections):
            if sec.id == sid:
                self._selected_section_idx = i
                self._load_section_to_editor(sec)
                break

    def _load_section_to_editor(self, sec: Section):
        self.sec_type_var.set(sec.section_type)
        self.sec_num_var.set(str(sec.number) if sec.number else "")
        self.sec_perf_var.set(sec.performance_tag if sec.performance_tag else "(aucun)")
        self.sec_spoken_var.set(sec.spoken_line)

        # Assignment combo
        assign_text = self._assignment_combo_text(sec.assignment)
        self.sec_assign_var.set(assign_text)

        # Mood tags
        self.mood_display.config(
            text=" | ".join(sec.mood_tags) if sec.mood_tags else "(aucun)")

        # Lyrics
        self.lyrics_text.delete("1.0", tk.END)
        self.lyrics_text.insert("1.0", sec.lyrics)

    def _assignment_combo_text(self, assignment):
        if assignment == "all":
            return "Tous (all)"
        elif assignment == "instrumental":
            return "Instrumental"
        elif assignment == "public":
            return "Public"
        elif assignment == "mixed":
            return "Mixte"
        else:
            singer = self.project.singer_by_id(assignment)
            if singer:
                icon = "M" if singer.voice_type == "male" else "F"
                return f"[{icon}] {singer.name}"
            return "Tous (all)"

    def _parse_assignment_from_combo(self, text):
        if text == "Tous (all)":
            return "all"
        elif text == "Instrumental":
            return "instrumental"
        elif text == "Public":
            return "public"
        elif text == "Mixte":
            return "mixed"
        else:
            for singer in self.project.singers:
                icon = "M" if singer.voice_type == "male" else "F"
                if text == f"[{icon}] {singer.name}":
                    return singer.id
            return "all"

    def _save_section_details(self):
        if self._selected_section_idx is None:
            messagebox.showinfo("Info", "Selectionnez une section d'abord.")
            return
        sec = self.project.sections[self._selected_section_idx]
        sec.section_type = self.sec_type_var.get()
        num_str = self.sec_num_var.get().strip()
        sec.number = int(num_str) if num_str.isdigit() else None

        perf = self.sec_perf_var.get()
        sec.performance_tag = "" if perf == "(aucun)" else perf
        sec.spoken_line = self.sec_spoken_var.get().strip()
        sec.assignment = self._parse_assignment_from_combo(self.sec_assign_var.get())
        sec.lyrics = self.lyrics_text.get("1.0", tk.END).strip()

        self._refresh_sections_tree()
        self._refresh_preview()
        self._set_status(f"Section '{sec.header_label()}' mise a jour")

    def _save_and_next_section(self):
        """Sauvegarde la section courante et passe à la suivante."""
        self._save_section_details()
        if self._selected_section_idx is not None and \
           self._selected_section_idx < len(self.project.sections) - 1:
            next_idx = self._selected_section_idx + 1
            next_sec = self.project.sections[next_idx]
            self.sections_tree.selection_set(next_sec.id)
            self.sections_tree.see(next_sec.id)
            self._selected_section_idx = next_idx
            self._load_section_to_editor(next_sec)
            self._set_status(f"Section suivante : {next_sec.header_label()}")

    def _add_section(self):
        # Insérer après la section sélectionnée, ou à la fin
        verse_count = len([s for s in self.project.sections if s.section_type == "VERSE"]) + 1
        sec = Section("VERSE", verse_count)

        if self._selected_section_idx is not None:
            insert_pos = self._selected_section_idx + 1
        else:
            insert_pos = len(self.project.sections)

        self.project.sections.insert(insert_pos, sec)
        self._selected_section_idx = insert_pos
        self._refresh_sections_tree()
        self.sections_tree.selection_set(sec.id)
        self.sections_tree.see(sec.id)
        self._load_section_to_editor(sec)
        self._refresh_preview()
        self._set_status(f"Section '{sec.header_label()}' ajoutee")

    def _dup_section(self):
        if self._selected_section_idx is None:
            return
        orig = self.project.sections[self._selected_section_idx]
        new = deepcopy(orig)
        new.id = str(uuid.uuid4())[:8]
        if new.number:
            new.number += 1
        insert_pos = self._selected_section_idx + 1
        self.project.sections.insert(insert_pos, new)
        self._selected_section_idx = insert_pos
        self._refresh_sections_tree()
        self.sections_tree.selection_set(new.id)
        self._refresh_preview()
        self._set_status(f"Section '{new.header_label()}' dupliquee")

    def _del_section(self):
        if self._selected_section_idx is None:
            return
        sec = self.project.sections[self._selected_section_idx]
        del self.project.sections[self._selected_section_idx]
        # Ajuster sélection
        if self.project.sections:
            new_idx = min(self._selected_section_idx, len(self.project.sections) - 1)
            self._selected_section_idx = new_idx
            new_sec = self.project.sections[new_idx]
            self._refresh_sections_tree()
            self.sections_tree.selection_set(new_sec.id)
            self._load_section_to_editor(new_sec)
        else:
            self._selected_section_idx = None
            self._refresh_sections_tree()
        self._refresh_preview()
        self._set_status(f"Section '{sec.header_label()}' supprimee")

    def _move_section_up(self):
        if self._selected_section_idx is None or self._selected_section_idx == 0:
            return
        i = self._selected_section_idx
        self.project.sections[i], self.project.sections[i - 1] = \
            self.project.sections[i - 1], self.project.sections[i]
        self._selected_section_idx = i - 1
        self._refresh_sections_tree()
        self._refresh_preview()

    def _move_section_down(self):
        if self._selected_section_idx is None or \
           self._selected_section_idx >= len(self.project.sections) - 1:
            return
        i = self._selected_section_idx
        self.project.sections[i], self.project.sections[i + 1] = \
            self.project.sections[i + 1], self.project.sections[i]
        self._selected_section_idx = i + 1
        self._refresh_sections_tree()
        self._refresh_preview()

    def _add_mood_tag(self):
        if self._selected_section_idx is None:
            messagebox.showinfo("Info", "Selectionnez une section d'abord.")
            return
        tag = self.sec_mood_var.get().strip()
        if not tag:
            return
        sec = self.project.sections[self._selected_section_idx]
        if tag not in sec.mood_tags:
            sec.mood_tags.append(tag)
        self.mood_display.config(text=" | ".join(sec.mood_tags) if sec.mood_tags else "(aucun)")
        self.sec_mood_var.set("")

    def _remove_last_mood_tag(self):
        if self._selected_section_idx is None:
            return
        sec = self.project.sections[self._selected_section_idx]
        if sec.mood_tags:
            sec.mood_tags.pop()
        self.mood_display.config(text=" | ".join(sec.mood_tags) if sec.mood_tags else "(aucun)")

    def _clear_mood_tags(self):
        if self._selected_section_idx is None:
            return
        sec = self.project.sections[self._selected_section_idx]
        sec.mood_tags = []
        self.mood_display.config(text="(aucun)")

    # ══════════════════════════════════════════
    # APERCU
    # ══════════════════════════════════════════

    def _refresh_preview(self):
        output = self.project.render_suno()
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", output)
        self._colorize_preview()
        self.preview_text.config(state=tk.DISABLED)

    def _colorize_preview(self):
        content = self.preview_text.get("1.0", tk.END)
        idx = "1.0"
        while True:
            start = self.preview_text.search("[", idx, tk.END)
            if not start:
                break
            end = self.preview_text.search("]", f"{start}+1c", tk.END)
            if not end:
                break
            end = f"{end}+1c"
            tag_text = self.preview_text.get(start, end)

            section_kws = ["VERSE", "CHORUS", "BRIDGE", "INTRO", "OUTRO", "HOOK",
                           "BREAK", "PRE-CHORUS", "POST-CHORUS", "INTERLUDE",
                           "ROUND", "END", "DROP", "INSTRUMENTAL"]
            if any(kw in tag_text.upper() for kw in section_kws):
                self.preview_text.tag_add("tag", start, end)
            elif any(kw in tag_text for kw in MOOD_TAGS):
                self.preview_text.tag_add("mood", start, end)
            else:
                self.preview_text.tag_add("singer", start, end)
            idx = end

    def _copy_preview(self):
        self.root.clipboard_clear()
        content = self.preview_text.get("1.0", tk.END).strip()
        self.root.clipboard_append(content)
        self._set_status("Texte copie dans le presse-papiers !")

    # ══════════════════════════════════════════
    # FICHIERS
    # ══════════════════════════════════════════

    def _new_project(self):
        if messagebox.askyesno("Nouveau projet",
                "Creer un nouveau projet ? Les modifications non sauvegardees seront perdues."):
            self.project = SongProject()
            self.title_var.set(self.project.title)
            self.style_var.set(self.project.style)
            self._singer_selection_idx = None
            self._selected_section_idx = None
            self._refresh_all()
            self._set_status("Nouveau projet cree")

    def _save_project(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Projet Suno", "*.json")],
            initialfile=f"{self.project.title}.json")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.project.to_dict(), f, ensure_ascii=False, indent=2)
        self._set_status(f"Projet sauvegarde : {os.path.basename(path)}")

    def _open_project(self):
        path = filedialog.askopenfilename(filetypes=[("Projet Suno", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.project = SongProject.from_dict(data)
        self.title_var.set(self.project.title)
        self.style_var.set(self.project.style)
        self._singer_selection_idx = 0 if self.project.singers else None
        self._selected_section_idx = 0 if self.project.sections else None
        self._refresh_all()
        if self.project.singers:
            self._load_singer_to_form(self.project.singers[0])
        self._set_status(f"Projet ouvert : {os.path.basename(path)}")

    def _export_suno(self):
        output = self.project.render_suno()
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texte Suno", "*.txt")],
            initialfile=f"{self.project.title}_suno.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
        self._set_status(f"Exporte pour Suno : {os.path.basename(path)}")

    def _import_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Texte", "*.txt")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self._parse_txt_to_project(content)
        self._singer_selection_idx = 0 if self.project.singers else None
        self._selected_section_idx = 0 if self.project.sections else None
        self._refresh_all()
        if self.project.singers:
            self._load_singer_to_form(self.project.singers[0])
        self._set_status(f"Fichier importe : {os.path.basename(path)} — Verifiez les sections")

    def _parse_txt_to_project(self, content: str):
        self.project = SongProject()
        lines = content.split("\n")
        current_section = None
        current_lyrics = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_lyrics and current_lyrics[-1] != "":
                    current_lyrics.append("")
                continue

            # Ligne globale type [4 singers, ...]
            if stripped.startswith("[") and "singer" in stripped.lower() and current_section is None:
                self.project.global_note = stripped
                continue

            # Tag entre crochets
            if stripped.startswith("[") and stripped.endswith("]"):
                tag_content = stripped[1:-1].strip()
                upper = tag_content.upper()

                is_section = False
                for stype in SECTION_TYPES:
                    if upper.startswith(stype):
                        is_section = True
                        if current_section is not None:
                            current_section.lyrics = "\n".join(current_lyrics).strip()
                            self.project.sections.append(current_section)
                            current_lyrics = []

                        rest = tag_content[len(stype):].strip()
                        number = None
                        assignment = "all"

                        # Numéro
                        parts = rest.split("-", 1)
                        if parts[0].strip().isdigit():
                            number = int(parts[0].strip())
                            rest = parts[1].strip() if len(parts) > 1 else ""
                        elif len(parts) > 1 and parts[0].strip() == "":
                            rest = parts[1].strip()

                        # Chanteur
                        if rest:
                            name_part = rest.split("(")[0].strip().rstrip("-").strip()
                            if name_part:
                                singer = self._find_or_create_singer(name_part, rest)
                                assignment = singer.id

                        current_section = Section(stype, number, assignment)
                        break

                if not is_section:
                    if current_section is not None:
                        if tag_content in MOOD_TAGS or any(m in tag_content for m in
                                ["Explosion", "Montee", "Chute", "Changement",
                                 "Batterie", "Synthe", "Piano", "Guitare", "Basse",
                                 "Fade", "Building", "Soft", "Energetic", "Aggressive",
                                 "Slow", "Epic"]):
                            current_section.mood_tags.append(tag_content)
                        elif tag_content in PERFORMANCE_TAGS:
                            current_section.performance_tag = tag_content
                        else:
                            current_lyrics.append(stripped)
                    continue
            else:
                if stripped:
                    current_lyrics.append(stripped)

        if current_section is not None:
            current_section.lyrics = "\n".join(current_lyrics).strip()
            self.project.sections.append(current_section)

    def _find_or_create_singer(self, name, full_tag):
        for s in self.project.singers:
            if s.name.lower() == name.lower():
                return s
        voice_type = "male"
        lower = full_tag.lower()
        if "female" in lower or "chanteuse" in lower or "femme" in lower:
            voice_type = "female"
        singer = Singer(name, voice_type)
        self.project.singers.append(singer)
        return singer

    # ══════════════════════════════════════════
    # TEMPLATES
    # ══════════════════════════════════════════

    def _apply_template(self, template_name):
        if self.project.sections and not messagebox.askyesno(
            "Template", f"Appliquer le template '{template_name}' ?\n"
                        "Les sections actuelles seront remplacees."):
            return
        self.project.sections = []
        template = SONG_TEMPLATES[template_name]
        for entry in template:
            sec_type, num, assign, lyrics, moods, perf = entry
            real_assign = assign
            if assign.startswith("singer_"):
                idx = int(assign.split("_")[1])
                if idx < len(self.project.singers):
                    real_assign = self.project.singers[idx].id
                else:
                    real_assign = "all"
            elif assign == "solo":
                if self.project.singers:
                    real_assign = self.project.singers[0].id
                else:
                    real_assign = "all"
            self.project.sections.append(
                Section(sec_type, num, real_assign, lyrics, list(moods), perf))
        self._selected_section_idx = 0 if self.project.sections else None
        self._refresh_all()
        self._set_status(f"Template '{template_name}' applique — {len(self.project.sections)} sections")

    # ══════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════

    def _on_title_change(self):
        self.project.title = self.title_var.get()

    def _on_style_change(self):
        self.project.style = self.style_var.get()

    def _set_status(self, msg):
        self.status_var.set(msg)

    def _refresh_all(self):
        self._refresh_singers_list()
        self._refresh_sections_tree()
        self._refresh_preview()

    # ══════════════════════════════════════════
    # AIDE
    # ══════════════════════════════════════════

    def _show_metatags_help(self):
        help_text = """
=====================================================
   GUIDE DES METATAGS SUNO  --  Reference rapide
=====================================================

Les metatags sont des instructions entre [crochets]
placees dans les paroles pour guider l'IA Suno.

-- TAGS DE STRUCTURE --------------------------------
  [Intro]              Debut instrumental
  [Verse 1], [Verse 2] Couplets
  [Pre-Chorus]         Pre-refrain (montee)
  [Chorus]             Refrain
  [Post-Chorus]        Apres le refrain
  [Bridge]             Pont / transition
  [Hook]               Accroche (rap/hip-hop)
  [Interlude]          Intermede
  [Instrumental]       Passage instrumental
  [Break]              Pause
  [Drop]               Drop (EDM)
  [Outro]              Conclusion
  [End]                Fin nette

-- TAGS DE VOIX / PERFORMANCE ----------------------
  [Male Vocals]        Voix masculine
  [Female Vocals]      Voix feminine
  [Duet]               Duo homme/femme
  [Harmony]            Harmonies vocales
  [Choir]              Chorale
  [Background Vocals]  Choeurs en arriere-plan
  [Spoken Word]        Parle (pas chante)
  [Whisper]            Chuchote
  [Rap]                Passage rappe
  [Ad-lib]             Improvisations vocales
  [A cappella]         Sans instruments
  [Belting]            Voix puissante, projetee
  [Falsetto]           Voix de tete / fausset
  [Growl]              Voix grondante (metal)
  [Humming]            Fredonnement
  [Call and Response]  Appel et reponse

-- TAGS DE DYNAMIQUE / AMBIANCE --------------------
  [Soft], [Gentle]     Doux, delicat
  [Building]           Montee en puissance
  [Crescendo]          Crescendo progressif
  [Energetic]          Energique
  [Aggressive]         Agressif
  [Slow Down]          Ralentissement
  [Fade Out]           Fondu de sortie
  [Drop]               Drop (EDM)

-- COMBINAISONS EFFICACES --------------------------

  [Verse 1 - Male Vocals, aggressive]
  [Chorus - Female Vocals, powerful]
  [Bridge - Whisper, intimate]
  [Spoken Word]
  "Texte parle entre guillemets"

-- ASTUCES ------------------------------------------

  * Les tags sont des SUGGESTIONS, pas des ordres
  * Suno interprete le contexte global (style+tags)
  * Combiner structure + voix + ambiance = meilleur
  * Les guillemets aident pour les parties parlees
  * La CASSE (majuscules) peut renforcer les tags
"""
        self._show_help_window("Guide des Metatags Suno", help_text)

    def _show_multivoice_help(self):
        help_text = """
=====================================================
   GUIDE MULTI-VOIX POUR SUNO
=====================================================

Suno ne supporte pas nativement les chanteurs nommes,
mais plusieurs techniques permettent de simuler des
multi-voix efficacement.

-- TECHNIQUE 1 : TAGS VOIX DANS LES SECTIONS ------

La plus fiable. Combinez le type de section avec une
description vocale :

  [VERSE 1 - Male Voice, deep and aggressive]
  (paroles du chanteur 1)

  [VERSE 2 - Female Voice, soft and melodic]
  (paroles de la chanteuse)

  [CHORUS - Duet, powerful harmonies]
  (paroles ensemble)

-- TECHNIQUE 2 : NOMS + TYPE VOCAL ----------------

Utilisez un nom + le type de voix entre parentheses.
Suno ne "connait" pas le nom, mais le type de voix
influence le rendu :

  [VERSE 1 - Mo (male)]
  [VERSE 2 - Fenrice (male)]
  [VERSE 3 - The (female)]

-- TECHNIQUE 3 : PERSONAS / VOICES (v5.5) ---------

La methode OFFICIELLE pour des voix distinctes :
1. Creez une Persona/Voice pour chaque chanteur
2. Generez chaque section SEPAREMENT
3. Assemblez dans Suno Studio / Extend

-- TECHNIQUE 4 : STYLE PROMPT + TAGS --------------

Dans le champ "Style of Music", precisez :
  "male and female vocal duet, alternating verses"
  "multi-voice rock anthem, 3 male 1 female"

-- TECHNIQUE 5 : APPEL ET REPONSE -----------------

  [Call and Response]
  [Male Voice] "Ou est l'ennemi ?"
  [Female Voice] "Derriere toi !"
  [All Voices] On fonce ensemble !

-- PHONETIQUE --------------------------------------

Pour que Suno prononce correctement un pseudo :
  * Ecrivez phonetiquement : "Cul-ro" -> "Kul-roh"
  * Separez les syllabes avec des tirets
  * Testez plusieurs variantes
  * Les noms courts marchent mieux
  Utilisez le champ "Phonetique Suno" de cet outil !

-- CONSEILS PRATIQUES ------------------------------

  1. MOINS C'EST PLUS : trop de tags confond Suno
  2. COHERENCE : gardez le meme format de tags
  3. STYLE PROMPT : le style global a PLUS d'impact
     que les tags individuels
  4. GENERER PAR SECTIONS : pour un vrai multi-voix,
     generez chaque partie separement
  5. EXTEND : utilisez "Extend" pour ajouter des
     sections avec des voix differentes
"""
        self._show_help_window("Guide Multi-Voix Suno", help_text)

    def _show_about(self):
        messagebox.showinfo("A propos",
            "Suno Song Builder\n\n"
            "Outil de structuration de chansons pour Suno AI.\n"
            "Gere les metatags, multi-voix et phonetique.\n\n"
            "Compatible Suno v4 / v4.5 / v5 / v5.5")

    def _show_help_window(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("650x600")
        txt = scrolledtext.ScrolledText(win, font=("Consolas", 10), wrap=tk.WORD,
                                         bg="#1e1e2e", fg="#cdd6f4")
        txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        txt.insert("1.0", text)
        txt.config(state=tk.DISABLED)


# ─────────────────────────────────────────────
# Point d'entree
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = SunoBuilderApp(root)
    root.mainloop()
