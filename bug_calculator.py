import tkinter as tk
from tkinter import ttk, font

# BUG Rating lookup tables from the spreadsheet (IES TM-15)

LZ_BACKLIGHT = {
    "LZ0": {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"},
    "LZ1": {"A": 0, "B": 1, "C": 2, "D": "No Limit"},
    "LZ2": {"A": 0, "B": 2, "C": 3, "D": "No Limit"},
    "LZ3": {"A": 1, "B": 3, "C": 4, "D": "No Limit"},
    "LZ4": {"A": 1, "B": 3, "C": 4, "D": "No Limit"},
}

LZ_UPLIGHT = {
    # (zone, fixture_type) -> max U
    ("LZ0", "Area Lighting"): "N/A",
    ("LZ0", "Other"):         "N/A",
    ("LZ1", "Area Lighting"): 0,
    ("LZ1", "Other"):         1,
    ("LZ2", "Area Lighting"): 0,
    ("LZ2", "Other"):         2,
    ("LZ3", "Area Lighting"): 0,
    ("LZ3", "Other"):         3,
    ("LZ4", "Area Lighting"): 0,
    ("LZ4", "Other"):         4,
}

LZ_GLARE = {
    "LZ0": {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"},
    "LZ1": {"A": 0, "B": 0, "C": 0, "D": 1},
    "LZ2": {"A": 0, "B": 0, "C": 1, "D": 2},
    "LZ3": {"A": 0, "B": 1, "C": 1, "D": 3},
    "LZ4": {"A": 1, "B": 1, "C": 2, "D": 4},
}

def get_ratio_category(distance, mh):
    """Return ratio category A/B/C/D based on distance vs mounting height."""
    if mh <= 0:
        return None
    ratio = distance / mh
    if ratio <= 0.5:
        return "A"
    elif ratio <= 1.0:
        return "B"
    elif ratio <= 2.0:
        return "C"
    else:
        return "D"

def calculate():
    try:
        mh = float(entry_mh.get())
        front = float(entry_front.get())
        back = float(entry_back.get())
    except ValueError:
        result_frame.config(bg="#fff3cd")
        lbl_error.config(text="⚠  Please enter valid numeric values.", fg="#856404", bg="#fff3cd")
        lbl_error.grid(row=0, column=0, columnspan=2, padx=16, pady=10)
        for w in result_widgets:
            w.grid_remove()
        return

    if mh <= 0:
        result_frame.config(bg="#fff3cd")
        lbl_error.config(text="⚠  Mounting height must be greater than 0.", fg="#856404", bg="#fff3cd")
        lbl_error.grid(row=0, column=0, columnspan=2, padx=16, pady=10)
        for w in result_widgets:
            w.grid_remove()
        return

    zone = combo_zone.get()
    fixture = combo_fixture.get()
    min_dist = min(front, back)

    b_ratio = get_ratio_category(min_dist, mh)
    g_ratio = get_ratio_category(min_dist, mh)

    max_b = LZ_BACKLIGHT[zone][b_ratio]
    max_u = LZ_UPLIGHT[(zone, fixture)]
    max_g = LZ_GLARE[zone][g_ratio]

    # Update ratio labels
    lbl_ratio_val.config(text=f"Ratio {b_ratio}  (min dist / MH = {min_dist/mh:.2f})")

    def fmt(v):
        return str(v) if v != "N/A" else "N/A (zone not applicable)"

    lbl_b_val.config(text=fmt(max_b))
    lbl_u_val.config(text=fmt(max_u))
    lbl_g_val.config(text=fmt(max_g))

    # Color-code results
    def color(v):
        if v == "N/A":
            return "#6c757d"
        if v == "No Limit":
            return "#198754"
        if isinstance(v, int) and v == 0:
            return "#dc3545"
        return "#0d6efd"

    lbl_b_val.config(fg=color(max_b))
    lbl_u_val.config(fg=color(max_u))
    lbl_g_val.config(fg=color(max_g))

    lbl_error.grid_remove()
    result_frame.config(bg="#f0f7ff")
    for w in result_widgets:
        w.grid()


# ── GUI setup ────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("BUG Rating Calculator")
root.resizable(False, False)
root.configure(bg="#f8f9fa")

title_font  = font.Font(family="Segoe UI", size=14, weight="bold")
label_font  = font.Font(family="Segoe UI", size=10)
value_font  = font.Font(family="Segoe UI", size=11, weight="bold")
small_font  = font.Font(family="Segoe UI", size=8)

ACCENT = "#0d6efd"
BG     = "#f8f9fa"
CARD   = "#ffffff"
BORDER = "#dee2e6"

# ── Title ────────────────────────────────────────────────────────────────────
tk.Label(root, text="BUG Rating Calculator", font=title_font,
         bg=BG, fg="#212529").grid(row=0, column=0, padx=24, pady=(18,2), sticky="w")
tk.Label(root, text="Based on IES TM-15 simplified guidelines",
         font=small_font, bg=BG, fg="#6c757d").grid(row=1, column=0, padx=24, sticky="w")

# ── Input card ───────────────────────────────────────────────────────────────
inp_frame = tk.LabelFrame(root, text=" Inputs ", font=label_font,
                          bg=CARD, fg="#495057", relief="groove", bd=1)
inp_frame.grid(row=2, column=0, padx=20, pady=12, sticky="ew")

fields = [
    ("Mounting Height (ft):",              "entry_mh",      "20"),
    ("Distance from Property Line – Front (ft):", "entry_front", "41"),
    ("Distance from Property Line – Back (ft):",  "entry_back",  "100"),
]
entries = {}
for i, (lbl, var, default) in enumerate(fields):
    tk.Label(inp_frame, text=lbl, font=label_font, bg=CARD, anchor="w"
             ).grid(row=i, column=0, padx=14, pady=6, sticky="w")
    e = tk.Entry(inp_frame, font=label_font, width=10, relief="solid", bd=1)
    e.insert(0, default)
    e.grid(row=i, column=1, padx=14, pady=6, sticky="w")
    entries[var] = e

entry_mh    = entries["entry_mh"]
entry_front = entries["entry_front"]
entry_back  = entries["entry_back"]

# Fixture Type
tk.Label(inp_frame, text="Fixture Type:", font=label_font, bg=CARD, anchor="w"
         ).grid(row=3, column=0, padx=14, pady=6, sticky="w")
combo_fixture = ttk.Combobox(inp_frame, values=["Area Lighting", "Other"],
                              state="readonly", width=16, font=label_font)
combo_fixture.set("Area Lighting")
combo_fixture.grid(row=3, column=1, padx=14, pady=6, sticky="w")

# Lighting Zone
tk.Label(inp_frame, text="Lighting Zone:", font=label_font, bg=CARD, anchor="w"
         ).grid(row=4, column=0, padx=14, pady=6, sticky="w")
combo_zone = ttk.Combobox(inp_frame, values=["LZ0","LZ1","LZ2","LZ3","LZ4"],
                           state="readonly", width=16, font=label_font)
combo_zone.set("LZ3")
combo_zone.grid(row=4, column=1, padx=14, pady=6, sticky="w")

# Calculate button
btn = tk.Button(inp_frame, text="Calculate BUG Rating", font=value_font,
                bg=ACCENT, fg="white", activebackground="#0b5ed7",
                activeforeground="white", relief="flat", padx=12, pady=6,
                cursor="hand2", command=calculate)
btn.grid(row=5, column=0, columnspan=2, padx=14, pady=14, sticky="ew")

# ── Results card ─────────────────────────────────────────────────────────────
result_frame = tk.LabelFrame(root, text=" Results ", font=label_font,
                              bg="#f0f7ff", fg="#495057", relief="groove", bd=1)
result_frame.grid(row=3, column=0, padx=20, pady=(0,12), sticky="ew")

lbl_error = tk.Label(result_frame, text="", font=label_font, bg="#fff3cd", wraplength=340)

def make_result_row(parent, label, row):
    lbl = tk.Label(parent, text=label, font=label_font, bg="#f0f7ff", anchor="w")
    lbl.grid(row=row, column=0, padx=14, pady=5, sticky="w")
    val = tk.Label(parent, text="—", font=value_font, bg="#f0f7ff", anchor="w")
    val.grid(row=row, column=1, padx=14, pady=5, sticky="w")
    return lbl, val

lbl_ratio_lbl, lbl_ratio_val = make_result_row(result_frame, "Calculated Ratio:", 1)
lbl_b_lbl,     lbl_b_val     = make_result_row(result_frame, "Max B (Backlight):", 2)
lbl_u_lbl,     lbl_u_val     = make_result_row(result_frame, "Max U (Uplight):",   3)
lbl_g_lbl,     lbl_g_val     = make_result_row(result_frame, "Max G (Glare):",     4)

result_widgets = [lbl_ratio_lbl, lbl_ratio_val,
                  lbl_b_lbl, lbl_b_val,
                  lbl_u_lbl, lbl_u_val,
                  lbl_g_lbl, lbl_g_val]

# ── Footer ───────────────────────────────────────────────────────────────────
tk.Label(root, text="Ratio A ≤0.5 MH  |  B >0.5–1 MH  |  C >1–2 MH  |  D >2 MH",
         font=small_font, bg=BG, fg="#6c757d").grid(row=4, column=0, pady=(0,14))

# Run initial calculation with defaults
root.after(100, calculate)
root.mainloop()
