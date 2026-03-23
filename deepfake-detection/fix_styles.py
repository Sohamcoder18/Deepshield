import sys

new_header = """:root {
    /* Cyber-Shield Elitist Palette */
    --primary-neon: #00f2ff;
    --primary-blue: #0066ff;
    --secondary-neon: #7000ff;
    --success-neon: #00ff88;
    --danger-neon: #ff0055;
    
    --bg-dark: #020617;
    --bg-accent: #0f172a;
    
    /* Advanced Glassmorphism Tokens */
    --glass-bg: rgba(15, 23, 42, 0.4);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-highlight: rgba(255, 255, 255, 0.15);
    --glass-blur: blur(20px);
    
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    
    --shadow-soft: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    --shadow-neon: 0 0 30px rgba(0, 242, 255, 0.2);
    --shadow-glow: 0 0 15px rgba(0, 102, 255, 0.3);
    
    --transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    --border-radius: 20px;
    --border-radius-lg: 32px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg-dark);
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(0, 102, 255, 0.1) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(112, 0, 255, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 1) 0%, rgba(2, 6, 23, 1) 100%);
    background-attachment: fixed;
    background-size: 200% 200%;
    animation: gradientFlow 15s ease infinite alternate;
    color: var(--text-main);
    line-height: 1.6;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
    min-height: 100vh;
}

@keyframes gradientFlow {
    0% { background-position: 0% 0%; }
    100% { background-position: 100% 100%; }
}

/* Glass Utility Classes */
.glass {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-soft);
    position: relative;
    overflow: hidden;
}

.glass::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.05),
        transparent
    );
    transition: 0.5s;
}

.glass:hover::before {
    left: 100%;
}

.glass-hover:hover {
    background: var(--glass-highlight);
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-5px);
    box-shadow: var(--shadow-neon);
}
"""

with open('styles.css', 'r', encoding='utf-8') as f:
    # We need to skip 91 lines from the ORIGINAL state, 
    # but the CURRENT state has 91 lines of NEW header + literal '\\n' (1 line) + original lines.
    # So we should skip 92 current lines to get back to .container.
    lines = f.readlines()

with open('styles.css', 'w', encoding='utf-8') as f:
    f.write(new_header + '\n')
    f.writelines(lines[92:])
