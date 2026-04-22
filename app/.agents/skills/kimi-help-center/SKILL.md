---
name: kimi-help-center
description: >
  Kimi product tutorial and help center. Handles user questions about Kimi subscription/membership services,
  user guides, membership benefits, and Agent features (Kimi Claw, Deep Research, OK Computer, Kimi PPT, Kimi Docs, etc.).
  Fetches answers from GitHub-hosted help documents via web_open_url.
---

# Kimi Tutorial & Help

## Usage

When user questions involve **Kimi subscription/membership services, user guides, membership benefits, or Agent features （e.g. Deep Research/深度研究 Kimi Agent/OK Computer, & Kimi PPT/Kimi docs/Kimi website agents)**, use `web_open_url` to fetch the corresponding GitHub raw content and respond to the user. Include images in your response when available.

## Example

User asks: "What is Kimi Claw and how do I install it?"

Use `web_open_url` tool to read the raw content:

```json
{
  "urls": ["https://raw.githubusercontent.com/MoonshotAI/kimi-help-center/master/kimi_claw_cn.md"]
}
```

Then summarize the content and respond to the user in a friendly, helpful tone.

## Reference Resources

Choose the most relevant document(s) based on the user's question:

| Topic | When to use | URL |
|-------|------------|-----|
| Overview | User asks "what is Kimi", product positioning, general feature introduction | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_overview_cn.md |
| UI Guide | User asks about interface layout, button locations, navigation | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_ui_overview_cn.md|
| Agentic Chat | User asks about Agent mode, OK Computer, Kimi Agent usage | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_agentic_chat_cn.md|
| Prompt Tips | User asks how to write prompts, improve Kimi responses | https://github.com/MoonshotAI/kimi-help-center/blob/master/prompts_a_key_to_better_AI_interactions_cn.md|
| Agentic Search | User asks about AI-powered search for latest news, stock data, verifying rumors, or accessing specific web pages | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_agentic_search_cn.md|
| Memory Space | User asks about cross-session memory, memory management, personalization |https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_memory_space_cn.md|
| Deep Research | User asks about Deep Research feature and usage | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_deepresearch_cn.md|
| Agent Mode | User asks about Agent mode and usage | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_agent_mode_cn.md|
|Kimi Websites| User asks about Kimi Websites and usage | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_agent_websites_cn.md|
|Kimi docs and sheets| User asks about generating downloadable Word/Excel/PDF files with annotations, or natural language driven spreadsheet functions | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_docs_and_kimi_sheets_cn.md|
|Kimi slides| User asks about generating PPT from a single sentence or converting long text into structured presentation | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_slides_cn.md|
|Kimi Agent Swarm| User asks about parallel execution of complex multi-step tasks with dynamic agent coordination | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_agent_swarm_cn.md|
| Membership | User asks about subscription, pricing, benefits comparison, usages, or invoice/billing issues |https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_membership_benefits_cn.md|
| Kimi Claw | User asks about Kimi Claw introduction, installation, deployment on Feishu, Weibo, Wechat |https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_claw_cn.md|
| Kimi Claw | User asks about Kimi Claw introduction, installation, deployment on Telegram | https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_claw_user_guide_en.md|
| FAQ | No match above, or user asks common questions, account issues, troubleshooting |https://github.com/MoonshotAI/kimi-help-center/blob/master/kimi_FAQ_cn.md|


# Note
Always respond in the language the user asked in, even if the source content you referenced is in a different language. Include the original source URL so the user can refer to it for more details.
