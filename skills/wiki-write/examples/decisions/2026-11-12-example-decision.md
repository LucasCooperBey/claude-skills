---
id: 2026-11-12-example-decision
type: decision
date: 2026-11-12
actors: [me, claude]
tags: [example, decisions, workflow]
summary: >
  Example only. This made-up note shows the shape of a decision. It records
  a choice to keep one dated note per decision in the wiki.
status: active
domain: workflow
confidence: high
alternatives_considered:
  - id: keep-it-in-chat
    one_liner: Leave the choice in the conversation
    rejected_because: A later reader will not search the chat
  - id: one-dated-note
    one_liner: File one dated note in the wiki
    chosen: true
    chosen_because: The date and the summary are enough to find it
links:
  - ./synthesis/2026-11-12-example-synthesis.md
---

# Example decision

This file is a made-up example. It is not a record of a real decision.

## What changed

Choices that pass the three gates get one dated note in the wiki.

## Why

A later reader can see the reason without replaying the original thread.

## Tradeoffs

A short note is easy to file. It can leave out detail a longer document would keep.
