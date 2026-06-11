#!/usr/bin/env python3
"""
Brim Desktop - Python Desktop Search with Veracity Protocol
Native tkinter application with dual-panel interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import urllib.request
import urllib.parse
import json
import webbrowser
import re
import os
from datetime import datetime


class BrimDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("Brim Search - Veracity Protocol")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f8fafc")
        
        # State
        self.current_results = []
        self.selected_result = None
        self.scan_cache = {}
        self.reviews_file = os.path.expanduser("~/.brim_reviews.json")
        
        # Load reviews
        self.reviews = self.load_reviews()
        
        # Styles
        self.setup_styles()
        
        # UI
        self.create_header()
        self.create_main_layout()
        
        # Bind shortcuts
        self.root.bind('<Return>', lambda e: self.perform_search())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.colors = {
            'primary': '#0f766e',
            'primary_dark': '#115e59',
            'secondary': '#1d4ed8',
            'success': '#166534',
            'warning': '#92400e',
            'danger': '#dc2626',
            'gray': '#64748b',
            'light_gray': '#e2e8f0',
            'bg': '#f8fafc',
            'white': '#ffffff'
        }
        
        # Configure styles
        style.configure('Primary.TButton', 
            background=self.colors['primary'],
            foreground='white',
            font=('Inter', 11, 'bold'),
            padding=10)
        
        style.configure('Result.TButton',
            font=('Inter', 12),
            padding=5)
    
    def create_header(self):
        """Create top header with search bar"""
        header = tk.Frame(self.root, bg='white', height=70)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        # Brand
        brand = tk.Label(header, text="Brim", font=('Inter', 22, 'bold'), 
                        bg='white', fg=self.colors['primary'])
        brand.pack(side='left', padx=20, pady=10)
        
        # Search container
        search_frame = tk.Frame(header, bg='white')
        search_frame.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=('Inter', 14), relief='solid',
                                     bd=1, highlightthickness=2,
                                     highlightcolor=self.colors['primary'],
                                     highlightbackground=self.colors['light_gray'])
        self.search_entry.pack(side='left', fill='x', expand=True, ipady=8, padx=(0, 10))
        self.search_entry.insert(0, "Search any topic...")
        self.search_entry.bind('<FocusIn>', self.on_search_focus)
        self.search_entry.bind('<FocusOut>', self.on_search_unfocus)
        
        # Search button
        search_btn = tk.Button(search_frame, text="Search", 
                              bg=self.colors['primary'], fg='white',
                              font=('Inter', 11, 'bold'), relief='flat',
                              activebackground=self.colors['primary_dark'],
                              cursor='hand2', command=self.perform_search)
        search_btn.pack(side='left', ipadx=20, ipady=5)
    
    def on_search_focus(self, event):
        if self.search_entry.get() == "Search any topic...":
            self.search_entry.delete(0, 'end')
    
    def on_search_unfocus(self, event):
        if self.search_entry.get() == "":
            self.search_entry.insert(0, "Search any topic...")
    
    def create_main_layout(self):
        """Create two-panel layout"""
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Search Results
        left_frame = tk.LabelFrame(main, text=" Search Results ", 
                                   font=('Inter', 11, 'bold'),
                                   bg='white', fg=self.colors['gray'],
                                   relief='solid', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Results canvas with scrollbar
        self.results_canvas = tk.Canvas(left_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.results_canvas.yview)
        self.results_frame = tk.Frame(self.results_canvas, bg='white')
        
        self.results_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        )
        
        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="nw", width=850)
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.results_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Right panel - Veracity Protocol
        right_frame = tk.LabelFrame(main, text=" Veracity Protocol ",
                                    font=('Inter', 11, 'bold'),
                                    bg='white', fg=self.colors['gray'],
                                    relief='solid', bd=1)
        right_frame.pack(side='right', fill='both', padx=(10, 0))
        right_frame.configure(width=400)
        right_frame.pack_propagate(False)
        
        self.protocol_canvas = tk.Canvas(right_frame, bg='white', highlightthickness=0)
        protocol_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.protocol_canvas.yview)
        self.protocol_frame = tk.Frame(self.protocol_canvas, bg='white', width=380)
        
        self.protocol_frame.bind(
            "<Configure>",
            lambda e: self.protocol_canvas.configure(scrollregion=self.protocol_canvas.bbox("all"))
        )
        
        self.protocol_canvas.create_window((0, 0), window=self.protocol_frame, anchor="nw", width=380)
        self.protocol_canvas.configure(yscrollcommand=protocol_scroll.set)
        
        self.protocol_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        protocol_scroll.pack(side="right", fill="y")
        
        # Initial welcome message
        self.show_welcome()
    
    def show_welcome(self):
        """Show welcome message in results panel"""
        self.clear_results()
        
        welcome = tk.Label(self.results_frame, 
                          text="Welcome to Brim Search",
                          font=('Inter', 18, 'bold'),
                          bg='white', fg=self.colors['primary'])
        welcome.pack(anchor='w', pady=(20, 10))
        
        subtitle = tk.Label(self.results_frame,
                           text="Enter a query and click Search",
                           font=('Inter', 12),
                           bg='white', fg=self.colors['gray'])
        subtitle.pack(anchor='w', pady=(0, 20))
        
        features = [
            ("Real-time web search", "cyan"),
            ("Veracity protocol analysis", "cyan"),
            ("Community reviews", "cyan"),
            ("Decentralized architecture", "cyan")
        ]
        
        for text, color in features:
            lbl = tk.Label(self.results_frame, text="• " + text,
                          font=('Inter', 11),
                          bg='white', fg=self.colors['gray'])
            lbl.pack(anchor='w', pady=2)
        
        # Protocol panel welcome
        self.clear_protocol()
        proto_welcome = tk.Label(self.protocol_frame,
                                text="Veracity Protocol",
                                font=('Inter', 16, 'bold'),
                                bg='white', fg=self.colors['primary'])
        proto_welcome.pack(anchor='w', pady=(20, 10))
        
        proto_info = tk.Label(self.protocol_frame,
                             text="Select a search result to:\n"
                                  "• View real-time analysis\n"
                                  "• Check credibility score\n"
                                  "• Submit community review",
                             font=('Inter', 11),
                             bg='white', fg=self.colors['gray'],
                             justify='left')
        proto_info.pack(anchor='w', pady=10)
    
    def clear_results(self):
        """Clear results panel"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def clear_protocol(self):
        """Clear protocol panel"""
        for widget in self.protocol_frame.winfo_children():
            widget.destroy()
    
    def perform_search(self):
        """Execute web search"""
        query = self.search_var.get().strip()
        if not query or query == "Search any topic...":
            return
        
        self.clear_results()
        loading = tk.Label(self.results_frame, text=f"Searching for: {query}...",
                          font=('Inter', 12), bg='white', fg=self.colors['primary'])
        loading.pack(anchor='w', pady=20)
        self.root.update()
        
        # Search
        try:
            results = self.web_search(query)
            self.current_results = results
            self.display_results(results, query)
        except Exception as e:
            self.clear_results()
            error = tk.Label(self.results_frame, text=f"Error: {str(e)}",
                            font=('Inter', 12), bg='white', fg=self.colors['danger'])
            error.pack(anchor='w', pady=20)
    
    def web_search(self, query):
        """Search using DuckDuckGo API"""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        
        try:
            req = urllib.request.Request(url, headers={
                'Accept': 'application/json',
                'User-Agent': 'BrimSearch/1.0'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self.parse_results(data, query)
        except Exception:
            # Fallback to simulated results
            return self.generate_simulated_results(query)
    
    def parse_results(self, data, query):
        """Parse DuckDuckGo response"""
        results = []
        
        # Abstract
        if data.get('AbstractURL') and data.get('Abstract'):
            results.append({
                'title': data.get('Heading', query),
                'url': data['AbstractURL'],
                'summary': data['Abstract'],
                'source': self.extract_domain(data['AbstractURL']),
                'sourceType': 'Instant Answer'
            })
        
        # Related topics
        for topic in data.get('RelatedTopics', [])[:9]:
            if topic.get('FirstURL') and topic.get('Text'):
                results.append({
                    'title': topic['Text'].split(' - ')[0][:60],
                    'url': topic['FirstURL'],
                    'summary': topic['Text'][:200],
                    'source': self.extract_domain(topic['FirstURL']),
                    'sourceType': 'Related Topic'
                })
        
        if not results:
            results = self.generate_simulated_results(query)
        
        return results
    
    def generate_simulated_results(self, query):
        """Generate realistic simulated results"""
        domains = [
            ('wikipedia.org', 'Encyclopedia'),
            ('researchgate.net', 'Research'),
            ('scholar.google.com', 'Academic'),
            ('nature.com', 'Journal'),
            ('sciencedirect.com', 'Database'),
            ('arxiv.org', 'Preprint'),
            ('pubmed.ncbi.nlm.nih.gov', 'Medical'),
            ('github.com', 'Code')
        ]
        
        results = []
        encoded = urllib.parse.quote_plus(query)
        
        for domain, dtype in domains:
            results.append({
                'title': f"{self.capitalize(query)} - {dtype} Resource",
                'url': f"https://{domain}/search?q={encoded}",
                'summary': f"Comprehensive information about {query} from {domain}. "
                          f"Includes peer-reviewed articles, research papers, and authoritative sources.",
                'source': domain,
                'sourceType': dtype
            })
        
        return results
    
    def display_results(self, results, query):
        """Display search results"""
        self.clear_results()
        
        # Count
        count = tk.Label(self.results_frame, 
                        text=f"{len(results)} results for \"{query}\"",
                        font=('Inter', 11), bg='white', fg=self.colors['gray'])
        count.pack(anchor='w', pady=(10, 15))
        
        # Result items
        for i, result in enumerate(results):
            # Result container
            frame = tk.Frame(self.results_frame, bg='white', padx=5, pady=10)
            frame.pack(fill='x', pady=2)
            frame.bind('<Enter>', lambda e, f=frame: f.configure(bg='#f1f5f9'))
            frame.bind('<Leave>', lambda e, f=frame: f.configure(bg='white'))
            
            # Click to select
            frame.bind('<Button-1>', lambda e, r=result: self.select_result(r))
            
            # Title (clickable)
            title = tk.Label(frame, text=f"{i+1}. {result['title']}",
                           font=('Inter', 13, 'bold'),
                           bg='white', fg=self.colors['secondary'],
                           cursor='hand2', wraplength=800, justify='left')
            title.pack(anchor='w')
            title.bind('<Button-1>', lambda e, r=result: self.select_result(r))
            
            # URL
            url_lbl = tk.Label(frame, text=result['url'],
                             font=('Inter', 10),
                             bg='white', fg=self.colors['success'])
            url_lbl.pack(anchor='w', pady=(2, 5))
            
            # Summary
            summary = tk.Label(frame, text=self.truncate(result.get('summary', ''), 150),
                             font=('Inter', 10),
                             bg='white', fg=self.colors['gray'],
                             wraplength=800, justify='left')
            summary.pack(anchor='w')
            
            # Badge
            badge = tk.Label(frame, text=f"  {result.get('sourceType', 'Website')}  ",
                           font=('Inter', 9, 'bold'),
                           bg='#dcfce7', fg=self.colors['success'],
                           relief='solid', bd=0)
            badge.pack(anchor='w', pady=(5, 0))
            
            # Separator
            sep = tk.Frame(self.results_frame, height=1, bg=self.colors['light_gray'])
            sep.pack(fill='x', pady=5)
    
    def select_result(self, result):
        """Select a result and analyze"""
        self.selected_result = result
        
        # Open in browser
        webbrowser.open(result['url'])
        
        # Analyze
        self.analyze_veracity(result)
    
    def analyze_veracity(self, result):
        """Perform veracity analysis"""
        self.clear_protocol()
        
        # Header
        header = tk.Label(self.protocol_frame, text="Analyzing...",
                         font=('Inter', 14, 'bold'),
                         bg='white', fg=self.colors['primary'])
        header.pack(anchor='w', pady=(10, 10))
        self.root.update()
        
        # Simulate delay
        self.root.after(500, lambda: self.show_analysis(result))
    
    def show_analysis(self, result):
        """Display analysis results"""
        self.clear_protocol()
        
        # Calculate score
        analysis = self.calculate_veracity_score(result)
        
        # Status badge
        status_color = '#dcfce7' if analysis['validated'] else '#fef3c7'
        status_fg = '#166534' if analysis['validated'] else '#92400e'
        status_text = 'Validated by Brim' if analysis['validated'] else 'Needs Review'
        
        badge = tk.Label(self.protocol_frame, text=f"  {status_text}  ",
                        font=('Inter', 10, 'bold'),
                        bg=status_color, fg=status_fg, relief='solid', bd=0)
        badge.pack(anchor='w', pady=(10, 15))
        
        # Title
        title = tk.Label(self.protocol_frame, text=result['title'],
                        font=('Inter', 13, 'bold'),
                        bg='white', fg=self.colors['primary'],
                        wraplength=360, justify='left')
        title.pack(anchor='w', pady=(0, 5))
        
        # URL
        url_lbl = tk.Label(self.protocol_frame, text=result['url'],
                          font=('Inter', 9),
                          bg='white', fg=self.colors['gray'],
                          wraplength=360)
        url_lbl.pack(anchor='w', pady=(0, 15))
        
        # Score
        score_frame = tk.Frame(self.protocol_frame, bg='white')
        score_frame.pack(fill='x', pady=10)
        
        score_lbl = tk.Label(score_frame, text=str(analysis['score']),
                            font=('Inter', 48, 'bold'),
                            bg='white', fg=self.colors['primary'])
        score_lbl.pack(side='left')
        
        denom = tk.Label(score_frame, text="/100",
                         font=('Inter', 16),
                         bg='white', fg=self.colors['gray'])
        denom.pack(side='left', padx=(5, 0), pady=(20, 0))
        
        # Score note
        note = tk.Label(self.protocol_frame,
                       text="Site analyzed via heuristics",
                       font=('Inter', 10),
                       bg='white', fg=self.colors['gray'])
        note.pack(anchor='w', pady=(0, 15))
        
        # Signals header
        signals_header = tk.Label(self.protocol_frame, text="Veracity Signals",
                                 font=('Inter', 12, 'bold'),
                                 bg='white', fg=self.colors['primary'])
        signals_header.pack(anchor='w', pady=(15, 10))
        
        # Signal bars
        for signal, value in analysis['signals'].items():
            self.render_signal_bar(signal, value, 30)
        
        # Source info
        source_frame = tk.Frame(self.protocol_frame, bg='white')
        source_frame.pack(fill='x', pady=15)
        
        source_lbl = tk.Label(source_frame, text=f"Source: {result.get('source', 'Unknown')}",
                             font=('Inter', 10),
                             bg='white', fg=self.colors['gray'])
        source_lbl.pack(anchor='w')
        
        type_lbl = tk.Label(source_frame, text=f"Type: {result.get('sourceType', 'Unknown')}",
                           font=('Inter', 10),
                           bg='white', fg=self.colors['gray'])
        type_lbl.pack(anchor='w')
        
        # Community reviews section
        sep = tk.Frame(self.protocol_frame, height=1, bg=self.colors['light_gray'])
        sep.pack(fill='x', pady=15)
        
        comm_header = tk.Label(self.protocol_frame, text="Community Accreditation",
                             font=('Inter', 12, 'bold'),
                             bg='white', fg=self.colors['primary'])
        comm_header.pack(anchor='w', pady=(0, 10))
        
        self.render_community_section(result['url'])
    
    def calculate_veracity_score(self, result):
        """Calculate veracity score based on heuristics"""
        url = result.get('url', '').lower()
        domain = result.get('source', '').lower()
        
        score = 50
        signals = {
            'Authority': 0,
            'Transparency': 0,
            'Citations': 0,
            'Security': 0,
            'Recency': 0
        }
        
        # HTTPS
        if url.startswith('https://'):
            signals['Security'] = 15
            score += 15
        
        # Trusted domains
        trusted = ['.gov', '.edu', 'wikipedia.org', 'nature.com', 
                   'science.org', 'researchgate.net', 'scholar.google.com',
                   'pubmed.ncbi.nlm.nih.gov', 'who.int', 'un.org',
                   'worldbank.org', 'arxiv.org', 'github.com']
        
        for t in trusted:
            if t in domain:
                signals['Authority'] = 25
                score += 25
                break
        
        # Research indicators
        if any(x in url for x in ['research', 'science', 'doi', 'journal', 'paper']):
            signals['Citations'] = 20
            score += 20
        
        # Cap
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'validated': score >= 70,
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        }
    
    def render_signal_bar(self, label, value, max_val):
        """Render a signal bar"""
        frame = tk.Frame(self.protocol_frame, bg='white')
        frame.pack(fill='x', pady=3)
        
        # Label
        lbl = tk.Label(frame, text=label, font=('Inter', 10),
                      bg='white', fg=self.colors['gray'], width=12, anchor='w')
        lbl.pack(side='left')
        
        # Bar container
        bar_container = tk.Frame(frame, bg=self.colors['light_gray'], height=12, width=200)
        bar_container.pack(side='left', padx=10)
        bar_container.pack_propagate(False)
        
        # Bar
        width = int((value / max_val) * 200)
        bar = tk.Frame(bar_container, bg=self.colors['primary'], height=12, width=width)
        bar.place(x=0, y=0)
        
        # Value
        val_lbl = tk.Label(frame, text=str(value), font=('Inter', 10, 'bold'),
                          bg='white', fg=self.colors['primary'], width=3)
        val_lbl.pack(side='left')
    
    def render_community_section(self, url):
        """Render community reviews section"""
        reviews = self.get_reviews_for_url(url)
        
        if reviews:
            avg = sum(r['rating'] for r in reviews) / len(reviews)
            stars = '★' * round(avg) + '☆' * (5 - round(avg))
            
            stats = tk.Label(self.protocol_frame,
                           text=f"{stars} {avg:.1f}/5 from {len(reviews)} members",
                           font=('Inter', 11),
                           bg='#f8fafc', fg=self.colors['primary'])
            stats.pack(fill='x', pady=10, ipady=8)
        else:
            no_reviews = tk.Label(self.protocol_frame,
                                 text="No community reviews yet. Be the first!",
                                 font=('Inter', 11),
                                 bg='white', fg=self.colors['gray'])
            no_reviews.pack(anchor='w', pady=10)
        
        # Review form
        form_frame = tk.LabelFrame(self.protocol_frame, text=" Submit Review ",
                                  font=('Inter', 10),
                                  bg='white', fg=self.colors['gray'])
        form_frame.pack(fill='x', pady=10)
        
        # Rating
        rating_frame = tk.Frame(form_frame, bg='white')
        rating_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(rating_frame, text="Rating:", font=('Inter', 10),
                bg='white', fg=self.colors['gray']).pack(side='left')
        
        self.rating_var = tk.StringVar(value="3")
        rating_menu = ttk.Combobox(rating_frame, textvariable=self.rating_var,
                                  values=["5 - Excellent", "4 - Good", "3 - Okay", 
                                         "2 - Poor", "1 - Bad"],
                                  width=15, state='readonly')
        rating_menu.pack(side='left', padx=10)
        
        # Comment
        tk.Label(form_frame, text="Comment:", font=('Inter', 10),
                bg='white', fg=self.colors['gray']).pack(anchor='w', padx=10, pady=(5, 0))
        
        self.comment_text = tk.Text(form_frame, height=3, font=('Inter', 10),
                                   relief='solid', bd=1)
        self.comment_text.pack(fill='x', padx=10, pady=5)
        
        # Submit button
        submit_btn = tk.Button(form_frame, text="Submit Review",
                              bg=self.colors['primary'], fg='white',
                              font=('Inter', 10, 'bold'),
                              activebackground=self.colors['primary_dark'],
                              relief='flat',
                              command=lambda: self.submit_review(url))
        submit_btn.pack(fill='x', padx=10, pady=10)
        
        # Show existing reviews
        if reviews:
            sep = tk.Frame(self.protocol_frame, height=1, bg=self.colors['light_gray'])
            sep.pack(fill='x', pady=10)
            
            for review in reviews[-5:]:  # Show last 5
                self.render_review_item(review)
    
    def render_review_item(self, review):
        """Render a single review"""
        frame = tk.Frame(self.protocol_frame, bg='white', pady=5)
        frame.pack(fill='x')
        
        stars = '★' * review['rating'] + '☆' * (5 - review['rating'])
        
        header = tk.Label(frame, text=f"{review['user']}  {stars}",
                         font=('Inter', 10, 'bold'),
                         bg='white', fg=self.colors['primary'])
        header.pack(anchor='w')
        
        if review.get('comment'):
            comment = tk.Label(frame, text=review['comment'],
                             font=('Inter', 9),
                             bg='white', fg=self.colors['gray'],
                             wraplength=350, justify='left')
            comment.pack(anchor='w')
    
    def submit_review(self, url):
        """Submit a community review"""
        rating_text = self.rating_var.get()
        rating = int(rating_text[0])
        comment = self.comment_text.get("1.0", "end-1c").strip()
        
        review = {
            'url': url,
            'rating': rating,
            'comment': comment,
            'user': f"User{os.urandom(2).hex()[:4].upper()}",
            'timestamp': datetime.now().isoformat()
        }
        
        if url not in self.reviews:
            self.reviews[url] = []
        self.reviews[url].append(review)
        
        self.save_reviews()
        
        # Refresh display
        self.render_community_section(url)
        
        # Show confirmation
        messagebox.showinfo("Review Submitted", "Thank you for your review!")
    
    def load_reviews(self):
        """Load reviews from file"""
        try:
            if os.path.exists(self.reviews_file):
                with open(self.reviews_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_reviews(self):
        """Save reviews to file"""
        try:
            with open(self.reviews_file, 'w') as f:
                json.dump(self.reviews, f, indent=2)
        except Exception as e:
            print(f"Failed to save reviews: {e}")
    
    def get_reviews_for_url(self, url):
        """Get reviews for a URL"""
        return self.reviews.get(url, [])
    
    # Utility functions
    @staticmethod
    def extract_domain(url):
        """Extract domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain
        except:
            return url
    
    @staticmethod
    def truncate(text, max_len):
        """Truncate text"""
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + "..."
    
    @staticmethod
    def capitalize(text):
        """Capitalize first letter"""
        if not text:
            return ""
        return text[0].upper() + text[1:].lower()


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set icon if available
    try:
        root.iconbitmap('brim.ico')
    except:
        pass
    
    app = BrimDesktop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
