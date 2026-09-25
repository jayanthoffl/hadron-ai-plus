import os
import re

css_path = "control_tower/static/control_tower.css"
html_path = "control_tower/templates/index.html"

# Update CSS
with open(css_path, "r") as f:
    css = f.read()

# Replace login-card
old_card = """.login-card {
  width: min(440px, 92vw);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 28px;
  padding: 40px 36px;
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.05), 0 35px 90px rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(36px) saturate(150%);
}"""

new_card = """.login-card {
  width: min(440px, 92vw);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0));
  backdrop-filter: blur(25px) saturate(160%);
  -webkit-backdrop-filter: blur(25px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 36px;
  padding: 44px 40px;
  box-shadow: inset 0 0 2px rgba(255, 255, 255, 0.6), inset 0 0 20px rgba(255, 255, 255, 0.15), 0 35px 80px rgba(0, 0, 0, 0.6);
}"""
css = css.replace(old_card, new_card)

# Replace input focus
old_input = """.input-with-icon input {
  padding-left: 42px; background: rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.12);
  height: 44px; font-size: 0.88rem; border-radius: 12px;
}
.input-with-icon input:focus {
  border-color: var(--gold);
  box-shadow: 0 0 16px rgba(226, 192, 121, 0.25);
}"""

new_input = """.input-with-icon input {
  padding-left: 42px; background: rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.15);
  height: 46px; font-size: 0.9rem; border-radius: 12px;
  color: #fff;
  transition: all 0.3s;
}
.input-with-icon input:focus {
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: inset 0 0 8px rgba(255, 255, 255, 0.1), 0 0 12px rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.3);
}"""
css = css.replace(old_input, new_input)

# Replace button
old_btn = """.btn-login-submit {
  margin-top: 8px; height: 48px;
  background: linear-gradient(135deg, #e2c079 0%, #b89345 100%);
  color: #050b14; border: none; border-radius: 14px;
  font-size: 0.88rem; font-weight: 800; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: all 0.25s; font-family: inherit;
  box-shadow: 0 8px 24px rgba(226, 192, 121, 0.35);
}
.btn-login-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(226, 192, 121, 0.55);
}"""

new_btn = """.btn-login-submit {
  margin-top: 12px; height: 48px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  color: #fff; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 14px;
  font-size: 1rem; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: all 0.3s ease; font-family: inherit;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.1), 0 10px 24px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  letter-spacing: 0.05em;
}
.btn-login-submit:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.1));
  transform: translateY(-2px);
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.25), 0 15px 32px rgba(0, 0, 0, 0.6);
  border-color: rgba(255, 255, 255, 0.6);
}"""
css = css.replace(old_btn, new_btn)

with open(css_path, "w") as f:
    f.write(css)

# Update HTML
with open(html_path, "r") as f:
    html = f.read()

old_html_btn = """<button type="submit" class="btn-login-submit">
        <span>Sign In to Executive Gateway</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </button>"""
new_html_btn = """<button type="submit" class="btn-login-submit">
        <span>Sign In</span>
      </button>"""
html = html.replace(old_html_btn, new_html_btn)

with open(html_path, "w") as f:
    f.write(html)

print("UI successfully updated!")
