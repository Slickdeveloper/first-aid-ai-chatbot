# Safety Policy

## Purpose

This chatbot is designed to provide first-aid guidance from approved medical sources. It is not a diagnosis system and it does not replace emergency services, clinical care, or certified first-aid training.

The safety goal is simple:

- give grounded first-aid help when approved content exists
- escalate clearly when the situation sounds dangerous
- refuse when the system does not have enough trusted evidence

## Source Restrictions

- answers must be based only on approved source content stored in the system
- preferred source order is:
  - `IFRC`
  - `WHO`
  - supporting sources such as `American Red Cross` or `Mayo Clinic` when needed
- unsupported medical claims must not be generated

## Emergency Detection

The system flags high-risk prompts such as:

- not breathing or severe breathing difficulty
- choking
- severe bleeding
- chest pain or suspected heart attack
- stroke warning signs
- seizures
- severe allergic reaction or anaphylaxis
- unresponsiveness
- electrical emergencies

When an emergency is detected, the chatbot surfaces a visible emergency warning and uses Ghana emergency numbers:

- General emergency: `112`
- Police: `191`
- Fire: `192`
- Ambulance: `193`

## Refusal Behavior

If the system does not have enough approved source material for a topic, it should refuse safely rather than guess.

This is an intentional safety decision. A short refusal is better than giving medical advice that cannot be traced back to an approved source.

Expected refusal style:

- explain that there is not enough approved source material
- encourage consultation of an official source or qualified medical professional

## Answer Style

The assistant should:

- stay grounded in retrieved passages
- keep answers short and actionable
- separate immediate actions from escalation steps where possible
- include citations with each answer

## User Disclaimer

Every chat response should remind the user that:

- the chatbot provides first-aid guidance from approved sources
- it does not replace professional diagnosis, treatment, or certified training

## Governance

- approved content should be reviewed before ingestion
- outdated or superseded content should be re-ingested or unapproved
- admin/source-management actions should preserve transparency around what is searchable
