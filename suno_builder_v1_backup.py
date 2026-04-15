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
    "Voix grave dans l'ombre",
]

SONG_TEMPLATES = {
    "Standard (Verse-Chorus)": [
        ("INTRO", None, "instrumental", ""),
        ("VERSE", 1, "solo", ""),
        ("PRE-CHORUS", None, "solo", ""),
        ("CHORUS", None, "all", ""),
        ("VERSE", 2, "solo", ""),
        ("PRE-CHORUS", None, "solo", ""),
        ("CHORUS", None, "all", ""),
        ("BRIDGE", None, "solo", ""),
        ("CHORUS", None, "all", ""),
        ("OUTRO", None, "instrumental", ""),
    ],
    "Multi-Chanteurs (Rotation)": [
        ("INTRO", None, "instrumental", ""),
        ("VERSE", 1, "singer_0", ""),
        ("PRE-CHORUS", None, "all", ""),
        ("CHORUS", None, "all", ""),
        ("VERSE", 2, "singer_1", ""),
        ("CHORUS", None, "all", ""),
        ("BRIDGE", None, "mixed", ""),
        ("VERSE", 3, "singer_2", ""),
        ("CHORUS", None, "all", ""),
        ("ROUND FINAL", None, "all", ""),
        ("OUTRO", None, "instrumental", ""),
    ],
    "Ballade (Lente)": [
        ("INTRO", None, "instrumental", ""),
        ("VERSE", 1, "solo", ""),
        ("VERSE", 2, "solo", ""),
        ("CHORUS", None, "all", ""),
        ("VERSE", 3, "solo", ""),
        ("CHORUS", None, "all", ""),
        ("BRIDGE", None, "solo", ""),
        ("CHORUS", None, "all", ""),
        ("OUTRO", None, "all", ""),
    ],
    "Rap / Hip-Hop": [
        ("INTRO", None, "instrumental", ""),
        ("VERSE", 1, "singer_0", ""),
        ("HOOK", None, "all", ""),
        ("VERSE", 2, "singer_1", ""),
        ("HOOK", None, "all", ""),
        ("BRIDGE", None, "solo", ""),
        ("VERSE", 3, "singer_2", ""),
        ("HOOK", None, "all", ""),
        ("OUTRO", None, "instrumental", ""),
    ],
    "Vide (personnalisé)": [],
}


# ─────────────────────────────────────────────
# Modèle de données
# ─────────────────────────────────────────────

class Singer:
    def __init__(self, name="", voice_type="male", phonetic="", description=""):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.voice_type = voice_type      # male / female
        self.phonetic = phonetic          # phonétique pour Suno
        self.description = description    # ex: "voix grave, agressive"

    def suno_display(self):
        """Nom affiché dans les metatags Suno."""
        return self.phonetic if self.phonetic else self.name

    def suno_voice_tag(self):
        """Tag de voix pour Suno — aide à switcher le timbre."""
        parts = []
        if self.voice_type == "male":
            parts.append("Male Voice")
        else:
            parts.append("Female Voice")
        if self.description:
            parts.append(self.description)
        return ", ".join(parts)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name,
            "voice_type": self.voice_type,
            "phonetic": self.phonetic,
            "description": self.description,
        }

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
        self.number = number              # numéro ou None
        self.assignment = assignment      # "all", "instrumental", singer_id, "mixed", "public"
        self.lyrics = lyrics
        self.mood_tags = mood_tags or []  # tags d'ambiance
        self.performance_tag = performance_tag  # Spoken Word, Rap, etc.
        self.spoken_line = ""             # ligne parlée avant section

    def header_label(self):
        label = self.section_type
        if self.number:
            label += f" {self.number}"
        return label

    def to_dict(self):
        return {
            "id": self.id, "section_type": self.section_type,
            "number": self.number, "assignment": self.assignment,
            "lyrics": self.lyrics, "mood_tags": self.mood_tags,
            "performance_tag": self.performance_tag,
            "spoken_line": self.spoken_line,
        }

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
        self.global_note = ""  # note en tête (ex: [4 singers, 3 males, 1 female])

    def singer_by_id(self, sid):
        for s in self.singers:
            if s.id == sid:
                return s
        return None

    def to_dict(self):
        return {
            "title": self.title, "style": self.style,
            "global_note": self.global_note,
            "singers": [s.to_dict() for s in self.singers],
            "sections": [s.to_dict() for s in self.sections],
        }

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
        """Génère le texte formaté pour Suno."""
        lines = []

        # Note globale
        note = self.global_note or self.generate_global_note()
        if note:
            lines.append(note)
            lines.append("")

        for sec in self.sections:
            # Mood tags (direction musicale)
            for tag in sec.mood_tags:
                lines.append(f"[{tag}]")

            # Header de section
            header = self._build_header(sec)
            lines.append(header)

            # Ligne parlée optionnelle (avant les paroles)
            if sec.spoken_line:
                lines.append(f'[Voix grave dans l\'ombre : "{sec.spoken_line}"]')
                lines.append("")

            # Performance tag
            if sec.performance_tag and sec.assignment not in ("instrumental",):
                lines.append(f"[{sec.performance_tag}]")

            # Paroles
            if sec.lyrics.strip():
                lines.append(sec.lyrics.strip())

            lines.append("")

        return "\n".join(lines).strip()

    def _build_header(self, sec: Section):
        """Construit le header [SECTION - SINGER (voice)] ou variante."""
        label = sec.section_type
        if sec.number:
            label += f" {sec.number}"

        if sec.assignment == "instrumental":
            return f"[{label}]"
        elif sec.assignment == "all":
            return f"[{label}]"
        elif sec.assignment == "public":
            return f"[{label} - PUBLIC]"
        elif sec.assignment == "mixed":
            return f"[{label}]"
        else:
            # Chanteur spécifique
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
        self.root.title("🎵 Suno Song Builder")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)

        self.project = SongProject()
        self._selected_section_idx = None

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
        for name in SONG_TEMPLATES:
            tpl_menu.add_command(label=name, command=lambda n=name: self._apply_template(n))
        menubar.add_cascade(label="Templates", menu=tpl_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guide des Metatags Suno", command=self._show_metatags_help)
        help_menu.add_command(label="Conseils Multi-Voix", command=self._show_multivoice_help)
        help_menu.add_command(label="À propos", command=self._show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)

        self.root.config(menu=menubar)

        # Raccourcis clavier
        self.root.bind("<Control-n>", lambda e: self._new_project())
        self.root.bind("<Control-o>", lambda e: self._open_project())
        self.root.bind("<Control-s>", lambda e: self._save_project())
        self.root.bind("<Control-e>", lambda e: self._export_suno())

    # ── UI principale ─────────────────────────
    def _build_ui(self):
        # Top bar — titre & style
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

        # Paned window 3 colonnes
        pw = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Colonne gauche : Chanteurs ────────
        left = ttk.LabelFrame(pw, text="🎤 Chanteurs / Voix", padding=5)
        pw.add(left, weight=1)

        self.singers_list = tk.Listbox(left, height=8, font=("Consolas", 10))
        self.singers_list.pack(fill=tk.BOTH, expand=True)
        self.singers_list.bind("<<ListboxSelect>>", self._on_singer_select)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="+ Ajouter", command=self._add_singer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Modifier", command=self._edit_singer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Supprimer", command=self._del_singer).pack(side=tk.LEFT, padx=2)

        # Détails chanteur
        det = ttk.LabelFrame(left, text="Détails du chanteur", padding=5)
        det.pack(fill=tk.X, pady=5)

        ttk.Label(det, text="Nom :").grid(row=0, column=0, sticky=tk.W)
        self.singer_name_var = tk.StringVar()
        ttk.Entry(det, textvariable=self.singer_name_var, width=20).grid(row=0, column=1, sticky=tk.EW, padx=3)

        ttk.Label(det, text="Type :").grid(row=1, column=0, sticky=tk.W)
        self.singer_type_var = tk.StringVar(value="male")
        type_frame = ttk.Frame(det)
        type_frame.grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(type_frame, text="Homme", variable=self.singer_type_var, value="male").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Femme", variable=self.singer_type_var, value="female").pack(side=tk.LEFT)

        ttk.Label(det, text="Phonétique :").grid(row=2, column=0, sticky=tk.W)
        self.singer_phonetic_var = tk.StringVar()
        ttk.Entry(det, textvariable=self.singer_phonetic_var, width=20).grid(row=2, column=1, sticky=tk.EW, padx=3)

        ttk.Label(det, text="Description voix :").grid(row=3, column=0, sticky=tk.W)
        self.singer_desc_var = tk.StringVar()
        ttk.Entry(det, textvariable=self.singer_desc_var, width=20).grid(row=3, column=1, sticky=tk.EW, padx=3)

        det.columnconfigure(1, weight=1)

        ttk.Button(det, text="💾 Sauver chanteur", command=self._save_singer_details).grid(
            row=4, column=0, columnspan=2, pady=5)

        # ── Colonne centre : Structure ────────
        center = ttk.LabelFrame(pw, text="🎼 Structure de la chanson", padding=5)
        pw.add(center, weight=2)

        # Liste des sections
        sec_top = ttk.Frame(center)
        sec_top.pack(fill=tk.BOTH, expand=True)

        self.sections_tree = ttk.Treeview(sec_top, columns=("type", "num", "assign", "preview"),
                                           show="headings", height=12)
        self.sections_tree.heading("type", text="Section")
        self.sections_tree.heading("num", text="#")
        self.sections_tree.heading("assign", text="Assigné à")
        self.sections_tree.heading("preview", text="Aperçu paroles")
        self.sections_tree.column("type", width=100)
        self.sections_tree.column("num", width=30)
        self.sections_tree.column("assign", width=120)
        self.sections_tree.column("preview", width=250)
        self.sections_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sections_tree.bind("<<TreeviewSelect>>", self._on_section_select)

        sb = ttk.Scrollbar(sec_top, orient=tk.VERTICAL, command=self.sections_tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.sections_tree.configure(yscrollcommand=sb.set)

        # Boutons sections
        sec_btns = ttk.Frame(center)
        sec_btns.pack(fill=tk.X, pady=5)
        ttk.Button(sec_btns, text="+ Section", command=self._add_section).pack(side=tk.LEFT, padx=2)
        ttk.Button(sec_btns, text="Dupliquer", command=self._dup_section).pack(side=tk.LEFT, padx=2)
        ttk.Button(sec_btns, text="Supprimer", command=self._del_section).pack(side=tk.LEFT, padx=2)
        ttk.Button(sec_btns, text="▲ Monter", command=self._move_section_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(sec_btns, text="▼ Descendre", command=self._move_section_down).pack(side=tk.LEFT, padx=2)

        # Éditeur de section
        editor = ttk.LabelFrame(center, text="Éditeur de section", padding=5)
        editor.pack(fill=tk.BOTH, expand=True)

        row0 = ttk.Frame(editor)
        row0.pack(fill=tk.X, pady=2)

        ttk.Label(row0, text="Type :").pack(side=tk.LEFT)
        self.sec_type_var = tk.StringVar()
        self.sec_type_combo = ttk.Combobox(row0, textvariable=self.sec_type_var,
                                            values=SECTION_TYPES, width=15, state="readonly")
        self.sec_type_combo.pack(side=tk.LEFT, padx=3)

        ttk.Label(row0, text="N° :").pack(side=tk.LEFT, padx=(10, 0))
        self.sec_num_var = tk.StringVar()
        ttk.Entry(row0, textvariable=self.sec_num_var, width=5).pack(side=tk.LEFT, padx=3)

        ttk.Label(row0, text="Assigné à :").pack(side=tk.LEFT, padx=(10, 0))
        self.sec_assign_var = tk.StringVar()
        self.sec_assign_combo = ttk.Combobox(row0, textvariable=self.sec_assign_var, width=25)
        self.sec_assign_combo.pack(side=tk.LEFT, padx=3)

        row1 = ttk.Frame(editor)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Ambiance :").pack(side=tk.LEFT)
        self.sec_mood_var = tk.StringVar()
        self.sec_mood_combo = ttk.Combobox(row1, textvariable=self.sec_mood_var,
                                            values=MOOD_TAGS, width=30)
        self.sec_mood_combo.pack(side=tk.LEFT, padx=3)
        ttk.Button(row1, text="+ Tag", command=self._add_mood_tag).pack(side=tk.LEFT, padx=2)
        self.mood_display = ttk.Label(row1, text="", foreground="blue")
        self.mood_display.pack(side=tk.LEFT, padx=5)

        row1b = ttk.Frame(editor)
        row1b.pack(fill=tk.X, pady=2)

        ttk.Label(row1b, text="Performance :").pack(side=tk.LEFT)
        self.sec_perf_var = tk.StringVar()
        ttk.Combobox(row1b, textvariable=self.sec_perf_var,
                      values=[""] + PERFORMANCE_TAGS, width=20).pack(side=tk.LEFT, padx=3)

        ttk.Label(row1b, text="Ligne parlée :").pack(side=tk.LEFT, padx=(10, 0))
        self.sec_spoken_var = tk.StringVar()
        ttk.Entry(row1b, textvariable=self.sec_spoken_var, width=30).pack(side=tk.LEFT, padx=3)

        ttk.Label(editor, text="Paroles :").pack(anchor=tk.W)
        self.lyrics_text = scrolledtext.ScrolledText(editor, height=6, font=("Consolas", 10), wrap=tk.WORD)
        self.lyrics_text.pack(fill=tk.BOTH, expand=True)

        ttk.Button(editor, text="💾 Appliquer modifications", command=self._save_section_details).pack(pady=5)

        # ── Colonne droite : Aperçu ──────────
        right = ttk.LabelFrame(pw, text="📋 Aperçu Suno (sortie finale)", padding=5)
        pw.add(right, weight=2)

        preview_btns = ttk.Frame(right)
        preview_btns.pack(fill=tk.X, pady=2)
        ttk.Button(preview_btns, text="🔄 Rafraîchir", command=self._refresh_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_btns, text="📋 Copier", command=self._copy_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_btns, text="💾 Exporter .txt", command=self._export_suno).pack(side=tk.LEFT, padx=2)

        self.preview_text = scrolledtext.ScrolledText(right, font=("Consolas", 10),
                                                       wrap=tk.WORD, state=tk.DISABLED,
                                                       bg="#1e1e2e", fg="#cdd6f4",
                                                       insertbackground="#cdd6f4")
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Tags pour la coloration syntaxique
        self.preview_text.tag_configure("tag", foreground="#f9e2af", font=("Consolas", 10, "bold"))
        self.preview_text.tag_configure("singer", foreground="#89b4fa")
        self.preview_text.tag_configure("mood", foreground="#a6e3a1", font=("Consolas", 10, "italic"))

    # ── Gestion chanteurs ─────────────────────
    def _refresh_singers_list(self):
        self.singers_list.delete(0, tk.END)
        for s in self.project.singers:
            icon = "♂" if s.voice_type == "male" else "♀"
            phon = f" → {s.phonetic}" if s.phonetic else ""
            self.singers_list.insert(tk.END, f"{icon} {s.name}{phon} ({s.voice_type})")
        self._update_assign_combo()

    def _update_assign_combo(self):
        choices = ["Tous (all)", "Instrumental", "Public"]
        for s in self.project.singers:
            choices.append(f"{s.name} ({s.voice_type})")
        self.sec_assign_combo["values"] = choices

    def _on_singer_select(self, event=None):
        sel = self.singers_list.curselection()
        if not sel:
            return
        idx = sel[0]
        singer = self.project.singers[idx]
        self.singer_name_var.set(singer.name)
        self.singer_type_var.set(singer.voice_type)
        self.singer_phonetic_var.set(singer.phonetic)
        self.singer_desc_var.set(singer.description)

    def _add_singer(self):
        s = Singer(f"Chanteur {len(self.project.singers) + 1}", "male")
        self.project.singers.append(s)
        self._refresh_singers_list()
        self.singers_list.selection_set(len(self.project.singers) - 1)
        self._on_singer_select()

    def _edit_singer(self):
        self._on_singer_select()

    def _save_singer_details(self):
        sel = self.singers_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez un chanteur d'abord.")
            return
        singer = self.project.singers[sel[0]]
        singer.name = self.singer_name_var.get().strip()
        singer.voice_type = self.singer_type_var.get()
        singer.phonetic = self.singer_phonetic_var.get().strip()
        singer.description = self.singer_desc_var.get().strip()
        self._refresh_singers_list()
        self._refresh_preview()

    def _del_singer(self):
        sel = self.singers_list.curselection()
        if not sel:
            return
        idx = sel[0]
        singer = self.project.singers[idx]
        # Réassigner les sections qui référençaient ce chanteur
        for sec in self.project.sections:
            if sec.assignment == singer.id:
                sec.assignment = "all"
        del self.project.singers[idx]
        self._refresh_all()

    # ── Gestion sections ─────────────────────
    def _refresh_sections_tree(self):
        self.sections_tree.delete(*self.sections_tree.get_children())
        for sec in self.project.sections:
            assign_label = self._assignment_label(sec.assignment)
            preview = sec.lyrics[:60].replace("\n", " ") + ("…" if len(sec.lyrics) > 60 else "")
            num = str(sec.number) if sec.number else ""
            self.sections_tree.insert("", tk.END, iid=sec.id,
                                       values=(sec.section_type, num, assign_label, preview))

    def _assignment_label(self, assignment):
        if assignment == "all":
            return "🎤 Tous"
        elif assignment == "instrumental":
            return "🎸 Instrumental"
        elif assignment == "public":
            return "📢 Public"
        elif assignment == "mixed":
            return "🎭 Mixte"
        else:
            singer = self.project.singer_by_id(assignment)
            if singer:
                icon = "♂" if singer.voice_type == "male" else "♀"
                return f"{icon} {singer.name}"
            return assignment

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
        self.sec_perf_var.set(sec.performance_tag)
        self.sec_spoken_var.set(sec.spoken_line)

        # Assignment combo
        if sec.assignment == "all":
            self.sec_assign_var.set("Tous (all)")
        elif sec.assignment == "instrumental":
            self.sec_assign_var.set("Instrumental")
        elif sec.assignment == "public":
            self.sec_assign_var.set("Public")
        else:
            singer = self.project.singer_by_id(sec.assignment)
            if singer:
                self.sec_assign_var.set(f"{singer.name} ({singer.voice_type})")
            else:
                self.sec_assign_var.set("Tous (all)")

        # Mood tags
        self.mood_display.config(text=" | ".join(sec.mood_tags) if sec.mood_tags else "(aucun)")

        # Lyrics
        self.lyrics_text.delete("1.0", tk.END)
        self.lyrics_text.insert("1.0", sec.lyrics)

    def _save_section_details(self):
        if self._selected_section_idx is None:
            messagebox.showinfo("Info", "Sélectionnez une section d'abord.")
            return
        sec = self.project.sections[self._selected_section_idx]
        sec.section_type = self.sec_type_var.get()
        num_str = self.sec_num_var.get().strip()
        sec.number = int(num_str) if num_str.isdigit() else None
        sec.performance_tag = self.sec_perf_var.get()
        sec.spoken_line = self.sec_spoken_var.get().strip()

        # Parse assignment
        assign_text = self.sec_assign_var.get()
        if assign_text == "Tous (all)":
            sec.assignment = "all"
        elif assign_text == "Instrumental":
            sec.assignment = "instrumental"
        elif assign_text == "Public":
            sec.assignment = "public"
        else:
            # Chercher le chanteur par nom
            found = False
            for singer in self.project.singers:
                if f"{singer.name} ({singer.voice_type})" == assign_text:
                    sec.assignment = singer.id
                    found = True
                    break
            if not found:
                sec.assignment = "all"

        sec.lyrics = self.lyrics_text.get("1.0", tk.END).strip()
        self._refresh_sections_tree()
        self._refresh_preview()

    def _add_section(self):
        sec = Section("VERSE", len([s for s in self.project.sections if s.section_type == "VERSE"]) + 1)
        self.project.sections.append(sec)
        self._refresh_sections_tree()
        self.sections_tree.selection_set(sec.id)
        self._on_section_select()

    def _dup_section(self):
        if self._selected_section_idx is None:
            return
        orig = self.project.sections[self._selected_section_idx]
        new = deepcopy(orig)
        new.id = str(uuid.uuid4())[:8]
        if new.number:
            new.number += 1
        self.project.sections.insert(self._selected_section_idx + 1, new)
        self._refresh_sections_tree()

    def _del_section(self):
        if self._selected_section_idx is None:
            return
        del self.project.sections[self._selected_section_idx]
        self._selected_section_idx = None
        self._refresh_sections_tree()
        self._refresh_preview()

    def _move_section_up(self):
        if self._selected_section_idx is None or self._selected_section_idx == 0:
            return
        i = self._selected_section_idx
        self.project.sections[i], self.project.sections[i - 1] = \
            self.project.sections[i - 1], self.project.sections[i]
        self._selected_section_idx = i - 1
        self._refresh_sections_tree()
        self.sections_tree.selection_set(self.project.sections[i - 1].id)
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
        self.sections_tree.selection_set(self.project.sections[i + 1].id)
        self._refresh_preview()

    def _add_mood_tag(self):
        if self._selected_section_idx is None:
            messagebox.showinfo("Info", "Sélectionnez une section d'abord.")
            return
        tag = self.sec_mood_var.get().strip()
        if not tag:
            return
        sec = self.project.sections[self._selected_section_idx]
        if tag not in sec.mood_tags:
            sec.mood_tags.append(tag)
        self.mood_display.config(text=" | ".join(sec.mood_tags))
        self.sec_mood_var.set("")

    # ── Aperçu ────────────────────────────────
    def _refresh_preview(self):
        output = self.project.render_suno()
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", output)
        self._colorize_preview()
        self.preview_text.config(state=tk.DISABLED)

    def _colorize_preview(self):
        """Coloration syntaxique basique des tags entre crochets."""
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

            if any(kw in tag_text.upper() for kw in ["VERSE", "CHORUS", "BRIDGE", "INTRO",
                                                       "OUTRO", "HOOK", "BREAK", "PRE-CHORUS",
                                                       "POST-CHORUS", "INTERLUDE", "ROUND", "END"]):
                self.preview_text.tag_add("tag", start, end)
            elif any(kw in tag_text for kw in MOOD_TAGS[:5]):
                self.preview_text.tag_add("mood", start, end)
            else:
                self.preview_text.tag_add("singer", start, end)
            idx = end

    def _copy_preview(self):
        self.root.clipboard_clear()
        content = self.preview_text.get("1.0", tk.END).strip()
        self.root.clipboard_append(content)
        messagebox.showinfo("Copié !", "Le texte Suno a été copié dans le presse-papiers.")

    # ── Fichiers ──────────────────────────────
    def _new_project(self):
        if messagebox.askyesno("Nouveau projet", "Créer un nouveau projet ? Les modifications non sauvegardées seront perdues."):
            self.project = SongProject()
            self.title_var.set(self.project.title)
            self.style_var.set(self.project.style)
            self._refresh_all()

    def _save_project(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Projet Suno", "*.json")],
            initialfile=f"{self.project.title}.json",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.project.to_dict(), f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Sauvegardé", f"Projet sauvegardé dans :\n{path}")

    def _open_project(self):
        path = filedialog.askopenfilename(filetypes=[("Projet Suno", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.project = SongProject.from_dict(data)
        self.title_var.set(self.project.title)
        self.style_var.set(self.project.style)
        self._refresh_all()

    def _export_suno(self):
        output = self.project.render_suno()
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texte Suno", "*.txt")],
            initialfile=f"{self.project.title}_suno.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
        messagebox.showinfo("Exporté", f"Fichier Suno exporté :\n{path}")

    def _import_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Texte", "*.txt")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self._parse_txt_to_project(content)
        self._refresh_all()
        messagebox.showinfo("Importé", "Fichier importé et parsé. Vérifiez les sections.")

    def _parse_txt_to_project(self, content: str):
        """Parse basique d'un fichier texte Suno en projet."""
        self.project = SongProject()
        lines = content.split("\n")
        current_section = None
        current_lyrics = []

        for line in lines:
            stripped = line.strip()

            # Ligne globale type [4 singers, ...]
            if stripped.startswith("[") and "singer" in stripped.lower() and current_section is None:
                self.project.global_note = stripped
                continue

            # Section header
            if stripped.startswith("[") and stripped.endswith("]"):
                tag_content = stripped[1:-1].strip()
                upper = tag_content.upper()

                # Est-ce un header de section ?
                is_section = False
                for stype in SECTION_TYPES:
                    if upper.startswith(stype):
                        is_section = True
                        # Sauver la section précédente
                        if current_section is not None:
                            current_section.lyrics = "\n".join(current_lyrics).strip()
                            self.project.sections.append(current_section)
                            current_lyrics = []

                        # Parser le header
                        rest = tag_content[len(stype):].strip()
                        number = None
                        assignment = "all"

                        # Chercher un numéro
                        parts = rest.split("-", 1)
                        if parts[0].strip().isdigit():
                            number = int(parts[0].strip())
                            rest = parts[1].strip() if len(parts) > 1 else ""
                        elif len(parts) > 1 and parts[0].strip() == "":
                            rest = parts[1].strip()

                        # Chercher un nom de chanteur
                        if rest:
                            # Extraire le nom (avant parenthèses)
                            name_part = rest.split("(")[0].strip().rstrip("-").strip()
                            if name_part:
                                # Chercher ou créer le chanteur
                                singer = self._find_or_create_singer(name_part, rest)
                                assignment = singer.id

                        current_section = Section(stype, number, assignment)
                        break

                if not is_section:
                    # C'est un tag d'ambiance ou de performance
                    if current_section is not None:
                        if tag_content in MOOD_TAGS or any(m in tag_content for m in
                                ["Explosion", "Montée", "Chute", "Changement",
                                 "Batterie", "Synthé", "Piano", "Guitare", "Basse"]):
                            current_section.mood_tags.append(tag_content)
                        elif tag_content in PERFORMANCE_TAGS:
                            current_section.performance_tag = tag_content
                        else:
                            current_lyrics.append(stripped)
                    continue
            else:
                if stripped:
                    current_lyrics.append(stripped)

        # Dernière section
        if current_section is not None:
            current_section.lyrics = "\n".join(current_lyrics).strip()
            self.project.sections.append(current_section)

    def _find_or_create_singer(self, name, full_tag):
        """Cherche un chanteur par nom ou en crée un nouveau."""
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

    # ── Templates ─────────────────────────────
    def _apply_template(self, template_name):
        if self.project.sections and not messagebox.askyesno(
            "Template", f"Appliquer le template '{template_name}' ?\nLes sections actuelles seront remplacées."):
            return
        self.project.sections = []
        template = SONG_TEMPLATES[template_name]
        for sec_type, num, assign, lyrics in template:
            # Résoudre l'assignment
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
            self.project.sections.append(Section(sec_type, num, real_assign, lyrics))
        self._refresh_all()

    # ── Helpers ───────────────────────────────
    def _on_title_change(self):
        self.project.title = self.title_var.get()

    def _on_style_change(self):
        self.project.style = self.style_var.get()

    def _refresh_all(self):
        self._refresh_singers_list()
        self._refresh_sections_tree()
        self._refresh_preview()

    # ── Aide ──────────────────────────────────
    def _show_metatags_help(self):
        help_text = """
═══════════════════════════════════════════════════
   GUIDE DES METATAGS SUNO — Référence rapide
═══════════════════════════════════════════════════

Les metatags sont des instructions entre [crochets] placées 
dans les paroles pour guider l'IA Suno.

── TAGS DE STRUCTURE ──────────────────────────────
  [Intro]              Début instrumental
  [Verse 1], [Verse 2] Couplets
  [Pre-Chorus]         Pré-refrain (montée)
  [Chorus]             Refrain
  [Post-Chorus]        Après le refrain
  [Bridge]             Pont / transition
  [Hook]               Accroche (rap/hip-hop)
  [Interlude]          Intermède
  [Instrumental]       Passage instrumental
  [Break]              Pause
  [Outro]              Conclusion
  [End]                Fin nette

── TAGS DE VOIX / PERFORMANCE ─────────────────────
  [Male Vocals]        Voix masculine
  [Female Vocals]      Voix féminine
  [Duet]               Duo homme/femme
  [Harmony]            Harmonies vocales
  [Choir]              Chorale
  [Background Vocals]  Chœurs en arrière-plan
  [Spoken Word]        Parlé (pas chanté)
  [Whisper]            Chuchoté
  [Rap]                Passage rappé
  [Ad-lib]             Improvisations vocales
  [A cappella]         Sans instruments
  [Call and Response]  Appel et réponse

── TAGS DE DYNAMIQUE / AMBIANCE ───────────────────
  [Soft], [Gentle]     Doux, délicat
  [Building]           Montée en puissance
  [Crescendo]          Crescendo progressif
  [Energetic]          Énergique
  [Aggressive]         Agressif
  [Slow Down]          Ralentissement
  [Fade Out]           Fondu de sortie
  [Drop]               Drop (EDM)

── COMBINAISONS EFFICACES ─────────────────────────

  [Verse 1 - Male Vocals, aggressive]
  [Chorus - Female Vocals, powerful]
  [Bridge - Whisper, intimate]
  [Spoken Word]
  "Texte parlé entre guillemets"

── ASTUCES ────────────────────────────────────────

• Les tags sont des SUGGESTIONS, pas des ordres absolus
• Suno interprète le contexte global (style + tags)
• Combiner structure + voix + ambiance = meilleur résultat
• Les guillemets "" aident pour les parties parlées
• La CASSE (majuscules) peut renforcer certains tags
"""
        self._show_help_window("Guide des Metatags Suno", help_text)

    def _show_multivoice_help(self):
        help_text = """
═══════════════════════════════════════════════════
   GUIDE MULTI-VOIX POUR SUNO
═══════════════════════════════════════════════════

Suno ne supporte pas nativement les chanteurs nommés,
mais plusieurs techniques permettent de simuler des
multi-voix efficacement.

── TECHNIQUE 1 : TAGS VOIX DANS LES SECTIONS ─────

La plus fiable. Combinez le type de section avec une 
description vocale :

  [VERSE 1 - Male Voice, deep and aggressive]
  (paroles du chanteur 1)

  [VERSE 2 - Female Voice, soft and melodic]
  (paroles de la chanteuse)

  [CHORUS - Duet, powerful harmonies]
  (paroles ensemble)

── TECHNIQUE 2 : NOMS + TYPE VOCAL ────────────────

Utilisez un nom + le type de voix entre parenthèses. 
Suno ne "connaît" pas le nom, mais le type de voix 
influence le rendu :

  [VERSE 1 - Mo (male)]
  [VERSE 2 - Fènrice (male)]
  [VERSE 3 - Thé (female)]

── TECHNIQUE 3 : PERSONAS / VOICES (v5.5) ─────────

La méthode OFFICIELLE pour les voix multiples :
1. Créez une Persona/Voice pour chaque chanteur
2. Générez chaque section SÉPARÉMENT avec la Persona
3. Assemblez ensuite dans Suno Studio

C'est la méthode la plus fiable pour des voix 
véritablement distinctes.

── TECHNIQUE 4 : STYLE PROMPT + TAGS ─────────────

Dans le champ "Style of Music", précisez :
  "male and female vocal duet, alternating verses"
  "multi-voice rock anthem, 3 male voices 1 female"

Puis dans les paroles, utilisez les tags de voix
pour guider les transitions.

── TECHNIQUE 5 : DIALOGUES / CALL & RESPONSE ─────

Pour des échanges rapides :

  [Call and Response]
  [Male Voice] "Où est l'ennemi ?"
  [Female Voice] "Derrière toi !"
  [All Voices] On fonce ensemble !

── PHONÉTIQUE ─────────────────────────────────────

Pour que Suno prononce correctement un pseudo :
• Écrivez phonétiquement : "Cul-ro" → "Kul-roh"
• Séparez les syllabes avec des tirets
• Testez plusieurs variantes
• Les noms courts marchent mieux

── CONSEILS PRATIQUES ─────────────────────────────

1. MOINS C'EST PLUS : Trop de tags confond Suno
2. COHÉRENCE : Gardez le même format de tags
3. STYLE PROMPT : Le style global a PLUS d'impact
   que les tags individuels
4. GÉNÉRER PAR SECTIONS : Pour un vrai multi-voix,
   générez chaque partie séparément
5. EXTEND : Utilisez "Extend" pour ajouter des
   sections avec des voix différentes
"""
        self._show_help_window("Guide Multi-Voix Suno", help_text)

    def _show_about(self):
        messagebox.showinfo("À propos",
            "🎵 Suno Song Builder\n\n"
            "Outil de structuration de chansons pour Suno AI.\n"
            "Gère les metatags, multi-voix et phonétique.\n\n"
            "Compatible Suno v4 / v4.5 / v5 / v5.5")

    def _show_help_window(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("700x600")
        txt = scrolledtext.ScrolledText(win, font=("Consolas", 10), wrap=tk.WORD,
                                         bg="#1e1e2e", fg="#cdd6f4")
        txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        txt.insert("1.0", text)
        txt.config(state=tk.DISABLED)


# ─────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = SunoBuilderApp(root)
    root.mainloop()
