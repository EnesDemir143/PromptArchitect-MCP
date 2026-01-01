---
description: Generates an architected prompt and then optionally executes it.
---
1. Ask the user for their request if it wasn't provided in the initial prompt.

2. Run the Architect to generate a plan:
   ```bash
   python src/cli.py "<USER_REQUEST>" --raw
   ```

3. Display the generated "Architected Prompt" to the user clearly.

4. Ask the user:
   > "Do you want me to proceed with this plan?"

5. If the user says **YES**:
   - Treat the "Architected Prompt" as your new set of instructions.
   - Begin executing the tasks defined in that prompt immediately using your coding tools.
