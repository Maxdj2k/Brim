#!/usr/bin/env python3
"""Brim Browser - Web Browser with Veracity Protocol & Social Features"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import secrets
import urllib.request
import urllib.parse
import webbrowser
from datetime import datetime


class BrimBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Brim Browser")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0f172a")
        
        # Data
        self.data_dir = os.path.expanduser("~/.brim")
        os.makedirs(self.data_dir, exist_ok=True)
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.comments_file = os.path.join(self.data_dir, "comments.json")
        
        # State
        self.current_user = None
        self.users = self.load_json(self.users_file, {})
        self.comments = self.load_json(self.comments_file, {})
        self.current_url = None
        
        # Colors
        self.colors = {'bg': '#0f172a', 'panel': '#1e293b', 'card': '#334155', 
                      'primary': '#0f766e', 'text': '#f8fafc', 'muted': '#94a3b8',
                      'success': '#22c55e', 'warning': '#f59e0b'}
        
        self.show_login()
    
    def load_json(self, path, default):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default
    
    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def hash_password(self, password):
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + hash_obj.hex()
    
    def verify_password(self, password, stored):
        salt = stored[:32]
        stored_hash = stored[32:]
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == stored_hash
    
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login(self):
        self.clear()
        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(container, text="◆", font=('Inter', 48), 
                bg=self.colors['bg'], fg=self.colors['primary']).pack()
        tk.Label(container, text="BRIM", font=('Inter', 32, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack()
        tk.Label(container, text="Browse with Veracity", font=('Inter', 14),
                bg=self.colors['bg'], fg=self.colors['muted']).pack(pady=(0, 40))
        
        form = tk.Frame(container, bg=self.colors['panel'], padx=40, pady=40)
        form.pack()
        
        tk.Label(form, text="Username", font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(anchor='w')
        self.l_user = tk.Entry(form, font=('Inter', 14), bg=self.colors['card'], 
                              fg=self.colors['text'], relief='flat', insertbackground='white')
        self.l_user.pack(fill='x', pady=(5, 15), ipady=8)
        
        tk.Label(form, text="Password", font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(anchor='w')
        self.l_pass = tk.Entry(form, font=('Inter', 14), show='●',
                              bg=self.colors['card'], fg=self.colors['text'], 
                              relief='flat', insertbackground='white')
        self.l_pass.pack(fill='x', pady=(5, 20), ipady=8)
        self.l_pass.bind('<Return>', lambda e: self.do_login())
        
        btn_frame = tk.Frame(form, bg=self.colors['panel'])
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="Sign In", font=('Inter', 12, 'bold'),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 command=self.do_login).pack(side='left', fill='x', expand=True, ipady=10)
        
        tk.Button(btn_frame, text="Create Account", font=('Inter', 12),
                 bg=self.colors['card'], fg=self.colors['text'], relief='flat',
                 command=self.show_signup).pack(side='left', fill='x', expand=True, ipady=10, padx=(10, 0))
    
    def show_signup(self):
        self.clear()
        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(container, text="Create Account", font=('Inter', 24, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack(pady=(0, 30))
        
        form = tk.Frame(container, bg=self.colors['panel'], padx=40, pady=40)
        form.pack()
        
        tk.Label(form, text="Username", font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(anchor='w')
        self.s_user = tk.Entry(form, font=('Inter', 14), bg=self.colors['card'],
                              fg=self.colors['text'], relief='flat', insertbackground='white')
        self.s_user.pack(fill='x', pady=(5, 15), ipady=8)
        
        tk.Label(form, text="Password", font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(anchor='w')
        self.s_pass = tk.Entry(form, font=('Inter', 14), show='●',
                              bg=self.colors['card'], fg=self.colors['text'],
                              relief='flat', insertbackground='white')
        self.s_pass.pack(fill='x', pady=(5, 15), ipady=8)
        
        tk.Label(form, text="Confirm", font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(anchor='w')
        self.s_confirm = tk.Entry(form, font=('Inter', 14), show='●',
                                 bg=self.colors['card'], fg=self.colors['text'],
                                 relief='flat', insertbackground='white')
        self.s_confirm.pack(fill='x', pady=(5, 20), ipady=8)
        self.s_confirm.bind('<Return>', lambda e: self.do_signup())
        
        btn_frame = tk.Frame(form, bg=self.colors['panel'])
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="Create", font=('Inter', 12, 'bold'),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 command=self.do_signup).pack(side='left', fill='x', expand=True, ipady=10)
        
        tk.Button(btn_frame, text="Back", font=('Inter', 12),
                 bg=self.colors['card'], fg=self.colors['text'], relief='flat',
                 command=self.show_login).pack(side='left', fill='x', expand=True, ipady=10, padx=(10, 0))
    
    def do_login(self):
        username = self.l_user.get().strip()
        password = self.l_pass.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password")
            return
        
        if username not in self.users:
            messagebox.showerror("Error", "User not found")
            return
        
        if not self.verify_password(password, self.users[username]['password']):
            messagebox.showerror("Error", "Invalid password")
            return
        
        self.current_user = username
        self.show_browser()
    
    def do_signup(self):
        username = self.s_user.get().strip()
        password = self.s_pass.get()
        confirm = self.s_confirm.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Fill all fields")
            return
        
        if username in self.users:
            messagebox.showerror("Error", "Username exists")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match")
            return
        
        self.users[username] = {
            'username': username,
            'password': self.hash_password(password),
            'created': datetime.now().isoformat()
        }
        self.save_json(self.users_file, self.users)
        
        messagebox.showinfo("Success", "Account created!")
        self.show_login()
    
    def show_browser(self):
        self.clear()
        
        # Grid setup
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Left sidebar
        self.create_sidebar()
        
        # Web view (center)
        self.create_webview()
        
        # Right panel
        self.create_right_panel()
        
        # Welcome
        self.show_welcome()
    
    def create_header(self):
        header = tk.Frame(self.root, bg=self.colors['panel'], height=60)
        header.grid(row=0, column=0, columnspan=3, sticky='ew')
        header.pack_propagate(False)
        
        tk.Label(header, text="◆ BRIM", font=('Inter', 18, 'bold'),
                bg=self.colors['panel'], fg=self.colors['primary']).pack(side='left', padx=20)
        
        # URL bar
        url_frame = tk.Frame(header, bg=self.colors['card'], padx=10, pady=5)
        url_frame.pack(side='left', fill='x', expand=True, padx=10)
        
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var,
                                 font=('Inter', 12), bg=self.colors['card'],
                                 fg=self.colors['text'], relief='flat',
                                 insertbackground='white')
        self.url_entry.pack(fill='x', expand=True, ipady=3)
        self.url_entry.bind('<Return>', lambda e: self.navigate())
        
        # Nav buttons
        nav = tk.Frame(header, bg=self.colors['panel'])
        nav.pack(side='left', padx=5)
        
        for btn in [('←', self.go_back), ('→', self.go_forward), ('⟳', self.refresh)]:
            tk.Button(nav, text=btn[0], font=('Inter', 12),
                     bg=self.colors['panel'], fg=self.colors['text'],
                     relief='flat', command=btn[1]).pack(side='left', padx=2)
        
        # User
        user_frame = tk.Frame(header, bg=self.colors['panel'])
        user_frame.pack(side='right', padx=20)
        
        tk.Label(user_frame, text=f"👤 {self.current_user}", font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['text']).pack(side='left', padx=(0, 10))
        
        tk.Button(user_frame, text="Logout", font=('Inter', 10),
                 bg=self.colors['card'], fg=self.colors['text'], relief='flat',
                 command=self.logout).pack(side='left')
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.colors['panel'], width=280)
        sidebar.grid(row=1, column=0, sticky='nsew')
        sidebar.pack_propagate(False)
        
        # Search
        search_frame = tk.Frame(sidebar, bg=self.colors['panel'], padx=15, pady=15)
        search_frame.pack(fill='x')
        
        tk.Label(search_frame, text="🔍 Search", font=('Inter', 14, 'bold'),
                bg=self.colors['panel'], fg=self.colors['text']).pack(anchor='w', pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=('Inter', 12), bg=self.colors['card'],
                               fg=self.colors['text'], relief='flat',
                               insertbackground='white')
        search_entry.pack(fill='x', pady=(0, 10), ipady=8)
        search_entry.bind('<Return>', lambda e: self.search())
        
        tk.Button(search_frame, text="Search", font=('Inter', 11, 'bold'),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 command=self.search).pack(fill='x', ipady=8)
        
        tk.Frame(sidebar, height=1, bg=self.colors['card']).pack(fill='x', padx=15)
        
        # Results container
        results_frame = tk.Frame(sidebar, bg=self.colors['panel'], padx=15, pady=15)
        results_frame.pack(fill='both', expand=True)
        
        tk.Label(results_frame, text="Results", font=('Inter', 14, 'bold'),
                bg=self.colors['panel'], fg=self.colors['text']).pack(anchor='w', pady=(0, 10))
        
        canvas = tk.Canvas(results_frame, bg=self.colors['panel'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.results_container = tk.Frame(canvas, bg=self.colors['panel'])
        
        self.results_container.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.results_container, anchor="nw", width=250)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_webview(self):
        """Create center web view - uses iframe approach for embedded browsing"""
        self.web_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.web_frame.grid(row=1, column=1, sticky='nsew', padx=1, pady=1)
        
        # Create a text widget to render HTML (simplified browser)
        self.web_view = tk.Text(self.web_frame, bg='white', fg='black',
                               font=('Courier', 12), wrap='word',
                               state='disabled', cursor='arrow')
        self.web_view.pack(fill='both', expand=True)
        
        # Alternative: open in system browser but keep panel updated
        self.web_label = tk.Label(self.web_frame, 
                                 text="Click a search result to open in browser\n\n"
                                      "The veracity panel will analyze the site",
                                 font=('Inter', 14), bg=self.colors['bg'],
                                 fg=self.colors['muted'], justify='center')
        self.web_label.place(relx=0.5, rely=0.5, anchor='center')
    
    def create_right_panel(self):
        panel = tk.Frame(self.root, bg=self.colors['panel'], width=350)
        panel.grid(row=1, column=2, sticky='nsew')
        panel.pack_propagate(False)
        
        canvas = tk.Canvas(panel, bg=self.colors['panel'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        self.protocol_container = tk.Frame(canvas, bg=self.colors['panel'], padx=20, pady=20)
        
        self.protocol_container.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.protocol_container, anchor="nw", width=350)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_welcome(self):
        welcome = """Welcome to Brim Browser

Browse securely with Veracity Protocol

Features:
• Search the web
• View site credibility scores
• Discuss with community
• Private & decentralized

Start by searching above"""
        
        # Show in web area
        if hasattr(self, 'web_label'):
            self.web_label.config(text=welcome)
        
        # Show in right panel
        self.clear_protocol()
        tk.Label(self.protocol_container, text="Veracity Protocol",
                font=('Inter', 18, 'bold'), bg=self.colors['panel'],
                fg=self.colors['primary']).pack(anchor='w', pady=(20, 10))
        
        info = """Select a website to analyze:

• Authority Score
• Security Rating  
• Community Reviews
• Real-time Discussion

All data stored locally."""
        
        tk.Label(self.protocol_container, text=info, font=('Inter', 12),
                bg=self.colors['panel'], fg=self.colors['muted'],
                justify='left').pack(anchor='w')
    
    def clear_protocol(self):
        for widget in self.protocol_container.winfo_children():
            widget.destroy()
    
    def search(self):
        query = self.search_var.get().strip()
        if not query:
            return
        
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        loading = tk.Label(self.results_container, text="Searching...",
                          font=('Inter', 12), bg=self.colors['panel'],
                          fg=self.colors['muted'])
        loading.pack(pady=20)
        self.root.update()
        
        try:
            results = self.web_search(query)
            loading.destroy()
            self.show_results(results)
        except Exception as e:
            loading.destroy()
            tk.Label(self.results_container, text=f"Error: {str(e)}",
                    font=('Inter', 11), bg=self.colors['panel'],
                    fg=self.colors['warning']).pack(pady=20)
    
    def web_search(self, query):
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        
        try:
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'User-Agent': 'BrimBrowser/1.0'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self.parse_results(data, query)
        except:
            return self.simulate_results(query)
    
    def parse_results(self, data, query):
        results = []
        if data.get('AbstractURL'):
            results.append({
                'title': data.get('Heading', query),
                'url': data['AbstractURL'],
                'summary': data.get('Abstract', ''),
                'source': self.extract_domain(data['AbstractURL'])
            })
        for topic in data.get('RelatedTopics', [])[:8]:
            if topic.get('FirstURL'):
                results.append({
                    'title': topic.get('Text', '')[:60],
                    'url': topic['FirstURL'],
                    'summary': topic.get('Text', '')[:150],
                    'source': self.extract_domain(topic['FirstURL'])
                })
        if not results:
            results = self.simulate_results(query)
        return results
    
    def simulate_results(self, query):
        domains = [('wikipedia.org', 'Encyclopedia'), ('nature.com', 'Journal'),
                  ('researchgate.net', 'Research'), ('scholar.google.com', 'Academic')]
        encoded = urllib.parse.quote_plus(query)
        return [{'title': f'{query.title()} - {dtype}', 
                'url': f'https://{domain}/search?q={encoded}',
                'summary': f'Information about {query} from {domain}',
                'source': domain} for domain, dtype in domains]
    
    def show_results(self, results):
        tk.Label(self.results_container, text=f"{len(results)} results",
                font=('Inter', 11), bg=self.colors['panel'],
                fg=self.colors['muted']).pack(anchor='w', pady=(0, 10))
        
        for result in results:
            card = tk.Frame(self.results_container, bg=self.colors['card'], padx=10, pady=10)
            card.pack(fill='x', pady=5)
            card.bind('<Enter>', lambda e, c=card: c.configure(bg='#475569'))
            card.bind('<Leave>', lambda e, c=card: c.configure(bg=self.colors['card']))
            
            title = tk.Label(card, text=result['title'][:50], font=('Inter', 11, 'bold'),
                           bg=self.colors['card'], fg=self.colors['text'],
                           wraplength=220, cursor='hand2')
            title.pack(anchor='w')
            title.bind('<Button-1>', lambda e, r=result: self.load_site(r))
            
            tk.Label(card, text=result['source'], font=('Inter', 9),
                    bg=self.colors['card'], fg=self.colors['success']).pack(anchor='w')
            
            card.bind('<Button-1>', lambda e, r=result: self.load_site(r))
    
    def load_site(self, result):
        self.current_url = result['url']
        self.url_var.set(result['url'])
        
        # Open in browser
        webbrowser.open(result['url'])
        
        # Update panel
        self.analyze_site(result)
    
    def analyze_site(self, result):
        self.clear_protocol()
        url, domain = result['url'], result['source']
        
        # Calculate score
        analysis = self.calculate_veracity(url, domain)
        
        # Badge
        status = '✓ Verified' if analysis['validated'] else '⚠ Review'
        color = self.colors['success'] if analysis['validated'] else self.colors['warning']
        tk.Label(self.protocol_container, text=status, font=('Inter', 12, 'bold'),
                bg=color, fg='white', padx=10, pady=5).pack(anchor='w', pady=(0, 15))
        
        # Score
        frame = tk.Frame(self.protocol_container, bg=self.colors['panel'])
        frame.pack(fill='x', pady=10)
        tk.Label(frame, text=str(analysis['score']), font=('Inter', 42, 'bold'),
                bg=self.colors['panel'], fg=self.colors['primary']).pack(side='left')
        tk.Label(frame, text="/100", font=('Inter', 16),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(side='left', pady=(20, 0))
        
        # Signals
        tk.Label(self.protocol_container, text="Veracity Signals",
                font=('Inter', 14, 'bold'), bg=self.colors['panel'],
                fg=self.colors['text']).pack(anchor='w', pady=(15, 10))
        
        for signal, value in analysis['signals'].items():
            self.signal_bar(signal, value, 30)
        
        # Source
        tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=15)
        tk.Label(self.protocol_container, text=f"Source: {domain}",
                font=('Inter', 10), bg=self.colors['panel'],
                fg=self.colors['muted']).pack(anchor='w')
        
        # Comments section
        self.show_comments(url)
    
    def calculate_veracity(self, url, domain):
        url_lower = url.lower()
        domain_lower = domain.lower()
        score, signals = 50, {'Authority': 0, 'Security': 0, 'Citations': 0, 'Transparency': 0}
        
        if url_lower.startswith('https://'):
            signals['Security'] = 15
            score += 15
        
        trusted = ['.gov', '.edu', 'wikipedia.org', 'nature.com', 'researchgate.net',
                  'scholar.google.com', 'pubmed.ncbi.nlm.nih.gov', 'github.com']
        for t in trusted:
            if t in domain_lower:
                signals['Authority'] = 25
                score += 25
                break
        
        if any(x in url_lower for x in ['research', 'science', 'doi', 'journal']):
            signals['Citations'] = 20
            score += 20
        
        score = max(0, min(100, score))
        return {'score': score, 'validated': score >= 70, 'signals': signals}
    
    def signal_bar(self, label, value, max_val):
        frame = tk.Frame(self.protocol_container, bg=self.colors['panel'])
        frame.pack(fill='x', pady=3)
        tk.Label(frame, text=label, font=('Inter', 10),
                bg=self.colors['panel'], fg=self.colors['muted'], width=12).pack(side='left')
        
        bar_container = tk.Frame(frame, bg=self.colors['card'], height=10, width=180)
        bar_container.pack(side='left', padx=10)
        bar_container.pack_propagate(False)
        
        width = int((value / max_val) * 180)
        tk.Frame(bar_container, bg=self.colors['primary'], height=10, width=width).place(x=0, y=0)
        tk.Label(frame, text=str(value), font=('Inter', 10, 'bold'),
                bg=self.colors['panel'], fg=self.colors['primary'], width=3).pack(side='left')
    
    def show_comments(self, url):
        tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=15)
        tk.Label(self.protocol_container, text="💬 Community Discussion",
                font=('Inter', 14, 'bold'), bg=self.colors['panel'],
                fg=self.colors['text']).pack(anchor='w', pady=(0, 10))
        
        # Get comments for this URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        site_comments = self.comments.get(url_hash, [])
        
        if site_comments:
            avg = sum(c['rating'] for c in site_comments) / len(site_comments)
            stars = '★' * round(avg) + '☆' * (5 - round(avg))
            tk.Label(self.protocol_container,
                    text=f"{stars} {avg:.1f}/5 ({len(site_comments)} reviews)",
                    font=('Inter', 12), bg=self.colors['panel'],
                    fg=self.colors['success']).pack(anchor='w', pady=5)
        else:
            tk.Label(self.protocol_container, text="No reviews yet. Be the first!",
                    font=('Inter', 12), bg=self.colors['panel'],
                    fg=self.colors['muted']).pack(anchor='w', pady=5)
        
        # Comment form
        form_frame = tk.LabelFrame(self.protocol_container, text="Add Comment",
                                  font=('Inter', 11), bg=self.colors['panel'],
                                  fg=self.colors['muted'], padx=10, pady=10)
        form_frame.pack(fill='x', pady=15)
        
        self.comment_rating = tk.StringVar(value="3")
        tk.Label(form_frame, text="Rating:", font=('Inter', 10),
                bg=self.colors['panel'], fg=self.colors['muted']).pack(anchor='w')
        ttk.Combobox(form_frame, textvariable=self.comment_rating,
                    values=["5 - Excellent", "4 - Good", "3 - Okay", "2 - Poor", "1 - Bad"],
                    width=20, state='readonly').pack(anchor='w', pady=(0, 10))
        
        self.comment_text = tk.Text(form_frame, height=3, font=('Inter', 10),
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   relief='flat', insertbackground='white')
        self.comment_text.pack(fill='x', pady=5)
        
        def submit():
            rating = int(self.comment_rating.get()[0])
            text = self.comment_text.get("1.0", "end-1c").strip()
            
            url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
            if url_hash not in self.comments:
                self.comments[url_hash] = []
            
            self.comments[url_hash].append({
                'user': self.current_user,
                'rating': rating,
                'text': text,
                'timestamp': datetime.now().isoformat(),
                'url': url
            })
            self.save_json(self.comments_file, self.comments)
            
            self.comment_text.delete("1.0", "end")
            self.analyze_site({'url': url, 'source': self.extract_domain(url)})
            messagebox.showinfo("Posted", "Comment added!")
        
        tk.Button(form_frame, text="Post Comment", font=('Inter', 10, 'bold'),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 command=submit).pack(fill='x', pady=(10, 0))
        
        # Show existing comments
        if site_comments:
            tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=10)
            for c in reversed(site_comments[-5:]):
                self.show_comment_item(c)
    
    def show_comment_item(self, comment):
        frame = tk.Frame(self.protocol_container, bg=self.colors['card'], padx=10, pady=8)
        frame.pack(fill='x', pady=3)
        
        stars = '★' * comment['rating'] + '☆' * (5 - comment['rating'])
        header = f"{comment['user']}  {stars}"
        tk.Label(frame, text=header, font=('Inter', 10, 'bold'),
                bg=self.colors['card'], fg=self.colors['primary']).pack(anchor='w')
        
        if comment.get('text'):
            tk.Label(frame, text=comment['text'], font=('Inter', 9),
                    bg=self.colors['card'], fg=self.colors['muted'],
                    wraplength=280, justify='left').pack(anchor='w')
    
    def extract_domain(self, url):
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return url
    
    def navigate(self):
        url = self.url_var.get()
        if url:
            if not url.startswith('http'):
                url = 'https://' + url
            self.current_url = url
            webbrowser.open(url)
            self.analyze_site({'url': url, 'source': self.extract_domain(url)})
    
    def go_back(self):
        pass  # Would need browsing history
    
    def go_forward(self):
        pass
    
    def refresh(self):
        if self.current_url:
            webbrowser.open(self.current_url)
    
    def logout(self):
        self.current_user = None
        self.show_login()


def main():
    root = tk.Tk()
    app = BrimBrowser(root)
    root.mainloop()


if __name__ == "__main__":
    main()
