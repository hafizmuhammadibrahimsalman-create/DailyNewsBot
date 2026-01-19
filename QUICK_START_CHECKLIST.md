# Quick Start Checklist

Fast-track guide to get DailyNewsBot running smoothly.

---

## Pre-Flight Checklist

### 1. Environment Setup ✓

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated (recommended)
- [ ] `.env` file exists with real values
- [ ] Run: `python env_validator.py` - all checks pass

### 2. Dependencies ✓

```bash
pip install -r requirements.txt
```

- [ ] All packages installed without errors
- [ ] No import errors when running scripts

### 3. API Keys ✓

- [ ] GEMINI_API_KEY is set (39+ characters)
- [ ] WHATSAPP_NUMBER is set with country code
- [ ] (Optional) NEWS_API_KEY configured
- [ ] (Optional) GNEWS_API_KEY configured

---

## Testing Checklist

### Step 1: Validate Environment
```bash
python env_validator.py
```
- [ ] All critical checks pass
- [ ] No ERROR-level failures

### Step 2: Health Check
```bash
python run_automation.py --health
```
- [ ] Network connected
- [ ] API keys validated
- [ ] All components loaded

### Step 3: Dry Run
```bash
python run_automation.py --dry-run
```
- [ ] News fetched successfully
- [ ] Summary generated
- [ ] No crashes or exceptions

### Step 4: Test Suite
```bash
python test_suite.py
```
- [ ] Tests run without import errors
- [ ] Most tests pass

---

## First Live Run

```bash
python run_automation.py --run
```

**Before running:**
- [ ] WhatsApp Web logged in (scan QR code first)
- [ ] Browser window visible
- [ ] Don't move mouse during send

**After running:**
- [ ] Message appears in WhatsApp
- [ ] Check `logs/` for any errors
- [ ] Dashboard generated at `dashboard.html`

---

## Troubleshooting

### "GEMINI_API_KEY is missing"
→ Check `.env` file exists and has the key

### "Module not found"
→ Run: `pip install -r requirements.txt`

### "WhatsApp message not sent"
→ Make sure WhatsApp Web is logged in
→ Don't move mouse during send
→ Increase wait_time in config

### "Network not connected"
→ Check internet connection
→ Check firewall/proxy settings

---

## Daily Operations

### Morning Check
```bash
python run_automation.py --health
```

### Generate Report
```bash
python run_automation.py --run
```

### View Analytics
```bash
python run_automation.py --dashboard
# Open dashboard.html in browser
```

---

## Files to Know

| File | Purpose |
|------|---------|
| `run_automation.py` | Main entry point |
| `env_validator.py` | Pre-flight checks |
| `.env` | API keys (DO NOT COMMIT) |
| `config.py` | All settings |
| `logs/` | Debug logs |
| `cache/` | Cached news data |

---

Ready to go! 🚀
