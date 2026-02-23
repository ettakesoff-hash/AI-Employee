# AI Digital Employee — Skool Course

**Price:** $97
**Lessons:** 7 videos
**Total recording time:** ~90-120 min
**Template repo:** github.com/systemstoscale/AI-Digital-Employee

---

# LESSON 1: The AI Employee Model
**Video length:** 10-15 min | **Format:** Talking head + screen share diagrams

## Copy this into the Skool lesson description:

> Most people use AI like a chatbot — long messy conversations, inconsistent output, no memory between sessions. In this lesson, you'll learn how to set up AI as a digital employee with context, workflows, and tools — the same model we use at Skalers to build AI systems for 7-9 figure companies.

---

### SECTION 1: The Problem (3 min)

**Talking points:**

You're using AI wrong. Here's what most people do:
- Open ChatGPT or Claude
- Type a long prompt
- Get a mediocre answer
- Try again with a different prompt
- Waste 30 minutes going back and forth
- End up rewriting it yourself anyway

The output is inconsistent because the AI has zero context about who you are, what you do, or what you're trying to achieve. It's like hiring someone and giving them no onboarding, no SOPs, and no tools — then wondering why they can't do the job.

### SECTION 2: The Fix — Treat AI Like an Employee (3 min)

**Talking points:**

When you hire a new employee, you give them:
- **Onboarding** — who the company is, what it does, how it works
- **Task guides** — SOPs for the work they'll be doing
- **Tools** — software, accounts, access to what they need
- **A place to put finished work** — shared drives, project boards

That's exactly what we're going to build. One folder on your computer with 4 sub-folders:

**Show this diagram on screen:**

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR WORKSPACE                       │
│                                                         │
│  ┌─────────┐  ┌──────────────┐  ┌─────────┐  ┌──────┐ │
│  │ context/ │→ │instructions/ │→ │scripts/ │→ │outputs│ │
│  │         │  │              │  │         │  │      │  │
│  │WHO YOU  │  │ WHAT TO DO   │  │  HOW    │  │RESULTS│ │
│  │  ARE    │  │              │  │         │  │      │  │
│  └─────────┘  └──────────────┘  └─────────┘  └──────┘ │
│                                                         │
│  Onboarding    Task Guides       Tools      Deliverables│
└─────────────────────────────────────────────────────────┘
```

- `context/` = Onboarding. Who you are, your business, your goals.
- `instructions/` = SOPs. Step-by-step task guides the AI follows.
- `scripts/` = Tools. Code that pulls data from APIs, automates actions.
- `outputs/` = Deliverables. Where finished work gets saved.

### SECTION 3: Context Stacking (3 min)

**Talking points:**

The secret to great AI output is context stacking. You layer information so the AI has the full picture before it does anything.

**Show this diagram on screen:**

```
┌─────────────────────────────────────────────┐
│                                             │
│          💬 INTELLIGENT CONVERSATION        │
│          (Your tasks and requests)          │
│                                             │
├─────────────────────────────────────────────┤
│  Layer 5: data.md      → Current numbers    │
├─────────────────────────────────────────────┤
│  Layer 4: strategy.md  → What matters now   │
├─────────────────────────────────────────────┤
│  Layer 3: personal.md  → Who you are        │
├─────────────────────────────────────────────┤
│  Layer 2: business.md  → What the company   │
│                           does              │
├─────────────────────────────────────────────┤
│  Layer 1: CLAUDE.md    → Workspace rules    │
│                          & purpose          │
└─────────────────────────────────────────────┘
```

Every time you start a new session, the AI reads all of this first. Then when you give it a task, it has the full picture — your business, your voice, your goals, your metrics. The output quality difference is massive.

### SECTION 4: The 4 Mistakes (3 min)

**Show this on screen:**

```
MISTAKE                          → FIX
─────────────────────────────────────────────────
1. Using AI like a chatbot       → Reusable commands
2. No context each session       → /project:prime
3. No planning loops             → /project:create-plan
                                   + /project:implement
4. No external data              → Scripts that pull
                                   real-time data
```

**Talking points:**

1. **Chatbot mode** — You chat back and forth, waste tokens, get diluted output. Fix: create reusable command files (instructions) that you run every time.
2. **No context** — Every session starts from zero. Fix: run `/project:prime` every time — loads your full context in seconds.
3. **No planning** — You try to do everything in one message. Fix: use `/project:create-plan` to design the workflow, then `/project:implement` to execute it.
4. **No real data** — The AI is guessing instead of using your actual numbers. Fix: scripts that pull real-time data from APIs.

**End with:** "That's the model. Now let's set it up."

---
---

# LESSON 2: Setup — Zero to Working in 10 Minutes
**Video length:** 15-20 min | **Format:** Full screen share, every click shown

## Copy this into the Skool lesson description:

> In this lesson, you'll install everything, clone the template, and run a live demo that fetches real AI news and turns it into LinkedIn posts, tweets, and a newsletter — automatically. By the end of this video, you'll have a working AI employee on your machine.

---

### PART 1: Install the Tools (5 min)

**Step by step on screen:**

1. **Download VS Code**
   - Go to code.visualstudio.com
   - Download for your machine (Mac/Windows)
   - Install it, open it
   - OR download Antigravity from antigravity.devcycle.cc (VS Code fork with Claude built in)

2. **Install Claude Code**
   - In VS Code: go to Extensions (Cmd+Shift+X)
   - Search "Claude Code"
   - Install the official Anthropic extension

3. **Open the terminal**
   - Terminal → New Terminal (or Ctrl+`)
   - Say: "This is where you'll type commands. It's not scary."

4. **Verify prerequisites**
   ```
   node --version    → need v18 or higher
   python3 --version → need 3.x
   ```

### PART 2: Clone the Template (3 min)

**On screen:**

```bash
git clone https://github.com/systemstoscale/AI-Digital-Employee.git
```

Then: File → Open Folder → select the cloned folder.

**Quick tour** — 30 seconds, point at each folder:
- context/ → "This is where your info goes"
- instructions/ → "These are your task guides"
- scripts/ → "Code that pulls external data"
- outputs/ → "Where finished work lands"
- CLAUDE.md → "The AI reads this every session"

### PART 3: Get Your Free API Key (2 min)

**On screen:**

1. Go to newsapi.org/register
2. Sign up (name, email, password — 30 seconds)
3. Copy the API key
4. In VS Code: open `.env`
5. Paste after `NEWS_API_KEY=`
6. Cmd+S to save

Say: "This is a free API that gives us real news data. 100 requests per day. We're using it to show you the full pipeline."

### PART 4: Set Up Your Shortcut Aliases (3 min)

**IMPORTANT — explain clearly:**

Say: "There are TWO places you type things. The regular terminal — where you run normal commands. And inside Claude Code — where you chat with the AI. Right now we're going to set up shortcuts so you can start Claude Code with just 2 letters."

**On screen — paste this into the terminal:**

```bash
echo '
# AIDE — AI Digital Employee aliases
alias cs="cd ~/AI-Digital-Employee && claude"
alias cr="cd ~/AI-Digital-Employee && claude --dangerously-skip-permissions -p /project:prime"' >> ~/.zshrc
```

Then close and reopen the terminal (or `source ~/.zshrc`).

**Explain:**

```
cs = Claude Safe
     Starts Claude Code. You type /project:prime manually.
     Good for learning.

cr = Claude Risky (YOLO mode)
     Starts Claude Code with all permissions + auto-primes.
     No permission popups, reads your context automatically.
     This is what you'll use 90% of the time.
```

**Demo:** Type `cr` → watch it start and auto-prime.

Say: "From now on, every time you want your AI employee, you open a terminal and type `cr`. Two letters. That's it."

### PART 5: Run the Live Demo (5 min)

**On screen:**

1. In the regular terminal (NOT inside Claude Code):
   ```bash
   python3 scripts/fetch-news.py
   ```
2. Open `outputs/latest-news.md` — show 10 real AI articles

3. Type `cr` to start Claude Code — it auto-primes

4. Type:
   ```
   Follow the news-to-content instruction using the news you just fetched.
   ```

5. Watch Claude:
   - Read the news articles
   - Pick the 3 best stories
   - Write 3 LinkedIn posts with hooks
   - Write 6 tweets (2 per story)
   - Write a newsletter snippet
   - Save everything to outputs/

6. Open the output file — show the finished content

7. Bonus — try other topics:
   ```bash
   python3 scripts/fetch-news.py "startup funding"
   python3 scripts/fetch-news.py "remote work"
   ```

**End with:** "You just automated content creation in 10 minutes using a free API. Now let's make it actually know who you are."

---
---

# LESSON 3: Context — Onboard Your AI in 5 Minutes
**Video length:** 10-15 min | **Format:** Screen share, running the setup command live

## Copy this into the Skool lesson description:

> You wouldn't hire an employee without onboarding them. In this lesson, you run one command that interviews you about your business, role, goals, and metrics — then automatically fills in all your context files. By the end, your AI employee knows exactly who you are.

---

### THE ONE COMMAND (10 min)

**On screen:**

1. Start Claude Code (type `cr` or `claude`)

2. Type:
   ```
   /project:setup
   ```

3. Claude asks you questions in 4 rounds:

**Show this diagram:**

```
┌──────────────────────────────────────────────────┐
│              /project:setup                      │
│                                                  │
│  Round 1: Your Business  → writes business.md    │
│  ┌──────────────────────────────────────┐        │
│  │ Company name? What do you do?       │        │
│  │ Products/services? Who do you serve? │        │
│  │ Tech stack? Key links?              │        │
│  └──────────────────────────────────────┘        │
│                                                  │
│  Round 2: You            → writes personal.md    │
│  ┌──────────────────────────────────────┐        │
│  │ Name? Role? Coding experience?      │        │
│  │ Communication style? Pet peeves?    │        │
│  └──────────────────────────────────────┘        │
│                                                  │
│  Round 3: Your Strategy  → writes strategy.md    │
│  ┌──────────────────────────────────────┐        │
│  │ Top priority? Goals? Active projects?│        │
│  │ Metrics? What's NOT a priority?     │        │
│  └──────────────────────────────────────┘        │
│                                                  │
│  Round 4: Your Data      → writes data.md       │
│  ┌──────────────────────────────────────┐        │
│  │ Current metrics? Data sources?      │        │
│  │ (Optional — can skip)               │        │
│  └──────────────────────────────────────┘        │
│                                                  │
│  ✅ Done → auto-primes → ready to work          │
└──────────────────────────────────────────────────┘
```

4. Answer each round naturally — just talk/type like you're explaining your business to a new hire

5. Claude writes each file immediately after you answer

6. At the end: Claude gives you a summary and says "Your AI employee is set up and ready."

**Live on screen:** Run through the whole setup for a real business. Show how each context file gets filled in automatically.

**For people who want to do it manually:**
Say: "If you'd rather fill in the files yourself, check `context/_examples.md` — there are three filled-in examples you can use as a guide. A content agency, a student, and a consulting firm."

**End with:** "Your AI employee now knows who you are, what you do, and what you're working on. Every session from now on, it starts with this context. Next: teach it what to do."

---
---

# LESSON 4: Instructions — Automate Any Workflow
**Video length:** 15-20 min | **Format:** Screen share, building a real instruction live

## Copy this into the Skool lesson description:

> Instructions are reusable task guides your AI follows every time — like SOPs for your digital employee. In this lesson, you'll learn the create-plan → implement loop and build your first custom workflow from scratch. This is where the real power is.

---

### SECTION 1: How Instructions Work (3 min)

**Talking points:**

An instruction is just a text file with:
- A goal (what it accomplishes)
- Inputs (what info it needs)
- Steps (what to do, in order)
- Output format (where to save, how to structure)

```
┌──────────────────────────────────────────────┐
│  instructions/_example-news-to-content.md    │
│                                              │
│  Goal: Turn news into social content         │
│  Inputs: topic, platforms                    │
│  Steps:                                      │
│    1. Run fetch-news.py                      │
│    2. Pick 3 best stories                    │
│    3. Write LinkedIn posts                   │
│    4. Write tweets                           │
│    5. Write newsletter snippet               │
│  Output: outputs/news-content-[date].md      │
└──────────────────────────────────────────────┘
```

Why this beats chatting:
- **Consistent** — same quality every time
- **Fast** — no re-explaining
- **Reusable** — run it daily, weekly, whenever

The template includes 7 example instructions. Quick tour — show each filename and what it does.

### SECTION 2: The Planning Loop (5 min)

**Show this diagram:**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  YOU        │     │ CREATE PLAN  │     │ IMPLEMENT   │
│             │     │              │     │             │
│ "I want to  │────→│ Claude reads │────→│ Claude      │
│  automate   │     │ workspace,   │     │ executes    │
│  my weekly  │     │ designs the  │     │ every step, │
│  report"    │     │ full plan    │     │ creates     │
│             │     │              │     │ files,      │
│             │     │ Saves to     │     │ self-       │
│             │     │ instructions/│     │ corrects    │
└─────────────┘     └──────────────┘     └─────────────┘
                                               │
                                               ▼
                                    ┌─────────────────┐
                                    │ ERROR?          │
                                    │ Read → Fix →    │
                                    │ Retest → Update │
                                    │ instruction     │
                                    └─────────────────┘
```

**Demo on screen:**

1. Type: `/project:create-plan I want to automate writing a weekly LinkedIn recap of what I worked on`
2. Watch Claude: read the workspace, analyze what exists, write a detailed plan
3. Show the plan file — steps, files to create, decisions
4. Type: `/project:implement`
5. Watch Claude: create the instruction file, update CLAUDE.md, test it

### SECTION 3: Build Your First Custom Instruction Live (7 min)

**Pick a real task.** Suggestions:
- "Automate my weekly email newsletter from rough notes"
- "Create a competitor analysis report from a company name"
- "Turn a meeting transcript into action items and follow-ups"

Run through create-plan → implement live. Show every step.

### SECTION 4: What's Possible — Real Examples from Skalers (3 min)

**Talking points:**

At Skalers.io, we build AI systems for 7-9 figure companies. The same model applies at any scale:

```
WHAT WE AUTOMATE AT SKALERS     → YOUR VERSION
──────────────────────────────────────────────────
AI Knowledge Base                → context/ files
  (company data → instant        that give your
  answers for any employee)       AI full context

AI Client Acquisition            → instructions/
  (autonomous outbound that       that automate
  books calls 24/7)               your outreach

AI Client Fulfillment            → scripts/ that
  (onboarding, reporting,         pull data + do
  QA, client comms)               the actual work
```

The difference between a $5K task automation and a $50K+ role automation is scope — but the building blocks are the same. Context. Instructions. Scripts. Outputs.

You're learning the foundation that scales from personal productivity to enterprise systems.

**End with:** "You can now create any workflow in minutes. Next: pulling real-time data."

---
---

# LESSON 5: Scripts — Pull Live Data Into Your Workspace
**Video length:** 10-15 min | **Format:** Screen share, building a new script live

## Copy this into the Skool lesson description:

> Scripts are how your AI employee connects to the outside world — pulling real-time data from APIs, scraping websites, fetching analytics. You don't write the code. Claude does. In this lesson, you'll add a new data source to your workspace.

---

### SECTION 1: What Scripts Do (2 min)

**Show this diagram:**

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  EXTERNAL    │    │  SCRIPT      │    │  YOUR        │
│  DATA        │    │              │    │  WORKSPACE   │
│              │    │ fetch-news.py│    │              │
│  NewsAPI ────│───→│ pulls data,  │───→│  outputs/    │
│  YouTube     │    │ formats it,  │    │  latest-     │
│  CRM         │    │ saves to     │    │  news.md     │
│  Analytics   │    │ outputs/     │    │              │
│  Any API     │    │              │    │  Claude      │
│              │    │              │    │  reads this  │
└──────────────┘    └──────────────┘    └──────────────┘
```

Pattern: Script fetches → saves to outputs/ → instruction processes it.

You don't write the code. You tell Claude what data you want. It figures out how to get it.

### SECTION 2: Add a New Script Live (8 min)

**On screen:**

1. Type: `/project:create-plan I want a script that fetches the top 10 Hacker News posts and saves them to outputs/`

2. Watch Claude:
   - Research the Hacker News API
   - Design the script
   - Write the plan

3. Type: `/project:implement`

4. Watch Claude:
   - Write the script
   - Save it to scripts/
   - Test it
   - If it fails → read error → fix → retest (show this if it happens!)

5. Run the script manually: `python3 scripts/fetch-hackernews.py`

6. Show the output file

### SECTION 3: Free APIs You Can Connect (2 min)

**Show this on screen:**

```
API                  WHAT IT DOES                    COST
─────────────────────────────────────────────────────────
NewsAPI              Latest news on any topic        Free (100/day)
Serper               Google search results           Free (2,500 credits)
Apify                Web scraping (YouTube, etc.)    Free tier
OpenWeatherMap       Weather data                    Free (1,000/day)
Hacker News          Top tech posts                  Free (unlimited)
Reddit JSON          Subreddit posts                 Free (no key needed)
─────────────────────────────────────────────────────────
Any API:  Add key to .env → tell Claude what you want
          → it builds the script for you
```

**Skalers example:**

Say: "At Skalers, we use Apify to scrape competitor data, LinkedIn profiles, and YouTube channels — then feed that into AI systems that generate reports and outreach. Same pattern, bigger scale. The building block is always: script pulls data → AI processes it."

**End with:** "Your AI employee can now pull live data from anywhere. Next: let's see complete workflows."

---
---

# LESSON 6: Real-World Workflows You Can Steal
**Video length:** 15-20 min | **Format:** Screen share, running each workflow end to end

## Copy this into the Skool lesson description:

> Watch 3 complete workflows run from start to finish — content creation, business operations, and research. Each one shows the full pipeline: data in → AI processing → formatted output. Pick the one closest to your role and start using it today.

---

### WORKFLOW 1: Content Creator (6 min)

**Context:** Content marketing agency (show example from `_examples.md`)

**On screen — run the full pipeline:**

```
INPUT                    INSTRUCTION                  OUTPUT
─────────────────────────────────────────────────────────────
"AI trends"         →   news-to-content          →   3 LinkedIn posts
                                                      6 tweets
                                                      1 newsletter snippet

"How to build a     →   write-blog-post          →   1,500-word SEO blog
 content calendar"                                    with metadata

blog post file      →   repurpose-content        →   3 LinkedIn posts
                                                      5 tweets
                                                      1 newsletter snippet
                                                      1 thread
```

Run each one live. Show the output.

Say: "This whole pipeline — news to content to repurposed social — takes about 5 minutes. Doing it manually takes 3+ hours."

### WORKFLOW 2: Business Operations (5 min)

**Context:** Consulting firm ops manager

**On screen:**

```
INPUT                    INSTRUCTION                  OUTPUT
─────────────────────────────────────────────────────────────
Rough weekly notes  →   weekly-report            →   Formatted status report
                                                      with highlights, metrics,
                                                      priorities

Competitor name     →   competitor-analysis      →   Full competitor profile
                                                      with comparison table
                                                      and opportunities
```

Run each one live. Show the output.

**Skalers connection:**
Say: "This is exactly what our AI Fulfillment systems do at scale — automated reporting, client status updates, competitive intelligence. We charge $60-120K to build these for enterprise clients. You're learning the same patterns for free."

### WORKFLOW 3: Student / Researcher (5 min)

**Context:** CS student

**On screen:**

```
INPUT                    INSTRUCTION                  OUTPUT
─────────────────────────────────────────────────────────────
Research topic      →   research-paper           →   Annotated bibliography
                                                      Paper outline
                                                      Full draft
                                                      References

Course topic        →   study-guide              →   Key concepts
                                                      Practice questions
                                                      Exam topics
                                                      Answers
```

Run each one live. Show the multi-step output.

### BUILD YOUR OWN (3 min)

**Show this pattern:**

```
ANY REPEATING TASK YOU DO:

1. Identify it      → "I write a weekly report every Monday"
2. /create-plan     → Claude designs the workflow
3. /implement       → Claude builds the instruction
4. Test it          → Run the instruction, check the output
5. Iterate          → Refine steps, add edge cases
6. Reuse forever    → Same quality, every time, in minutes
```

Say: "Pick ONE task you do every week. Automate it before moving on to the next lesson."

**End with:** "You've seen 6 workflows across 3 different roles. Next: power user tips to make this even faster."

---
---

# LESSON 7: Level Up — Speed, Skills, and Scaling
**Video length:** 10-15 min | **Format:** Screen share with tips and demos

## Copy this into the Skool lesson description:

> You've got the foundation. Now make it fast. In this lesson: YOLO mode for speed, running multiple AI instances in parallel, installing skills/plugins, and the path from personal productivity to building AI systems as a service.

---

### TIP 1: YOLO Mode for Speed (3 min)

**On screen:**

```
SAFE MODE (cs)                   YOLO MODE (cr)
─────────────────────────────────────────────────
Claude asks permission           Claude just does it
for every action
                                 + auto-primes
Good for learning                (reads your context
                                  automatically)

"Can I write to this file?"      Just writes it

Slower but safer                 Fast. Use this 90%
                                 of the time.
```

Demo: Show the speed difference. `cr` → instant primed session → immediately give it a task.

### TIP 2: Multiple Instances (2 min)

**On screen:**

- Cmd+\ → new terminal pane
- Type `cr` in each → two Claude instances side by side

Use cases:
- Plan in one terminal, implement in another
- Run a long task in one, start something else in the other
- Research in one, write in the other

### TIP 3: Claude Skills / Plugins (3 min)

**On screen:**

Skills are installable packages that add capabilities to your workspace.

Where to find them: github.com/anthropics/skills

Example: PowerPoint skill → turns any markdown report into a .pptx presentation.

Demo: Install a skill, show Claude using it.

### TIP 4: The Self-Correction Loop (2 min)

**Show this diagram:**

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐
│  ERROR   │───→│  READ   │───→│  FIX    │───→│  UPDATE  │
│  happens │    │  error  │    │  code   │    │  instruc-│
│          │    │  message│    │  & re-  │    │  tion    │
│          │    │         │    │  test   │    │  with    │
│          │    │         │    │         │    │  lesson  │
└─────────┘    └─────────┘    └─────────┘    └──────────┘
                                                   │
                                                   ▼
                                         SYSTEM IS SMARTER
                                         Same mistake never
                                         happens twice
```

Over time, your instruction files accumulate lessons learned. The workspace compounds.

### TIP 5: From Personal Productivity to Building AI Systems (3 min)

**Talking points:**

Everything you just learned is the foundation of what we build at Skalers for enterprise clients:

```
YOUR WORKSPACE                    ENTERPRISE AI SYSTEM
──────────────────────────────────────────────────────
context/                      →   AI Knowledge Base
  (your business info)            (company-wide RAG database)
                                  Value: $25-40K setup

instructions/                 →   AI Acquisition System
  (your task guides)              (autonomous outbound SDR)
                                  Value: $45-80K setup

scripts/                      →   AI Fulfillment System
  (your data connectors)          (delivery + operations AI)
                                  Value: $75-120K setup
```

The patterns are identical. The scale is different.

If you want to go deeper:
- Join the free Skalers community at skalers.io
- Learn the IDEA Framework (Instructions → Decisions → Executions → AI)
- Build these systems for clients at $20-100K per project

**End with:** "You now have everything you need. The template, the context, the instructions, the scripts. Go build. Share what you create in the community."

---
---

# SKOOL SETUP CHECKLIST

## Community Settings
- **Name:** AI Digital Employee
- **Price:** $97
- **Access:** Classroom + Community

## Classroom Structure

| # | Lesson Title | Video Length |
|---|-------------|-------------|
| 1 | The AI Employee Model | 10-15 min |
| 2 | Setup — Zero to Working in 10 Minutes | 15-20 min |
| 3 | Context — Onboard Your AI in 5 Minutes | 10-15 min |
| 4 | Instructions — Automate Any Workflow | 15-20 min |
| 5 | Scripts — Pull Live Data Into Your Workspace | 10-15 min |
| 6 | Real-World Workflows You Can Steal | 15-20 min |
| 7 | Level Up — Speed, Skills, and Scaling | 10-15 min |

## Pinned Post (Copy-Paste)

```
🚀 START HERE

1. Watch Lesson 1 (10 min) — understand the model
2. Watch Lesson 2 (15 min) — get set up + run the live demo
3. Watch Lesson 3 (10 min) — onboard your AI with /project:setup
4. Watch Lessons 4-7 at your own pace

Template repo: github.com/systemstoscale/AI-Digital-Employee

Free API key: newsapi.org/register

Stuck? Post in the community. We're here to help.
```

## Community Channels

1. **General** — Main discussion
2. **Share Your Workflows** — Members post their custom instructions
3. **Troubleshooting** — Help with setup and errors
4. **Wins** — Show what your AI employee produced

## Drip Schedule (Optional)

- Lessons 1-3: Available immediately (get them set up and seeing results fast)
- Lessons 4-5: Unlock after 3 days
- Lessons 6-7: Unlock after 7 days

## CTA for Skalers (End of Lesson 7)

```
Want to build AI systems like this for clients at $20-100K per project?

Join the free Skalers community: skalers.io

Learn the IDEA Framework. Build the 3 core AI systems.
Land your first client in 90 days.
```
