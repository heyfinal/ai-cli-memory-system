# 🚀 Deployment Instructions

## Quick Deploy to GitHub

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `ai-cli-memory-system`
3. Description: `🧠 Contextual persistent memory system for AI CLI tools (Claude, Codex, Gemini, Aider)`
4. Make it **Public** (so others can benefit!)
5. **DON'T** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Push Your Code

Copy your repository URL from GitHub, then run:

```bash
cd ~/ai-cli-memory-system

# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/ai-cli-memory-system.git

# Push code
git branch -M main
git push -u origin main
```

### Step 3: Update README URLs

After pushing, update these placeholders in README.md:
- `heyfinal` → Your GitHub username
- `support@yourdomain.com` → Your email
- Discord/Twitter links → Your social links (or remove)

Then commit and push:
```bash
git add README.md
git commit -m "Update README with actual URLs"
git push
```

### Step 4: Add Topics to Repository

On GitHub, add these topics to make it discoverable:
- `ai`
- `cli`
- `memory`
- `claude`
- `copilot`
- `gemini`
- `developer-tools`
- `productivity`
- `python`
- `sqlite`

### Step 5: Enable GitHub Pages (Optional)

For a nice project page:
1. Go to Settings → Pages
2. Source: Deploy from branch `main` / `root`
3. Your site will be at: `https://USERNAME.github.io/ai-cli-memory-system/`

---

## Deploy to Other Machines

### Quick Deploy (after GitHub push)

```bash
# On any new machine:
curl -fsSL https://raw.githubusercontent.com/USERNAME/ai-cli-memory-system/main/install.sh | bash
```

### Manual Deploy

```bash
# Clone repository
git clone https://github.com/USERNAME/ai-cli-memory-system.git
cd ai-cli-memory-system

# Run installer
./install.sh
```

---

## Update Existing Installations

```bash
cd ~/ai-cli-memory-system
git pull
./install.sh
```

---

## Alternative: Using GitHub CLI

If you have `gh` CLI configured:

```bash
cd ~/ai-cli-memory-system

# Authenticate (if needed)
gh auth login

# Create repository and push
gh repo create ai-cli-memory-system --public --source=. --remote=origin --push

# Add description
gh repo edit --description "🧠 Contextual persistent memory system for AI CLI tools (Claude, Codex, Gemini, Aider)"

# Add topics
gh repo edit --add-topic ai,cli,memory,claude,copilot,gemini,developer-tools,productivity,python,sqlite
```

---

## Verify Deployment

After deployment, test the installation URL:

```bash
# On a different machine or clean directory:
curl -fsSL https://raw.githubusercontent.com/USERNAME/ai-cli-memory-system/main/install.sh | bash
```

---

## Share Your Repository

Once deployed, share on:
- Twitter/X with hashtags: `#AI #CLI #DevTools #Claude #Copilot`
- Reddit: r/programming, r/commandline, r/ChatGPT
- Hacker News: Show HN
- Dev.to: Write a blog post about it
- Your LinkedIn/blog

---

## Next Steps

1. ✅ Push to GitHub
2. ✅ Update README URLs
3. ✅ Add repository topics
4. ✅ Test installation on another machine
5. ✅ Share with the community!
