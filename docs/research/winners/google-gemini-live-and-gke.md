# Google Cloud agent hackathons: Gemini Live Agent Challenge (2026) and GKE Turns 10 (2025)

Prepared for Alex Velazquez (solo, UC Berkeley CS) for "Life After Code", the GitLab Transcend Hackathon (Oct 2026; judges from GitLab, Google and Anthropic). Researched 2026-10-06.

**How this was researched.** I read the two official winners posts, the two announcement posts and the two "What's new in Google Cloud" logs on cloud.google.com. The winners posts link only to Devpost project pages, and devpost.com is blocked here, so neither post gives a GitHub or GitLab link. I found repositories by searching github.com and then checked each README against the post's description. For each repo found I read the README in full, listed the root and the agent and test folders, and read the agent code that decides when the agent acts. Live demo hosts and videos could not be opened (see "Blocked"). Anything I could not confirm is marked "(unverified)". "Why it most likely won" is my inference. The posts publish no scores.

**Short version**

- Deep-dived 14 of 20 winners (7 per event). Six winners have no repo I could find.
- Solo builders won most prizes: 8 of 12 Gemini Live winners and 6 of 8 GKE winners are credited to one person ([Gemini winners post][glac-win], [GKE winners post][gke-win]).
- The Gemini Live grand prize and two of the three category prizes went to agents that work in the physical world or on a real computer: a surgeon who cannot break scrub, a drone, a desktop you control by voice. These winners also make deep, named use of the Live API, ADK and Cloud Run.
- Many winners keep a human in control: VibeCat waits for permission, Moonwalk asks you to press "Proceed" on risky plans, JohnKeats.AI sends its learning changes to human review, and V-Commerce Studio has an admin approve or reject generated ads. Of the repos I read, only Vigil AI takes a high-stakes action that no human asked for (locking a bank account), and its README lists human approval as future work.
- No GKE Turns 10 winner built the announcement's "monitor microservices and auto-remediate" idea. Vigil AI (detect, investigate, act) is the closest.

---

## Event facts

### Gemini Live Agent Challenge (2026)

| Fact | Value | Source |
|---|---|---|
| Organizer and platform | Google Cloud; entries on Devpost (geminiliveagentchallenge.devpost.com) | [announcement][glac-join] |
| Submission window | February 16, 2026 to March 16, 2026: "Submissions are open from February 16, 2026 to March 16, 2026." | [What's new in Google Cloud, week Feb 23 - Feb 27][whatsnew-2026] |
| Announcement post | Mar 7, 2026, by Dilasha Panigrahi. "Submissions are open until March 16, 2026." | [announcement][glac-join] |
| Winners post | May 15, 2026, by Dilasha Panigrahi | [winners post][glac-win] |
| Prize pool | "a share of $80,000 in prizes" (announcement); "$80,000+ in prizes" (What's new) | [announcement][glac-join], [What's new][whatsnew-2026] |
| Prize tiers | Grand prize: trip to Google Cloud Next '26 ("tickets, a travel stipend, and a chance to present on stage"), $25,000, $3,000 in credits, virtual coffee, possible social feature. Category winners: trip to Next '26 (tickets), $10,000, $1,000 in credits. Subcategory winners: $5,000 and $500 in credits. Honorable mentions: $2,000 and $500 in credits | [announcement][glac-join] |
| Cash check | $25,000 + 3 x $10,000 + 3 x $5,000 + 5 x $2,000 = $80,000, which matches the 12 winners listed (my arithmetic) | [announcement][glac-join], [winners post][glac-win] |
| Participation | "11,878 participants and 1,536 submitted projects from 151 countries" | [winners post][glac-win] |
| Categories | The Live Agent, The Creative Storyteller, The UI Navigator. Three special awards in the winners post: "Best multimodal integration and user experience", "Best technical execution and agent architecture", "Best innovation and thought leadership" | [announcement][glac-join], [winners post][glac-win] |
| Hard requirements | "Your project must use a Gemini model (like Gemini 3 or Nano Banana) and the Gen AI SDK or Agent Development Kit (ADK). Lastly, you must use at least one Google Cloud service, such as Firestore, CloudSQL, Cloud Run, or Vertex AI." | [announcement][glac-join] |
| Mission | "Your mission is to build and deploy an AI agent on Google Cloud that utilizes multimodal inputs and outputs. We want you to go beyond the traditional text-in/text-out approach." | [announcement][glac-join] |
| Judging criteria | Not stated in the winners post or the announcement. The official rules live on Devpost, which is blocked here (unverified). The three special award names are the only scoring hints in the post. | [winners post][glac-win] |
| Submission package | A participant's notes (in Korean) list a main demo video of up to 4 minutes (required) and a 2 to 3 minute Google Cloud deployment proof video (optional, can be replaced by a code link), deadline 5:00 PM PDT on March 16 (unverified against the official rules) | [VibeCat challenge notes][vc-challenge] |
| In-person recognition | Category winners Jeremiah Somoine and Bryen Param gave Lightning Talks at Next '26 in Las Vegas and sat for interviews | [winners post][glac-win] |

**What the posts say the judges and organizers valued (quotes):**

- "We challenged developers worldwide to break out of the traditional 'text box' paradigm by building next-generation AI agents." ([winners post][glac-win])
- "The mission was to seamlessly integrate multimodal capabilities - building agents that help you see, hear, speak, and create in real time - using the Gemini Live API, the Agent Development Kit (ADK), and the robust infrastructure of Google Cloud." ([winners post][glac-win])
- "These winning teams combined technical precision with bold imagination, completely redefining how users can interact with and experience agents." ([winners post][glac-win])
- On drone-copilot: "his project was driven by the question of "what if a model could interact with the real world?", showcasing how multimodal capabilities can bridge the gap between AI and physical environments." ([winners post][glac-win])
- Jeremiah (Sankofa), "currently a college student": "the best response to a technical limitation was a creative one." and "The best way to learn is by doing." ([winners post][glac-win])
- Category prompts: "Build an agent we can talk to naturally that handles interruptions gracefully." (Live Agent); "Blend text, images, audio, and video into one seamless experience." (Creative Storyteller); "Create a helping hand that interprets visual screens." (UI Navigator) ([announcement][glac-join])

### GKE Turns 10 Hackathon (2025)

| Fact | Value | Source |
|---|---|---|
| Organizer and platform | Google Cloud; entries on Devpost (gketurns10.devpost.com) | [announcement][gke-join] |
| Submission window | Aug 18, 2025 to Sep 22, 2025: "Submissions are open from Aug 18, 2025 to Sept, 22 2025" | [What's new 2025, week Aug 4 - Aug 8][whatsnew-2025] |
| Announcement post | Sep 5, 2025, by Dilasha Panigrahi and Willie Turney | [announcement][gke-join] |
| Winners post | Dec 3, 2025, by Willie Turney | [winners post][gke-win] |
| Prize pool | "Compete for over $50,000 in prizes" | [What's new 2025][whatsnew-2025] |
| Prize tiers | Grand prize: $15,000, $3,000 in credits, a chance at up to two KubeCon North America passes (Atlanta, Nov 10-13, 2025), one year of Google Developer Program Premium, a Kubernetes Podcast guest interview, a GKE team video feature, virtual coffee, social promo. Regional winners: $8,000, $1,000 in credits, video feature, virtual coffee, social promo. Honorable mentions: $1000 and $500 in credits | [announcement][gke-join] |
| Cash check | $15,000 + 4 x $8,000 + 3 x $1,000 = $50,000 (my arithmetic) | [announcement][gke-join] |
| Participation | "4,773 registered participants from 133 countries, culminating in 133 innovative gallery projects" | [winners post][gke-win] |
| Award structure | 1 grand prize, 4 regional winners (North America, Latin America, Asia Pacific, Europe/Middle East/Africa), 3 honorable mentions | [winners post][gke-win] |
| Task | Take Bank of Anthos or Online Boutique. "The goal is not to modify the core application code directly, but instead build new components that interact with its established APIs!" | [announcement][gke-join] |
| Hard requirements | "Your project must be built using GKE and Google AI models such as Gemini, focusing on how the agents interact with your chosen microservice application." | [announcement][gke-join] |
| Encouraged | "utilize Agent Development Kit (ADK), Model Context Protocol (MCP), and the Agent2Agent (A2A) protocol for extra powerful functionality!" | [announcement][gke-join] |
| Suggested ideas | A chatbot for Online Boutique; and "Develop an agent that intelligently monitors microservice performance on GKE, suggests troubleshooting steps, and even automates remediation." | [announcement][gke-join] |
| Judging criteria | Not stated in either post. Devpost rules blocked here (unverified) | [winners post][gke-win] |

**What the post says the judges valued (quotes):**

- "Now, let's give a massive round of applause to our remarkable winners whose projects are a testament to the creativity, technical mastery, and deep understanding of GKE and AI at the heart of this challenge." ([winners post][gke-win])
- "We are excited to celebrate our regional winners who demonstrated remarkable technical skill and exemplified the potential of integrating agentic AI with GKE." ([winners post][gke-win])
- Anh Lam "presented a lightning talk highlighting her technical execution on GKE." ([winners post][gke-win])
- Amie Wei "highlighted how Google credits and available resources made it easier to get hands-on experience with GKE and AI." and: "You miss 100% of the shots you do not take" ([winners post][gke-win])
- "The goal was to seamlessly integrate next-generation agentic AI capabilities, all orchestrated on GKE, to elevate existing applications to new heights." ([winners post][gke-win])

---

## Winners table: Gemini Live Agent Challenge

Award, project, names and team sizes come from the [winners post][glac-win]. The "Google tech" and "Autonomy" columns come from the repo code I read.

| # | Award | Project (post link) | By (team size) | Repo | Google tech seen in the repo | Autonomy | Live URL | Deep-dived |
|---|---|---|---|---|---|---|---|---|
| 1 | Grand Prize | [ORION][d-orion] | Aditya Shukla (1) | [40tify/orion][r-orion] | Live API native audio plus 1 fps video, ADK root agent plus 9 sub-agents with tool callbacks, Vertex AI, Cloud Run, Cloud Build, GCS | Acts on voice command, but only shows data and logs events; "The surgeon decides." | Listed on run.app (not opened) | yes |
| 2 | The Live Agent | [drone-copilot][d-drone] | Bryen Param (1) | [BryenInsights/drone-copilot][r-drone] | Live API through Vertex AI (Gen AI SDK, no ADK), Gemini Flash for vision, Cloud Run, Terraform | Acts alone on missions inside a code safety guard; the LLM narrates | None (hardware); demo replay mode | yes |
| 3 | Creative Storyteller | [Sankofa][d-sankofa] | Jeremiah Somoine (1) | [Jeremiah-Sakuda/Sankofa][r-sankofa] | 3 ADK agents (narrator, live, critic), Gemini 2.5 Flash, Flash Image, Pro TTS, Live, Cloud Run, Firestore | Generates content only; a critic agent reviews it | None (README TODO) | yes |
| 4 | UI Navigator | [Moonwalk][d-moonwalk] | Enaiho Uwas Paul, Aman Kumar Sah (2) | [OactoDev/Moonwalk][r-moonwalk] | Gen AI SDK with Gemini 3 Flash, 3.1 Pro and a 2.5 Flash router, Cloud Run, Firestore, GCS, Cloud TTS | Acts; risky plans need a "Proceed" click | getmoonwalk.top (not opened) | yes |
| 5 | Best multimodal integration and UX | [Wand][d-wand] | David Li (1) | Not found | Not checked | Not checked | Not checked | no |
| 6 | Best technical execution and agent architecture | [JohnKeats.AI][d-keats] | Matthew Keats (1) | [johnkeats-ai/johnkeats-ai][r-keats] | ADK agent on the Live native audio model, ADK bidi streaming, Vertex AI, Firestore, Cloud Run | Talks only; learning-loop changes need human approval | johnkeats.ai (not opened) | yes |
| 7 | Best innovation and thought leadership | [Rayan Memory][d-rayan] | Yusuf Elnady (1) | [yelnady/rayan][r-rayan] | Two Live API sessions with affective dialog, 2.5 Flash, Flash Image, text-embedding-005, Firestore, GCS, Cloud Run, Firebase Hosting, Terraform | Background agent writes memories on its own; asks you to confirm uncertain room placement | rayan-memory.web.app (not opened) | yes |
| 8 | Honorable mention | [NagarDrishti][d-nagar] | Nikita Dongre, Omkar Dongre (2) | Not found | Not checked | Not checked | Not checked | no |
| 9 | Honorable mention | [Ekaette][d-ekaette] | Bassey John (1) | Not found | Not checked | Not checked | Not checked | no |
| 10 | Honorable mention | [VibeCat][d-vibecat] | Sejun Kim, Michael Chang (2) | [Two-Weeks-Team/vibeCat][r-vibecat] | Live API (Go Gen AI SDK), ADK for Go, two Cloud Run services, Firestore, Secret Manager, Cloud Logging and Trace | Suggests, waits for permission, then acts; code-level risk gate | DMG release; Cloud Run URLs (not opened) | yes |
| 11 | Honorable mention | [Call My Parts][d-parts] | Sugam Palav, Nikhil Lohar, Siddhant Panday, Vishal Parekh (4) | Not found | Not checked | Post says it "autonomously searches vendor websites, calls suppliers" | Not checked | no |
| 12 | Honorable mention | [Relay][d-relay] | Faith Ogundimu (1) | Not found | Not checked | Not checked | Not checked | no |

## Winners table: GKE Turns 10 Hackathon

| # | Award | Project (post link) | By (team size) | Repo | Google tech seen in the repo | Autonomy | Live URL | Deep-dived |
|---|---|---|---|---|---|---|---|---|
| 1 | Grand prize | [The cart-to-kitchen AI assistant on GKE][d-c2k] | Amie Wei (1) | [amiewei/cart-to-kitchen-ai-assistant-gke][r-c2k] | ADK agents, official A2A SDK, Gemini 2.5 Flash Lite, Imagen 3.0 Fast, GKE (Terraform, Artifact Registry, Skaffold) | Suggests recipes; adds to cart only after the user clicks "Add to Cart" | None listed | yes |
| 2 | North America regional | [CardOS][d-cardos] | Anh Lam (1) | Not found | Not checked | Not checked | Not checked | no |
| 3 | Latin America regional | [NeroFashion][d-nero] | Hudson Araújo, Gabriel Valentim, Samuel Cavalcanti, Giovanna Moeller (4) | [xValentim/nero-fashion][r-nero] (plus [frontend][r-nero-fe]) | Gemini 2.0 Flash and 2.5 Flash Image Preview through LangChain and the Gen AI SDK, FastAPI service on GKE; no ADK, A2A or MCP | Answers requests; no autonomous actions | API docs on a bare IP; Vercel frontend (not opened) | yes |
| 4 | Asia Pacific regional | [V-Commerce Studio][d-vcom] | Rakesh E, Poujhit MU, Manjunathan R, Mary Shermila (4) | GKE-era README at [Siddharth-Khattar/gke-online-boutique][r-vcom] (affiliation unverified); later rebuild at [mvp-ing/v-commerce-studio][r-vcom2] | ADK LlmAgent plus an MCP service, Vertex AI RAG Engine, Gemini 2.x, Nano Banana, Veo 3, GKE | Proactive nudges; an admin approves or rejects generated video ads | vcommercestudio.xyz from the later repo (not opened) | yes (with caveat) |
| 5 | EMEA regional | [Cartmate][d-cartmate] | Victor Bash (1) | [victorbash400/Cartmate][r-cartmate] | Vertex AI Gemini chat sessions, Vision AI, Kubernetes, Cloud Build; custom agent messaging over Redis; Perplexity API | Recommends; cart changes on request; checkout needs a form the user fills in | None listed | yes |
| 6 | Honorable mention #1 | [Voice Teller - Dial ADK + MCP][d-voice] | Julian Hecker (1) | [julian-hecker/gke-hackathon][r-voice] | ADK agent with McpToolset, Gemini 2.0 Flash, GKE Autopilot, Gateway with Certificate Manager; Twilio | Acts on the caller's request (log in, balance, create transaction); prompt says to confirm inputs | heckerlabs.com subdomains (not opened) | yes |
| 7 | Honorable mention #2 | [CO2-Aware Shopping Assistant][d-co2] | Prabhakaran Jayaraman Masani (1) | [prabhakaran-jm/co2-shopping-assistant][r-co2] | Gemini 2.0 Flash via google.generativeai; google-adk pinned but not imported in the base agent; custom A2A module; MCP server files; GKE Autopilot, Terraform, HPA, Prometheus | Assists on request; agents can add to cart and check out | assistant.cloudcarta.com (not opened) | yes |
| 8 | Honorable mention #3 | [Vigil AI][d-vigil] | Ayan Liger (1) | [ayanliger/gke-turns10-hackathon-vigil][r-vigil] | ADK LlmAgent with Gemini 2.5 Flash, a2a-sdk, GKE, Artifact Registry | Acts alone: locks the account when the risk score is 7 or more; no human approval | None | yes |

---

## Gemini Live Agent Challenge: winner deep dives

### 1. ORION, Operating Room Intelligent Orchestration Node (Grand Prize)

- **Post description (verbatim):** "ORION, or Operating Room Intelligent Orchestration Node, is a voice-directed surgical co-pilot for robotic surgery. Surgeons can speak naturally and instantly receive answers, live data on display, and real-time visual assistance - all without breaking scrub." By Aditya Shukla. ([winners post][glac-win])
- **Repo:** [github.com/40tify/orion][r-orion]: 97 commits, not a fork, branch main ([repo page][r-orion]). The README's clone URL and Cloud Build trigger name the owner `adityashukla8`, which matches the winner's name. The repo now sits under `40tify`, so the account link is likely but unverified ([README][r-orion-readme]).
- **What it does:** A voice console for a da Vinci robotic surgery case. The surgeon says things like "ORION, show hemoglobin", "run the timeout", "I have bleeding" or "is cefazolin safe?", and ORION shows labs, CT slices, a 3D lung model and phase checklists, logs timestamped events, and writes an operative report. It watches the surgical video at 1 fps ([README][r-orion-readme]). Patient data and the 10-drug database are synthetic, hard-coded demo data ([README][r-orion-readme], [tools.py][r-orion-tools]).
- **Google tools and depth (deep):**
  - Gemini Live API on Vertex AI with a native audio model. Barge-in uses `StreamingMode.BIDI`, video frames go through `send_realtime()`, input and output are transcribed, and the agent has a custom voice ([README][r-orion-readme]).
  - ADK 1.26.0. A root `LlmAgent` named `ORION_Orchestrator` has 9 sub-agents: Briefing, Timeout, Report, Complication_Advisor, EBL_Tracker, Drug_Checker, Anatomy_Spotter, Handoff and Screen_Advisor. It routes with `transfer_to_agent()`, and `before_tool_callback` and `after_tool_callback` grounding run on every agent ([agent.py][r-orion-agent]). The README's own counts vary (8 or 9 agents, 22 or 24 tools).
  - Hosting: Cloud Run, with Cloud Build CI/CD on every push to main, Artifact Registry, and GCS for assets ([README][r-orion-readme]).
  - Not used: A2A, MCP, GKE.
- **Autonomy:** Acts on spoken commands, but every tool only changes the screen or the event log. There is no clinical action, so no approval step. A wake-word rule tells it to stay silent for staff chatter. The prompt says: "You are a ROUTING and DISPLAY system, NOT a medical advisor." Argument whitelists block invented fields before any tool runs ([agent.py][r-orion-agent]). README: "**ORION does not give clinical opinions.** It surfaces data, enforces protocols, and logs events. The surgeon decides. ORION makes sure they have what they need to decide correctly." ([README][r-orion-readme])
- **Human story (role-based, no named person):** "During robotic surgery, the operating surgeon's hands are **locked on instrument controls** inside a sterile field for the entire procedure. They cannot type, click, tap, or interact with any computer system." This is backed by a table of five failures with PubMed citations, such as "Only **23.1%** of laparoscopic cholecystectomies have CVS documented" ([README][r-orion-readme]).
- **Live URL:** The README lists `orion-518946358970.us-central1.run.app` (could not be opened; run.app is blocked here). Demo on Vimeo (`vimeo.com/1173959084`) and a "GCP Backend & Logs Demo" on YouTube (`youtu.be/LLaFp_8n4k0`); neither was opened ([README][r-orion-readme]).
- **README structure:**
  - Opening block: title, one-line pitch, then "Built for / Hackathon Category / Built with / Demo / Live deployment".
  - Then: table of contents, Disclaimer ("may contain clinical inaccuracies"), Problem (five cited challenges), Solution table, Architecture (diagram plus ASCII), Agent System tables, "Gemini & ADK Features Used", Features, Tech Stack.
  - Then: "GCP Backend & Logs Demo (for Hackathon)", Local Setup, Assets Setup, Cloud Deployment (manual plus Cloud Build), Project Structure, Data Sources with licenses, Key Voice Commands, Hackathon ([README][r-orion-readme]).
- **Tests:** No tests folder ([repo page][r-orion]).
- **Why it most likely won (inference):**
  - The highest-stakes, most vivid setting in the field, and the pitch states its own limits.
  - The deepest use of every required piece: Live API audio and video, ADK multi-agent with callbacks, and Cloud Run with CI/CD.
  - A deployment-proof video made for the judges.
  - Safety is built into the design (display-only tools, whitelists, a disclaimer).
- **Deep-dived:** yes.

### 2. drone-copilot (The Live Agent winner)

- **Post description (verbatim):** "Drone-copilot transforms how users interact with hardware by enabling natural, real-time conversations with a drone instead of using a joystick or complex menus. Simply by speaking, users can instruct the drone to navigate, perform autonomous visual inspections, or describe its surroundings, while the drone verbally responds and confirms its actions in real time." By Bryen Param, who presented at Next '26 ([winners post][glac-win]).
- **Repo:** [github.com/BryenInsights/drone-copilot][r-drone]: 32 commits, 14 stars, 8 forks ([repo page][r-drone]).
- **What it does:**
  - You talk to a DJI Tello drone while it streams video to Gemini. You can say "take off", ask "what do you see?", or say "find the red bag".
  - It runs autonomous search, approach, orbit and inspection missions, and writes inspection reports.
  - A demo mode replays recorded missions so judges need no drone ([README][r-drone-readme]).
- **Google tools and depth (medium-deep):**
  - The Gemini Live API runs through Vertex AI on a Cloud Run WebSocket relay, using the Gen AI SDK, not ADK. It uses context window compression and session resumption ([README][r-drone-readme], [gemini_session.py][r-drone-session]).
  - Gemini Flash handles bounding-box perception and reports.
  - Deployment uses Cloud Run scripts or Terraform.
  - Not used: ADK, A2A, MCP, GKE.
  - The tools declared to Gemini include `takeoff`, `land`, `move_drone`, `rotate_drone`, `hover`, `set_speed`, `report_perception` and `start_inspection`. The README says 10 tools ([tools.py][r-drone-tools]).
- **Autonomy:** Acts, with no approval step, but code keeps control of the risky parts:
  - During missions a deterministic mission controller flies, and the LLM only narrates: "The scan is handled by deterministic code." and "The mission controller uses its own visual perception (Flash API) - your role is narrator." ([config.py][r-drone-config])
  - A `SafetyGuard` checks every command for connection, battery, temperature and post-takeoff stabilization. It clamps distances and rotation and triggers auto-land on critical battery or heat ([safety_guard.py][r-drone-guard]).
  - Stop rule: "Respond to stop commands immediately: hover in place and await further instructions." ([config.py][r-drone-config])
- **Human story:** The post quotes Bryen: "what if a model could interact with the real world?" No named person in the README ([winners post][glac-win]).
- **Live URL:** None (needs hardware). Two YouTube demos, `youtu.be/_FCgmYjGCVs` and `youtu.be/38d4ZavOyTw`, not opened ([README][r-drone-readme]).
- **README structure:** Pitch and badges, then "Try it without a drone" first, "Watch the demo", "How it works" (mermaid, plus why the split design: the Tello's own Wi-Fi cuts the laptop's internet), Setup & run (mock and real drone), Google Cloud deployment, "Built with" and "Gemini features used", Project structure ([README][r-drone-readme]).
- **Tests:** One script, `tests/validate_live_api.py`, a "Phase 0 Validation Gate" that checks audio, video and tool calls can share one Live session ([test file][r-drone-test]). No unit suite.
- **Why it most likely won (inference):**
  - A real machine moving in the room on voice command, which is exactly the category's "talk to naturally" brief.
  - Smart engineering around a hardware limit.
  - Advanced Live API features.
  - A clear line between LLM intent and deterministic flight control.
  - A no-hardware demo mode for judges.
- **Deep-dived:** yes.

### 3. Sankofa (Creative Storyteller winner)

- **Post description (verbatim):** "Sankofa acts as a multimodal AI "griot" - a traditional West African storyteller - transforming fragmented family histories into deeply immersive narratives. Based on just a few user details, it weaves together rich voice narration, watercolor imagery, and ambient soundscapes into a historical story, allowing users to engage in a real-time voice conversation with the storyteller to explore their roots further." By Jeremiah Somoine, "currently a college student" ([winners post][glac-win]).
- **Repo:** [github.com/Jeremiah-Sakuda/Sankofa][r-sankofa]: 210 commits, AGPL-3.0, topics `gemini`, `ai-agents`, `hackathon-project`, `adk-google` ([repo page][r-sankofa]). The README says "Built for the **Gemini Live Agent Challenge** ... in the **Creative Storyteller** category" and "Author: **Jeremiah Sakuda**". That last name differs from the post's "Somoine"; the project and first name match (same person unverified) ([README][r-sankofa-readme]).
- **What it does:**
  - Input: a surname, a region, a time period and any fragments the user knows.
  - Output: a three-act heritage narrative with griot-style narration (TTS), watercolor images, per-act ambient soundscapes, and trust labels on every segment (Historical, Cultural or Reconstructed).
  - Users can ask follow-up questions and talk live with the griot ([README][r-sankofa-readme]).
- **Google tools and depth (deep):**
  - Three ADK agents in [adk_agent.py][r-sankofa-agent]:
    - `sankofa_heritage_narrator`, with tools such as `lookup_cultural_context`, `plan_narrative_arc`, `validate_narrative_arc`, `generate_act_segments`, `enrich_segment` and `notify_user`.
    - `sankofa_heritage_live_narrator`, on the Live model with the "Kore" voice.
    - `sankofa_heritage_critic`.
  - Models: Gemini 2.5 Flash, 2.5 Flash Image, 2.5 Pro Preview TTS and 2.0 Flash Live ([README][r-sankofa-readme]).
  - Hosting: Cloud Run for frontend and backend, with Firestore for sessions.
  - Not used: A2A, MCP, GKE.
- **Autonomy:** Generates content only, with no actions in the outside world. The agent picks the tool order, validates its own story arc and re-plans when needed. With review on, the critic gates quality: "If it fails (score < 7 or critical issues), the narrative is regenerated (max 1 retry)." No human approval step. "Sankofa never fabricates specific genealogical claims." ([README][r-sankofa-readme])
- **Human story (quote):** "Named after the Akan concept of "go back and get it," Sankofa addresses a profound gap: hundreds of millions of people in diaspora communities have lost tangible connection to their ancestral heritage." and "**Sankofa doesn't just tell you where you're from - it makes you *feel* it.**" ([README][r-sankofa-readme])
- **Live URL:** None; the live demo link is a commented-out TODO ([README][r-sankofa-readme]).
- **README structure:**
  - Opening: Akan proverb epigraph and pitch.
  - Then: The Problem, What It Does (long feature list), Experience & Immersion, Architecture (mermaid), Tech Stack table, Supported Regions, Local Development, ADK Agent Orchestration, Testing, API Endpoints.
  - Then: Google Cloud Deployment, Session store (Firestore), Error Handling, Trust & Accuracy, Hackathon, License, Author ([README][r-sankofa-readme]).
- **Tests:** `backend/tests` has four test files: critic (12 tests), sanitization (31 tests), intake and session ([tests folder][r-sankofa-tests]). The README says CI runs them on every push and PR, and the root has `.github/workflows` ([README][r-sankofa-readme]).
- **Why it most likely won (inference):**
  - A strong emotional and cultural story that fits the Storyteller brief exactly: text, images, audio and live voice in one flow.
  - Honest trust labels.
  - Real ADK use, including a self-critic.
  - The most tested codebase among the Gemini winners I read.
- **Deep-dived:** yes.

### 4. Moonwalk (UI Navigator winner)

- **Post description (verbatim):** "Moonwalk is a conversational, hands-free desktop assistant that helps users intuitively navigate their computer and complete complex tasks using just their voice. By remembering personal preferences and past interactions, it acts as an intelligent co-pilot that can seamlessly control your mouse and keyboard to execute everyday workflows - like booking flights or managing spreadsheets - while you simply sit back and speak." By Enaiho Uwas Paul and Aman Kumar Sah ([winners post][glac-win]).
- **Repo:** [github.com/OactoDev/Moonwalk][r-moonwalk]: 18 commits, 11 stars, 11 forks, MIT; About links `www.getmoonwalk.top` ([repo page][r-moonwalk]). The README names no authors; I matched it by name and description (unverified).
- **What it does:**
  - A macOS glass-pill overlay. You say "Hey Moonwalk" or press a hotkey.
  - It plans and runs tasks through macOS Accessibility APIs, AppleScript and a Chrome extension, plus Google Workspace tools.
  - It works in a Sense, Plan, Act, Verify loop with milestones and a verifier ([README][r-moonwalk-readme]).
- **Google tools and depth (medium):**
  - Gen AI SDK with a model router: `gemini-2.5-flash` routes each request to `gemini-3-flash-preview` or `gemini-3.1-pro-preview-customtools` ([router.py][r-moonwalk-router]).
  - Cloud Run "brain" server, cloud memory in Firestore with large files in GCS ([cloud_memory.py][r-moonwalk-mem]), and Google Cloud Text-to-Speech ([requirements][r-moonwalk-req]).
  - Voice input uses Picovoice wake word and SpeechRecognition packages. I did not find Live API use in the files I read.
  - Not used: ADK, A2A, MCP, GKE.
- **Autonomy (acts, with approval for risky plans):** `_should_gate_plan` in [core_v2.py][r-moonwalk-core] sorts every plan by risk:
  - Read-only plans run without asking.
  - A single medium-risk step, such as opening an app or URL, runs.
  - Any high-risk tool, or 3 or more steps with side effects, triggers a plan modal: "Review this plan and choose Proceed to execute it." High-risk tools include `write_file`, `run_shell`, browser clicks and typing, `type_text`, `mouse_action`, `gmail_send`, `gcal_create_event` and `gsheets_write`.
  - A pending plan expires after 600 seconds, and is thrown out if the active app or browser domain changes.
  - The user can approve, modify or cancel by voice or text. The README shows the "Plan preview modal: Step-by-step with "Proceed" button" ([README][r-moonwalk-readme]).
- **Human story:** None named. The post frames it as "while you simply sit back and speak" ([winners post][glac-win]).
- **Live URL:** getmoonwalk.top (not opened); a DMG build path; YouTube demo `youtu.be/u3QoaT3pIMs` (not opened) ([README][r-moonwalk-readme]).
- **README structure:** Pitch, Features, UI States (SVG mockups), response card and plan preview, Architecture and SPAV loop diagrams, Quick Start, keyboard shortcuts, Project Structure, Cloud Deployment, Chrome Extension, Testing, Building for Distribution, License ([README][r-moonwalk-readme]).
- **Tests:** About 30 test files in `tests/` (agent, milestone executor, browser scenarios, replanning, verifier and more) plus `benchmarks/` ([tests folder][r-moonwalk-tests]).
- **Why it most likely won (inference):**
  - Real control of a real computer, which is the UI Navigator brief.
  - A plan, act and verify loop.
  - A visible, risk-based approval step.
  - Memory, and a large test suite.
- **Deep-dived:** yes.

### 5. JohnKeats.AI (Best technical execution and agent architecture)

- **Post description (verbatim):** "JohnKeats.AI is a voice-first emotional companion designed to actively listen and hold space for users without rushing to offer solutions. By processing subtle vocal cues like pitch, pacing, and tone, it reacts naturally to a user's emotional state in real time to provide a deeply reflective and empathetic conversational experience." By Matthew Keats ([winners post][glac-win]).
- **Repo:** [github.com/johnkeats-ai/johnkeats-ai][r-keats]: 68 commits, MIT. "**Built for the Gemini Live Agent Challenge.**" ([README][r-keats-readme]) The link between the org and Matthew Keats is unverified.
- **What it does:**
  - A voice-only companion; the screen shows only a breathing orb. "A voice agent with one rule: hold, don't solve."
  - It silently saves the user's core uncertainties to Firestore and has a crisis-resources tool.
  - A separate 14-agent "governed calibration pipeline" anonymises transcripts, scores attunement on six dimensions and proposes calibration changes ([README][r-keats-readme]).
- **Google tools and depth (deep):**
  - An ADK `Agent` named `keats` on `gemini-live-2.5-flash-native-audio`, with tools `save_to_passage`, `get_passage_history`, `resolve_uncertainty` and `crisis_resources` ([agent.py][r-keats-agent]).
  - ADK bidi-streaming over WebSocket, the Vertex AI Live API, and Firestore.
  - Cloud Run deployed through Artifact Registry ([README][r-keats-readme]).
  - Not used: A2A, MCP, GKE.
- **Autonomy:** The voice agent only talks and saves notes. The learning loop is gated twice ([README][r-keats-readme]):
  - First, a deterministic policy gate ("Deterministic rules. No LLM.") rejects suggestions such as "encourage longer sessions", "maximize engagement", "diagnose" or "be more upbeat" ([policy_gate.py][r-keats-gate]).
  - Second, suggestions that pass are marked `"pending"` "ready for human review" ([policy_gate.py][r-keats-gate]). README: "All recommendations require human approval." and "Principle Zero: the voice agent never depends on the learning loop."
- **Human story:** "The first AI agent designed not to solve your problem, but to sit with you in it." (repo About) and Keats' "negative capability" in the knowledge base ([repo page][r-keats], [README][r-keats-readme]). No named user story; the dev.to post with the backstory is blocked.
- **Live URL:** johnkeats.ai (not opened); YouTube demo `youtu.be/zNKhR3e2ym4` (not opened) ([README][r-keats-readme]).
- **README structure:** Pitch, Live Demo, Demo Video, What It Is, Architecture, Tech Stack, Local Development, Running the Calibration Pipeline, Cloud Deployment, Project Structure, Knowledge Base, Tools, Governed Calibration Pipeline, Blog Post, License ([README][r-keats-readme]).
- **Tests:** No tests folder. `backend/app/evals` holds a promptfoo config, an eval matrix and an anonymisation provider ([evals folder][r-keats-evals]).
- **Why it most likely won (inference):** The award is for architecture. It cleanly separates the live agent from the learning loop, uses LLM proposals with a deterministic gate and human approval, and audits for PII (personal data) with an adversarial reviewer. It is a strong technical design wrapped in an emotional product.
- **Deep-dived:** yes.

### 6. Rayan Memory (Best innovation and thought leadership)

- **Post description (verbatim):** "Rayan Memory tackles the universal problem of forgetting by turning your daily learnings into a fully explorable 3D "memory palace." A background agent passively listens to your real-world audio to extract important ideas as physical artifacts, allowing you to walk through themed virtual rooms and converse with a dedicated AI companion to easily retrieve your exact memories." By Yusuf Elnady ([winners post][glac-win]).
- **Repo:** [github.com/yelnady/rayan][r-rayan]: 152 commits, topic `geminiliveagentchallenge`; the README credits "g.dev/yelnady" ([repo page][r-rayan], [README][r-rayan-readme]).
- **What it does:**
  - A CaptureAgent listens to your mic and screen and turns key ideas into typed 3D artifacts in themed rooms.
  - A RecallAgent is a voice companion inside a walkable Three.js palace. Its answers are grounded in your stored memories, and it can draw a mind-map image for each room ([README][r-rayan-readme]).
- **Google tools and depth (deep on Live API and Google Cloud, light on ADK):**
  - Two Gemini Live sessions on `gemini-live-2.5-flash-native-audio` with `enable_affective_dialog=True`.
  - `gemini-2.5-flash` sorts captures into rooms, and `gemini-2.5-flash-image` makes the mind maps.
  - Grounding: Vertex AI `text-embedding-005` for memories, plus the `google_search` grounding tool.
  - Storage and hosting: Firestore, Cloud Storage, Cloud Run with session affinity, and Firebase Hosting, all set up by one Terraform apply ([README][r-rayan-readme]).
  - `google-adk` is in [requirements][r-rayan-req], but the capture and recall agents I read call the Gen AI SDK directly, with no ADK import ([capture_agent.py][r-rayan-capture]).
  - Not used: A2A, MCP, GKE.
- **Autonomy:** Acts alone on low-stakes writes to your own memory store, with limits ([capture_agent.py][r-rayan-capture]):
  - A capture needs confidence of 0.7 or more and a minimum gap since the last one.
  - It prefers editing an existing memory over creating a new one.
  - It may create at most 2 new rooms per session.
  - Near-duplicates (0.90 similarity or more) are merged.
  - The room-sorting agent auto-assigns only on a high match. A middle match comes back as `requires_confirmation=True`, meaning the user confirms ([memory_architect.py][r-rayan-arch]).
  - README: "only explicitly chosen screenshots are stored" ([README][r-rayan-readme]).
- **Human story (quote):** "I was in a conversation with someone I respect. A mentor. We were talking about a book , *a book I had read*, underlined, and supposedly absorbed. And I had nothing." ([STORY.md][r-rayan-story])
- **Live URL:** rayan-memory.web.app (not opened) ([README][r-rayan-readme]).
- **README structure:**
  - Opening: centered hero with many badges, then a pull-quote problem ("The problem isn't capture... Rayan fixes retrieval.").
  - Then: What Is Rayan, Features, Quick Start (Terraform), How People Use Rayan (long use-case list), Architecture (ASCII plus mermaid), How Rayan Avoids Hallucination, Affective Dialog.
  - Then: Tech Stack, Project Structure, Environment Variables, Development Commands, Hackathon Submission table.
  - Screenshot placeholders were left unfilled ([README][r-rayan-readme]). The repo also has STORY.md, PRODUCT.md and ARCHITECTURE.md ([repo page][r-rayan]).
- **Tests:** The frontend has a `vitest` test script ([package.json][r-rayan-pkg]); backend tests not seen (unverified). `.github/workflows` exists ([repo page][r-rayan]).
- **Why it most likely won (inference):** A new interaction idea (a walkable memory palace fed by a passive listener). It also shows rich Live API use (two concurrent sessions, affective dialog), grounding against hallucination, one-command infrastructure, and a personal "why".
- **Deep-dived:** yes.

### 7. VibeCat (Honorable mention)

- **Post description (verbatim):** "VibeCat is a proactive macOS desktop companion that continuously watches your screen, understands your context, and suggests helpful actions before you even ask. Instead of waiting for a command, it speaks up first - like offering to fix a missing line of code or execute a terminal command - and completes the task only after receiving your permission." By Sejun Kim and Michael Chang ([winners post][glac-win]).
- **Repo:** [github.com/Two-Weeks-Team/vibeCat][r-vibecat]: 213 commits, default branch `master`. Topics include `gemini-live-api`, `google-adk` and `cloud-run` ([repo page][r-vibecat]). The recording guide's local path names `kimsejun` ([challenge notes][vc-challenge]).
- **What it does:**
  - A pixel cat on your desktop that watches the screen, suggests something, waits for a yes, then acts. It acts through the macOS Accessibility API, hotkeys and the Chrome DevTools Protocol.
  - Failed steps are retried with another method, and a screenshot check confirms each step ([README][r-vibecat-readme]).
- **Google tools and depth (deep):**
  - Gemini Live API through the Go Gen AI SDK v1.49.0, in a Go "Realtime Gateway" on Cloud Run.
  - An ADK for Go v0.6.0 orchestrator on a second Cloud Run service, for screenshot reasoning, escalation and memory ([go.mod][r-vibecat-gomod]).
  - Firestore, Secret Manager, and Cloud Logging, Trace and Monitoring ([README][r-vibecat-readme]).
  - Not used: A2A, MCP, GKE.
- **Autonomy (suggests, waits for approval, then acts):** The approval rule lives in two places:
  - The prompt: "Confirmation gate: always waits for user approval before acting" ([README][r-vibecat-readme]).
  - Code in [navigator.go][r-vibecat-nav]. If the command or typed text contains a risk keyword ("password", "token", "deploy", "prod", "delete", "git push", "publish", "send", "rm -rf", "sudo " and others) and the plan pastes text, presses a button or hits Enter, the planned steps are cleared. The agent then asks: "This could change something important. Do you want me to proceed, or should I only explain the next step?"
  - Steps run one at a time and are checked by screenshot. Repeated failure falls back to "guided mode or human explanation" ([README][r-vibecat-readme]).
- **Human story (quote):** "We kept asking ourselves - what if your desktop had a senior colleague sitting right next to you, watching your screen, and quietly saying *"hey, want me to handle that?"* before you even had to ask?" and "Proactive AI requires careful safety design. The confirm-before-acting model isn't a limitation - it's what makes proactive suggestions feel trustworthy rather than alarming." ([Devpost text in repo][r-vibecat-devpost])
- **Live URL:** A DMG in GitHub releases; Cloud Run URLs in the README (not opened); YouTube demo `youtu.be/j1zzfoDr7qA` (not opened) ([README][r-vibecat-readme]).
- **README structure:**
  - Opening: hero with badges ("tests 131 passing", "dev.to 18 posts").
  - Then: The Problem, The Flip, Core Flow ("OBSERVE → SUGGEST → WAIT → ACT → FEEDBACK"), a comparison table against "Traditional UI Agents", and three Demo Scenarios.
  - Then: a long Architecture section (version matrix, diagrams, endpoint contracts), Quick Start, Project Structure, Deployment, Safety Model, Technology Stack, Observability, and Submission Assets (including `PROOF_OF_GCP_DEPLOYMENT.md`) ([README][r-vibecat-readme]).
- **Tests:** The README claims 131 Swift tests in 20 files. Go `_test.go` files sit next to the gateway code (handler, navigator, navigator eval, registry, action state store) ([ws folder][r-vibecat-ws]), plus `tests/e2e`.
- **Why an honorable mention and not higher (inference):** The safety model is the most complete in the field, but the demo tasks are small (play music, add comments, run `go vet`) next to surgery or a flying drone.
- **Deep-dived:** yes.

### Gemini Live winners not deep-dived (no repo found)

- **Wand** (Best multimodal integration and user experience), David Li: "Wand is a voice-first, pointer-aware browser assistant that helps you seamlessly navigate and interact with any website using a combination of natural speech and hand gestures. By simply pointing at your screen and speaking - like asking to "play this video" or "zoom in here" - this live agent helps you instantly execute clicks, searches, and commands without ever needing to touch a mouse or keyboard." ([winners post][glac-win]). Searches for "wand pointer voice browser", "wand gemini live browser", "wand pointer gemini", "sees browses clicks", "pointer-aware browser agent" and "wand gemini" found nothing. Deep-dived: no.
- **NagarDrishti**, Nikita and Omkar Dongre: "allowing citizens to safely report potholes and waterlogging using a hands-free voice assistant while driving. These real-time reports instantly populate an interactive dashboard, where city officials can use natural language to easily identify hazard hotspots and manage critical repairs." ([winners post][glac-win]). Many same-name repos exist, none tied to this team. Deep-dived: no.
- **Ekaette**, Bassey John: "replacing frustrating hold queues with a conversational, multimodal AI assistant that operates across live phone calls and text messaging. Customers can speak naturally with the agent over a standard phone line while seamlessly sharing photos, reviewing product options, or completing payments via WhatsApp, c" (the sentence is cut off in the post itself) ([winners post][glac-win]). The only near match, `Sandgrouse/ekaette-nova`, describes an Amazon Nova Sonic build, not this entry. Deep-dived: no.
- **Call My Parts**, a team of 4: "Users simply speak their part request, and the AI agent autonomously searches vendor websites, calls suppliers to check pricing and inventory, and compiles the best options into a ranked, easy-to-read dashboard." ([winners post][glac-win]). This is the clearest "acts alone in the real world" honorable mention. Repo not found. Deep-dived: no.
- **Relay**, Faith Ogundimu: "uses your webcam to watch and guide your physical electronics projects in real time ... catches wiring mistakes before they happen" ([winners post][glac-win]). Repo not found. Deep-dived: no.

---

## GKE Turns 10 Hackathon: winner deep dives

### 1. The cart-to-kitchen AI assistant on GKE (Grand prize)

- **Post description (verbatim):** "This AI shopping assistant analyzes a user's grocery cart and recommends recipes. It uses Google products including Gemini, GKE Autopilot, Agent Development Kit (ADK), and Agent-to-Agent (A2A) protocols to enable AI model communication. The assistant helps users decide what to make for dinner based on what they already have." By Amie Wei, who gave a KubeCon NA 2025 lightning talk, an interview at the House of Kube and a theCUBE broadcast ([winners post][gke-win]).
- **Repo:** [github.com/amiewei/cart-to-kitchen-ai-assistant-gke][r-c2k]: a single commit; it extends Online Boutique and keeps the original README as `online-boutique-README.md` ([repo page][r-c2k]).
- **What it does:**
  - When the cart holds 2 or more items, the store suggests recipes ("What can I make with this?") with Imagen pictures.
  - The user ticks ingredients and clicks "Add to Cart".
  - A RecipeService (ADK) pulls out the ingredients. An IngredientMatcherAgent maps them to catalog products, and a CartAdderAgent adds them through the cart service's gRPC API. The page updates live over SSE ([recipeservice README][r-c2k-svc]).
- **Google tools and depth (deep on the requested stack):**
  - An ADK `Agent` `recipe_agent` on `gemini-2.5-flash-lite` with tools `process_recipe` and `get_cart_contents` ([agent.py][r-c2k-agent]).
  - The official A2A SDK (`A2ACardResolver`, `A2AStarletteApplication`) ([agent_server.py][r-c2k-cart]).
  - Imagen 3.0 Fast through the Gen AI SDK.
  - GKE via Terraform, Artifact Registry and Skaffold ([README][r-c2k-readme]). The post says GKE Autopilot ([winners post][gke-win]).
  - Not used: MCP.
- **Autonomy:** Suggests on its own; acts only after the user clicks. The recipe page's flow is "User selects specific ingredients" then "User clicks "Add to Cart"" ([recipeservice README][r-c2k-svc]).
- **Human story:** "The assistant helps users decide what to make for dinner based on what they already have." and Amie's advice: "You miss 100% of the shots you do not take" ([winners post][gke-win]).
- **Live URL:** None listed ([README][r-c2k-readme]).
- **README structure:** Short. Overview, core AI services, tech stack, architecture image, key capabilities, two screenshots. Then long local (minikube, Skaffold) and production GKE (Terraform) steps ([README][r-c2k-readme]).
- **Tests:** None in the new agent folders (`recipeservice`, `cartadderagent`) ([recipeservice folder][r-c2k-svcdir], [cartadderagent folder][r-c2k-cartdir]). The rest of the repo was not checked (unverified).
- **Why it most likely won (inference):**
  - An everyday problem anyone understands.
  - Every technology the organizers named (Gemini, ADK, A2A, GKE), used for real: official A2A SDK, separate agent services.
  - It follows the "do not modify core code" rule by adding services.
  - A clean, screenshot-able flow.
  - README polish and commit count were clearly not decisive: a single commit and a plain README.
- **Deep-dived:** yes.

### 2. CardOS: AI-Powered Credit Pre-Approval System (North America regional)

- **Post description (verbatim):** "CardOS uses a multi-agent AI pipeline to revolutionize credit pre-approval. It analyzes spending patterns from Bank of Anthos data, tailors terms and perks, and balances bank profitability with customer value." By Anh Lam, who gave a KubeCon NA lightning talk "highlighting her technical execution on GKE" ([winners post][gke-win]).
- **Repo:** Not found. I searched "cardos credit pre-approval", "cardos bank of anthos", "cardos gke", "credit pre-approval multi-agent", "CardOS AI-Powered Credit", "anh lam gke" and "credit pre-approval bank of anthos". Deep-dived: no.

### 3. NeroFashion (Latin America regional)

- **Post description (verbatim):** "NeroFashion created a plug-and-play AI microservice for the Online Boutique application running on GKE. The project enhances the online shopping experience by adding a layer of intelligence with features like image mixing to allow users to see themselves wearing the product, and smart descriptions for accessibility." By Hudson Araújo, Gabriel Valentim, Samuel Cavalcanti and Giovanna Moeller ([winners post][gke-win]).
- **Repo:**
  - [github.com/xValentim/nero-fashion][r-nero]: 16 commits; About "Bringing online shopping closer to reality with AI."; website `nero-fashion.vercel.app` ([repo page][r-nero]). The README brands it "NanoBanana Fashion AI".
  - Frontend: [giovannamoeller/nero-fashion-frontend][r-nero-fe] (README in Portuguese: a React app with a Node backend-for-frontend that calls the Product Catalog service over gRPC).
  - Linking `xValentim` to Gabriel Valentim is by name only (unverified).
- **What it does:** A new FastAPI service, `nanobananaservice`, inside Online Boutique. Endpoints: `/remix-images` (person plus product image), `/describe-image` (product or person description), `/assistant-fashion`, `/sell-product-from-query`, and cart and email endpoints that call the store over gRPC ([app.py][r-nero-app], [README][r-nero-readme]).
- **Google tools and depth (light):**
  - Gemini 2.0 Flash and `gemini-2.5-flash-image-preview` through LangChain's Google Gen AI package and the Gen AI SDK ([app.py][r-nero-app], [requirements.in][r-nero-req]).
  - A GKE cluster and Artifact Registry ([README][r-nero-readme]).
  - Not used: ADK, A2A, MCP.
- **Autonomy:** Request and response only; no autonomous actions. The "agent" is a set of AI endpoints ([app.py][r-nero-app]).
- **Human story:** Accessibility through "smart descriptions" (post); no named person ([winners post][gke-win]).
- **Live URL:** API docs link to a bare IP address (`34.61.215.100:8080/docs`) and a Vercel frontend; neither opened ([README][r-nero-readme], [repo page][r-nero]).
- **README structure:**
  - Opening: hero, "Competition Project Overview" bullets, enhanced architecture diagram, screenshots, service table, AI features, endpoint list.
  - Middle: the full original Online Boutique README pasted in.
  - Then: quick start (PowerShell script or manual GKE steps), curl tests, local development, "Competition Highlights", roadmap ([README][r-nero-readme]).
- **Tests:** Two Jupyter notebooks (`testing_api_complete.ipynb`, `testing_api_image_feats.ipynb`) instead of a test suite ([service folder][r-nero-dir]).
- **Why it most likely won (inference):**
  - A very visual "see yourself wearing it" demo built on Nano Banana image editing, an accessibility angle, and a drop-in service that leaves the core app alone.
  - Regional awards may also mean a smaller pool per region (unverified).
- **Deep-dived:** yes.

### 4. V-Commerce Studio (Asia Pacific regional)

- **Post description (verbatim):** "V-Commerce Studio redefines e-commerce with AI personalized chat, proactive engagement, virtual try-ons, and instant ad generation, all built on Google's ecosystem for intelligent retail automation. It enhances customer experience and automates business workflows, using Gemini models and GKE orchestration." By Rakesh E, Poujhit MU, Manjunathan R and Mary Shermila ([winners post][gke-win]).
- **Repo:**
  - The GKE-era README is at [github.com/Siddharth-Khattar/gke-online-boutique][r-vcom]. Its About text reads "We built V-Commerce Studio (where V stands for virtual) on top of Online Botique repo..." and it lists the same four features as the post. The repo shows 2,502 commits, most likely inherited from Online Boutique's history (unverified) ([repo page][r-vcom]). The owner is not on the post's team list, so the affiliation is unverified.
  - A later rebuild, [mvp-ing/v-commerce-studio][r-vcom2], has commits by "Poujhit" starting Dec 6, 2025 ([commit history][r-vcom2-commits]). It is labelled "Built for AI Partner Catalyst Hackathon" and focuses on Datadog LLM observability ([README][r-vcom2-readme]), so it is not the GKE submission.
- **What it does:** Four features ([GKE-era README][r-vcom-readme]):
  - RAG chat (Vertex AI RAG Engine plus Gemini).
  - A PEAU ("Proactive Engagement & Upselling") agent: a nudge after 5 or more views without add-to-cart, and an upsell after add-to-cart.
  - Nano Banana virtual try-on.
  - Veo 3 product video ads for admins.
- **Google tools and depth (medium-deep):**
  - An ADK `LlmAgent` on `gemini-2.0-flash` with ADK `Runner` and `InMemorySessionService` ([peau_agent.py][r-vcom-peau]).
  - An MCP service that exposes the product catalog ([src folder][r-vcom-src]).
  - Vertex AI RAG Engine, Gemini 2.5 Flash Image, Veo 3, GKE ([GKE-era README][r-vcom-readme]).
  - No A2A seen.
- **Autonomy:**
  - Proactive suggestions appear as notifications; the shopper decides.
  - Generated ads need a human: "The admin user can approve/reject the video, and the Frontend sends feedback to the Video Generation Service." The code has a validate endpoint that records approved or rejected ([video main.py][r-vcom-video]).
  - Video generation is limited to admins (RBAC).
- **Human story:** Team statement only: "By relentlessly iterating through a learning-development cycle under tight deadlines, we successfully integrated chat, notifications, virtual try-on, and ad creation." ([GKE-era README][r-vcom-readme])
- **Live URL:** `vcommercestudio.xyz`, linked from the later repo (not opened) ([later README][r-vcom2-readme]).
- **README structure (GKE-era):** Intro with four feature bullets, architecture diagram, "AI Services Added" with a step-by-step user flow per service, screenshots, team achievement paragraph ([GKE-era README][r-vcom-readme]).
- **Tests:** None seen in the AI service folders (`chatbotservice`, `mcp_service`, `peau_agent`, `video_generation`) ([src folder][r-vcom-src]).
- **Why it most likely won (inference):** Breadth across Google AI products (Gemini, RAG Engine, Nano Banana, Veo, ADK, MCP) in one storefront, with a business story (upsell, ads) and a human approval step on generated marketing content.
- **Deep-dived:** yes, with the repo-ownership caveat above.

### 5. Cartmate (Europe, Middle East, Africa regional)

- **Post description (verbatim):** "Cartmate transforms online shopping into an intelligent, conversational experience. The AI assistant understands style, learns preferences, and provides a truly personalized shopping experience through six specialized AI agents, all orchestrated using a multi-agent architecture deployed on GKE." By Victor Bash ([winners post][gke-win]).
- **Repo:**
  - [github.com/victorbash400/Cartmate][r-cartmate]: 24 commits, About "a new way to shop" ([repo page][r-cartmate]); owner display name "Victor bash" ([user repos][r-cartmate-user]).
  - The README never mentions the hackathon. Its badges point to a different path (`github.com/cartmate/cartmate`) and its clone URL is a placeholder (`your-org`) ([README][r-cartmate-readme]).
  - The README lists five agents. The `agents` folder holds `ads`, `cart_management`, `checkout`, `orchestrator_refactored`, `price_comparison` and `product_discovery`, plus a base class and manager ([agents folder][r-cartmate-agents]).
- **What it does:** Chat shopping over WebSocket. It learns your style from uploaded photos (Vision AI), searches Online Boutique, compares prices through the Perplexity API, and manages the cart and checkout ([README][r-cartmate-readme]).
- **Google tools and depth (medium):**
  - Gemini through Vertex AI `ChatSession` ([orchestrator][r-cartmate-orch]) and Google Vision AI.
  - `google-adk==1.13.0` and `google-genai` are pinned in [requirements][r-cartmate-req], but the orchestrator does not import ADK.
  - Agent messaging is a custom "A2A" layer on a Redis message bus ([README][r-cartmate-readme]).
  - Kubernetes manifests and `cloudbuild.yaml` ([repo page][r-cartmate]).
- **Autonomy:** Recommends; changes the cart when asked ("Add the blue one to cart"). Checkout hands control back to the user: "I'd be happy to help you checkout! Please fill out the form below with your details:" ([orchestrator][r-cartmate-orch], [README][r-cartmate-readme]).
- **Human story:** A persona example only: "I'm looking for something casual but stylish for a weekend brunch" ([README][r-cartmate-readme]).
- **Live URL:** None listed.
- **README structure:** Marketing style. Tagline, "What Makes CartMate Different", architecture mermaid, agent table, tech stack with code snippets, sequence diagram, quick start, configuration, project structure, testing strategy, deployment, monitoring, usage examples, contributing, security, performance, troubleshooting ([README][r-cartmate-readme]).
- **Tests:** Three backend test files (core infrastructure, websocket, websocket integration) ([tests folder][r-cartmate-tests]).
- **Why it most likely won (inference):** A polished conversational shopping demo with image-based style learning and a visible multi-agent flow, deployed on GKE. It also won the EMEA regional pool.
- **Deep-dived:** yes.

### 6. Voice Teller - Dial ADK + MCP (Honorable mention #1)

- **Post description (verbatim):** "Voice Teller is an AI phone agent that handles core banking actions (log in by voice, check balance, create transaction) by replacing clunky IVR systems with an intelligent, real-time voice interface. It runs all components on a GKE Autopilot cluster and uses Agent Development Kit (ADK) for conversational logic and tool orchestration." By Julian Hecker ([winners post][gke-win]).
- **Repo:** [github.com/julian-hecker/gke-hackathon][r-voice]: 19 commits; About "Changing how we call. Intelligent phone bots instead of clunky IVR."; links to the Devpost project ([repo page][r-voice]).
- **What it does:** A phone call (Twilio) reaches a "Voice Bridge" service. An ADK banking agent named "Sam" uses an MCP server that wraps Bank of Anthos with `login_for_token`, `get_balance` and `add_transaction` ([agent.py][r-voice-agent], [MCP main.py][r-voice-mcp], [k8s README][r-voice-k8s]).
- **Google tools and depth (medium-deep for its size):**
  - An ADK `Agent` with `McpToolset` over streamable HTTP, model `gemini-2.0-flash-exp`; a comment suggests `gemini-2.0-flash-live-001` ([agent.py][r-voice-agent]).
  - GKE Autopilot, a Gateway with a static IP, Certificate Manager wildcard certificates, and Artifact Registry ([k8s README][r-voice-k8s], [MCP README][r-voice-mcp-readme]).
  - Not used: A2A.
- **Autonomy:** Acts on the caller's spoken request, including creating a transaction. Only the prompt guards this: "When asking the user for information, confirm what they said. If you are unsure about something, ask the user for clarification." No code-level approval gate found ([agent.py][r-voice-agent]).
- **Human story:** The pain of phone menus (IVR): "Intelligent phone bots instead of clunky IVR." ([repo page][r-voice])
- **Live URL:** The k8s README lists `bank.`, `mcp.` and `voice.heckerlabs.com` (not opened) ([k8s README][r-voice-k8s]).
- **README structure:** The root README is a few lines (purpose, deployment pointer, architecture image) ([README][r-voice-readme]). The detail is in `k8s/README.md`: Autopilot cluster, static IP, certificate map, secrets, image builds, `kubectl apply -k` ([k8s README][r-voice-k8s]).
- **Tests:** The `evals` folder holds only `__init__.py` ([evals folder][r-voice-evals]). No tests.
- **Why it most likely won (inference):** A real phone call demo with ADK plus MCP on GKE Autopilot, exactly as the organizers encouraged. Small but complete.
- **Deep-dived:** yes.

### 7. CO2-Aware Shopping Assistant (Honorable mention #2)

- **Post description (verbatim):** "This project is an intelligent shopping companion that helps users make environmentally conscious purchasing decisions. It features AI-powered product discovery with real-time environmental impact scoring, sustainable shipping optimization, and uses six specialized AI agents that collaborate using the ADK, MCP, and A2A protocols on GKE Autopilot." By Prabhakaran Jayaraman Masani ([winners post][gke-win]).
- **Repo:** [github.com/prabhakaran-jm/co2-shopping-assistant][r-co2]: 101 commits, default branch `master`, website `assistant.cloudcarta.com`, topics include `a2a`, `gke`, `mcp` ([repo page][r-co2]).
- **What it does:** A shopping assistant over Online Boutique with CO2 scores, eco shipping options and agents for routing, product discovery, CO2 math, cart, checkout and comparison ([README][r-co2-readme], [submission summary][r-co2-sub]).
- **Google tools and depth (claimed deep, partly verified):**
  - The README describes ADK `LlmAgent` classes with sample code ([README][r-co2-readme]).
  - In the code I read, agents subclass a custom `BaseAgent` that calls `google.generativeai` with Gemini 2.0 Flash, and it keeps running without the model: "Non-fatal: continue without LLM" ([base_agent.py][r-co2-base]).
  - "A2A" is a custom module ([protocol.py][r-co2-a2a]), and `google-adk==1.14.1` is pinned ([requirements][r-co2-req]).
  - MCP server files exist (`boutique_mcp.py`, `co2_mcp.py`, `comparison_mcp.py`), not read ([mcp_servers folder][r-co2-mcp]).
  - Infrastructure: GKE Autopilot, Terraform, HPA, network policies, and Prometheus, Grafana and Jaeger configs ([README][r-co2-readme]).
- **Autonomy:** Assists on request; agents can add to cart and run checkout with the shipping method the user picks ([README][r-co2-readme]). No approval gate found.
- **Human story:** None named; the motive is sustainability.
- **Live URL:** `assistant.cloudcarta.com` (not opened) ([submission summary][r-co2-sub]).
- **README structure:**
  - Very long: badges, "Hackathon Alignment" (maps the project to the guidelines), features and optimizations, agent architecture with code samples, "5-Minute Judge Testing Setup", "Key Demo Points for Judges", a cost table, deployment options.
  - It also lists "Success Metrics" with numbers the repo does not back up, such as "**25% reduction** in average CO2 emissions per order" and "**99.9% uptime**" ([README][r-co2-readme]).
- **Tests:** `tests/` with `unit`, `integration`, `performance`, `e2e`, `ui`, `fixtures`, plus `pytest.ini` ([tests folder][r-co2-tests]).
- **Why it most likely won, and why only an honorable mention (inference):** It named every encouraged protocol and showed real operations depth on GKE, and it wrote directly to the judges. But the README claims run ahead of the code, and the grand prize went to a simpler, more honest repo.
- **Deep-dived:** yes.

### 8. Vigil AI (Honorable mention #3)

- **Post description (verbatim):** "Vigil AI is a proactive, hierarchical multi-agent system designed to enhance the security of the Bank of Anthos application against sophisticated fraud. It uses four specialized agents (TransactionMonitor, Orchestrator, Investigation Agent, Actuator) orchestrated on GKE to flag suspicious activity, investigate using a Gemini model, and lock the user's account if necessary, without modifying the existing application code." By Ayan Liger ([winners post][gke-win]).
- **Repo:** [github.com/ayanliger/gke-turns10-hackathon-vigil][r-vigil]: 69 commits, branch `master`, MIT; README badge "GKE Turns 10 - Honorable Mention"; Bank of Anthos included as a git submodule ([repo page][r-vigil], [README][r-vigil-readme]).
- **What it does:**
  - A Transaction Monitor polls the ledger for transactions over $1,000 and alerts the Orchestrator.
  - The Orchestrator (ADK, Gemini 2.5 Flash) asks an Investigation Agent (ADK) for a 0-10 risk score.
  - If the score is 7 or more, an Actuator locks the account through a "GenAI Toolbox" Go service that exposes fixed database operations. All agents talk over A2A ([README][r-vigil-readme]).
- **Google tools and depth (medium-deep):** ADK `LlmAgent` with `Gemini(model="gemini-2.5-flash")` ([orchestrator agent.py][r-vigil-orch]), `a2a-sdk` ([requirements][r-vigil-req]), GKE, Artifact Registry, per-agent Kubernetes manifests ([README][r-vigil-readme]).
- **Autonomy (acts alone):**
  - Accounts are locked with no human approval.
  - If the LLM fails to call the Actuator when the score is over the threshold, code locks the account anyway, logged as "Automatic fallback: risk score ..." ([orchestrator agent.py][r-vigil-orch]).
  - The README lists "**Human-in-the-Loop**: Add approval workflow for high-stakes enforcement actions" as an unchecked future improvement ([README][r-vigil-readme]).
- **Human story:** None named.
- **Live URL:** None. YouTube demo `youtube.com/watch?v=S7xQgOoeFOw` (not opened) ([README][r-vigil-readme]).
- **README structure:** Badges, short pitch, ASCII architecture, components table, key features, a 6-step "Detection Flow", deployment, configuration table (thresholds as environment variables), observing with kubectl, future improvements, tech stack ([README][r-vigil-readme]).
- **Tests:** None found ([repo page][r-vigil], [orchestrator folder][r-vigil-orchdir]).
- **Why it most likely won (inference):** It is the only winner close to the organizers' "monitor and act" idea. It also has a clear agent hierarchy over A2A, explicit thresholds, and a non-invasive add-on to the sample app.
- **Deep-dived:** yes.

---

## What Google judges rewarded

The posts publish no scores, so the patterns below combine what the posts say with what I saw in the winning repos. Counts are mine.

**What Google says it rewarded (quotes):**

- Gemini Live: "technical precision with bold imagination", and agents that "break out of the traditional 'text box' paradigm" and help users "see, hear, speak, and create in real time" ([winners post][glac-win]).
- GKE Turns 10: "creativity, technical mastery, and deep understanding of GKE and AI", and "technical execution on GKE" ([winners post][gke-win]).
- Both contests required deployment on Google Cloud and a Google model ([Gemini announcement][glac-join], [GKE announcement][gke-join]).

**Patterns in the winners (evidence):**

1. **Solo builders win.** 8 of 12 Gemini Live winners, including the grand prize and all three special awards, and 6 of 8 GKE winners, including the grand prize, are credited to one person ([Gemini winners post][glac-win], [GKE winners post][gke-win]).
2. **A concrete person in a concrete moment comes first.** Every post description leads with a situation: a surgeon "without breaking scrub", a family history, a driver reporting potholes, "what to make for dinner" ([Gemini winners post][glac-win], [GKE winners post][gke-win]).
3. **Real-world or real-computer action earned the grand prize and two of three category prizes.** Robotic surgery (grand prize), a flying drone (Live Agent), and mouse and keyboard control of a desktop (UI Navigator). The exception is Sankofa, a storytelling app (Creative Storyteller) ([winners post][glac-win]).
4. **The sponsor's stack, used deeply and named feature by feature.** Winning READMEs list exact features: ADK sub-agents, `transfer_to_agent` and tool callbacks ([ORION][r-orion-readme]); Live API barge-in, context window compression and session resumption ([drone-copilot][r-drone-readme]); affective dialog ([Rayan][r-rayan-readme]); the official A2A SDK on GKE ([cart-to-kitchen][r-c2k-cart]).
5. **Proof that it runs on Google Cloud.** All 7 Gemini repos I read deploy to Cloud Run. Several add Cloud Build CI/CD ([ORION][r-orion-readme]), Terraform ([Rayan][r-rayan-readme], [drone-copilot][r-drone-readme]), or a "proof of GCP deployment" asset ([VibeCat][r-vibecat-readme]). All 7 GKE repos I read ship Kubernetes manifests or GKE deploy steps; four name GKE Autopilot (cart-to-kitchen per the [post][gke-win], [Voice Teller][r-voice-k8s], [CO2-Aware][r-co2-readme], and V-Commerce's [later README][r-vcom2-readme]).
6. **Safety and human control appear as features.** Approaches seen across the winners:
   - Display-only tools and argument whitelists ([ORION][r-orion-agent]).
   - A code safety guard under the LLM ([drone-copilot][r-drone-guard]).
   - A deterministic policy gate plus human approval ([JohnKeats.AI][r-keats-gate]).
   - A risk-tiered "Proceed" gate ([Moonwalk][r-moonwalk-core]).
   - A keyword risk gate plus confirm-before-act ([VibeCat][r-vibecat-nav]).
   - Admin approve or reject of generated ads ([V-Commerce][r-vcom-video]).
   - A user click before cart writes ([cart-to-kitchen][r-c2k-svc]).

   Vigil AI is the only repo I read that takes a high-stakes action no human asked for (locking a bank account), and it ranked as an honorable mention ([README][r-vigil-readme]).
7. **Tests, commit counts and README hype did not decide the top prize.** ORION, the Gemini grand prize, has no tests folder ([repo page][r-orion]). Cart-to-kitchen, the GKE grand prize, has one commit and a plain README ([repo page][r-c2k]). The CO2 assistant had the biggest claims and a judge-facing README but got an honorable mention ([README][r-co2-readme]). (Inference: these things help but are not what wins.)
8. **The ops idea did not win at GKE Turns 10.** The announcement suggested an agent that "monitors microservice performance on GKE, suggests troubleshooting steps, and even automates remediation" ([announcement][gke-join]). None of the 8 winner descriptions is that ([winners post][gke-win]). Five are shopping or retail, three are banking, and the closest is Vigil AI's fraud response.
9. **Judge-friendly demos.** drone-copilot ships a replay mode so no drone is needed ([README][r-drone-readme]). Six of the 14 repos I read link a demo video in the README (ORION, drone-copilot, Moonwalk, JohnKeats.AI, VibeCat, Vigil AI); the others may have linked one only on Devpost (unverified).

**What this suggests for Life After Code (inference):**

- Open with one person and one moment, then show the agent acting in the real world or on a real system, not in a chat box.
- Make the human approval step part of the demo, not a footnote. The strongest pattern is a code gate (rules, not a prompt) plus one clear human "approve" moment, as in VibeCat, JohnKeats.AI and Moonwalk. Show what the agent does on its own and where it stops.
- If you use Google pieces, use them deeply and name the features (ADK sub-agents and callbacks, Live API barge-in and session resumption, Cloud Run deployed by CI). Show proof that it runs.
- Give judges a way to try it without your setup (a replay or mock mode), plus a demo of 4 minutes or less (per VibeCat's notes; unverified).
- Keep claims modest and state limits, as ORION's disclaimer does. Unbacked metrics did not help the CO2 assistant.
- Building solo is normal among these winners.

---

## Blocked

- **devpost.com and its subdomains:** all 20 winner project pages linked from the posts, plus `geminiliveagentchallenge.devpost.com` and `gketurns10.devpost.com` (official rules and judging criteria). Not attempted, per the access notes. Judging criteria therefore stay unverified.
- **YouTube and Vimeo videos (links recorded, content could not be opened):**
  - Gemini Live kickoff video `https://www.youtube.com/watch?v=-AAwoj4qN8M` ([announcement][glac-join]); Next '26 livestream `https://www.youtube.com/watch?v=N7N0TU9tkzw` ([winners post][glac-win]).
  - ORION: `https://vimeo.com/1173959084?fl=ip&fe=ec` and `https://youtu.be/LLaFp_8n4k0`.
  - drone-copilot: `https://youtu.be/_FCgmYjGCVs` and `https://youtu.be/38d4ZavOyTw`.
  - Moonwalk: `https://youtu.be/u3QoaT3pIMs`. JohnKeats.AI: `https://youtu.be/zNKhR3e2ym4`. VibeCat: `https://youtu.be/j1zzfoDr7qA`. Vigil AI: `https://www.youtube.com/watch?v=S7xQgOoeFOw`.
- **siliconangle.com:** the article on Amie Wei's interview, linked from the GKE winners post, was blocked by the egress proxy (1 attempt).
- **dev.to:** JohnKeats.AI's build blog and VibeCat's 18-post series were blocked by the egress proxy (1 attempt).
- **LinkedIn and Instagram:** the House of Kube interview and the Next '26 social recap were not attempted.
- **Live demo hosts:** all blocked by the egress proxy (CONNECT 403), so whether each app is still live is unverified:
  - `orion-518946358970.us-central1.run.app` (also blocked in WebFetch)
  - `johnkeats.ai`, `rayan-memory.web.app`, `www.getmoonwalk.top`
  - `assistant.cloudcarta.com`, `vcommercestudio.xyz`
  - `bank.heckerlabs.com`, `voice.heckerlabs.com`
- **GitHub through the shell proxy:** repo archives, repo HTML pages and `api.github.com` returned 403 ("GitHub access to this repository is not enabled for this session"). `data.jsdelivr.com` was refused. I used WebFetch for github.com pages and raw.githubusercontent.com for files instead. GitHub search rate-limited one query (HTTP 429), which I re-ran with different terms.
- **Repos not found:** Wand, NagarDrishti, Ekaette, Call My Parts, Relay (Gemini Live); CardOS (GKE).

---

## Sources

[glac-win]: https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-of-the-gemini-live-agent-challenge
[glac-join]: https://cloud.google.com/blog/topics/training-certifications/join-the-gemini-live-agent-challenge
[whatsnew-2026]: https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud
[gke-win]: https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-from-gke-hackathon
[gke-join]: https://cloud.google.com/blog/topics/training-certifications/join-the-gke-turns-10-hackathon
[whatsnew-2025]: https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud-2025
[d-orion]: https://devpost.com/software/orion-operating-room-intelligent-orchestration-node
[d-drone]: https://devpost.com/software/drone-copilot
[d-sankofa]: https://devpost.com/software/sankofa-y47f9p
[d-moonwalk]: https://devpost.com/software/moonwalk-tojsay
[d-wand]: https://devpost.com/software/wand-a-live-agent-that-sees-browses-and-clicks-with-you
[d-keats]: https://devpost.com/software/johnkeats-ai
[d-rayan]: https://devpost.com/software/rayan-memory
[d-nagar]: https://devpost.com/software/nagardrishti
[d-ekaette]: https://geminiliveagentchallenge.devpost.com/submissions/970955-ekaette
[d-vibecat]: https://geminiliveagentchallenge.devpost.com/submissions/949057-vibecat
[d-parts]: https://geminiliveagentchallenge.devpost.com/submissions/945801-call-my-parts
[d-relay]: https://geminiliveagentchallenge.devpost.com/submissions/967879-relay-real-time-voice-vision-lab-tutor-for-electronics
[d-c2k]: https://devpost.com/software/cart-to-kitchen-gke-ai-assistant
[d-cardos]: https://devpost.com/software/cardos
[d-nero]: https://devpost.com/software/neroai
[d-vcom]: https://devpost.com/software/v-commerce-studio
[d-cartmate]: https://devpost.com/software/cartmate-mygdtk
[d-voice]: https://devpost.com/software/voice-teller-dial-adk-mcp
[d-co2]: https://devpost.com/software/co2-aware-shopping-assistant
[d-vigil]: https://devpost.com/software/vigil-ai
[r-orion]: https://github.com/40tify/orion
[r-orion-readme]: https://github.com/40tify/orion/blob/main/README.md
[r-orion-agent]: https://github.com/40tify/orion/blob/main/app/orion_orchestrator/agent.py
[r-orion-tools]: https://github.com/40tify/orion/blob/main/app/orion_orchestrator/tools.py
[r-drone]: https://github.com/BryenInsights/drone-copilot
[r-drone-readme]: https://github.com/BryenInsights/drone-copilot/blob/main/README.md
[r-drone-session]: https://github.com/BryenInsights/drone-copilot/blob/main/backend/src/gemini_session.py
[r-drone-tools]: https://github.com/BryenInsights/drone-copilot/blob/main/backend/src/models/tools.py
[r-drone-config]: https://github.com/BryenInsights/drone-copilot/blob/main/backend/src/config.py
[r-drone-guard]: https://github.com/BryenInsights/drone-copilot/blob/main/client/src/drone/safety_guard.py
[r-drone-test]: https://github.com/BryenInsights/drone-copilot/blob/main/tests/validate_live_api.py
[r-sankofa]: https://github.com/Jeremiah-Sakuda/Sankofa
[r-sankofa-readme]: https://github.com/Jeremiah-Sakuda/Sankofa/blob/main/README.md
[r-sankofa-agent]: https://github.com/Jeremiah-Sakuda/Sankofa/blob/main/backend/app/services/adk_agent.py
[r-sankofa-tests]: https://github.com/Jeremiah-Sakuda/Sankofa/tree/main/backend/tests
[r-moonwalk]: https://github.com/OactoDev/Moonwalk
[r-moonwalk-readme]: https://github.com/OactoDev/Moonwalk/blob/main/README.md
[r-moonwalk-core]: https://github.com/OactoDev/Moonwalk/blob/main/backend/agent/core_v2.py
[r-moonwalk-router]: https://github.com/OactoDev/Moonwalk/blob/main/backend/providers/router.py
[r-moonwalk-mem]: https://github.com/OactoDev/Moonwalk/blob/main/backend/agent/cloud_memory.py
[r-moonwalk-req]: https://github.com/OactoDev/Moonwalk/blob/main/backend/requirements.txt
[r-moonwalk-tests]: https://github.com/OactoDev/Moonwalk/tree/main/tests
[r-keats]: https://github.com/johnkeats-ai/johnkeats-ai
[r-keats-readme]: https://github.com/johnkeats-ai/johnkeats-ai/blob/main/README.md
[r-keats-agent]: https://github.com/johnkeats-ai/johnkeats-ai/blob/main/backend/app/keats_agent/agent.py
[r-keats-gate]: https://github.com/johnkeats-ai/johnkeats-ai/blob/main/backend/app/agents/policy_gate.py
[r-keats-evals]: https://github.com/johnkeats-ai/johnkeats-ai/tree/main/backend/app/evals
[r-rayan]: https://github.com/yelnady/rayan
[r-rayan-readme]: https://github.com/yelnady/rayan/blob/main/README.md
[r-rayan-story]: https://github.com/yelnady/rayan/blob/main/STORY.md
[r-rayan-req]: https://github.com/yelnady/rayan/blob/main/backend/requirements.txt
[r-rayan-capture]: https://github.com/yelnady/rayan/blob/main/backend/app/agents/capture_agent.py
[r-rayan-arch]: https://github.com/yelnady/rayan/blob/main/backend/app/agents/memory_architect.py
[r-rayan-pkg]: https://github.com/yelnady/rayan/blob/main/frontend/package.json
[r-vibecat]: https://github.com/Two-Weeks-Team/vibeCat
[r-vibecat-readme]: https://github.com/Two-Weeks-Team/vibeCat/blob/master/README.md
[r-vibecat-devpost]: https://github.com/Two-Weeks-Team/vibeCat/blob/master/docs/DEVPOST_SUBMISSION.md
[r-vibecat-nav]: https://github.com/Two-Weeks-Team/vibeCat/blob/master/backend/realtime-gateway/internal/ws/navigator.go
[r-vibecat-ws]: https://github.com/Two-Weeks-Team/vibeCat/tree/master/backend/realtime-gateway/internal/ws
[r-vibecat-gomod]: https://github.com/Two-Weeks-Team/vibeCat/blob/master/backend/adk-orchestrator/go.mod
[vc-challenge]: https://github.com/Two-Weeks-Team/vibeCat/blob/master/docs/challenge/README.md
[r-c2k]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke
[r-c2k-readme]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke/blob/main/README.md
[r-c2k-svc]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke/blob/main/src/recipeservice/README.md
[r-c2k-svcdir]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke/tree/main/src/recipeservice
[r-c2k-agent]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke/blob/main/src/recipeservice/multi_tool_agent/agent.py
[r-c2k-cart]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke/blob/main/src/cartadderagent/agent_server.py
[r-c2k-cartdir]: https://github.com/amiewei/cart-to-kitchen-ai-assistant-gke/tree/main/src/cartadderagent
[r-nero]: https://github.com/xValentim/nero-fashion
[r-nero-readme]: https://github.com/xValentim/nero-fashion/blob/main/README.md
[r-nero-app]: https://github.com/xValentim/nero-fashion/blob/main/src/nanobananaservice/app.py
[r-nero-req]: https://github.com/xValentim/nero-fashion/blob/main/src/nanobananaservice/requirements.in
[r-nero-dir]: https://github.com/xValentim/nero-fashion/tree/main/src/nanobananaservice
[r-nero-fe]: https://github.com/giovannamoeller/nero-fashion-frontend
[r-vcom]: https://github.com/Siddharth-Khattar/gke-online-boutique
[r-vcom-readme]: https://github.com/Siddharth-Khattar/gke-online-boutique/blob/main/README.md
[r-vcom-src]: https://github.com/Siddharth-Khattar/gke-online-boutique/tree/main/src
[r-vcom-peau]: https://github.com/Siddharth-Khattar/gke-online-boutique/blob/main/src/peau_agent/peau_agent.py
[r-vcom-video]: https://github.com/Siddharth-Khattar/gke-online-boutique/blob/main/src/video_generation/main.py
[r-vcom2]: https://github.com/mvp-ing/v-commerce-studio
[r-vcom2-readme]: https://github.com/mvp-ing/v-commerce-studio/blob/main/README.md
[r-vcom2-commits]: https://github.com/mvp-ing/v-commerce-studio/commits/main/
[r-cartmate]: https://github.com/victorbash400/Cartmate
[r-cartmate-user]: https://github.com/victorbash400?tab=repositories
[r-cartmate-readme]: https://github.com/victorbash400/Cartmate/blob/main/README.md
[r-cartmate-agents]: https://github.com/victorbash400/Cartmate/tree/main/cartmate-backend/agents
[r-cartmate-orch]: https://github.com/victorbash400/Cartmate/blob/main/cartmate-backend/agents/orchestrator_refactored.py
[r-cartmate-req]: https://github.com/victorbash400/Cartmate/blob/main/cartmate-backend/requirements.txt
[r-cartmate-tests]: https://github.com/victorbash400/Cartmate/tree/main/cartmate-backend/tests
[r-voice]: https://github.com/julian-hecker/gke-hackathon
[r-voice-readme]: https://github.com/julian-hecker/gke-hackathon/blob/main/README.md
[r-voice-agent]: https://github.com/julian-hecker/gke-hackathon/blob/main/libs/adk-agents/src/adk_agents/agents/banking_agent/agent.py
[r-voice-mcp]: https://github.com/julian-hecker/gke-hackathon/blob/main/apps/anthos-mcp/src/anthos_mcp/main.py
[r-voice-mcp-readme]: https://github.com/julian-hecker/gke-hackathon/blob/main/apps/anthos-mcp/README.md
[r-voice-k8s]: https://github.com/julian-hecker/gke-hackathon/blob/main/k8s/README.md
[r-voice-evals]: https://github.com/julian-hecker/gke-hackathon/tree/main/libs/adk-agents/src/adk_agents/evals
[r-co2]: https://github.com/prabhakaran-jm/co2-shopping-assistant
[r-co2-readme]: https://github.com/prabhakaran-jm/co2-shopping-assistant/blob/master/README.md
[r-co2-sub]: https://github.com/prabhakaran-jm/co2-shopping-assistant/blob/master/SUBMISSION_SUMMARY.md
[r-co2-base]: https://github.com/prabhakaran-jm/co2-shopping-assistant/blob/master/src/agents/base_agent.py
[r-co2-a2a]: https://github.com/prabhakaran-jm/co2-shopping-assistant/blob/master/src/a2a/protocol.py
[r-co2-req]: https://github.com/prabhakaran-jm/co2-shopping-assistant/blob/master/requirements.txt
[r-co2-mcp]: https://github.com/prabhakaran-jm/co2-shopping-assistant/tree/master/src/mcp_servers
[r-co2-tests]: https://github.com/prabhakaran-jm/co2-shopping-assistant/tree/master/tests
[r-vigil]: https://github.com/ayanliger/gke-turns10-hackathon-vigil
[r-vigil-readme]: https://github.com/ayanliger/gke-turns10-hackathon-vigil/blob/master/README.md
[r-vigil-orch]: https://github.com/ayanliger/gke-turns10-hackathon-vigil/blob/master/vigil-system/orchestrator_agent/agent.py
[r-vigil-orchdir]: https://github.com/ayanliger/gke-turns10-hackathon-vigil/tree/master/vigil-system/orchestrator_agent
[r-vigil-req]: https://github.com/ayanliger/gke-turns10-hackathon-vigil/blob/master/vigil-system/orchestrator_agent/requirements.txt

Source list (same links as above, visible):

- Gemini Live winners post: https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-of-the-gemini-live-agent-challenge
- Gemini Live announcement: https://cloud.google.com/blog/topics/training-certifications/join-the-gemini-live-agent-challenge
- What's new in Google Cloud (2026 log): https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud
- GKE Turns 10 winners post: https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-from-gke-hackathon
- GKE Turns 10 announcement: https://cloud.google.com/blog/topics/training-certifications/join-the-gke-turns-10-hackathon
- What's new in Google Cloud (2025 log): https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud-2025
