---
description: Generates an architected prompt using the internal agent.
---
1. Ask the user for their request if it wasn't provided in the initial prompt.
2. Run the following command (substituting the user's request):
   ```bash
   python src/cli.py "<USER_REQUEST>"
   ```
3. Display the output to the user.
