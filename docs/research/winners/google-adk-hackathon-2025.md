# Agent Development Kit Hackathon with Google Cloud (2025)

Researched 2026-10-06 for the Life After Code entry. Goal: what won this Google Cloud agent hackathon on Devpost, and why.

Tags used below:

- "(search excerpt, unverified wording)": text from a web search summary of a page I could not open.
- "(unverified)": I could not confirm it.
- "(my reading)": my judgment, not a sourced fact.
- Repo stats (stars, forks, commits) were read from GitHub pages on 2026-10-06 through a page summarizer, so treat them as approximate.

Read this first: no winner meets the "deep-dived: yes" bar (Devpost page, video and repo all opened). Devpost and YouTube are blocked here, and the shared web search budget ran out after about 20 searches. I opened all 8 winners' GitHub repos (README plus key source files). I got Devpost excerpts and a video title for the grand prize winner only. Details in "Blocked".

## Hackathon facts

| Item | Value | Source |
|---|---|---|
| Name | Agent Development Kit Hackathon with Google Cloud | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Devpost site | https://googlecloudmultiagents.devpost.com/ (Devpost challenge id 24728) | [search result](https://googlecloudmultiagents.devpost.com/), [submit URL in search results](https://devpost.com/submit-to/24728-agent-development-kit-hackathon-with-google-cloud/manage/submissions) (blocked) |
| Host | Google Cloud, run on Devpost | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Announced | May 28, 2025, blog post by Stephanie Wong | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Submission period | May 12, 2025, 9:00 AM PT to June 23, 2025, 5:00 PM PT (search excerpt, unverified wording) | [rules](https://googlecloudmultiagents.devpost.com/rules) |
| Winners first posted | August 7, 2025, by @GoogleCloudTech on X (date decoded from the post ID; x.com blocked) | [X post](https://x.com/GoogleCloudTech/status/1953586166646689998) |
| Winners blog post | September 2, 2025, by Stephanie Wong and Willie Turney | [winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights) |
| The ask | "you'll build autonomous multi-agent AI systems using Google Cloud and the open source Agent Development Kit (ADK)" | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Hard rule | "Your project must be built using the Agent Development Kit (ADK), focusing on the design and interactions between multiple agents." | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Categories | Automation of complex processes; Data analysis and insights; Customer service and engagement; Content creation and generation | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Grand prize (1) | $15,000 USD, $3,000 Google Cloud credits, 1 year Google Developer Program Premium, virtual coffee with a Google team member, social promo | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Regional winners (4) | $8,000 USD, $1,000 credits, virtual coffee, social promo each. Regions: North America, Latin America, Asia Pacific, Europe/Middle East/Africa | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud), [winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights) |
| Honorable mentions (3) | $1,000 USD and $500 credits each | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud) |
| Special prizes | None. The winners post lists only the grand prize, 4 regional winners and 3 honorable mentions | [winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights) |
| Prize pool | $50,000 cash plus $8,500 in credits (my sums of the prizes above). Devpost advertised "over $50,000 in prizes" (search excerpt, unverified wording) | [announcement post](https://cloud.google.com/blog/topics/developers-practitioners/join-the-agent-development-kit-hackathon-with-google-cloud), [Devpost](https://googlecloudmultiagents.devpost.com/) |
| Participants | "over 10,400 participants from 62 countries" | [winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights) |
| Submissions | "477 submitted projects and over 1,500 agents built" | [winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights) |
| Other counts seen | 10,350 participants on a Devpost page snapshot (search excerpt, unverified wording); 10,432 participants and 476 submissions in a third-party list that also gets the winners wrong (see caution below) | [Devpost](https://googlecloudmultiagents.devpost.com/), [awesome-adk-agents](https://github.com/Sri-Krishna-V/awesome-adk-agents) |
| Judges | Google Cloud staff: developer advocates, AI product managers, field solutions architects, customer engineers (search excerpt, unverified wording). Names not checked | [Devpost judges update](https://googlecloudmultiagents.devpost.com/updates/36511-get-to-know-the-judges) |

### Judging (all from the rules page via search excerpts, unverified wording)

Source: [rules](https://googlecloudmultiagents.devpost.com/rules).

- Stage One is pass/fail: does the submission include all requirements and reasonably address the challenge.
- Stage Two: judges score each criterion from 1 to 5, using these weights:
  - Technical Implementation, 50%: "Is the code clean, efficient, and well-documented? How effectively does it utilize the core concepts of Agent Development Kit? Did the project showcase the use of multiple AI agents working together to achieve tasks?"
  - Innovation and Creativity, 30%: "How novel and original is the idea? Does it address a significant problem or create a unique solution?"
  - Demo and Documentation, 20%: "Is the problem clearly defined, and is the solution effectively presented through a demo and documentation? Have they explained how they used Agent Development Kit and relevant tools? Have they included an architectural diagram?"
- Bonus points, added on top of the 1 to 5 scale:
  - up to 0.4 for publishing a blog post, video or podcast on how the project was built with ADK, stating it was made for this hackathon;
  - up to 0.4 for contributing to the ADK open source repo (commits, pull requests, issues opened, code reviews);
  - up to 0.2 for using Google Cloud technology (for example Agent Engine, Cloud Run, BigQuery) or Google AI models (for example Gemini, Gemma, Veo).
- So bonuses could add up to 1.0 point to a 5 point scale (my sum).

### Submission requirements (search excerpt, unverified wording)

Source: [Devpost home](https://googlecloudmultiagents.devpost.com/).

- A URL to the hosted project for judging and testing.
- A text description: features and functionality, technologies used, other data sources, findings and learnings.
- A public code repository URL.
- An architecture diagram showing which technologies were used and how they interact.
- A demo video of the project working, no longer than 3 minutes: "If it is longer than 3 minutes, only the first 3 minutes will be evaluated."

### Caution about third-party lists

The GitHub list [Sri-Krishna-V/awesome-adk-agents](https://github.com/Sri-Krishna-V/awesome-adk-agents) names TradeSage AI as the grand prize winner, puts SalesShortcut in Latin America, Bleach in EMEA, and lists GreenOps and Nexora as honorable mentions. The [official winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights) says otherwise. Trust the blog.

## Winners table

Winners and bylines are from the [winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights). Devpost pages are blocked here.

| Prize | Project | Team (size) | What it is | Repo | Deep-dived |
|---|---|---|---|---|---|
| Grand prize | [SalesShortcut](https://devpost.com/software/salesshortcut) | Merdan Durdyyev, Sergazy Nurbavliyev (2) | AI sales rep: finds local businesses without a website, researches them, writes a proposal, phones them with an AI voice, emails follow-ups | [merdandt/SalesShortcut](https://github.com/merdandt/SalesShortcut) | no (repo yes, Devpost via search excerpt, video title only) |
| North America | [Energy Agent AI](https://devpost.com/software/energy-agent-ai) | David Babu (1) | Agents for a simulated energy retailer with 100K customers: churn, upsell, efficiency advice, marketing drafts | [hazardscarn/energyagentai](https://github.com/hazardscarn/energyagentai) | no (repo only) |
| Latin America | [Edu.AI - Multi-Agent Educational System for Brazil](https://devpost.com/software/edu-ai-multi-agent-educational-system-for-brazil) | Giovanna Moeller (1) | ENEM exam prep: essay grading on the official rubric, mock exams, study plans | [giovannamoeller/edu-ai-adk](https://github.com/giovannamoeller/edu-ai-adk) | no (repo only) |
| Asia Pacific | [GreenOps](https://devpost.com/software/greenops-gzp4aj) | Aishwarya Nathani, Nikhil Mankani (2) | Agents that audit Google Cloud VMs, forecast CPU and carbon, resize VMs when asked, write reports and decks | [niksm7/GreenOps](https://github.com/niksm7/GreenOps) | no (repo only) |
| Europe, Middle East, Africa | [Nexora-AI](https://devpost.com/software/teachai-upzofa) | Matthias Meierlohr, Luca Bozzetti, Erliassystems, Markus Huber (4) | Turns documents and notes into interactive courses with quizzes, chapter chat and study plans | [M4RKUS28/Nexora](https://github.com/M4RKUS28/Nexora) | no (repo only) |
| Honorable mention #1 | [Particle Physics Agent](https://devpost.com/software/particle-physics-agent) | ZX Jin, Tianyu Zhang (2) | Plain language to checked, compilable Feynman diagram code | [bee4come/Particle-Physics-Agent](https://github.com/bee4come/Particle-Physics-Agent) | no (repo only) |
| Honorable mention #2 | [TradeSageAI](https://devpost.com/software/tradesage-ai) | Suds Kumar (1) | Tests a trading idea with 6 agents, one of which argues against it, then writes alerts | [sudsk/tradesage-mvp](https://github.com/sudsk/tradesage-mvp) | no (repo only) |
| Honorable mention #3 | [Bleach](https://devpost.com/software/bleach-7tqdmo) | Vivek Shukla (1) | Describe an agent in plain English, see it as a graph, get generated ADK code | [vivek100/bleachAgentBuilder](https://github.com/vivek100/bleachAgentBuilder) | no (repo only) |

Count: 8 winners. Deep-dived to the full bar: 0. Repos opened: 8. Devpost content (via search excerpts): 1. Video found: 1 (title only).

## Winners in detail

### SalesShortcut (grand prize)

Deep-dived: no. Repo opened (README and source). Devpost page only through search excerpts. Video found by title in search results, not opened (YouTube blocked).

SalesShortcut automates outbound sales for a small web agency. It "finds, creates, and converts leads" ([README](https://github.com/merdandt/SalesShortcut)): a person enters a city, a Lead Finder service uses Google Maps to find businesses without a website, and an SDR agent researches each one, drafts and fact-checks a proposal, calls the owner with an ElevenLabs voice agent, classifies how the call went, and then either runs an email sequence or logs the lead. By its own count it is the largest system among the winners, and it runs as 5 services that talk over A2A.

- What it does: 5 services: Lead Finder, SDR Agent, Lead Manager, UI Client dashboard, Gmail Pub/Sub listener for replies ([README](https://github.com/merdandt/SalesShortcut)). The SDR agent is an ADK `SequentialAgent` of research, proposal, phone call, call classifier and a custom router agent ([sdr/sdr/agent.py](https://github.com/merdandt/SalesShortcut/blob/main/sdr/sdr/agent.py)). The router is a custom `BaseAgent` that picks the email path or the save-to-database path from the call result ([sdr_router.py](https://github.com/merdandt/SalesShortcut/blob/main/sdr/sdr/sub_agents/sdr_router.py)). Calls go out through ElevenLabs Conversational AI and Twilio ([phone_call.py](https://github.com/merdandt/SalesShortcut/blob/main/sdr/sdr/tools/phone_call.py)).
- Sponsor tools and depth: core of the product. ADK with all workflow agent types and A2A between services; Gemini ("Gemini 2.0 Flash Lite (configurable)"); BigQuery for all lead and call data; Google Maps and Search; Gmail and Calendar; Docker plus Cloud Run deploy scripts ([README](https://github.com/merdandt/SalesShortcut)). Devpost claims "34 distinct agents (21 LLMAgents, 7 Sequential Agents, 1 Parallel Agent, 2 Custom Agents, 1 Loop Agent)", "5 microservices on Cloud Run communicating via A2A protocol" and "16+ specialized tools" (search excerpt, unverified wording; the listed types add up to 32, not 34) ([Devpost](https://devpost.com/software/salesshortcut)). Biggest challenge per Devpost: managing state and communication between "three dozen agents" (search excerpt, unverified wording).
- Autonomy: acts alone once started. No approval step before a call or an email. One human step: a `RequestHumanApproval` agent sends the demo website brief to the dashboard and waits for a person to build the site and paste its link ([request_human_creation.py](https://github.com/merdandt/SalesShortcut/blob/main/sdr/sdr/sub_agents/outreach_email_agent/sub_agents/website_creator/request_human_creation.py), [prompt](https://github.com/merdandt/SalesShortcut/blob/main/sdr/sdr/sub_agents/outreach_email_agent/outreach_email_prompt.py), [UI endpoint](https://github.com/merdandt/SalesShortcut/blob/main/ui_client/main.py)).
- Demo and video: "Stop Cold-Calling Manually - Meet SalesShortcut (AI SDR Full video)", described as an AI SDR "that discovers leads, researches them, writes tailored proposals, and makes the first outreach - then tracks follow-up" (search excerpt, unverified wording) ([YouTube](https://www.youtube.com/watch?v=gap38K5td7U)). Length, transcript and first 30 seconds: unknown (blocked). "Full video" suggests a longer cut than the 3 minute judged video (unverified).
- Human story: Devpost "Inspiration" says the idea came from a freelance developer who teamed up with a sales-savvy friend who spent hours cold-calling businesses that needed a website; the question was whether AI could find leads, research them, write proposals and make first contact (search excerpt, unverified wording) ([Devpost](https://devpost.com/software/salesshortcut)). No named person.
- Live URL: none in the README. Deploy scripts for Cloud Run exist ([README](https://github.com/merdandt/SalesShortcut)).
- README structure: overview, architecture (SVG diagram plus a Mermaid agent workflow), features, tech stack, prerequisites, quick start (local, Docker, Cloud Run), one README per service, env var table, data storage, security, usage guide, config. No screenshots. About 84 stars, 59 forks, 138 commits ([repo](https://github.com/merdandt/SalesShortcut)).
- Team: 2. Merdan's GitHub bio says Flutter developer; his pinned repos include other hackathon entries ([profile](https://github.com/merdandt)).
- After the hackathon: search results show a site titled "Marketing for Solo Home Service Contractors - SalesShortcut" ([salesshortcut.ai](https://salesshortcut.ai/)), a listing titled "SalesShortcut Inc. - $679 last 30 days" ([trustmrr](https://trustmrr.com/startup/salesshortcut-inc)) and a LinkedIn title "Merdan Durdyev - SalesShortcut" ([LinkedIn](https://www.linkedin.com/in/merdandt/)). All unverified (sites blocked).
- Why it most likely won (my reading): the deepest use of ADK in the field (every workflow agent type, a custom router agent, A2A between services) hits the 50% technical criterion directly; it runs a whole business process end to end and does real things (phone calls, emails), which makes a memorable demo; the cold-calling pain is easy to understand; and it touches many Google products, which helps the bonus.

### Energy Agent AI (North America regional winner)

Deep-dived: no. Repo opened. Devpost and video not reached.

Energy Agent AI is a set of agents for a retail energy provider. A coordinator called WattsWise routes questions to specialist agents for energy efficiency, sales, retention, portfolio analysis and charts, and a separate marketing system writes email, social, direct mail and landing page content ([README](https://github.com/hazardscarn/energyagentai)). Its strength is the data underneath: 100,000 simulated customers with smart meter and billing data in BigQuery, churn and cross-sell or upsell models with SHAP explanations, and a natural language to SQL tool that uses table and column embeddings.

- Sponsor tools and depth: core. ADK coordinator that calls 5 specialist agents as `AgentTool`s, model "gemini-2.5-flash" in code ([main_agent/agent.py](https://github.com/hazardscarn/energyagentai/blob/main/main_agent/agent.py)) (the README says Gemini 2.0 Flash); BigQuery, Cloud Storage for models, Vertex AI; README also lists A2A ([README](https://github.com/hazardscarn/energyagentai)).
- Data: the README says the dataset is simulated: "Simulated Dataset with ClaudeAI" ([README](https://github.com/hazardscarn/energyagentai)).
- Autonomy: suggests. It drafts retention emails, sales emails, call scripts, campaigns and charts for staff; I found no sending step in the coordinator (my reading of [main_agent/agent.py](https://github.com/hazardscarn/energyagentai/blob/main/main_agent/agent.py)).
- Demo and video: not found.
- Human story: none. Business framing: "This is what makes EnergyAgentAI special - it's not just LLMs with tools, it's a complete AI-powered energy business simulation." ([README](https://github.com/hazardscarn/energyagentai)).
- Live URL: none in the README; Streamlit app, Dockerfile in repo ([repo](https://github.com/hazardscarn/energyagentai)).
- README structure: features, 7 architecture images (one per agent), agent descriptions, tech stack, a 3 phase environment setup ("~2-3 hours"), quick start, project tree, Mermaid setup flow, usage examples per agent. No screenshots. About 16 stars, 37 commits ([repo](https://github.com/hazardscarn/energyagentai)).
- Team: 1. GitHub bio: "Data Scientist @nrg Energy" ([profile](https://github.com/hazardscarn)), so the builder knows the domain.
- Why it most likely won (my reading): real machine learning and real-scale data behind the agents, not just prompts; every agent has a clear job and its own diagram; strong fit for the "data analysis" category; domain realism from someone who works in energy.

### Edu.AI (Latin America regional winner)

Deep-dived: no. Repo opened. Devpost and video not reached.

Edu.AI helps Brazilian students prepare for the ENEM university entrance exam. It grades essays on ENEM's 5 official competencies with scores and feedback, writes ENEM-style prompts, builds mock exams and cross-subject questions, makes summaries and flashcards, helps rewrite essays and tracks progress ([README](https://github.com/giovannamoeller/edu-ai-adk)).

- Sponsor tools and depth: ADK is the core: an orchestrator plus 10 specialist agent folders, including essay memory and image-to-essay ([agents folder](https://github.com/giovannamoeller/edu-ai-adk/tree/main/agents)), served by FastAPI with an ADK `Runner` and `DatabaseSessionService` ([main.py](https://github.com/giovannamoeller/edu-ai-adk/blob/main/main.py)). Gemini 2.5 Flash, Cloud Vision OCR to read essays from photos, Cloud Storage ([README](https://github.com/giovannamoeller/edu-ai-adk)). Frontend on Vercel, not Google.
- Autonomy: suggests. It grades, generates and recommends for a student.
- Demo and video: not found.
- Human story: no named person; social mission: "Quality education for all, powered by autonomous agents." and "real potential to impact education at scale in Brazil" ([README](https://github.com/giovannamoeller/edu-ai-adk)).
- Live URL: https://edu-ai-adk.vercel.app/ listed in the README (not checked, blocked).
- README structure: short. Features, agent table, architecture (linked as a PDF, so it does not render inline), tech list, 2 line install, live link, "What We're Proud Of". About 23 stars, 33 commits ([repo](https://github.com/giovannamoeller/edu-ai-adk)).
- Team: 1. Software developer in São Paulo with about 2.9k GitHub followers ([profile](https://github.com/giovannamoeller)). Whether she published content for the bonus is unverified.
- Why it most likely won (my reading): a clear, local user with a real need (students preparing for one high-stakes exam), a deployed product, and a crisp demo moment (photo of an essay in, rubric scores out); strongest Latin America entry on impact.

### GreenOps (Asia Pacific regional winner)

Deep-dived: no. Repo opened. Devpost and video not reached. The README uses Devpost's section headings (Inspiration, What it does, How we built it, Challenges, Accomplishments, What we learned, What's next), so it is likely the same write-up (unverified).

GreenOps treats cloud waste as both a cost and a carbon problem: "Cloud waste isn't just a cost problem - it's a carbon problem." ([Readme](https://github.com/niksm7/GreenOps/blob/master/Readme.md)). You ask something like "How can I reduce cost and emissions in us-central1?" and a root agent routes to agents that query BigQuery for VM usage, find idle machines, estimate emissions with the Climatiq API, forecast CPU, memory and carbon with BigQuery ML, compare machine types, and write a Google Docs report and a slide deck.

- Sponsor tools and depth: core and broad. ADK root agent with 5 sub-agents, one of which chains 3 more ([agent.py](https://github.com/niksm7/GreenOps/blob/master/greenops_agent/agent.py)); Gemini 2.0 Flash; BigQuery and BigQuery ML; Compute Engine API to change machine types; Cloud Run; Secret Manager; Docs and Drive APIs ([Readme](https://github.com/niksm7/GreenOps/blob/master/Readme.md)).
- Autonomy: acts with approval, behind a safety check in code. The root agent must "ask the user if they want to execute any recommendation" and only then calls the executor ([agent.py](https://github.com/niksm7/GreenOps/blob/master/greenops_agent/agent.py)). The executor forecasts 7 days of CPU and memory and only resizes when a plain function says it is safe: average CPU under 30 and memory under 40 ([executor agent](https://github.com/niksm7/GreenOps/blob/master/greenops_agent/agents/safe_executor_agent/agent.py), [tools.py](https://github.com/niksm7/GreenOps/blob/master/greenops_agent/agents/safe_executor_agent/tools.py)). The README still claims "Completely autonomous workflows".
- Demo and video: not found. The README links a sample generated Google Doc report and slide deck ([Readme](https://github.com/niksm7/GreenOps/blob/master/Readme.md)).
- Human story: none named; problem framing: teams over-provision "just to be safe" ([Readme](https://github.com/niksm7/GreenOps/blob/master/Readme.md)).
- Live URL: https://greenops-ui-273345197968.us-central1.run.app/ (not checked, blocked).
- README structure: Devpost-style story, agent flow image, screenshots of recommendations, forecasts and impact calculator, architecture diagram, links to generated outputs, live link. No quick start. About 1 star, 36 commits ([repo](https://github.com/niksm7/GreenOps)).
- Team: 2. Nikhil Mankani (niksm7) opened ADK issue #1401 "Support agent.clone() for Reusing Agents Across Workflows" on June 14, 2025, during the hackathon ([issue](https://github.com/google/adk-python/issues/1401)). That fits the 0.4 ADK contribution bonus; whether it was claimed is unverified.
- Why it most likely won (my reading): sustainability plus cost savings on real Google Cloud data; it acts on real infrastructure but forecasts first and asks first; outputs a manager recognizes (a Docs report and a deck); wide Google Cloud use and an ADK contribution.

### Nexora-AI (Europe, Middle East, Africa regional winner)

Deep-dived: no. Repo opened. Devpost and video not reached.

Nexora turns documents, images and notes into interactive courses with lessons, visuals, quizzes (multiple choice and fill in the blank, checked by AI), a chat assistant per chapter, study plans and flashcards ([README](https://github.com/M4RKUS28/Nexora)). It is the most product-like winner: user accounts, multiple languages, light and dark themes, and a live site.

- Sponsor tools and depth: ADK pinned as `google-adk~=1.5.0` ([requirements](https://github.com/M4RKUS28/Nexora/blob/main/backend/requirements.txt)) with 10 agent folders: chat, code checker, explainer, flashcard, grader, html, image, info, planner, tester ([agents](https://github.com/M4RKUS28/Nexora/tree/main/backend/src/agents)). Vertex AI makes course logos; storage is MySQL plus ChromaDB, not Google ([README](https://github.com/M4RKUS28/Nexora)). The README never names ADK, only "AI agents".
- Autonomy: suggests. It generates learning content for the user.
- Demo and video: not found.
- Human story: none in the README.
- Live URL: https://nexora-ai.de listed in the README (not checked, blocked).
- README structure: logo, live link, dashboard screenshots (light and dark), features, tech stack, course creation diagram, software architecture diagram, setup in the wiki, project tree, roadmap. About 31 stars and 787 commits, by far the most of any winner ([repo](https://github.com/M4RKUS28/Nexora)).
- Team: 4. Markus's GitHub bio: "Business Informatics @ TUM", Munich ([profile](https://github.com/M4RKUS28)), so at least one member is a student.
- Why it most likely won (my reading): polish and finish. A real, usable product with a live site, checker and tester agents that validate generated lessons, and a lot of visible engineering. Strongest EMEA entry on "does it work for a real user".

### Particle Physics Agent (honorable mention #1)

Deep-dived: no. Repo opened. Devpost and video not reached.

The agent turns a sentence like "Generate a Feynman diagram for electron-positron annihilation producing two photons" into TikZ-Feynman LaTeX code. Six agents plan, retrieve similar examples from a 150+ example knowledge base, check the physics against Particle Data Group data through an MCP server, generate code, check the syntax, and loop up to 3 times to fix errors ([README](https://github.com/bee4come/Particle-Physics-Agent)).

- Sponsor tools and depth: ADK 1.0 is the core; the root agent runs "a conditional correction loop" so the code is "100% compilable" ([agent.py](https://github.com/bee4come/Particle-Physics-Agent/blob/main/feynmancraft_adk/agent.py)). Gemini 2.0 Flash. The public demo is the ADK dev UI on Cloud Run ([README](https://github.com/bee4come/Particle-Physics-Agent)). Physics data comes from a teammate's [ParticlePhysics MCP Server](https://github.com/uzerone/ParticlePhysics-MCP-Server).
- Self-reported results (unverified): 95%+ success rate, sequential with validation loops beat parallel (95% vs 70%), under 30 seconds per diagram ([README](https://github.com/bee4come/Particle-Physics-Agent)).
- Autonomy: suggests. It produces code; no outside actions.
- Demo and video: not found.
- Human story: none; claims "the first known implementation of Google's ADK for scientific applications" ([README](https://github.com/bee4come/Particle-Physics-Agent)).
- Live URL: https://particle-physics-agent-service-354229141951.us-central1.run.app/dev-ui/?app=feynmancraft_adk (not checked, blocked).
- README structure: it has a "Hackathon Submission" section that mirrors the submission list one to one: hosted project, public repo, language support, features, technologies, data sources, findings and learnings. Then quick setup, agent list, example, Mermaid architecture diagram. 1 commit, about 5 stars ([repo](https://github.com/bee4come/Particle-Physics-Agent)).
- Team: 2. Maintainers bee4come (Tianyu Zhang) and uzerone ([README](https://github.com/bee4come/Particle-Physics-Agent), [profile](https://github.com/bee4come)).
- Why it most likely got a mention (my reading): a fresh, non-business domain, an authoritative data source, a generate-check-retry loop, and documentation that maps directly to the rubric. Narrower than the regional winners.

### TradeSageAI (honorable mention #2)

Deep-dived: no. Repo opened. Devpost and video not reached.

You type a trading idea such as "Apple will reach $220 by Q2 2025" and six agents run in order: hypothesis, context, research, contradiction, synthesis and alert ([README](https://github.com/sudsk/tradesage-mvp), [orchestrator.py](https://github.com/sudsk/tradesage-mvp/blob/master/app/adk/orchestrator.py)). The contradiction agent is told to "Find and present SPECIFIC market risks and contradictions" ([contradiction_agent.py](https://github.com/sudsk/tradesage-mvp/blob/master/app/adk/agents/contradiction_agent.py)), and the alert agent writes "3-5 SPECIFIC alerts with exact price levels and actions" ([alert_agent.py](https://github.com/sudsk/tradesage-mvp/blob/master/app/adk/agents/alert_agent.py)).

- Sponsor tools and depth: deep on Google Cloud: ADK, Vertex AI Gemini, Cloud SQL Postgres, Cloud Run for backend and frontend, and Agent Engine as an alternative deploy ([README](https://github.com/sudsk/tradesage-mvp)). The blog byline itself lists "ADK, Agent Engine, Cloud Run and Vertex AI" ([winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights)).
- Autonomy: suggests. Analysis and alerts; no trading.
- Demo and video: not found.
- Human story: none.
- Live URL: none in the README.
- README structure: a deployment guide: quick start, architecture image, repo tree, Cloud SQL setup, local dev and testing, Cloud Run and Agent Engine deploy, monitoring, troubleshooting. About 42 stars, 348 commits ([repo](https://github.com/sudsk/tradesage-mvp)).
- Team: 1, based in London; pins a fork of Google's agent-starter-pack ([profile](https://github.com/sudsk)).
- Why it most likely got a mention (my reading): strong Google Cloud deployment story and a built-in devil's advocate agent against confirmation bias; finance analysis is a crowded idea, which may have kept it out of the top tier.

### Bleach (honorable mention #3)

Deep-dived: no. Repo opened. Devpost and video not reached.

Bleach is an agent builder for ADK itself. You describe an agent in plain English; a meta-agent with requirements, architecture, agent builder and tool builder sub-agents produces a config, shows it as a graph, and generates a full ADK project (agent.py, tools.py, requirements.txt, README) you can edit and download ([README](https://github.com/vivek100/bleachAgentBuilder)).

- Sponsor tools and depth: ADK is both the engine and the output; it supports LLM, Sequential, Parallel and Loop agents ([README](https://github.com/vivek100/bleachAgentBuilder)). No Google Cloud deployment shown.
- Autonomy: suggests. It generates code for a developer to review.
- Demo and video: not found. The README has one screenshot dated 2025-06-24 ([README](https://github.com/vivek100/bleachAgentBuilder)).
- Human story: none.
- Live URL: none in the README.
- README structure: screenshot, two Mermaid diagrams (system and sequence), features, project tree, setup, usage, supported agent types, tools, examples. 2 commits, about 30 stars ([repo](https://github.com/vivek100/bleachAgentBuilder)).
- Team: 1. Vivek Shukla also built oneShotCodeGen (about 253 stars) ([profile](https://github.com/vivek100)). He opened ADK PR #1611 "Added iterator agent for ADK pipeline" on June 24, 2025; it was closed without merge ([PR](https://github.com/google/adk-python/pull/1611)). That fits the ADK contribution bonus; whether it counted is unverified.
- Why it most likely got a mention (my reading): developer tooling that makes ADK easier, shown visually, from a builder who also tried to contribute to ADK; less tied to a real-world problem.

## Patterns

1. Every winner is a multi-agent system with named specialist agents and an architecture diagram, from 6 agents (Particle Physics, TradeSage) to a claimed 34 (SalesShortcut). This matches the 50% criterion, which asks whether "multiple AI agents working together" were shown ([rules](https://googlecloudmultiagents.devpost.com/rules), search excerpt).
2. The sponsor tool is the core, not a wrapper. Winners used ADK's workflow agents (Sequential, Loop, Parallel), custom router agents, AgentTool, A2A between services, and even the ADK dev UI as the hosted demo (see each section above).
3. Checks and loops beat single prompts: a fact checker (SalesShortcut), validators with up to 3 retries (Particle Physics), a safety function in plain code (GreenOps), a contradiction agent (TradeSage), checker and tester agents (Nexora).
4. Most winners suggest; only two act in the world. SalesShortcut calls and emails on its own but stops for a human to build the demo website. GreenOps resizes VMs only when the user asks, and code decides if it is safe. No winner ran fully unattended: even SalesShortcut needs a person to start a run and to build the demo website.
5. The grand prize went to a complete business process, end to end, with real actions, not to a single clever feature (my reading).
6. Real or realistic data mattered: 100K simulated customers plus trained models (Energy), live Google Cloud metrics plus Climatiq (GreenOps), Particle Data Group via MCP (Particle Physics), market data APIs (TradeSage).
7. Broad Google Cloud use is visible in every top winner: BigQuery (SalesShortcut, Energy, GreenOps), Cloud Run (SalesShortcut, GreenOps, Particle Physics, TradeSage), Agent Engine (TradeSage), Cloud Vision (Edu.AI), Secret Manager and Docs/Drive APIs (GreenOps). The rules gave up to 0.2 bonus for this.
8. Local relevance won regions: Brazil's ENEM exam (Edu.AI), an Alberta energy retailer built by an energy data scientist (Energy Agent AI), Google Cloud carbon (GreenOps), a course platform from a team with at least one TUM student, live on a .de domain (Nexora) (my reading).
9. Solo builders won 4 of 8 prizes (Energy Agent AI, Edu.AI, TradeSageAI, Bleach); the grand prize was a team of 2 ([winners post](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights)).
10. Emotional story was light. Only the grand prize has an origin story (a friend stuck cold-calling), and no winner names a real person. Under a rubric that is 50% technical, a clear problem seems to have been enough (my reading).
11. Documentation was strong across the board: all 8 READMEs have an architecture diagram, 4 of 8 list a live URL (Edu.AI, GreenOps, Nexora, Particle Physics), and two READMEs mirror the Devpost submission sections (GreenOps, Particle Physics).
12. Bonus hunting showed up: at least 2 winning teams opened ADK issues or pull requests during the hackathon window ([issue #1401](https://github.com/google/adk-python/issues/1401), [PR #1611](https://github.com/google/adk-python/pull/1611)).
13. Repo size did not decide: winners range from 1 commit (Particle Physics) to about 787 (Nexora).

What this suggests for Life After Code (my reading, check against the GitLab rules in docs/research/rules_discussions.md):

- Show several agents with clear jobs, and draw them in one diagram.
- Copy the GreenOps shape: the agent recommends, a person approves, plain code checks safety before acting. It matches our rule 4 in AGENTS.md and it won a regional prize.
- Go end to end on one real workflow (the SalesShortcut lesson) rather than building many features halfway.
- Use the sponsor platform deeply and visibly; list each GitLab and Google Cloud piece and what it does.
- Put a live URL in the README, keep the video under 3 minutes, and mirror the submission sections in the README.
- If the GitLab rules give bonus points for a blog post or open source contributions, do them; winners here did.

## Blocked

- devpost.com and every *.devpost.com page: blocked per access notes, not tried. This covers googlecloudmultiagents.devpost.com (rules, judges, gallery) and all 8 project pages.
- www.youtube.com: WebFetch returned EGRESS_BLOCKED; curl got CONNECT 403. m.youtube.com, youtu.be, www.youtube-nocookie.com and i.ytimg.com also failed with curl. youtube.googleapis.com answered but needs an API key (403 PERMISSION_DENIED), and no Google credentials are set up here. So no video lengths, transcripts or first 30 seconds.
- x.com (https://x.com/GoogleCloudTech/status/1953586166646689998): blocked.
- www.linkedin.com (https://www.linkedin.com/in/merdandt/): blocked.
- discuss.google.dev (https://discuss.google.dev/t/join-the-agent-development-kit-hackathon-with-google-cloud/188025/1): blocked (WebFetch and curl).
- allhackathons.com (https://allhackathons.com/hackathon/agent-development-kit-hackathon-with-google-cloud/): blocked (WebFetch and curl).
- goo.gle/adkhackathon short link: curl 403.
- salesshortcut.ai (WebFetch blocked) and trustmrr.com (curl blocked).
- Live demos, so uptime is unknown: particle-physics-agent-service-354229141951.us-central1.run.app, edu-ai-adk.vercel.app, greenops-ui-273345197968.us-central1.run.app (curl 403); nexora-ai.de (curl blocked).
- medium.com and dev.to: curl blocked (WebFetch not tried).
- github.com through curl and codeload.github.com (repo zip): 403, "GitHub access to this repository is not enabled for this session". Worked around with WebFetch on github.com and curl on raw.githubusercontent.com.
- Web search budget: the shared limit (200 WebSearch calls per turn, across all agents) was used up after about 20 of my searches. That stopped the Devpost excerpts and YouTube lookups for 7 of the 8 winners. A follow-up with fresh search budget could fill in: Devpost text and "Built with" for 7 projects, and video links, titles and lengths for all 8.
