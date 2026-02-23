# AI Employee

**Price:** $97
**Lessons:** 7 videos
**Total recording time:** ~90-120 min
**Template repo:** github.com/systemstoscale/AI-Employee

---

# LESSON 1: Why Your AI Sucks (And How to Fix It)
**Video length:** 10-15 min | **Format:** Talking head + screen share diagrams

## Copy this into the Skool lesson description:

> Most people use AI like a chatbot. Long messy conversations, inconsistent output, no memory between sessions. In this lesson, you'll learn how to set up AI as an employee with context, workflows, and tools. The same model we use at Skalers to build AI systems for 7-9 figure companies.

---

### The Problem

You're using AI wrong. Here's what most people do:
- Open ChatGPT or Claude
- Type a long prompt
- Get a mediocre answer
- Try again with a different prompt
- Waste 30 minutes going back and forth
- End up rewriting it yourself anyway

The output is inconsistent because the AI has zero context about who you are, what you do, or what you're trying to achieve. It's like hiring someone and giving them no onboarding, no SOPs, and no tools, then wondering why they can't do the job.

### The Fix: Treat AI Like an Employee

When you hire a new employee, you give them:
- **Onboarding**. Who the company is, what it does, how it works
- **Task guides**. SOPs for the work they'll be doing
- **Tools**. Software, accounts, access to what they need
- **A place to put finished work**. Shared drives, project boards

That's exactly what we're going to build. One folder on your computer with 4 sub-folders:

```
┌────────────────────────────────────────────────────────────────────────┐
│                             YOUR WORKSPACE                             │
│                                                                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌───────────┐  │
│  │ context/    │→ │instructions/ │→ │ scripts/      │→ │ outputs/  │  │
│  │             │  │              │  │               │  │           │  │
│  │ WHO YOU ARE │  │  WHAT TO DO  │  │ HOW YOU DO IT │  │  RESULTS  │  │
│  │             │  │              │  │               │  │           │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  └───────────┘  │
│                                                                        │
│   Onboarding       Task Guides        Tools             Deliverables   │
└────────────────────────────────────────────────────────────────────────┘
```

- `context/` = Onboarding. Who you are, your business, your goals.
- `instructions/` = SOPs. Step-by-step task guides the AI follows.
- `scripts/` = Tools. Code that pulls data from APIs, automates actions.
- `outputs/` = Deliverables. Where finished work gets saved.

### Context Stacking

The secret to great AI output is context stacking. You layer information so the AI has the full picture before it does anything.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│            INTELLIGENT CONVERSATION                 │
│            (Your tasks and requests)                │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Layer 5:  data.md       →  Current numbers         │
├─────────────────────────────────────────────────────┤
│  Layer 4:  strategy.md   →  What matters now        │
├─────────────────────────────────────────────────────┤
│  Layer 3:  personal.md   →  Who you are             │
├─────────────────────────────────────────────────────┤
│  Layer 2:  business.md   →  What the company does   │
├─────────────────────────────────────────────────────┤
│  Layer 1:  CLAUDE.md     →  Workspace rules         │
└─────────────────────────────────────────────────────┘
```

Every time you start a new session, the AI reads all of this first. Then when you give it a task, it has the full picture. Your business, your voice, your goals, your metrics. The output quality difference is massive.

### The 4 Mistakes

```
MISTAKE                             FIX
────────────────────────────────────────────────────────
1. Using AI like a chatbot       →  Reusable commands
2. No context each session       →  /project:prime
3. No planning loops             →  /project:create-plan
                                    + /project:implement
4. No external data              →  Scripts that pull
                                    real-time data
```

1. **Chatbot mode.** You chat back and forth, waste tokens, get diluted output. Fix: create reusable command files (instructions) that you run every time.
2. **No context.** Every session starts from zero. Fix: run `/project:prime` every time. Loads your full context in seconds.
3. **No planning.** You try to do everything in one message. Fix: use `/project:create-plan` to design the workflow, then `/project:implement` to execute it.
4. **No real data.** The AI is guessing instead of using your actual numbers. Fix: scripts that pull real-time data from APIs.

---
---

# LESSON 2: Install and Run Your First Demo
**Video length:** 15-20 min | **Format:** Full screen share, every click shown

## Copy this into the Skool lesson description:

> In this lesson, you'll install everything, clone the template, and run a live demo that fetches real AI news and turns it into LinkedIn posts, tweets, and a newsletter automatically. By the end of this video, you'll have a working AI employee on your machine.

---

### Install the Tools

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

4. **Verify prerequisites**
   ```
   node --version    → need v18 or higher
   python3 --version → need 3.x
   ```

### Clone the Template

```bash
git clone https://github.com/systemstoscale/AI-Employee.git
```

Then: File → Open Folder → select the cloned folder.

Quick tour of each folder:
- context/ → your info goes here
- instructions/ → your task guides
- scripts/ → code that pulls external data
- outputs/ → where finished work lands
- CLAUDE.md → the AI reads this every session

### Get Your Free API Key

1. Go to newsapi.org/register
2. Sign up (name, email, password, 30 seconds)
3. Copy the API key
4. In VS Code: open `.env`
5. Paste after `NEWS_API_KEY=`
6. Cmd+S to save

This is a free API that gives us real news data. 100 requests per day. We're using it to show you the full pipeline.

### Set Up Your Shortcut Aliases

There are TWO places you type things. The regular terminal, where you run normal commands. And inside Claude Code, where you chat with the AI. Right now we're going to set up shortcuts so you can start Claude Code with just 2 letters.

Paste this into the terminal:

```bash
echo '
# AI Employee aliases
alias cs="cd ~/AI-Employee && claude"
alias cr="cd ~/AI-Employee && claude --dangerously-skip-permissions -p /project:prime"' >> ~/.zshrc
```

Then close and reopen the terminal (or `source ~/.zshrc`).

```
cs = Claude Safe
     Starts Claude Code. You type /project:prime manually.
     Good for learning.

cr = Claude Risky (YOLO mode)
     Starts Claude Code with all permissions + auto-primes.
     No permission popups, reads your context automatically.
     This is what you'll use 90% of the time.
```

Type `cr` → it starts and auto-primes. From now on, every time you want your AI employee, you open a terminal and type `cr`. Two letters. That's it.

### Run the Live Demo

1. In the regular terminal (NOT inside Claude Code):
   ```bash
   python3 scripts/fetch-news.py
   ```
2. Open `outputs/latest-news.md`. 10 real AI articles.

3. Type `cr` to start Claude Code. It auto-primes.

4. Type:
   ```
   Follow the news-to-content instruction using the news you just fetched.
   ```

5. Claude will:
   - Read the news articles
   - Pick the 3 best stories
   - Write 3 LinkedIn posts with hooks
   - Write 6 tweets (2 per story)
   - Write a newsletter snippet
   - Save everything to outputs/

6. Open the output file.

7. Bonus, try other topics:
   ```bash
   python3 scripts/fetch-news.py "startup funding"
   python3 scripts/fetch-news.py "remote work"
   ```

---
---

# LESSON 3: Teach It Who You Are
**Video length:** 10-15 min | **Format:** Screen share, running the setup command live

## Copy this into the Skool lesson description:

> You wouldn't hire an employee without onboarding them. In this lesson, you run one command that interviews you about your business, role, goals, and metrics, then automatically fills in all your context files. By the end, your AI employee knows exactly who you are.

---

### The One Command

1. Start Claude Code (type `cr` or `claude`)

2. Type:
   ```
   /project:setup
   ```

3. Claude asks you questions in 4 rounds:

```
┌────────────────────────────────────────────────────────┐
│                    /project:setup                       │
│                                                        │
│  Round 1: Your Business    →  writes business.md       │
│  ┌──────────────────────────────────────────────┐      │
│  │ Company name? What do you do?                │      │
│  │ Products/services? Who do you serve?          │      │
│  │ Tech stack? Key links?                        │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  Round 2: You              →  writes personal.md       │
│  ┌──────────────────────────────────────────────┐      │
│  │ Name? Role? Coding experience?                │      │
│  │ Communication style? Pet peeves?              │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  Round 3: Your Strategy    →  writes strategy.md       │
│  ┌──────────────────────────────────────────────┐      │
│  │ Top priority? Goals? Active projects?         │      │
│  │ Metrics? What's NOT a priority?               │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  Round 4: Your Data        →  writes data.md           │
│  ┌──────────────────────────────────────────────┐      │
│  │ Current metrics? Data sources?                │      │
│  │ (Optional, can skip)                          │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  Done → auto-primes → ready to work                    │
└────────────────────────────────────────────────────────┘
```

4. Answer each round naturally. Just talk/type like you're explaining your business to a new hire.

5. Claude writes each file immediately after you answer.

6. At the end, Claude gives you a summary and says "Your AI employee is set up and ready."

If you'd rather fill in the files yourself, check `context/_examples.md`. There are three filled-in examples you can use as a guide. A content agency, a student, and a consulting firm.

---
---

# LESSON 4: Build Your First Automated Workflow
**Video length:** 15-20 min | **Format:** Screen share, building a real instruction live

## Copy this into the Skool lesson description:

> Instructions are reusable task guides your AI follows every time, like SOPs for your digital employee. In this lesson, you'll learn the create-plan, implement loop and build your first custom workflow from scratch. This is where the real power is.

---

### How Instructions Work

An instruction is just a text file with:
- A goal (what it accomplishes)
- Inputs (what info it needs)
- Steps (what to do, in order)
- Output format (where to save, how to structure)

```
┌────────────────────────────────────────────────────┐
│  instructions/_example-news-to-content.md          │
│                                                    │
│  Goal:    Turn news into social content            │
│  Inputs:  topic, platforms                         │
│  Steps:                                            │
│    1. Run fetch-news.py                            │
│    2. Pick 3 best stories                          │
│    3. Write LinkedIn posts                         │
│    4. Write tweets                                 │
│    5. Write newsletter snippet                     │
│  Output:  outputs/news-content-[date].md           │
└────────────────────────────────────────────────────┘
```

Why this beats chatting:
- **Consistent.** Same quality every time
- **Fast.** No re-explaining
- **Reusable.** Run it daily, weekly, whenever

The template includes 7 example instructions.

### The Planning Loop

```
┌───────────────┐     ┌────────────────┐     ┌───────────────┐
│  YOU          │     │  CREATE PLAN   │     │  IMPLEMENT    │
│               │     │                │     │               │
│ "I want to   │────→│  Claude reads  │────→│  Claude       │
│  automate    │     │  workspace,    │     │  executes     │
│  my weekly   │     │  designs the   │     │  every step,  │
│  report"     │     │  full plan     │     │  creates      │
│               │     │                │     │  files,       │
│               │     │  Saves to      │     │  self-        │
│               │     │  instructions/ │     │  corrects     │
└───────────────┘     └────────────────┘     └───────────────┘
                                                    │
                                                    ▼
                                         ┌───────────────────┐
                                         │  ERROR?           │
                                         │  Read → Fix →     │
                                         │  Retest → Update  │
                                         │  instruction      │
                                         └───────────────────┘
```

1. Type: `/project:create-plan I want to automate writing a weekly LinkedIn recap of what I worked on`
2. Claude reads the workspace, analyzes what exists, writes a detailed plan
3. Type: `/project:implement`
4. Claude creates the instruction file, updates CLAUDE.md, tests it

### Build Your First Custom Instruction Live

Pick a real task. Suggestions:
- "Automate my weekly email newsletter from rough notes"
- "Create a competitor analysis report from a company name"
- "Turn a meeting transcript into action items and follow-ups"

### What's Possible: Real Examples from Skalers

At Skalers.io, we build AI systems for 7-9 figure companies. The same model applies at any scale:

```
WHAT WE AUTOMATE AT SKALERS          YOUR VERSION
────────────────────────────────────────────────────────
AI Knowledge Base                  →  context/ files
  (company data → instant             that give your
  answers for any employee)            AI full context

AI Client Acquisition              →  instructions/
  (autonomous outbound that            that automate
  books calls 24/7)                    your outreach

AI Client Fulfillment              →  scripts/ that
  (onboarding, reporting,              pull data + do
  QA, client comms)                    the actual work
```

The difference between a $5K task automation and a $50K+ role automation is scope, but the building blocks are the same. Context. Instructions. Scripts. Outputs.

You're learning the foundation that scales from personal productivity to enterprise systems.

---
---

# LESSON 5: Connect Any API in Minutes
**Video length:** 10-15 min | **Format:** Screen share, building a new script live

## Copy this into the Skool lesson description:

> Scripts are how your AI employee connects to the outside world, pulling real-time data from APIs, scraping websites, fetching analytics. You don't write the code. Claude does. In this lesson, you'll add a new data source to your workspace.

---

### What Scripts Do

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│  EXTERNAL      │    │  SCRIPT        │    │  YOUR          │
│  DATA          │    │                │    │  WORKSPACE     │
│                │    │ fetch-news.py  │    │                │
│  NewsAPI ──────│───→│ pulls data,    │───→│  outputs/      │
│  YouTube       │    │ formats it,    │    │  latest-       │
│  CRM           │    │ saves to       │    │  news.md       │
│  Analytics     │    │ outputs/       │    │                │
│  Any API       │    │                │    │  Claude        │
│                │    │                │    │  reads this    │
└────────────────┘    └────────────────┘    └────────────────┘
```

Pattern: Script fetches → saves to outputs/ → instruction processes it.

You don't write the code. You tell Claude what data you want. It figures out how to get it.

### Add a New Script Live

1. Type: `/project:create-plan I want a script that fetches the top 10 Hacker News posts and saves them to outputs/`

2. Claude will:
   - Research the Hacker News API
   - Design the script
   - Write the plan

3. Type: `/project:implement`

4. Claude will:
   - Write the script
   - Save it to scripts/
   - Test it
   - If it fails → read error → fix → retest

5. Run the script manually: `python3 scripts/fetch-hackernews.py`

### Free APIs You Can Connect

```
API                  WHAT IT DOES                     COST
──────────────────────────────────────────────────────────────
NewsAPI              Latest news on any topic         Free (100/day)
Serper               Google search results            Free (2,500 credits)
Apify                Web scraping (YouTube, etc.)     Free tier
OpenWeatherMap       Weather data                     Free (1,000/day)
Hacker News          Top tech posts                   Free (unlimited)
Reddit JSON          Subreddit posts                  Free (no key needed)
──────────────────────────────────────────────────────────────
Any API:  Add key to .env → tell Claude what you want
          → it builds the script for you
```

At Skalers, we use Apify to scrape competitor data, LinkedIn profiles, and YouTube channels, then feed that into AI systems that generate reports and outreach. Same pattern, bigger scale. The building block is always: script pulls data → AI processes it.

---
---

# LESSON 6: Steal These 6 Workflows
**Video length:** 15-20 min | **Format:** Screen share, running each workflow end to end

## Copy this into the Skool lesson description:

> Watch 3 complete workflows run from start to finish. Content creation, business operations, and research. Each one shows the full pipeline: data in, AI processing, formatted output. Pick the one closest to your role and start using it today.

---

### Workflow 1: Content Creator

Content marketing agency example from `_examples.md`

```
INPUT                      INSTRUCTION                    OUTPUT
──────────────────────────────────────────────────────────────────────
"AI trends"           →    news-to-content           →    3 LinkedIn posts
                                                          6 tweets
                                                          1 newsletter snippet

"How to build a       →    write-blog-post           →    1,500-word SEO blog
 content calendar"                                        with metadata

blog post file        →    repurpose-content         →    3 LinkedIn posts
                                                          5 tweets
                                                          1 newsletter snippet
                                                          1 thread
```

This whole pipeline, news to content to repurposed social, takes about 5 minutes. Doing it manually takes 3+ hours.

### Workflow 2: Business Operations

Consulting firm ops manager example

```
INPUT                      INSTRUCTION                    OUTPUT
──────────────────────────────────────────────────────────────────────
Rough weekly notes    →    weekly-report              →    Formatted status report
                                                           with highlights, metrics,
                                                           priorities

Competitor name       →    competitor-analysis        →    Full competitor profile
                                                           with comparison table
                                                           and opportunities
```

This is exactly what our AI Fulfillment systems do at scale. Automated reporting, client status updates, competitive intelligence. We charge $60-120K to build these for enterprise clients. You're learning the same patterns for free.

### Workflow 3: Student / Researcher

CS student example

```
INPUT                      INSTRUCTION                    OUTPUT
──────────────────────────────────────────────────────────────────────
Research topic        →    research-paper             →    Annotated bibliography
                                                           Paper outline
                                                           Full draft
                                                           References

Course topic          →    study-guide                →    Key concepts
                                                           Practice questions
                                                           Exam topics
                                                           Answers
```

### Build Your Own

```
ANY REPEATING TASK YOU DO:

1. Identify it       →  "I write a weekly report every Monday"
2. /create-plan      →  Claude designs the workflow
3. /implement        →  Claude builds the instruction
4. Test it           →  Run the instruction, check the output
5. Iterate           →  Refine steps, add edge cases
6. Reuse forever     →  Same quality, every time, in minutes
```

Pick ONE task you do every week. Automate it before moving on to the next lesson.

---
---

# LESSON 7: 10x Your Speed
**Video length:** 10-15 min | **Format:** Screen share with tips and demos

## Copy this into the Skool lesson description:

> You've got the foundation. Now make it fast. In this lesson: YOLO mode for speed, running multiple AI instances in parallel, installing skills/plugins, and the path from personal productivity to building AI systems as a service.

---

### YOLO Mode for Speed

```
SAFE MODE (cs)                     YOLO MODE (cr)
──────────────────────────────────────────────────────
Claude asks permission             Claude just does it
for every action
                                   + auto-primes
Good for learning                  (reads your context
                                    automatically)

"Can I write to this file?"        Just writes it

Slower but safer                   Fast. Use this 90%
                                   of the time.
```

### Multiple Instances

- Cmd+\ → new terminal pane
- Type `cr` in each → two Claude instances side by side

Use cases:
- Plan in one terminal, implement in another
- Run a long task in one, start something else in the other
- Research in one, write in the other

### Claude Skills / Plugins

Skills are installable packages that add capabilities to your workspace.

Where to find them: github.com/anthropics/skills

Example: PowerPoint skill → turns any markdown report into a .pptx presentation.

### The Self-Correction Loop

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  ERROR     │───→│  READ     │───→│  FIX      │───→│  UPDATE   │
│  happens   │    │  error    │    │  code     │    │  instruc- │
│            │    │  message  │    │  and      │    │  tion     │
│            │    │           │    │  retest   │    │  with     │
│            │    │           │    │           │    │  lesson   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
                                                        │
                                                        ▼
                                              SYSTEM IS SMARTER
                                              Same mistake never
                                              happens twice
```

Over time, your instruction files accumulate lessons learned. The workspace compounds.

### From Personal Productivity to Building AI Systems

Everything you just learned is the foundation of what we build at Skalers for enterprise clients:

```
YOUR WORKSPACE                       ENTERPRISE AI SYSTEM
──────────────────────────────────────────────────────────────
context/                          →  AI Knowledge Base
  (your business info)                (company-wide RAG database)
                                      Value: $25-40K setup

instructions/                     →  AI Acquisition System
  (your task guides)                  (autonomous outbound SDR)
                                      Value: $45-80K setup

scripts/                          →  AI Fulfillment System
  (your data connectors)              (delivery + operations AI)
                                      Value: $75-120K setup
```

The patterns are identical. The scale is different.

If you want to go deeper:
- Join the free Skalers community at skalers.io
- Learn the IDEA Framework (Instructions → Decisions → Executions → AI)
- Build these systems for clients at $20-100K per project

---
---

# SKOOL SETUP CHECKLIST

## Community Settings
- **Name:** AI Employee
- **Price:** $97
- **Access:** Classroom + Community

## Classroom Structure

| # | Lesson Title | Video Length |
|---|-------------|-------------|
| 1 | Why Your AI Sucks (And How to Fix It) | 10-15 min |
| 2 | Install and Run Your First Demo | 15-20 min |
| 3 | Teach It Who You Are | 10-15 min |
| 4 | Build Your First Automated Workflow | 15-20 min |
| 5 | Connect Any API in Minutes | 10-15 min |
| 6 | Steal These 6 Workflows | 15-20 min |
| 7 | 10x Your Speed | 10-15 min |

## Pinned Post (Copy-Paste)

```
START HERE

1. Watch Lesson 1 (10 min). Understand the model.
2. Watch Lesson 2 (15 min). Get set up + run the live demo.
3. Watch Lesson 3 (10 min). Onboard your AI with /project:setup.
4. Watch Lessons 4-7 at your own pace.

Template repo: github.com/systemstoscale/AI-Employee

Free API key: newsapi.org/register

Stuck? Post in the community. We're here to help.
```

## Community Channels

1. **General.** Main discussion
2. **Share Your Workflows.** Members post their custom instructions
3. **Troubleshooting.** Help with setup and errors
4. **Wins.** Show what your AI employee produced

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
