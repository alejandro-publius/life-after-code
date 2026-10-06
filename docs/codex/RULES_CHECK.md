# Rules check

Checked on 2026-10-06. This check reads the five pages requested for this task, rather than relying on the old handoff. The official rules control where event materials disagree, as stated in Section 11.

Quotes preserve the source words. HTML markup and layout whitespace are removed. Under the repository's dash rule and `docs/DECISIONS.md`, every long dash in quoted text is replaced by a spaced ASCII hyphen. Those specific quotes therefore have normalized punctuation, not byte-for-byte punctuation. No other wording is changed.

The current deadline is **October 27, 2026 at 1:00 pm UTC (13:00 UTC)**. Five equally weighted criteria imply **20% each**, before the optional Google Cloud addition. A genuine GitLab Duo Agent Platform feature is mandatory, not an optional bonus. A standalone Claude API integration does not satisfy that requirement.

For this Path A entry: create new work on or after October 5; submit a public MIT-licensed GitLab repository, visible running CI/CD history, an English description, and a public YouTube demonstration strictly under three minutes. Deployment is optional for Path A. For the Google Cloud bonus, include the deployment code and a public live Google Cloud URL. These points are quoted below.

## Retrieval status

| Requested page | Direct canonical request | Successful reading |
| --- | --- | --- |
| [Main](https://gitlab-transcend.devpost.com/) | HTTP 403 | Same official page with `?amp=1`, HTTP 200 |
| [Rules](https://gitlab-transcend.devpost.com/rules) | HTTP 403 | Same official page with `?amp=1`, HTTP 200 |
| [Resources](https://gitlab-transcend.devpost.com/resources) | HTTP 403 | Same official page with `?amp=1`, HTTP 200 |
| [Dates](https://gitlab-transcend.devpost.com/details/dates) | HTTP 403 | Same official page with `?amp=1`, HTTP 200 |
| [Updates](https://gitlab-transcend.devpost.com/updates) | HTTP 403 | Same official page with `?amp=1`, HTTP 200 |

All five were read successfully. The bare URLs were blocked in the initial HTTP client, not left unread. Requests using a curl user agent and `Accept: text/html` succeeded. The web retrieval tool also read the canonical pages. `source-status.json` records the successful URLs, status and content hashes. Dates or organizer instructions may change, so check again before submission.

## Deadline and judging dates

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Registration Period: September 29, 2026 (10:00 am UTC) - October 27, 2026 (1:00 pm UTC) (“Registration Period”).
>
> Submission Period: October 5, 2026 (10:00 am UTC) - October 27, 2026 (1:00 pm UTC) ("Submission Period").
>
> Judging Period: October 28, 2026 (10:00 am UTC) - November 14, 2026 (5:00 pm UTC) ("Judging Period").
>
> Winners Announced: On or around November 16, 2026 (2:00 pm UTC).

## Registration and required access

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Entrants may enter by visiting gitlab-transcend.devpost.com ("Hackathon Website") and following the below steps:
>
> Register for the Hackathon on the Hackathon Website by clicking the "Join Hackathon" button. To complete registration, sign up to create a free Devpost account, or log in with an existing Devpost account. This will enable you to receive important updates and to create your Submission.
>
> Register as a GitLab Contributor.
>
> Upon approval from GitLab (about 24 business hours), you will receive automatic provisioning to a group and subgroup with the appropriate access level, a project within the subgroup, and a welcome onboarding issue.
>
> Entrants will obtain access to the required developer tools/platform and complete a Project described below in Project Requirements. Use of the developer tools will be subject to the license agreement related thereto. Entry in the Hackathon constitutes consent for the Sponsor and Devpost to collect and maintain an entrant's personal information for the purpose of operating and publicizing the Hackathon.
>
> Complete and enter all of the required fields on the "Enter a Submission" page of the Hackathon Website (each a "Submission") during the Submission Period and follow the requirements below.

The linked Contributor registration is [https://contributors.gitlab.com/transcend-hackathon](https://contributors.gitlab.com/transcend-hackathon). Allow time for the stated approval process. Do not assume that creating an ordinary GitLab account alone grants hackathon Duo access.

## Required Duo use and autonomy level

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> What to Create: Select one of the following Paths: Start Fresh or Bring Your Own and build a project using GitLab Duo Agent Platform that fits within one of three levels of autonomy (each a Project):
>
> Assisted: you approve every step. Your agents/flows propose actions and wait for your go-ahead before proceeding. You stay in the loop at every stage.
>
> -> Example: An agent reviews your MR and flags a security vulnerability. It suggests a fix and waits for you to approve before committing. Then it runs the pipeline and waits for you to approve the deployment.
>
> Supervised: you approve the outcome, not the individual steps. Your agents execute a multi-step workflow on their own, clearing gates and making decisions along the way. You review the end result, not every individual action.
>
> -> Example: You push code. Agents handle code review, fix a failing pipeline, remediate a security finding, and deploy to staging. You get a summary and approve the production deployment.
>
> Hands-off: you set the intent and walk away. A full loop from code to production with no human in the middle. You push code or create an issue, and the next time you check in, it's live.
>
> -> Example: You create an issue. Agents review it, create 1+ MRs, run security scans, fix what they find, merge when everything passes, deploy to staging, validate, promote to production, and post a summary on the original issue. You touched nothing.
>
> The examples above are here to get you thinking. We expect submissions that go well beyond them.

## Required Duo use confirmed by the main page

Source: [https://gitlab-transcend.devpost.com/](https://gitlab-transcend.devpost.com/).

> Every project must use GitLab Duo Agent Platform features, such as agents, flows, or MCP clients.

## Path A, Path B, new work and functionality

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Path A: Start Fresh
>
> Build a new AI powered project on GitLab that demonstrates agentic automation of the post-code lifecycle. You create the app, the CI/CD pipeline, and the automation from scratch. The focus is on how many post-code steps your agents handle in the DevSecOps lifecycle including but not limited to: code review, security scanning, testing, compliance, deployment, monitoring, etc.
>
> Path B: Bring Your Own
>
> Take an existing open-source project (yours or forked, MIT license), import it to GitLab, and build the AI powered post-code automation around it to be deployed on any platform*. The focus is on showing what a real project gains when it moves to GitLab's full lifecycle platform: the "before" (manual, fragmented) vs. the "after" (automated, integrated).
>
> *Projects deployed on Google Cloud are eligible for 0.2 Bonus Points. See Section 6 for details.
>
> Functionality: The Project must be capable of being successfully installed and running consistently on the platform for which it is intended and must function as depicted in the video and/or expressed in the text description.
>
> Platforms: A submitted Project must run on the platform for which it is intended and which is specified in the Submission Requirements.
>
> New & Existing: Projects must be either newly created on or after October 5, 2026 by the Entrant in Path A or, if the Entrant’s Project is entered into Path B, it may have existed prior to the Hackathon Submission Period, and must have been updated to build the AI-powered post-code automation and deployed to any platform (preferably Google Cloud) after the start of the Hackathon Submission Period. All existing Projects must include a URL to the original MIT licensed and open-sourced project .
>
> Third Party Integrations: If a Project integrates any third-party SDK, APIs and/or data, Entrant must be authorized to use them in accordance with any terms and conditions or licensing requirements of the tool.

## Every required submission item

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Submissions to the Hackathon must meet the following requirements:
>
> Include a Project built with the required developer technologies and meets the above Project Requirements.
>
> Include a text description that should explain the features and functionality of your Project.
>
> Provide a public GitLab URL to your code repository for judging and testing. The repository must contain all necessary source code, assets, and instructions required for the project to be functional. The repository must be public and must be open source MIT-licensed by including an MIT license file. This license should be detectable and visible at the top of the repository page (in the About section).
>
> The project's CI/CD pipeline history must be visible and show the automation running.
>
> If you enter Path B, URL to original MIT licensed and open-sourced project (REQUIRED)
>
> If entering Path B, URL to deployed Project which is publicly accessible and available to judges.
>
> It should stay live until winners are announced on or around November 16, 2026.
>
> If entering your Project for Bonus Points, provide a live project deployed on Google Cloud which is publicly accessible and available to judges.
>
> Include a demonstration video of your Project. The video portion of the Submission:
>
> should be less than three (3) minutes. Judges are not required to watch beyond three minutes
>
> should include footage that shows the Project functioning on the device for which it was built
>
> must be uploaded to and made publicly visible on YouTube and a link to the video must be provided on the submission form on the Hackathon Website; and
>
> must not include third party trademarks, or copyrighted music or other material unless the Entrant has permission to use such material.

## Description and optional prize submission details

Source: [https://gitlab-transcend.devpost.com/](https://gitlab-transcend.devpost.com/).

> A text description of what your project does, the problem it solves, and how you used GitLab to automate the post-code lifecycle.
>
> Explain what you added or changed during the Submission Period. The agentic automation and the deployment must be new work, done on or after October 5th.
>
> Optional: Most Environmentally Impactful prize. To be considered for the Environmentally Impactful Prize, explain how your Project demonstrates exceptional sustainability practices in its design, from model and pipeline optimization to energy-efficient architecture choices. It should quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks.

## Video host and length clarification

Source: [https://gitlab-transcend.devpost.com/resources](https://gitlab-transcend.devpost.com/resources).

> How long can my demo video be?
>
> Under three minutes. Upload it to YouTube and set it to Public or Unlisted, not Private. Judges are not required to watch past three minutes.

Use a video below 3:00, such as 2:40, and set YouTube visibility to Public. The FAQ also permits Unlisted; Public follows the stricter wording in the rules. The rules allow third-party material only with permission.

## Repository and licence requirements

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Submission IP requirements
>
> By entering this Hackathon, Entrants agree to the following licensing requirements:
>
> Original Work: Any software and associated documentation files owned or created by Entrant as part of the Submission, including agent configuration YAML files, are subject to the MIT License and GitLab's Developer Certificate of Origin (version 1.1), located here: https://docs.gitlab.com/ee/legal/developer_certificate_of_origin.html.
>
> Third-Party Components: Entrants may include third-party open source software in their Project, provided the Entrant complies with the applicable open source licenses, which must be Open Source Initiative (OSI) approved licenses. Entrants are responsible for ensuring license compatibility.
>
> Projects must not violate the intellectual property rights or other rights including but not limited to copyright, trademark, patent, contract, and/or privacy rights, of any other person or entity.

A root `LICENSE` must contain the MIT text and be detected in GitLab's About section. The rules also refer to [GitLab's Developer Certificate of Origin](https://docs.gitlab.com/ee/legal/developer_certificate_of_origin.html). Preserve licences for third-party components and confirm compatibility. Do not sign a certificate on Alex's behalf.

## Testing access and English materials

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Testing
>
> Access must be provided to an Entrant's working Project for judging and testing by providing a link to the code repository. If Entrant's repository is private, Entrant must include access instructions. The Entrant must make the Project available free of charge and without any restriction, for testing, evaluation and use by the Sponsor, Administrator and Judges until the Judging Period ends. Judges are not required to test the Project and may choose to judge based solely on the text description, images, and video provided in the Submission.
>
> Language Requirements
>
> All Submission materials must be in English or, if not in English, the Entrant must provide an English translation of the demonstration video, text description, and testing instructions as well as all other materials submitted.

## Judging stages, criteria and weights

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Stage One) The first stage will determine via pass/fail whether the ideas meet a baseline level of viability, in that the Project reasonably fits the theme and reasonably uses GitLab Duo Agent Platform.
>
> Stage Two) All Submissions that pass Stage One will be evaluated in Stage Two based on the following equally-weighted criteria (the "Judging Criteria"):
>
> Entries will be judged on the following equally weighted criteria, and according to the sole and absolute discretion of the judges:
>
> Technological Implementation: How thoroughly and skillfully does the project use GitLab to automate the post-code DevSecOps lifecycle? Does the code and pipeline config reflect genuine effort and a working, non-trivial implementation? *Projects deployed on Google Cloud are eligible for up to 0.2 bonus points. See Stage Three.
>
> Design: Does the project deliver a complete, coherent end-to-end workflow, not just a technical proof of concept?
>
> Potential Impact: Does the project make a credible, specific case for solving a real problem for a real audience  -  and does the solution actually address that problem based on what's demonstrated?
>
> Innovation/Idea: How creative and novel is the concept and how inventively does it apply agentic automation compared to existing concepts?
>
> Presentation: Does the video clearly demonstrate the automation running end-to-end? Does it communicate what problem is solved, who it's for, and why it matters? Is the overall presentation easy to follow?

| Criterion | Weight before bonus |
| --- | --- |
| Technological Implementation | 20% |
| Design | 20% |
| Potential Impact | 20% |
| Innovation/Idea | 20% |
| Presentation | 20% |

The source says "equally weighted" across five criteria. The percentages are arithmetic, not printed percentages from the source. There is no separately listed Duo bonus: Duo is required at the pass/fail stage and affects the technical implementation being judged.

## Google Cloud bonus, exact rules wording

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Stage Three) The Submissions that pass Stage One and Two will be evaluated based on Google Cloud Deployment:
>
> Demonstrate that you have deployed your Project on Google Cloud. This code must be included in your public repository. A maximum of 0.2 points will be added.
>
> Each Submission will receive a Final score between 1 to 5.2, with the highest possible Final score being 5.2.

## Google Cloud bonus, exact FAQ wording

Source: [https://gitlab-transcend.devpost.com/resources](https://gitlab-transcend.devpost.com/resources).

> How do Google Cloud bonus points work?
>
> Deploy your project on Google Cloud to be eligible for up to 0.2 bonus points. This is open to both Paths. We add the points once, after judges score your project. The highest possible final score is 5.2.
>
> To be eligible:
>
> Include your Google Cloud deployment code in your public GitLab repository.
>
> Provide a link to your live project on Google Cloud. It must be public and available to judges.
>
> Read the Official Rules for details.

## Deployment optional for Path A

Source: [https://gitlab-transcend.devpost.com/resources](https://gitlab-transcend.devpost.com/resources).

> No. Deploy anywhere. Path A (Start Fresh) does not require deployment. Path B (Bring Your Own) requires a live URL on any platform. Projects deployed on Google Cloud are eligible for up to 0.2 bonus points. See full rules for details.Does Google Cloud cost money?

The source extraction above preserves a malformed FAQ line: the page joins "See full rules for details." to a duplicate "Does Google Cloud cost money?" label. That duplicate is not an additional requirement.

## Every prize and amount

Source: [Official rules, Section 8](https://gitlab-transcend.devpost.com/rules).

The prize names, amounts, quantities and eligibility cells below are copied from the rules table. The extra Path column preserves the two table group headings.

| Path or group | Winner | Prize | Qty | Eligibility |
| --- | --- | --- | --- | --- |
| Path A: Start Fresh Prizes | Best Assisted Agent | $4,000 USD in cash | 1 | All eligible Projects that enter Path A |
| Path A: Start Fresh Prizes | Best Supervised Agent | $4,000 USD in cash | 1 | All eligible Projects that enter Path A |
| Path A: Start Fresh Prizes | Best Hands-off Agent | $5,000 USD in cash | 1 | All eligible Projects that enter Path A |
| Path B: Bring Your Own | Best Assisted Agent | $4,000 USD in cash | 1 | All eligible Projects that enter Path B |
| Path B: Bring Your Own | Best Supervised Agent | $4,000 USD in cash | 1 | All eligible Projects that enter Path B |
| Path B: Bring Your Own | Best Hands-off Agent | $5,000 USD in cash | 1 | All eligible Projects that enter Path B |
| Special Prizes | Most Stages Covered | $5,000 USD in cash | 2 | The Projects from each Path which touch the most DevSecOps lifecycle steps (https://about.gitlab.com/stages-devops-lifecycle/) in the most creative way. |
| Special Prizes | Most Environmentally Impactful | $5,000 USD in cash | 1 | This prize will be awarded to the submission that demonstrates exceptional sustainability practices in its design, from model and pipeline optimization to energy-efficient architecture choices. The submission should quantify the sustainability gain using the latest public measurement methodologies and SCI frameworks. |
| Special Prizes | Most Creative | $4,000 USD in cash | 1 | The Project from either Path which scores highest in the Innovation/Idea judging criteria |

The two Most Stages Covered awards are one per Path. The listed cash totals $45,000.

## Multiple prize eligibility and tie breaking

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Each Project can win one (1) Prize from either Path A or Path B and one (1) Special Prize.
>
> For each Prize listed below, if two or more Submissions are tied, the tied Submission with the highest score in the first applicable criterion listed above will be considered the higher scoring Submission. In the event any ties remain, this process will be repeated, as needed, by comparing the tied Submissions' scores on the next applicable criterion. If two or more Submissions are tied on all applicable criteria, the panel of Judges will vote on the tied Submissions.

## Eligible entrants and all exclusions

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> The Hackathon IS open to:
>
> Individuals who are at least the age of majority where they reside as of the time of entry ("Eligible Individuals");
>
> Teams of Eligible Individuals ("Teams"); and
>
> Organizations (including corporations, not-for-profit corporations and other nonprofit organizations, limited liability companies, partnerships, and other legal entities) that exist and have been organized or incorporated at the time of entry.
>
> (the above are collectively, "Entrants")
>
> An Eligible Individual may join more than one Team or Organization and an Eligible Individual who is part of a Team or Organization may also enter the Hackathon on an individual basis. If a Team or Organization is entering the Hackathon, they must appoint and authorize one individual (the "Representative") to represent, act, and enter a Submission, on their behalf. By entering a Submission on behalf of a Team or Organization you represent and warrant that you are the Representative authorized to act on behalf of your Team or Organization.
>
> The Hackathon IS NOT open to:
>
> Individuals who are residents of, and individuals and Organizations located in the following locations are not eligible to participate or receive prizes: Brazil, China, Quebec, Russia, Cuba, Iran, North Korea, Syria, Crimea, Donetsk, and Luhansk regions of Ukraine, and any other country or region where participation or prize fulfillment is prohibited by U.S. law, local law, or is otherwise unavailable.
>
> Organizations involved with the design, production, paid promotion, execution, or distribution of the Hackathon, including the Sponsor and Administrator ("Promotion Entities").
>
> Employees, representatives and agents** of such Promotion Entities, and all members of their immediate family or household*
>
> Any other individual involved with the design, production, promotion, execution, or distribution of the Hackathon, and each member of their immediate family or household*
>
> Any Judge (defined below), or company or individual that employs a Judge
>
> Any parent company, subsidiary, or other affiliate*** of any organization described above
>
> Any other individual or organization whose participation in the Hackathon would create, in the sole discretion of the Sponsor and/or Administrator, a real or apparent conflict of interest
>
> *The members of an individual's immediate family include the individual's spouse, children and stepchildren, parents and stepparents, and siblings and stepsiblings. The members of an individual's household include any other person that shares the same residence as the individual for at least three (3) months out of the year.
>
> **Agents include individuals or organizations that in creating a Submission to the Hackathon, are acting on behalf of, and at the direction of, a Promotion Entity through a contractual or similar relationship.
>
> ***An affiliate is: (a) an organization that is under common control, sharing a common majority or controlling owner, or common management; or (b) an organization that has a substantial ownership in, or is substantially owned by the other organization.

## Multiple entries and team representation

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> An Entrant may submit more than one Submission, however, each Submission must be unique and substantially different from each of the Entrant's other Submissions, as determined by the Sponsor and Devpost in their sole discretion.
>
> If a team or organization is entering the Hackathon, they must appoint and authorize one individual (the "Representative") to represent, act, and enter a Submission, on their behalf. The Representative must meet the eligibility requirements above. By entering a Submission on the Hackathon Website on behalf of a team or organization you represent and warrant that you are the Representative authorized to act on behalf of your team or organization.

## Financial support or conflicts that can disqualify

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Financial or Preferential Support
>
> A Project must not have been developed, or derived from a Project developed, with financial or preferential support from the Sponsor or Administrator. Such Projects include, but are not limited to, those that received funding or investment for their development, were developed under contract, or received a commercial license, from the Sponsor or Administrator any time prior to the end of Hackathon Submission Period. The Sponsor, at their sole discretion, may disqualify a Project, if awarding a prize to the Project would create a real or apparent conflict of interest.

## IP rights and harmful code exclusions

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Entrant Representations. By submitting an entry or accepting any prize, entrants represent and warrant that (a) the Submission complies with all licensing requirements set forth in Section 4 of these Official Rules; (b) submitted content is not copyrighted, protected by trade secret or otherwise subject to third party intellectual property rights or other proprietary rights, including privacy and publicity rights, unless (i) entrant is the owner of such rights, (ii) entrant has permission from the rightful owner to use such content and to grant the licenses set forth in this Section 7 to the extent of such permission, or (iii) such content is third-party open source software used in compliance with its applicable open source license as required by Section 4; and (c) the content submitted does not contain any viruses, Trojan horses, worms, spyware or other disabling devices or harmful or malicious code.

## Late or incomplete entries

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> The Released Parties are not responsible for incomplete, late, misdirected, damaged, lost, illegible, or incomprehensible Submissions or for address or email address changes of the Entrants. Proof of sending or submitting the aforementioned will not be deemed to be proof of receipt by the Sponsor or Administrator. If for any reason any Entrant's Submission is determined to have not been received or been erroneously deleted, lost, or otherwise destroyed or corrupted, the Entrant's sole remedy is to request the opportunity to resubmit its Submission. Such a request must be made promptly after the Entrant knows or should have known there was a problem and will be determined at the sole discretion of the Sponsor.

## General grounds for disqualification

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Sponsor and Administrator reserve the right in their sole discretion to disqualify any individual or Entrant if it finds to be actually or presenting the appearance of tampering with the entry process or the operation of the Hackathon or to be acting in violation of these Official Rules or in a manner that is inappropriate, unsportsmanlike, not in the best interests of this Hackathon, or a violation of any applicable law or regulation.
>
> Any attempt by any person to undermine the proper conduct of the Hackathon may be a violation of criminal and civil law. Should the Sponsor or Administrator suspect that such an attempt has been made or is threatened, they reserve the right to take appropriate action including but not limited to requiring an Entrant to cooperate with an investigation and referral to criminal and civil law enforcement authorities.

## Winner verification and forms

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Verification Requirement: THE AWARD OF A PRIZE TO A POTENTIAL WINNER IS SUBJECT TO VERIFICATION OF THE IDENTITY, QUALIFICATIONS AND ROLE OF THE POTENTIAL WINNER IN THE CREATION OF THE SUBMISSION. No Submission or Entrant shall be deemed a winning Submission or winner until their post-competition prize affidavits have been completed and verified, even if prospective winners have been announced verbally or on the competition website. The final decision to designate a winner shall be made by the Sponsor and/or Administrator.
>
> Prize Delivery: Cash prizes will be payable to the Entrant, if an individual; to the Entrant's Representative, if a Team; or to the Organization, if the Entrant is an Organization. It will be the responsibility of the winning Entrant's Representative to allocate the Prize among their Team or Organization's participating members, as the Representative deems appropriate. A monetary Prize will be mailed to the winning Entrant's address (if an individual) or the Representative's address (if a Team or Organization), or sent electronically to the Entrant, Entrant's Representative, or Organization's bank account, only after receipt of the completed winner affidavit and other required forms (collectively the "Required Forms"), if applicable. The deadline for returning the Required Forms to the Administrator is ten (10) business days after the Required Forms are sent. Failure to provide correct information on the Required Forms, or other correct information required for the delivery of a Prize, may result in delayed Prize delivery, disqualification of the Entrant, or forfeiture of a Prize. Cash prizes will be delivered within 60 days of the Sponsor or Devpost's receipt of the completed Required Forms. Non-cash store credits will be distributed within 30 days of the end of the Judging Period.

## Submission changes after deadline

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Draft Submissions
>
> Prior to the end of the Submission Period, you may save draft versions of your submission on Devpost to your portfolio before submitting the Submission materials to the Hackathon for evaluation. Once the Submission Period has ended, you may not make any changes or alterations to your Submission, but you may continue to update the Project in your Devpost portfolio.
>
> Modifications After the Submission Period
>
> The Sponsor and Devpost may permit you to modify part of your Submission after the Submission Period for the purpose of adding, removing or replacing material that potentially infringes a third party mark or right, discloses personally identifiable information, or is otherwise inappropriate. The modified Submission must remain substantively the same as the original Submission with the only modification being what the Sponsor and Devpost permits.

## Stricter freeze instruction in the FAQ

Source: [https://gitlab-transcend.devpost.com/resources](https://gitlab-transcend.devpost.com/resources).

> Can I edit my submission after the deadline?
>
> No. You can edit as many times as you like before the deadline. Once it passes, leave everything alone until winners are announced. That includes your submission form, your code repository, your video, and anything linked from your submission. Changes during judging put your eligibility at risk.
>
> If you want to keep building, fork your repository or make a copy and work on the copy. A fork is a separate copy under your own account. Work there and leave the submitted version untouched.

## Live project availability

Source: [https://gitlab-transcend.devpost.com/resources](https://gitlab-transcend.devpost.com/resources).

> How long does my project need to stay live?
>
> Your project should stay live until winners are announced on or around November 16th, so judges can test it. If it goes down, you are not disqualified. But you may score lower, because judges will rely only on your video and repository. Show strong proof in your demo video either way.

The FAQ expressly says downtime alone does not disqualify an entry, although it can lower its score. Keep the live bonus deployment available through the announcement around November 16. Do not claim that having a deploy skeleton earns the bonus; judges need an actual public working deployment.

## Official rules control conflicting event statements

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> If there is any discrepancy or inconsistency between the terms and conditions of the Official Rules and disclosures or other statements contained in any Hackathon materials, including but not limited to the Hackathon Submission form, Hackathon Website, or advertising, the terms and conditions of the Official Rules shall prevail.
>
> The terms and conditions of the Official Rules are subject to change at any time, including the rights or obligations of the Entrant, the Sponsor and Administrator. The Sponsor and Administrator will post the terms and conditions of the amended Official Rules on the Hackathon Website. To the fullest extent permitted by law, any amendment will become effective at the time specified in the posting of the amended Official Rules or, if no time is specified, the time of posting.
>
> If at any time prior to the deadline, an Entrant or prospective Entrant believes that any term in the Official Rules is or may be ambiguous, they must submit a written request for clarification.

## Differences to carry into Claude's decisions log

Codex owns only `deploy/` and `docs/codex/`, so these findings belong here. Claude should copy the decisions it adopts into `docs/DECISIONS.md`.

| Difference | Evidence | Working choice |
| --- | --- | --- |
| Submission opening time | Rules Section 1 says October 5 at 10:00 am UTC. Dates page says "October 05 at 5:00pm UTC". | Rules control: October 5 at 10:00 UTC. Deadline agrees across both: October 27 at 13:00 UTC. |
| Judging opening time | Rules says October 28 at 10:00 am UTC. Dates page says "October 28 at 9:00am UTC". | Rules control: 10:00 UTC. |
| Public versus private repository | Rules Submission Requirements says repository "must be public". Testing paragraph contains "If Entrant's repository is private, Entrant must include access instructions." FAQ insists public. | Public GitLab repository, visible CI history. Do not treat the generic testing paragraph as a private-repo exemption. |
| Third-party licences | Rules allow third-party OSI-approved compatible licences. FAQ says "Yes, everything that you use or make must be MIT-licensed." | Original work and submitted repository use MIT. Third-party licence handling follows the more specific Official Rules clause; retain notices and ask the organizer if interpretation is material. |
| YouTube visibility | Rules say "made publicly visible on YouTube". FAQ says "Public or Unlisted, not Private". | Set Public and stay strictly below three minutes. |
| Changes after deadline | Rules prohibit changing the Submission while allowing changes to the Devpost portfolio. FAQ explicitly includes the submitted repository, video and linked material, until winners are announced. | Freeze submitted form, repo, video and links through the announcement; keep new development in a separate copy. |
| Webinar time typo | Resources says "October 9th at 2:00 PM UTC / 10 AM UTC". Main says "Oct 9, 10am ET". | Do not interpret both resource clock readings as UTC; verify the registration calendar before attending. |

Eligibility blockers include missing required Duo use, unqualified entrant or excluded location, missing public MIT GitLab source or visible automation, unsupported new-work timing, absent required Path B live/original links, missing required video or description, rights violations, misleading functionality, prohibited financial support or conflicts, tampering, and rule violations. This is a practical checklist derived from the quoted conditions, not a new organizer rule.

## Current updates

Source: [https://gitlab-transcend.devpost.com/updates](https://gitlab-transcend.devpost.com/updates).

> Stay tuned for important announcements. Organizers will post them here and also send an email to registered participants.

No organizer update entries were visible on the public Updates page at retrieval. The site also displayed this maintenance notice:

> We will be undergoing planned maintenance on Oct 7th 6:00AM UTC / Oct 7th 2:00AM ET

## Current schedule wording

Source: [https://gitlab-transcend.devpost.com/details/dates](https://gitlab-transcend.devpost.com/details/dates).

> Submissions
>
> October 05 at 5:00pm UTC
>
> October 27 at 1:00pm UTC
>
> Judging
>
> October 28 at 9:00am UTC
>
> November 14 at 5:00pm UTC
>
> Winners Announced
>
> November 16 at 2:00pm UTC

## Useful resources wording

Source: [https://gitlab-transcend.devpost.com/resources](https://gitlab-transcend.devpost.com/resources).

> How do I get free access to GitLab?
>
> Start Transcend Hackathon contributor onboarding. GitLab approves requests in about 24 business hours. Your group, subgroup, project, and onboarding issue are created automatically after that.
>
> How do I enter the Most Environmentally Impactful prize?
>
> Opt in on the submission form. Explain how your project "demonstrates exceptional sustainability practices in its design, from model and pipeline optimization to energy-efficient architecture choices." You should measure your sustainability gain with current public methods and the Software Carbon Intensity (SCI) framework.

## Devpost terms also apply

Source: [https://gitlab-transcend.devpost.com/rules](https://gitlab-transcend.devpost.com/rules).

> Please review the Devpost Terms of Service at https://info.devpost.com/terms for additional rules that apply to your participation in the Hackathon and more generally your use of the Hackathon Website. Such Terms of Service are incorporated by reference into these Official Rules, including that the term "Poster" in the Terms of Service shall mean the same as "Sponsor" in these Official Rules. If there is a conflict between the Terms of Service and these Official Rules, these Official Rules shall control with respect to this Hackathon only.

The linked Devpost terms are [https://info.devpost.com/terms](https://info.devpost.com/terms). This bounded task reads the five requested event pages; it does not claim a fresh review of every external legal document, linked technical page or authenticated submission form. Follow the form fields when Alex submits. No eligibility or prize outcome is guaranteed.

