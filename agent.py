from julep import Client
# Global UUID is generated for agent and task
import uuid
from task import task_def

AGENT_UUID = uuid.uuid4()
TASK_UUID = uuid.uuid4()

JULEP_API_KEY = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZjc0OTJmMi1kNjNmLTVhZjEtOTJiZC05ZTY0M2Y2NzRhOWIiLCJlbWFpbCI6InZhaWRpa3BhbmRleXR0QGdtYWlsLmNvbSIsImlhdCI6MTc1MTQ2MTc1NywiZXhwIjoxNzUyMDY2NTU3fQ.FR-Ln5_dLlZNHsM_0xrjsH8K8e5mkpaa3vre7PssPzK37c-OP-tnSXsYj1QNQYyNvKDdZLutU1KerDFHz0DEkw"

client = Client(api_key=JULEP_API_KEY, environment="production")

# Defining the agent
name = "Amit"
about = "Generates city-based meal itineraries using weather data, local cuisines, and restaurant search."


# Create the agent
agent = client.agents.create_or_update(
    agent_id=AGENT_UUID,
    name=name,
    about=about,
    model="gpt-4o",
)


# creating the task object
task = client.tasks.create_or_update(
    task_id=TASK_UUID,
    agent_id=AGENT_UUID,
    **task_def
)


execution = client.executions.create(
    task_id=task.id,
    input={
         "locations": ["Jaipur"]
    }
)

print("Started an execution. Execution ID:", execution.id)


import time

execution = client.executions.get(execution.id)

while execution.status != "succeeded":
    time.sleep(5)
    execution = client.executions.get(execution.id)
    print(execution)
    print(execution.output)

execution = client.executions.get(execution.id)
print(execution.output)