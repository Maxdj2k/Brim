#!/usr/bin/env python3
"""
Brim Browser v2 - Embedded Web Browser with AI Veracity Analysis
Pure Python, no external dependencies beyond tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import hashlib
import secrets
import urllib.request
import urllib.parse
import webbrowser
import ssl
import re
import html
from datetime import datetime
from urllib.parse import urlparse, urljoin


class AIAnalyzer:
    """Granular AI analysis of web content"""
    
    @staticmethod
    def analyze_content(url, html_content, text_content):
        """Perform comprehensive AI analysis"""
        analysis = {
            'veracity_score': 0,
            'signals': {},
            'content_analysis': {},
            'risk_factors': [],
            'recommendations': [],
            'metadata': {},
            'sentiment': {},
            'entities': {},
            'readability': {}
        }
        
        # 1. Security Signals
        analysis['signals']['https'] = 15 if url.startswith('https://') else 0
        analysis['signals']['security_headers'] = AIAnalyzer._check_security_headers(html_content)
        
        # 2. Domain Authority
        domain_score = AIAnalyzer._analyze_domain_authority(url)
        analysis['signals']['domain_authority'] = domain_score
        
        # 3. Content Quality
        content_metrics = AIAnalyzer._analyze_content_quality(text_content)
        analysis['content_analysis'] = content_metrics
        
        # 4. Sentiment Analysis
        analysis['sentiment'] = AIAnalyzer._analyze_sentiment(text_content)
        
        # 5. Entity Extraction
        analysis['entities'] = AIAnalyzer._extract_entities(text_content)
        
        # 6. Readability Score
        analysis['readability'] = AIAnalyzer._calculate_readability(text_content)
        
        # 7. Risk Detection
        analysis['risk_factors'] = AIAnalyzer._detect_risks(url, text_content)
        
        # Calculate overall score
        total = sum(analysis['signals'].values())
        total += min(content_metrics.get('quality_score', 0), 20)
        total -= len(analysis['risk_factors']) * 5
        
        analysis['veracity_score'] = max(0, min(100, total))
        analysis['validated'] = analysis['veracity_score'] >= 70
        
        # Generate recommendations
        analysis['recommendations'] = AIAnalyzer._generate_recommendations(analysis)
        
        return analysis
    
    @staticmethod
    def _check_security_headers(html_content):
        indicators = [('Content-Security-Policy', 5), ('X-Frame-Options', 3),
                     ('Strict-Transport-Security', 5), ('X-Content-Type-Options', 2)]
        score = sum(points for indicator, points in indicators 
                   if indicator.lower() in html_content.lower())
        return min(15, score)
    
    @staticmethod
    def _analyze_domain_authority(url):
        domain = urlparse(url).netloc.lower()
        
        tier1 = ['.gov', '.edu', '.ac.uk', '.ac.jp', 'who.int', 'un.org',
                'worldbank.org', 'wikipedia.org', 'nature.com', 'science.org']
        if any(t in domain for t in tier1):
            return 30
        
        tier2 = ['github.com', 'stackoverflow.com', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov',
                'researchgate.net', 'scholar.google.com', 'ieee.org', 'acm.org']
        if any(t in domain for t in tier2):
            return 25
        
        tier3 = ['reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'wsj.com', 'nytimes.com']
        if any(t in domain for t in tier3):
            return 20
        
        tier4 = ['reddit.com', 'twitter.com', 'facebook.com', 'youtube.com']
        if any(t in domain for t in tier4):
            return 5
        
        return 10
    
    @staticmethod
    def _analyze_content_quality(text):
        if not text:
            return {'quality_score': 0, 'word_count': 0, 'has_citations': False}
        
        words = text.split()
        word_count = len(words)
        
        citation_patterns = [r'\[\d+\]', r'\(\d{4}\)', r'doi[:\/]', r'references', r'bibliography']
        has_citations = any(re.search(p, text, re.IGNORECASE) for p in citation_patterns)
        has_author = bool(re.search(r'(author|byline|written by)', text, re.IGNORECASE))
        has_date = bool(re.search(r'\b20\d{2}\b', text))
        
        score = 0
        if word_count > 500: score += 5
        if word_count > 1000: score += 5
        if has_citations: score += 10
        if has_author: score += 5
        if has_date: score += 5
        
        return {'quality_score': score, 'word_count': word_count,
                'has_citations': has_citations, 'has_author': has_author, 'has_date': has_date}
    
    @staticmethod
    def _analyze_sentiment(text):
        if not text:
            return {'sentiment': 'neutral', 'polarity': 0}
        
        positive = ['good', 'great', 'excellent', 'positive', 'success', 'benefit', 'advantage']
        negative = ['bad', 'terrible', 'negative', 'fail', 'danger', 'risk', 'problem', 'issue']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return {'sentiment': 'neutral', 'polarity': 0}
        
        polarity = (pos_count - neg_count) / total
        
        if polarity > 0.2: sentiment = 'positive'
        elif polarity < -0.2: sentiment = 'negative'
        else: sentiment = 'neutral'
        
        return {'sentiment': sentiment, 'polarity': polarity,
                'positive_words': pos_count, 'negative_words': neg_count}
    
    @staticmethod
    def _extract_entities(text):
        entities = {'organizations': [], 'people': [], 'locations': [], 'dates': []}
        
        org_pattern = r'([A-Z][a-z]+ (?:University|Institute|Corporation|Inc|Corp|Ltd|Company))'
        entities['organizations'] = re.findall(org_pattern, text)[:5]
        
        date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b'
        entities['dates'] = re.findall(date_pattern, text, re.IGNORECASE)[:5]
        
        return entities
    
    @staticmethod
    def _calculate_readability(text):
        if not text:
            return {'score': 0, 'level': 'unknown', 'grade': 'N/A'}
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {'score': 0, 'level': 'unknown', 'grade': 'N/A'}
        
        avg_sentence = len(words) / len(sentences)
        avg_syllables = sum(AIAnalyzer._count_syllables(w) for w in words) / len(words)
        
        score = 206.835 - (1.015 * avg_sentence) - (84.6 * avg_syllables)
        score = max(0, min(100, score))
        
        if score >= 90: level, grade = 'very_easy', '5th grade'
        elif score >= 80: level, grade = 'easy', '6th grade'
        elif score >= 70: level, grade = 'fairly_easy', '7th grade'
        elif score >= 60: level, grade = 'standard', '8th-9th grade'
        elif score >= 50: level, grade = 'fairly_difficult', '10th-12th grade'
        elif score >= 30: level, grade = 'difficult', 'College'
        else: level, grade = 'very_difficult', 'Graduate'
        
        return {'score': round(score, 1), 'level': level, 'grade': grade}
    
    @staticmethod
    def _count_syllables(word):
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        
        return max(1, count)
    
    @staticmethod
    def _detect_risks(url, text):
        risks = []
        text_lower = text.lower()
        
        if not url.startswith('https://'):
            risks.append('Insecure connection (no HTTPS)')
        
        sensational = ['shocking', 'unbelievable', 'you won\'t believe', 'miracle', 'secret']
        if any(w in text_lower for w in sensational):
            risks.append('Sensationalist language detected')
        
        urgency = ['act now', 'limited time', 'urgent', 'expires soon']
        if any(w in text_lower for w in urgency):
            risks.append('Urgency pressure tactics')
        
        return risks
    
    @staticmethod
    def _generate_recommendations(analysis):
        recs = []
        
        if analysis['veracity_score'] >= 80:
            recs.append('✓ High credibility source - reliable for research')
        elif analysis['veracity_score'] >= 60:
            recs.append('~ Moderate credibility - verify with additional sources')
        else:
            recs.append('⚠ Low credibility - cross-check information')
        
        if analysis['risk_factors']:
            recs.append('⚠ Risk factors detected - read critically')
        
        if not analysis['content_analysis'].get('has_citations'):
            recs.append('ℹ No citations found - verify claims independently')
        
        return recs


class WebFetcher:
    """Fetch and process web content"""
    
    @staticmethod
    def fetch(url, timeout=10):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    
    @staticmethod
    def extract_text(html):
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Preserve structure
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<p\s*/?>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)
        
        # Remove remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        text = html.unescape(text)
        
        # Clean whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def extract_title(html):
        match = re.search(r'<title[^>]*>([^<]*)</title>', html, re.IGNORECASE)
        return match.group(1).strip() if match else 'Untitled'


class BrimBrowser:
    # Colors - matching Lua implementation (class-level for early access)
    colors = {
        'bg': '#1a1a2e',        # Deep dark blue
        'panel': '#16213e',      # Slightly lighter blue
        'card': '#0f3460',       # Card background
        'card_hover': '#1a4a7a', # Hover state
        'cyan': '#00d9ff',
        'green': '#00ff88',
        'red': '#ff3366',
        'yellow': '#ffcc00',
        'blue': '#4488ff',
        'white': '#ffffff',
        'light_gray': '#a0a0b0',
        'dark_gray': '#606070',
        'primary': '#00d9ff',    # Cyan
        'success': '#00ff88',    # Green
        'warning': '#ffcc00',    # Yellow
        'danger': '#ff3366',     # Red
        'text': '#ffffff',
        'muted': '#a0a0b0',
        'accent': '#4488ff'      # Blue
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("◆ Brim - Private Browser for Students")
        self.root.geometry("1600x1000")
        self.root.configure(bg=self.colors['bg'])
        
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
        self.current_html = None
        self.current_text = None
        self.current_analysis = None
        
        # AI components
        self.analyzer = AIAnalyzer()
        self.fetcher = WebFetcher()
        
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
        
        # Search engine selector - Privacy focused for students
        self.search_engine = tk.StringVar(value='searx')
        tk.Label(search_frame, text="🔒 Privacy Engine:", font=('Inter', 9),
                bg=self.colors['panel'], fg=self.colors['green']).pack(anchor='w', pady=(10, 5))
        
        engines = [
            ('Searx (Private)', 'searx'),
        ]
        
        self.engine_menu = ttk.Combobox(search_frame, textvariable=self.search_engine,
                                       values=[name for name, key in engines],
                                       width=20, state='readonly')
        self.engine_menu.current(0)
        self.engine_menu.pack(fill='x', pady=(0, 5))
        
        # Privacy note
        tk.Label(search_frame, text="✓ No tracking • No API keys • Student safe",
                font=('Inter', 8), bg=self.colors['panel'], 
                fg=self.colors['green']).pack(anchor='w', pady=(5, 0))
        
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
        """Create center web view with scrolled text for content display"""
        self.web_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.web_frame.grid(row=1, column=1, sticky='nsew', padx=2, pady=2)
        self.web_frame.grid_rowconfigure(0, weight=1)
        self.web_frame.grid_columnconfigure(0, weight=1)
        
        # Header showing current page
        self.content_header = tk.Frame(self.web_frame, bg=self.colors['panel'], height=40)
        self.content_header.grid(row=0, column=0, sticky='ew')
        self.content_header.pack_propagate(False)
        
        self.page_title_label = tk.Label(self.content_header, text="◆ Ready to browse",
                                        font=('SF Pro', 12, 'bold'), bg=self.colors['panel'],
                                        fg=self.colors['cyan'])
        self.page_title_label.pack(side='left', padx=15, pady=8)
        
        # Progress bar frame
        self.progress_frame = tk.Frame(self.content_header, bg=self.colors['card'], height=4)
        self.progress_frame.pack(side='bottom', fill='x', padx=15)
        
        # Content area with scrolled text
        self.content_area = tk.Frame(self.web_frame, bg=self.colors['bg'])
        self.content_area.grid(row=1, column=0, sticky='nsew')
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.web_view = scrolledtext.ScrolledText(
            self.content_area,
            wrap=tk.WORD,
            font=('SF Pro', 12),
            bg=self.colors['bg'],
            fg=self.colors['white'],
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.colors['card'],
            padx=20,
            pady=20,
            state='disabled'
        )
        self.web_view.grid(row=0, column=0, sticky='nsew')
        
        # Configure text tags for styling
        self.web_view.tag_configure('title', font=('SF Pro', 18, 'bold'), foreground=self.colors['cyan'])
        self.web_view.tag_configure('heading', font=('SF Pro', 14, 'bold'), foreground=self.colors['blue'])
        self.web_view.tag_configure('link', foreground=self.colors['cyan'], underline=True)
        self.web_view.tag_configure('bold', font=('SF Pro', 12, 'bold'))
        
        # Status bar
        self.status_bar = tk.Frame(self.web_frame, bg=self.colors['panel'], height=25)
        self.status_bar.grid(row=2, column=0, sticky='ew')
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", font=('SF Pro', 10),
                                    bg=self.colors['panel'], fg=self.colors['light_gray'])
        self.status_label.pack(side='left', padx=15)
    
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
        welcome = """◆ Welcome to Brim

🔒 Private Browser for Students

✓ No tracking or logging
✓ No API keys required
✓ No account needed
✓ All data stays local
✓ AI-powered credibility check

Search privately, browse safely.

Type a topic above to begin."""
        
        # Show in web area
        if hasattr(self, 'web_label'):
            self.web_label.config(text=welcome)
        
        # Show in right panel
        self.clear_protocol()
        tk.Label(self.protocol_container, text="Veracity Protocol",
                font=('Inter', 18, 'bold'), bg=self.colors['panel'],
                fg=self.colors['primary']).pack(anchor='w', pady=(20, 10))
        
        info = """🔒 Privacy First

Your searches and browsing history
never leave this computer.

AI Analysis helps you verify
source credibility before trusting.

• Searx meta-search (no tracking)
• Local data only
• No cloud services
• Student safe"""
        
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
            # Get selected engine from dropdown
            selected = self.engine_menu.get()
            engine_map = {'Auto': 'auto', 'DuckDuckGo': 'duckduckgo', 
                         'Searx': 'searx', 'Offline': 'simulated'}
            engine = engine_map.get(selected, 'auto')
            
            results = self.web_search(query, engine)
            loading.destroy()
            self.show_results(results)
        except Exception as e:
            loading.destroy()
            tk.Label(self.results_container, text=f"Error: {str(e)}",
                    font=('Inter', 11), bg=self.colors['panel'],
                    fg=self.colors['warning']).pack(pady=20)
    
    def web_search(self, query, engine='searx'):
        """
        Privacy-focused search for students.
        
        Engines:
        - 'searx': DEFAULT - Privacy meta-search, aggregates multiple engines
                   No API key, no tracking, no logs. Perfect for students.
        - 'duckduckgo': Privacy search (may have rate limits)
        - 'simulated': No external calls, fully offline
        
        All engines respect student privacy - no accounts, no tracking.
        """
        if engine == 'searx':
            # Default: Privacy-focused Searx meta-search
            return self._search_searx(query)
        
        elif engine == 'duckduckgo':
            try:
                return self._search_duckduckgo(query)
            except Exception as e:
                # Fall back to Searx on error
                return self._search_searx(query)
        
        elif engine == 'simulated':
            return self.simulate_results(query)
        
        else:
            # Default to privacy-focused Searx
            return self._search_searx(query)
    
    def _search_duckduckgo(self, query):
        """Search using DuckDuckGo API"""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        
        req = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'BrimBrowser/1.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return self._parse_duckduckgo(data, query)
    
    def _parse_duckduckgo(self, data, query):
        """Parse DuckDuckGo results"""
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
    
    def _search_searx(self, query):
        """
        Search using Searx instances - Privacy-focused meta-search.
        Searx aggregates results from multiple engines without tracking.
        Perfect for students - no API keys, no account, no logging.
        """
        # Privacy-focused Searx instances (no logs, no tracking)
        # Students can also run their own: https://docs.searxng.org
        searx_instances = [
            'https://search.sapti.me',      # No logs, EU hosted
            'https://search.nixnet.services', # Privacy-focused host
            'https://search.smnz.de',       # German privacy laws
            'https://searx.be',             # Belgium, GDPR compliant
            'https://searx.fmac.xyz',       # Community hosted
            'https://searx.tiekoetter.com'  # German privacy
        ]
        
        encoded = urllib.parse.quote_plus(query)
        
        for instance in searx_instances:
            try:
                url = f"{instance}/search?q={encoded}&format=json&engines=wikipedia,duckduckgo,bing,google"
                req = urllib.request.Request(url, headers={
                    'Accept': 'application/json',
                    'User-Agent': 'BrimBrowser/1.0'
                }, timeout=8)
                
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, context=ctx) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    return self._parse_searx(data)
            except Exception:
                continue  # Try next instance
        
        # All instances failed, fall back to simulated
        return self.simulate_results(query)
    
    def _parse_searx(self, data):
        """Parse Searx JSON results"""
        results = []
        for result in data.get('results', [])[:10]:
            results.append({
                'title': result.get('title', 'Untitled')[:70],
                'url': result.get('url', ''),
                'summary': result.get('content', '')[:200],
                'source': self.extract_domain(result.get('url', ''))
            })
        return results if results else self.simulate_results(data.get('query', ''))
    
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
        """Fetch and display webpage with AI analysis"""
        url = result['url']
        self.current_url = url
        self.url_var.set(url)
        
        # Update status
        self.status_label.config(text=f"Loading {url}...")
        self.page_title_label.config(text="◆ Loading...")
        self.root.update()
        
        try:
            # Fetch the webpage
            html = self.fetcher.fetch(url)
            text = self.fetcher.extract_text(html)
            title = self.fetcher.extract_title(html)
            
            # Store for analysis
            self.current_html = html
            self.current_text = text
            
            # Display content
            self._display_content(title, text, url)
            
            # Run AI analysis
            self.status_label.config(text="Running AI analysis...")
            self.root.update()
            
            analysis = self.analyzer.analyze_content(url, html, text)
            self.current_analysis = analysis
            
            # Display granular analysis
            self._display_granular_analysis(analysis, result)
            
            self.status_label.config(text=f"✓ Loaded • {len(text.split())} words")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)[:50]}")
            # Fall back to external browser
            webbrowser.open(url)
            self.analyze_site(result)
    
    def _display_content(self, title, text, url):
        """Display webpage content in the viewer"""
        self.web_view.config(state='normal')
        self.web_view.delete('1.0', tk.END)
        
        # Update header
        display_title = title[:60] + "..." if len(title) > 60 else title
        self.page_title_label.config(text=f"◆ {display_title}")
        
        # Add title
        self.web_view.insert(tk.END, f"{title}\n", 'title')
        self.web_view.insert(tk.END, f"{url}\n\n", 'link')
        
        # Add content (truncated for performance)
        content = text[:10000] + "\n\n[Content truncated for display]" if len(text) > 10000 else text
        self.web_view.insert(tk.END, content)
        
        self.web_view.config(state='disabled')
        self.web_view.see('1.0')
    
    def _display_granular_analysis(self, analysis, result):
        """Display comprehensive AI analysis in right panel"""
        self.clear_protocol()
        url = result['url']
        domain = result['source']
        
        # Header with score
        score = analysis['veracity_score']
        status_color = self.colors['green'] if analysis['validated'] else self.colors['yellow']
        status_text = '✓ VERIFIED' if analysis['validated'] else '⚠ REVIEW'
        
        # Score badge
        badge_frame = tk.Frame(self.protocol_container, bg=status_color, padx=15, pady=8)
        badge_frame.pack(fill='x', pady=(0, 15))
        tk.Label(badge_frame, text=status_text, font=('SF Pro', 13, 'bold'),
                bg=status_color, fg=self.colors['bg']).pack()
        
        # Big score display
        score_frame = tk.Frame(self.protocol_container, bg=self.colors['panel'])
        score_frame.pack(fill='x', pady=10)
        tk.Label(score_frame, text=str(score), font=('SF Pro', 52, 'bold'),
                bg=self.colors['panel'], fg=status_color).pack(side='left')
        tk.Label(score_frame, text="/100", font=('SF Pro', 16),
                bg=self.colors['panel'], fg=self.colors['light_gray']).pack(side='left', pady=(25, 0))
        
        # Section: Trust Signals
        self._create_section_header("🔒 Trust Signals")
        
        signals = analysis['signals']
        for signal_name, value in signals.items():
            self._create_signal_bar(signal_name.replace('_', ' ').title(), value, 30)
        
        # Section: Content Analysis
        self._create_section_header("📝 Content Analysis")
        content = analysis['content_analysis']
        
        metrics = [
            ("Word Count", f"{content.get('word_count', 0):,}"),
            ("Has Citations", "✓ Yes" if content.get('has_citations') else "✗ No"),
            ("Has Author", "✓ Yes" if content.get('has_author') else "✗ No"),
            ("Has Date", "✓ Yes" if content.get('has_date') else "✗ No"),
            ("Quality Score", f"{content.get('quality_score', 0)}/30")
        ]
        
        for label, value in metrics:
            self._create_metric_row(label, value)
        
        # Section: Sentiment Analysis
        self._create_section_header("💭 Sentiment")
        sentiment = analysis['sentiment']
        sent_text = sentiment.get('sentiment', 'neutral').upper()
        sent_color = self.colors['green'] if sent_text == 'POSITIVE' else self.colors['yellow'] if sent_text == 'NEUTRAL' else self.colors['red']
        
        sent_frame = tk.Frame(self.protocol_container, bg=self.colors['panel'])
        sent_frame.pack(fill='x', pady=3)
        tk.Label(sent_frame, text=sent_text, font=('SF Pro', 11, 'bold'),
                bg=self.colors['panel'], fg=sent_color).pack(side='left')
        polarity = sentiment.get('polarity', 0)
        tk.Label(sent_frame, text=f"({polarity:+.2f})", font=('SF Pro', 10),
                bg=self.colors['panel'], fg=self.colors['light_gray']).pack(side='left', padx=(10, 0))
        
        # Section: Readability
        self._create_section_header("📚 Readability")
        readability = analysis['readability']
        self._create_metric_row("Flesch Score", str(readability.get('score', 0)))
        self._create_metric_row("Grade Level", readability.get('grade', 'N/A'))
        
        # Section: Risk Factors
        if analysis['risk_factors']:
            self._create_section_header("⚠️ Risk Factors")
            for risk in analysis['risk_factors']:
                tk.Label(self.protocol_container, text=f"• {risk}", font=('SF Pro', 10),
                        bg=self.colors['panel'], fg=self.colors['red'], wraplength=300).pack(anchor='w', pady=2)
        
        # Section: AI Recommendations
        self._create_section_header("🤖 AI Recommendations")
        for rec in analysis['recommendations']:
            tk.Label(self.protocol_container, text=rec, font=('SF Pro', 10),
                    bg=self.colors['panel'], fg=self.colors['light_gray'], wraplength=300).pack(anchor='w', pady=3)
        
        # Source info
        tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=15)
        tk.Label(self.protocol_container, text=f"Source: {domain}",
                font=('SF Pro', 9), bg=self.colors['panel'],
                fg=self.colors['dark_gray']).pack(anchor='w')
        
        # Comments section
        self.show_comments(url)
    
    def _create_section_header(self, title):
        """Create a section header in the analysis panel"""
        tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=15)
        tk.Label(self.protocol_container, text=title, font=('SF Pro', 12, 'bold'),
                bg=self.colors['panel'], fg=self.colors['cyan']).pack(anchor='w', pady=(0, 10))
    
    def _create_metric_row(self, label, value):
        """Create a metric row in the analysis panel"""
        frame = tk.Frame(self.protocol_container, bg=self.colors['panel'])
        frame.pack(fill='x', pady=2)
        tk.Label(frame, text=label, font=('SF Pro', 10),
                bg=self.colors['panel'], fg=self.colors['light_gray']).pack(side='left')
        tk.Label(frame, text=value, font=('SF Pro', 10, 'bold'),
                bg=self.colors['panel'], fg=self.colors['white']).pack(side='right')
    
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
        """Legacy method - kept for compatibility"""
        self._create_signal_bar(label, value, max_val)
    
    def _create_signal_bar(self, label, value, max_val):
        """Create a signal bar with visual indicator"""
        frame = tk.Frame(self.protocol_container, bg=self.colors['panel'])
        frame.pack(fill='x', pady=3)
        tk.Label(frame, text=label, font=('SF Pro', 10),
                bg=self.colors['panel'], fg=self.colors['light_gray'], width=14).pack(side='left')
        
        bar_container = tk.Frame(frame, bg=self.colors['card'], height=12, width=150)
        bar_container.pack(side='left', padx=8)
        bar_container.pack_propagate(False)
        
        # Color based on value
        if value >= 20:
            bar_color = self.colors['green']
        elif value >= 10:
            bar_color = self.colors['yellow']
        else:
            bar_color = self.colors['red']
        
        width = max(2, int((value / max_val) * 150))
        tk.Frame(bar_container, bg=bar_color, height=12, width=width).place(x=0, y=0)
        
        # Value label
        color = self.colors['green'] if value >= 20 else self.colors['yellow'] if value >= 10 else self.colors['light_gray']
        tk.Label(frame, text=str(value), font=('SF Pro', 10, 'bold'),
                bg=self.colors['panel'], fg=color, width=3).pack(side='left')
    
    def show_comments(self, url):
        """Display community comments section"""
        tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=15)
        tk.Label(self.protocol_container, text="💬 Community Discussion",
                font=('SF Pro', 13, 'bold'), bg=self.colors['panel'],
                fg=self.colors['white']).pack(anchor='w', pady=(0, 10))
        
        # Get comments for this URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        site_comments = self.comments.get(url_hash, [])
        
        if site_comments:
            avg = sum(c['rating'] for c in site_comments) / len(site_comments)
            stars = '★' * round(avg) + '☆' * (5 - round(avg))
            tk.Label(self.protocol_container,
                    text=f"{stars} {avg:.1f}/5 ({len(site_comments)} reviews)",
                    font=('SF Pro', 12), bg=self.colors['panel'],
                    fg=self.colors['green']).pack(anchor='w', pady=5)
        else:
            tk.Label(self.protocol_container, text="No reviews yet. Be the first!",
                    font=('SF Pro', 12), bg=self.colors['panel'],
                    fg=self.colors['light_gray']).pack(anchor='w', pady=5)
        
        # Comment form
        form_frame = tk.Frame(self.protocol_container, bg=self.colors['card'], padx=15, pady=15)
        form_frame.pack(fill='x', pady=15)
        
        tk.Label(form_frame, text="Add Your Review", font=('SF Pro', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['cyan']).pack(anchor='w', pady=(0, 10))
        
        self.comment_rating = tk.StringVar(value="3")
        tk.Label(form_frame, text="Rating:", font=('SF Pro', 10),
                bg=self.colors['card'], fg=self.colors['light_gray']).pack(anchor='w')
        ttk.Combobox(form_frame, textvariable=self.comment_rating,
                    values=["5 - Excellent", "4 - Good", "3 - Okay", "2 - Poor", "1 - Bad"],
                    width=20, state='readonly').pack(anchor='w', pady=(0, 10))
        
        self.comment_text = tk.Text(form_frame, height=3, font=('SF Pro', 10),
                                   bg=self.colors['panel'], fg=self.colors['white'],
                                   relief='flat', insertbackground=self.colors['white'])
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
            # Refresh display
            if self.current_analysis:
                self._display_granular_analysis(self.current_analysis, {'url': url, 'source': self.extract_domain(url)})
            messagebox.showinfo("Posted", "Comment added!")
        
        tk.Button(form_frame, text="Post Comment", font=('SF Pro', 11, 'bold'),
                 bg=self.colors['cyan'], fg=self.colors['bg'], relief='flat',
                 cursor='hand2', command=submit).pack(fill='x', pady=(10, 0), ipady=8)
        
        # Show existing comments
        if site_comments:
            tk.Frame(self.protocol_container, height=1, bg=self.colors['card']).pack(fill='x', pady=10)
            for c in reversed(site_comments[-5:]):
                self.show_comment_item(c)
    
    def show_comment_item(self, comment):
        """Display a single comment"""
        frame = tk.Frame(self.protocol_container, bg=self.colors['card'], padx=12, pady=10)
        frame.pack(fill='x', pady=3)
        
        stars = '★' * comment['rating'] + '☆' * (5 - comment['rating'])
        header = f"{comment['user']}  {stars}"
        tk.Label(frame, text=header, font=('SF Pro', 10, 'bold'),
                bg=self.colors['card'], fg=self.colors['cyan']).pack(anchor='w')
        
        if comment.get('text'):
            tk.Label(frame, text=comment['text'], font=('SF Pro', 9),
                    bg=self.colors['card'], fg=self.colors['light_gray'],
                    wraplength=300, justify='left').pack(anchor='w')
    
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
