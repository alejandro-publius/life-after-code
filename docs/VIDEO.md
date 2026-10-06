# Video script

An English narrated video for Devpost, **target 2:40 and strictly below 3:00**, uploaded to YouTube with visibility set to Public. Judges may assess only the description, images and video, so show the human problem and functioning demo in the first 30 seconds. [Official rules](https://gitlab-transcend.devpost.com/rules).

This version can be filmed from the current local browser app. Start it using the [README quickstart](../README.md#try-one-night-in-the-browser), then record `http://localhost:8080/demo`. Every app shot below exists in this replay. No live GitLab, cloud, model or phone notification footage is assumed.

Keep a readable label on screen: **"Local demo replay. Simulated shop. Planted faults. Recorded agent replies."** Introduce Priya as a demo persona. Browser controls select recorded demo choices. The morning decision is recorded too. Local screenshots are [phone](images/demo-phone.png) and [laptop](images/demo-laptop.png).

## Shot list and narration

| Time | Filmable screen | Narration |
|---|---|---|
| 0:00 to 0:12 | Before bed chapter in a phone-sized viewport. Two orders visible. Click **Sign demo orders**. | "If you are the only engineer on call, one obvious fix can break your night's sleep. Night Orders lets you sign what the agent may do before bed. Everything else still needs you." |
| 0:12 to 0:30 | Continue to the inventory wake-up. Show both chart lines rising, the three-line message and **Approve demo fallback**. Click it. | "Priya is a demo persona. Here, both checkout paths fail. The recorded agent reply declines the narrow order and asks her about one fallback. She approves. This wake-up has a reason." |
| 0:30 to 0:48 | Continue to the checkout alert. Show the old and new lines, dashed 5% threshold and action marker. | "Later, only the new checkout fails. It has stayed above five percent for five complete minutes. This time, code applies the order she already signed, turns that path off and checks recovery. Priya stays asleep." |
| 0:48 to 1:10 | Open **Read the decision evidence**. Show signature, expiry, checks and ledger around 03:13 and 03:23. | "The model chooses where to look. Code decides what is true. The signature, expiry, measured condition, exact action and first use must all pass. The action comes from the signed file. Agent words and log instructions cannot widen it." |
| 1:10 to 1:31 | Return to Before bed. Select **Try leaving them unsigned**, then show the checkout outcome without authority. | "Leave the draft unsigned and the same fault gets a different answer: code wakes Priya and makes no automatic change. These buttons choose recorded demo inputs. They do not sign a real order or change GitLab." |
| 1:31 to 1:58 | Restore the signed and approved path, then open Over coffee. Show 1 wake-up, 1 automatically handled incident, 1 approved action; show keep and undo. | "On the signed and approved path, the ledger records one wake-up, one incident handled while she slept and one approved action. At seven, permission ends. The recorded morning countersign keeps checkout off and undoes the temporary fallback. Expiry itself does not undo changes." |
| 1:58 to 2:22 | Evidence panel: ledger, chart sample table, morning record. Briefly show the repository's Watch and flow files with legible captions. | "The replay uses the existing Watch code in isolated memory. Its chart and counts come from that result. Shop traffic, faults and agent replies are demo data. Three Duo flows are defined and validated, but live Duo execution, GitLab pipeline history and cloud deployment are still pending." |
| 2:22 to 2:40 | Close evidence and show morning brief in laptop layout. End on title and repository link. | "The intended audience is a small team without a follow-the-sun rotation. We have not measured sleep saved. What you can inspect today is the boundary: one exact action she permitted, a necessary wake-up outside it, and a clear account over coffee." |

## Recording notes

- Record the browser at laptop and phone-sized widths. Keep text large enough to read in the final video; crop around the active chapter and evidence.
- Pause on the two human choices, then on the chart and morning counts. Use cuts between scenes, and label the simulated night times clearly.
- Record the signed and approved run first, then the unsigned comparison. Restore the default path before showing morning.
- Include no invented production impact, fabricated green pipeline or simulated screen presented as a live integration.
- Check the final duration in the YouTube player, readable labels, English narration and access from a logged-out browser. Add the public link to [DEVPOST.md](DEVPOST.md).

## When real integration footage is available

Replace part of the 1:58 to 2:22 segment with captured Duo execution, real GitLab pipeline history and the public application URL only after those runs exist. Keep demo fault and persona labels. Update the narration and [Status](STATUS.md) to match exactly what the footage proves. The current browser video alone does not establish the required GitLab Duo integration or the Google Cloud bonus.
