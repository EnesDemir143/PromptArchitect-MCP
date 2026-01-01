---
description: Generates an architected prompt using the internal agent.
---

# Project Rules (Architecture First)

1.  **Intercept Request:** When the user makes a coding request, do NOT start coding immediately.
2.  **Consult Architect:** Use the `architect_request` MCP tool.
    * Input: The user's full request.
3.  **Review Plan:** The tool will update `.ai_state.json`. Read this plan.
4.  **Execute:** Implement the tasks defined in the plan.