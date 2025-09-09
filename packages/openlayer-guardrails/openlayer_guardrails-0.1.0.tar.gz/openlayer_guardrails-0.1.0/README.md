# Openlayer Guardrails

Open source guardrail implementations that work with Openlayer tracing.

## Installation

```bash
pip install openlayer-guardrails[pii]
```

## Usage

### Standalone Usage

```python
from openlayer_guardrails import PIIGuardrail

# Create guardrail
pii_guard = PIIGuardrail(
    block_entities={"CREDIT_CARD", "US_SSN"},
    redact_entities={"EMAIL_ADDRESS", "PHONE_NUMBER"}
)

# Check inputs manually
data = {"message": "My email is john@example.com and SSN is 123-45-6789"}
result = pii_guard.check_input(data)

if result.action.value == "block":
    print(f"Blocked: {result.reason}")
elif result.action.value == "modify":
    print(f"Modified data: {result.modified_data}")
```

### With Openlayer Tracing

```python
from openlayer_guardrails import PIIGuardrail
from openlayer.lib.tracing import trace

# Create guardrail
pii_guard = PIIGuardrail()

# Apply to traced functions
@trace(guardrails=[pii_guard])
def process_user_data(user_input: str):
    return f"Processed: {user_input}"

# PII is automatically detected and handled
result = process_user_data("My email is john@example.com")
# Output: "Processed: My email is [EMAIL-REDACTED]"
```

