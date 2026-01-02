import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import winsound
import database as db
import analytics

# --- THEME ---
C_BG_MAIN     = "#0B1120"
C_BG_SIDE     = "#151e32"
C_CARD        = "#1e293b"
C_CARD_HOVER  = "#334155"
C_ACCENT      = "#38bdf8"
C_TEXT_MAIN   = "#f1f5f9"
C_TEXT_SUB    = "#94a3b8"
C_DANGER      = "#ef4444"
C_SUCCESS     = "#4ade80"

# --- GLOBAL SETTINGS ---
SOUND_ON = True

def get_font(size, weight="normal", family="Segoe UI"):
    return (family, size, weight)

# --- SOUND UTILS ---
def play_click():
    if SOUND_ON:
        try: winsound.Beep(800, 50)
        except: pass

def play_success():
    if SOUND_ON:
        try: winsound.Beep(1200, 100)
        except: pass

# --- CUSTOM WIDGETS ---
class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, corner_radius, color, text, command, text_color="#0f172a"):
        super().__init__(parent, width=width, height=height, bg=C_BG_MAIN, highlightthickness=0)
        self.command = command
        self.color = color
        self.text = text
        self.text_color = text_color
        self.radius = corner_radius
        self.bind("<Button-1>", self._on_click)
        self.render()

    def render(self):
        self.delete("all")
        r = self.radius
        w, h = int(self["width"]), int(self["height"])
        self.create_oval(0, 0, r*2, r*2, fill=self.color, outline=self.color)
        self.create_oval(w-r*2, 0, w, r*2, fill=self.color, outline=self.color)
        self.create_oval(0, h-r*2, r*2, h, fill=self.color, outline=self.color)
        self.create_oval(w-r*2, h-r*2, w, h, fill=self.color, outline=self.color)
        self.create_rectangle(r, 0, w-r, h, fill=self.color, outline=self.color)
        self.create_rectangle(0, r, w, h-r, fill=self.color, outline=self.color)
        self.create_text(w/2, h/2, text=self.text, fill=self.text_color, font=get_font(11, "bold"))

    def _on_click(self, e):
        play_click()
        self.command()

class CircularProgress(tk.Canvas):
    def __init__(self, parent, size=140, width=12, bg_color=C_CARD):
        super().__init__(parent, width=size, height=size, bg=bg_color, highlightthickness=0)
        self.size = size
        self.width = width
        self.percentage = 0
        self.render()

    def set_progress(self, val):
        self.percentage = val
        self.render()

    def render(self):
        self.delete("all")
        w, h = self.size, self.size
        pad = self.width
        self.create_oval(pad, pad, w-pad, h-pad, outline="#334155", width=self.width)
        if self.percentage > 0:
            start = 90
            extent = -360 * (self.percentage / 100)
            col = C_SUCCESS if self.percentage == 100 else C_ACCENT
            self.create_arc(pad, pad, w-pad, h-pad, start=start, extent=extent, style="arc", outline=col, width=self.width)
        self.create_text(w/2, h/2 - 10, text=f"{int(self.percentage)}%", fill=C_TEXT_MAIN, font=get_font(22, "bold"))
        self.create_text(w/2, h/2 + 15, text="TODAY", fill=C_TEXT_SUB, font=get_font(9, "bold"))

class GoalCard(tk.Frame):
    def __init__(self, parent, goal_data, on_toggle, on_delete):
        super().__init__(parent, bg=C_BG_MAIN, pady=6)
        self.g_id, self.title, _, self.completed = goal_data
        self.on_toggle = on_toggle
        self.surface = tk.Frame(self, bg=C_CARD, padx=15, pady=15)
        self.surface.pack(fill="x", expand=True)
        
        # Checkbox
        self.chk = tk.Canvas(self.surface, width=26, height=26, bg=C_CARD, highlightthickness=0)
        self.chk.pack(side="left", padx=(0, 15))
        col = C_SUCCESS if self.completed else "#475569"
        self.chk.create_oval(2,2, 24,24, outline=col, width=2, fill=col if self.completed else "")
        if self.completed: self.chk.create_line(8,13, 12,17, 18,9, fill=C_BG_MAIN, width=3, smooth=True)
        
        # Label
        fg = "#64748b" if self.completed else C_TEXT_MAIN
        font = get_font(12, "overstrike" if self.completed else "normal")
        lbl = tk.Label(self.surface, text=self.title, font=font, bg=C_CARD, fg=fg, anchor="w")
        lbl.pack(side="left", fill="x", expand=True)
        
        # Delete
        btn_del = tk.Label(self.surface, text="×", font=("Arial", 18), bg=C_CARD, fg=C_CARD, cursor="hand2")
        btn_del.pack(side="right")
        btn_del.bind("<Button-1>", lambda e: on_delete(self.g_id))
        btn_del.bind("<Enter>", lambda e: btn_del.config(fg=C_DANGER))
        btn_del.bind("<Leave>", lambda e: btn_del.config(fg=C_CARD))

        for w in [self.surface, lbl, self.chk]:
            w.bind("<Button-1>", lambda e: self.on_toggle(self.g_id, self.completed))
            w.bind("<Enter>", lambda e: self.surface.config(bg=C_CARD_HOVER))
            w.bind("<Leave>", lambda e: self.surface.config(bg=C_CARD))

class UltraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Ultra")
        self.root.geometry("1150x780")
        self.root.configure(bg=C_BG_MAIN)
        try:
            self.root.iconbitmap("app.ico")
        except:
            pass     # Ignores error if app.ico file is missing
        
        db.init_db()
        self.current_date = date.today().isoformat()
        
        self.nav_buttons = {}
        self.setup_styles()
        self.build_layout()
        self.show_page("Dashboard")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=C_BG_MAIN)
        style.layout("Vertical.TScrollbar", [('Scrollbar.trough', {'children': [('Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'ns'})])
        style.configure("Vertical.TScrollbar", background=C_CARD, troughcolor=C_BG_MAIN, borderwidth=0)

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=C_BG_SIDE, width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="FOCUS", font=get_font(22, "bold"), bg=C_BG_SIDE, fg=C_TEXT_MAIN).pack(padx=30, pady=(50,5), anchor="w")

        self.create_nav_item("Dashboard")
        self.create_nav_item("Analytics")
        self.create_nav_item("Settings")

        self.main_container = tk.Frame(self.root, bg=C_BG_MAIN)
        self.main_container.pack(side="right", fill="both", expand=True)

        self.frames = {}
        for PageName in ["Dashboard", "Analytics", "Settings"]:
            frame = tk.Frame(self.main_container, bg=C_BG_MAIN)
            self.frames[PageName] = frame

        self.build_dashboard(self.frames["Dashboard"])
        self.build_analytics(self.frames["Analytics"])
        self.build_settings(self.frames["Settings"])

    def create_nav_item(self, name):
        container = tk.Frame(self.sidebar, bg=C_BG_SIDE, height=50)
        container.pack(fill="x", pady=2)
        indicator = tk.Frame(container, bg=C_BG_SIDE, width=4, height=50)
        indicator.pack(side="left")
        lbl = tk.Label(container, text=name, font=get_font(11), bg=C_BG_SIDE, fg=C_TEXT_SUB, cursor="hand2")
        lbl.pack(side="left", padx=25)
        self.nav_buttons[name] = (container, indicator, lbl)
        lbl.bind("<Button-1>", lambda e: self.show_page(name))
        container.bind("<Button-1>", lambda e: self.show_page(name))

    def show_page(self, page_name):
        for name, (cont, ind, lbl) in self.nav_buttons.items():
            if name == page_name:
                cont.config(bg="#1e293b")
                ind.config(bg=C_ACCENT)
                lbl.config(bg="#1e293b", fg=C_ACCENT, font=get_font(11, "bold"))
            else:
                cont.config(bg=C_BG_SIDE)
                ind.config(bg=C_BG_SIDE)
                lbl.config(bg=C_BG_SIDE, fg=C_TEXT_SUB, font=get_font(11))

        for frame in self.frames.values():
            frame.pack_forget()
        
        self.frames[page_name].pack(fill="both", expand=True, padx=50, pady=40)
        
        if page_name == "Dashboard": self.refresh_dashboard()
        elif page_name == "Analytics": self.refresh_analytics()

    # --- DASHBOARD ---
    def build_dashboard(self, parent):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greet = "Good Morning"
        elif 12 <= hour < 17:
            greet = "Good Afternoon"
        elif 17 <= hour < 21:
            greet = "Good Evening"
        else:
            greet = "Night Conqueror"

        tk.Label(parent, text=f"{greet},", font=get_font(32, "bold"), bg=C_BG_MAIN, fg=C_TEXT_MAIN).pack(anchor="w")
        tk.Label(parent, text="Let's get things done.", font=get_font(12), bg=C_BG_MAIN, fg=C_TEXT_SUB).pack(anchor="w", pady=(5, 30))

        input_frame = tk.Frame(parent, bg=C_BG_MAIN)
        input_frame.pack(fill="x", pady=(0, 20))
        self.entry = tk.Entry(input_frame, font=get_font(14), bg=C_BG_MAIN, fg=C_TEXT_MAIN, 
                              insertbackground=C_ACCENT, bd=0, highlightthickness=1, highlightcolor=C_ACCENT, highlightbackground=C_CARD)
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 15))
        self.entry.bind("<Return>", self.add_goal)
        RoundedButton(input_frame, 120, 45, 20, C_ACCENT, "+ ADD", self.add_goal, "#0f172a").pack(side="right")

        list_frame = tk.Frame(parent, bg=C_BG_MAIN)
        list_frame.pack(fill="both", expand=True)
        self.dash_canvas = tk.Canvas(list_frame, bg=C_BG_MAIN, highlightthickness=0)
        self.dash_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.dash_canvas.yview)
        self.dash_content = tk.Frame(self.dash_canvas, bg=C_BG_MAIN)
        
        self.dash_content.bind("<Configure>", lambda e: self.dash_canvas.configure(scrollregion=self.dash_canvas.bbox("all")))
        self.dash_canvas.create_window((0, 0), window=self.dash_content, anchor="nw", width=800)
        self.dash_canvas.configure(yscrollcommand=self.dash_scroll.set)
        
        self.dash_canvas.pack(side="left", fill="both", expand=True)
        self.dash_scroll.pack(side="right", fill="y")
        self.dash_canvas.bind_all("<MouseWheel>", lambda e: self.dash_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def refresh_dashboard(self):
        for w in self.dash_content.winfo_children(): w.destroy()
        goals = db.get_goals_by_date(self.current_date)
        if not goals: tk.Label(self.dash_content, text="No goals for today.", font=get_font(14), bg=C_BG_MAIN, fg=C_TEXT_SUB).pack(pady=40)
        for g in goals: GoalCard(self.dash_content, g, self.toggle_goal, self.delete_goal).pack(fill="x", pady=(0, 10))

    # --- ANALYTICS ---
    def build_analytics(self, parent):
        tk.Label(parent, text="Analytics Overview", font=get_font(24, "bold"), bg=C_BG_MAIN, fg=C_TEXT_MAIN).pack(anchor="w", pady=(0,20))
        
        # Main Grid
        grid = tk.Frame(parent, bg=C_BG_MAIN)
        grid.pack(fill="x")
        
        # --- LEFT: Daily Ring ---
        card_p = tk.Frame(grid, bg=C_CARD, padx=30, pady=30)
        card_p.pack(side="left", padx=(0, 20))
        self.ana_progress = CircularProgress(card_p, size=140, bg_color=C_CARD)
        self.ana_progress.pack()
        
        # --- RIGHT: Stats Column ---
        stats_col = tk.Frame(grid, bg=C_BG_MAIN)
        stats_col.pack(side="left", fill="both", expand=True)

        # Row 1: Activity Streak + Most Missed
        row1 = tk.Frame(stats_col, bg=C_BG_MAIN)
        row1.pack(fill="x", pady=(0, 10))
        
        # Activity Streak Card
        c1 = tk.Frame(row1, bg=C_CARD, padx=20, pady=15)
        c1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(c1, text="ACTIVE DAYS", font=get_font(9, "bold"), bg=C_CARD, fg="#64748b").pack(anchor="w")
        self.ana_streak = tk.Label(c1, text="0", font=get_font(20, "bold"), bg=C_CARD, fg=C_TEXT_MAIN)
        self.ana_streak.pack(anchor="w")

        # Missed Card
        c2 = tk.Frame(row1, bg=C_CARD, padx=20, pady=15)
        c2.pack(side="left", fill="x", expand=True)
        tk.Label(c2, text="OFTEN MISSED", font=get_font(9, "bold"), bg=C_CARD, fg="#64748b").pack(anchor="w")
        self.ana_missed = tk.Label(c2, text="-", font=get_font(12, "bold"), bg=C_CARD, fg=C_DANGER)
        self.ana_missed.pack(anchor="w")

        # Row 2: PERFECT STREAK (New Feature)
        row2 = tk.Frame(stats_col, bg=C_CARD, padx=20, pady=15)
        row2.pack(fill="x")
        
        GOLD = "#f59e0b"
        
        tk.Label(row2, text="PERFECT STREAK (100% DONE)", font=get_font(10, "bold"), bg=C_CARD, fg=GOLD).pack(anchor="w")
        self.ana_perfect = tk.Label(row2, text="0 Days", font=get_font(28, "bold"), bg=C_CARD, fg=C_TEXT_MAIN)
        self.ana_perfect.pack(anchor="w")
        tk.Label(row2, text="Consecutive days where you crushed every single goal.", font=get_font(9), bg=C_CARD, fg="#64748b").pack(anchor="w")

        # Chart Section
        tk.Label(parent, text="Last 7 Days", font=get_font(14, "bold"), bg=C_BG_MAIN, fg=C_TEXT_MAIN).pack(anchor="w", pady=(30, 10))
        
        chart_frame = tk.Frame(parent, bg=C_CARD, padx=20, pady=20)
        chart_frame.pack(fill="x")
        self.chart_canvas = tk.Canvas(chart_frame, bg=C_CARD, height=130, highlightthickness=0)
        self.chart_canvas.pack(fill="x")

    def refresh_analytics(self):
        all_goals = db.get_all_goals()
        goals_today = db.get_goals_by_date(self.current_date)
        
        # 1. Update Daily Ring
        self.ana_progress.set_progress(analytics.calculate_daily_completion(goals_today))
        
        # 2. Update Stats
        streak_active = analytics.calculate_streak(all_goals)
        streak_perfect = analytics.calculate_perfect_streak(all_goals) # New Logic
        missed = analytics.get_most_missed(all_goals)
        
        self.ana_streak.config(text=f"{streak_active} Days")
        self.ana_perfect.config(text=f"{streak_perfect} Days")
        self.ana_missed.config(text=missed if missed != "None" else "None")
        
        # 3. Draw Chart
        self.draw_chart(analytics.get_weekly_summary(all_goals))
       

    def draw_chart(self, summary):
        self.chart_canvas.delete("all")
        dates = sorted(list(summary.keys()))
        bar_w, gap = 50, 30
        start_x = 20
        for i, d in enumerate(dates):
            pct = summary[d]
            x = start_x + i * (bar_w + gap)
            bar_h = (pct / 100) * 120
            self.chart_canvas.create_rectangle(x, 0, x+bar_w, 120, fill="#334155", outline="")
            col = C_SUCCESS if pct == 100 else C_ACCENT
            if pct > 0: self.chart_canvas.create_rectangle(x, 120-bar_h, x+bar_w, 120, fill=col, outline="")
            self.chart_canvas.create_text(x+bar_w/2, 135, text=d.split("-")[-1], fill=C_TEXT_SUB, font=get_font(9))

    # --- SETTINGS ---
    def build_settings(self, parent):
        tk.Label(parent, text="Settings", font=get_font(24, "bold"), bg=C_BG_MAIN, fg=C_TEXT_MAIN).pack(anchor="w", pady=(0,30))
        
        # --- Section 1: Preferences ---
        tk.Label(parent, text="PREFERENCES", font=get_font(10, "bold"), bg=C_BG_MAIN, fg=C_TEXT_SUB).pack(anchor="w", pady=(0, 10))
        card_pref = tk.Frame(parent, bg=C_CARD, padx=20, pady=20)
        card_pref.pack(fill="x", pady=(0, 30))
        
        # Sound Row
        row_sound = tk.Frame(card_pref, bg=C_CARD)
        row_sound.pack(fill="x")
        tk.Label(row_sound, text="Sound Effects", font=get_font(12), bg=C_CARD, fg=C_TEXT_MAIN).pack(side="left")
        self.btn_sound = tk.Button(row_sound, text="ON" if SOUND_ON else "OFF", command=self.toggle_sound, 
                                   bg=C_ACCENT, fg="#0f172a", font=("Arial", 9, "bold"), width=6, relief="flat")
        self.btn_sound.pack(side="right")

        # --- Section 2: Danger Zone ---
        tk.Label(parent, text="DANGER ZONE", font=get_font(10, "bold"), bg=C_BG_MAIN, fg=C_DANGER).pack(anchor="w", pady=(0, 10))
        card_danger = tk.Frame(parent, bg=C_CARD, padx=20, pady=20)
        card_danger.pack(fill="x", pady=(0, 30))

        # Clear Data Row
        row_clear = tk.Frame(card_danger, bg=C_CARD)
        row_clear.pack(fill="x")
        
        text_frame = tk.Frame(row_clear, bg=C_CARD)
        text_frame.pack(side="left")
        tk.Label(text_frame, text="Clear All Data", font=get_font(12, "bold"), bg=C_CARD, fg=C_DANGER).pack(anchor="w")
        tk.Label(text_frame, text="Permanently delete all goals and statistics.", font=get_font(10), bg=C_CARD, fg=C_TEXT_SUB).pack(anchor="w")

        btn_del = tk.Button(row_clear, text="DELETE", command=self.clear_all_data, 
                            bg=C_DANGER, fg="white", font=("Arial", 9, "bold"), width=10, relief="flat")
        btn_del.pack(side="right")

        # --- Section 3: About Us  ---
        tk.Label(parent, text="ABOUT", font=get_font(10, "bold"), bg=C_BG_MAIN, fg=C_TEXT_SUB).pack(anchor="w", pady=(0, 10))
        card_about = tk.Frame(parent, bg=C_CARD, padx=20, pady=25)
        card_about.pack(fill="x")

        # Logo / Title
        tk.Label(card_about, text="Focus Ultra", font=get_font(16, "bold"), bg=C_CARD, fg=C_ACCENT).pack(anchor="center")
        
        # Author Credit
        tk.Label(card_about, text="Built by Prashant", font=get_font(11), bg=C_CARD, fg=C_TEXT_MAIN).pack(anchor="center", pady=(5, 0))
        
        # Version info 
        tk.Label(card_about, text="v1.0 • Offline Edition", font=get_font(9), bg=C_CARD, fg="#64748b").pack(anchor="center", pady=(10, 0))

    def toggle_sound(self):
        global SOUND_ON
        SOUND_ON = not SOUND_ON
        self.btn_sound.config(text="ON" if SOUND_ON else "OFF", bg=C_ACCENT if SOUND_ON else "#334155")
        play_click()

    def clear_all_data(self):
        play_click()
        confirm = messagebox.askyesno("Confirm Data Wipe", 
                                      "Are you strictly sure?\n\nThis will permanently delete ALL goals and history.\nThis action cannot be undone.", 
                                      icon='warning')
        if confirm:
            db.clear_all_data()
            messagebox.showinfo("Success", "All data has been cleared.")
            self.refresh_dashboard()

    # --- ACTIONS ---
    def add_goal(self, e=None):
        text = self.entry.get().strip()
        if text:
            db.add_goal(text, self.current_date)
            self.entry.delete(0, tk.END)
            play_click()
            self.refresh_dashboard()

    def toggle_goal(self, gid, status):
        db.toggle_goal_status(gid, status)
        if not status: play_success()
        else: play_click()
        self.refresh_dashboard()

    def delete_goal(self, gid):
        if messagebox.askyesno("Confirm", "Delete this goal?"):
            db.delete_goal(gid)
            self.refresh_dashboard()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = UltraApp(root)
    root.mainloop()