---
name: product-copy
description: Interface copy in the Linear, Notion and Apple voice. Use when writing or reviewing any product UI text (labels, buttons, dialogs, toasts, empty states, errors, table headers, page titles) or when asked to make copy sound like Linear, Notion or Apple.
---

# Product copy

The house voice for product UI is the one Linear, Notion and Apple share: plain, short, calm, specific. The interface states what is true and what to do next, then gets out of the way. This file is the umbrella: the voice, the replacement table, the patterns and the workflow. The skills credited under "Related skills" carry longer-form reference.

## House voice

- **Plain words.** The word a colleague would say out loud. "Remove", not "Disassociate". "Can't", not "Unable to".
- **Short.** One idea per string. Cut every word that leaves the meaning intact when removed.
- **Calm.** The same even tone for success and failure. The interface reports; it does not celebrate or apologise.
- **Specific.** Name the object and the count: "Delete 3 rules", "Rule added", "Can't reach the server".
- **Sentence case everywhere**: titles, buttons, tabs, menu items, column headers, toasts. Capitalise only the first word and proper nouns.
- **The product's own nouns.** Use exactly the term the product already uses for each object and action, one word per concept. If the sidebar says "Team", every string says "Team", never "Group" for the same thing.
- **Second person, present tense, active voice.** "You don't have access", not "Access has not been granted".

## Replacement table

Run every string against this table. Each left-hand item has a fixed replacement on the right.

| Instead of | Write |
| :--- | :--- |
| "Oops", "Uh oh", "Whoops" | The plain statement of what failed: "Couldn't save the rule." |
| "Something went wrong" | What failed and how to fix it: "Couldn't load members. Refresh to try again." |
| "successfully" ("Saved successfully") | The past-tense fact: "Saved." |
| "Please" ("Please enter a name") | The instruction itself: "Enter a name." |
| "!" | A period. |
| "Are you sure?" | The action as a question: "Delete this rule?" |
| "Click here", "Learn more" alone | A link on the words that name the destination: "Read the access docs". |
| "Submit", "Confirm", "Done" on a form | The verb plus object: "Create team", "Save changes". |
| "OK" / "Yes" / "No" on a dialog | Verb plus object for the action, "Cancel" for the escape: "Delete rule" / "Cancel". |
| "Let's", "Let's get started" | The action: "Create your first team". |
| "Awesome", "Great", "Yay", "All set!" | The fact: "Invite sent." |
| Em dash | A period, comma or colon, or two sentences. |
| Emoji | Nothing. Use the product's icon set if a visual is needed. |
| Title Case Labels | Sentence case labels. |
| "Unable to", "Failed to" | "Can't", "Couldn't". |

## Patterns

**Page title and description.** The title is the noun the nav uses ("Members", "Apps"). Under it, at most one sentence saying what the page is for: "People who can sign in to your apps." Plain description, not a pitch.

**Table column headers.** Short nouns, sentence case, no verbs: "Name", "Role", "Last active", "Apps". Units go in the header, not every cell: "Size (MB)".

**Empty states.** Two parts: what will live here, then one action. "No rules yet. Rules decide who can open this app." with a single button "Add rule". No illustrations of sadness, no jokes.

**Confirmations.** Only for actions that can't be undone; reversible actions take an undo toast instead.
- Title: verb + object + "?": "Remove Sam from Marketing?"
- Body: the consequence, one or two sentences: "Sam loses access to the 4 apps this team grants."
- Buttons: verb + object for the action, "Cancel" for the escape: "Remove member" / "Cancel".

**Dialog titles and primary buttons share the verb.** "Invite member" titles a dialog whose primary button is "Invite member" (or "Send invite" if the title is "Send invite"). Opening button, dialog title, primary action and success toast all use the same verb.

**Toasts.** Past tense, object first, a period: "Rule added." "Team renamed." "3 members removed." Add an "Undo" action when the change is reversible. Errors in toasts follow the error pattern.

**Errors.** What failed, then how to fix it, in two short sentences. "Couldn't send the invite. Check the email address and try again." Field errors sit under the field and say what is needed: "Enter an email address." Raw codes go in a details line for support, never as the message.

**Buttons and menu items.** Verb first, then object: "Add rule", "Export CSV", "Copy link". Keep labels to one to three words.

**Labels and placeholders.** The label names the field ("Team name"). The placeholder, if any, shows an example ("Marketing"), never the instructions.

**Loading.** Name what is loading when it takes more than a moment: "Loading members". An ellipsis character, not three dots.

## Workflow

1. **Inventory the terms.** Before writing, search the codebase for existing strings around the change (component text, locale files, nav labels, page titles). List the noun used for each object and the verb used for each action. Reuse them exactly. The step is done when every object and action in the new copy maps to an existing term or is flagged as new.
2. **Write** each string with the pattern for its element above.
3. **Sweep.** Run the replacement table over every string you wrote or touched, then check sentence case and the shared-verb rule across each flow (button, dialog title, primary action, toast). The sweep is done when every string has passed every row of the table.
4. **Report** changed strings as a table: location, before, after. For reviews, report findings in the same table without applying them.

## Related skills

This skill stands alone. These public skills by other authors cover the same ground in more depth and informed how it is used. They are not bundled here; install them from their own repositories.

- [content-designer/ux-writing-skill](https://github.com/content-designer/ux-writing-skill): broad UX writing reference with accessibility, voice and tone frameworks, and error pattern libraries.
- [neeeophytee/agent-stylebooks](https://github.com/neeeophytee/agent-stylebooks) (`apple-interface-writing`): one purpose per screen, labels that predict the result, supporting text only for a consequence or requirement, errors that support recovery.
- [Owl-Listener/designer-skills](https://github.com/Owl-Listener/designer-skills) (`designer-toolkit/skills/ux-writing`): another pattern set for interface text.
- [JohnSina86/ui-copy-skill](https://github.com/JohnSina86/ui-copy-skill): specificity test, ban list by element, state microcopy table and a placeholder detector.
- [Nandansai08/skillz](https://github.com/Nandansai08/skillz) (`microcopy-writing`): buttons, errors, confirm-versus-undo decisions and term sheets.
- [skillatlas/skills](https://github.com/skillatlas/skills) (`ux-copywriting`): compact before-and-after examples per element.
- [blader/humanizer](https://github.com/blader/humanizer): for longer prose (docs, help articles, release notes) that reads as AI-written.
