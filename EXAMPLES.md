# Example Scenarios & Use Cases

Practical examples demonstrating how to use the Agent Load Balancer system.

## 📋 Table of Contents

1. [Basic Usage](#basic-usage)
2. [Load Balancing Scenarios](#load-balancing-scenarios)
3. [API Integration Examples](#api-integration-examples)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Testing Scenarios](#testing-scenarios)

## 🚀 Basic Usage

### Scenario 1: First-Time Setup

**Goal**: Set up a basic support team with agents and process requests.

**Steps**:

1. **Start the application**
   ```bash
   docker-compose up --build
   ```

2. **Create agents**
   - Agent: "Sarah", Capacity: 2
   - Agent: "Mike", Capacity: 3
   - Agent: "Emma", Capacity: 2

3. **Submit first request**
   - Customer: "John Doe"
   - Description: "Password reset needed"
   - **Result**: Assigned to Mike (highest capacity: 3)

4. **Submit more requests**
   - Request 2 → Mike (capacity 3)
   - Request 3 → Mike (capacity 3, now full)
   - Request 4 → Sarah or Emma (both have capacity 2)

5. **Complete a request**
   - Complete one of Mike's requests
   - **Result**: Mike now has 1 free slot

### Scenario 2: Handling Rush Hour

**Goal**: Manage high volume of incoming requests.

**Setup**:
- 5 agents, each with capacity 3
- Total capacity: 15 concurrent requests

**Simulation**:
1. Submit 15 requests rapidly
2. All agents reach full capacity
3. Try to submit request #16
4. **Result**: "No available agents" error
5. Complete 3 requests
6. Submit 3 more requests
7. **Result**: Successfully processed

## 🎯 Load Balancing Scenarios

### Scenario 3: Testing Load Distribution

**Setup**:
```
Agent A: max_requests = 1
Agent B: max_requests = 2  
Agent C: max_requests = 3
```

**Expected Distribution**:
```
Request 1 → Agent C (3 slots)
Request 2 → Agent C (3 slots)
Request 3 → Agent C (3 slots, now full)
Request 4 → Agent B (2 slots)
Request 5 → Agent B (2 slots, now full)
Request 6 → Agent A (1 slot, now full)
Request 7 → Error: No capacity
```

**Verification**:
```bash
curl http://localhost:8000/stats
```

Expected output:
```json
{
  "total_agents": 3,
  "total_requests": 6,
  "active_requests": 6,
  "available_capacity": 0,
  "total_capacity": 6,
  "utilization": 100.0
}
```

### Scenario 4: Dynamic Rebalancing

**Goal**: Show how completing requests affects routing.

**Timeline**:

```
T0: Create 3 agents (A:2, B:2, C:2)
T1: Submit 4 requests
    - R1 → A, R2 → A (full)
    - R3 → B, R4 → B (full)
    
T2: Complete R1 (Agent A now has 1 slot)
T3: Submit R5
    - R5 → A (has 1 slot, others have 0)
    
T4: Complete R3 and R4 (Agent B now has 2 slots)
T5: Submit R6
    - R6 → B (has 2 slots, most available)
```

## 💻 API Integration Examples

### Scenario 5: Using cURL

**Create an agent**:
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Agent 1",
    "max_requests": 3
  }'
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Support Agent 1",
  "max_requests": 3,
  "current_requests": []
}
```

**Submit a request**:
```bash
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Alice Johnson",
    "description": "Cannot access account"
  }'
```

**Complete a request**:
```bash
REQUEST_ID="550e8400-e29b-41d4-a716-446655440001"
curl -X POST http://localhost:8000/requests/$REQUEST_ID/complete
```

### Scenario 6: Python Integration

**Full workflow example**:

```python
import requests
import time

API_BASE = "http://localhost:8000"

# 1. Create agents
agents = []
for i in range(3):
    response = requests.post(
        f"{API_BASE}/agents",
        json={
            "name": f"Agent {i+1}",
            "max_requests": 2
        }
    )
    agents.append(response.json())
    print(f"Created: {response.json()['name']}")

# 2. Submit requests
requests_list = []
for i in range(5):
    response = requests.post(
        f"{API_BASE}/requests",
        json={
            "customer_name": f"Customer {i+1}",
            "description": f"Issue #{i+1}"
        }
    )
    request_data = response.json()
    requests_list.append(request_data)
    print(f"Request {i+1} assigned to agent: {request_data['assigned_agent_id']}")
    time.sleep(0.5)

# 3. Check statistics
stats = requests.get(f"{API_BASE}/stats").json()
print(f"\nSystem Stats:")
print(f"  Utilization: {stats['utilization']}%")
print(f"  Active Requests: {stats['active_requests']}")
print(f"  Available Capacity: {stats['available_capacity']}")

# 4. Complete first 3 requests
for request in requests_list[:3]:
    requests.post(f"{API_BASE}/requests/{request['id']}/complete")
    print(f"Completed request: {request['id']}")
    time.sleep(0.5)

# 5. Final statistics
stats = requests.get(f"{API_BASE}/stats").json()
print(f"\nFinal Stats:")
print(f"  Completed: {stats['completed_requests']}")
print(f"  Still Active: {stats['active_requests']}")
```

### Scenario 7: JavaScript/Node.js Integration

**Automated load testing**:

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8000';

async function setupAgents(count, maxRequests) {
  const agents = [];
  for (let i = 0; i < count; i++) {
    const response = await axios.post(`${API_BASE}/agents`, {
      name: `Agent ${i + 1}`,
      max_requests: maxRequests
    });
    agents.push(response.data);
  }
  return agents;
}

async function submitRequests(count) {
  const requests = [];
  for (let i = 0; i < count; i++) {
    try {
      const response = await axios.post(`${API_BASE}/requests`, {
        customer_name: `Customer ${i + 1}`,
        description: `Support request #${i + 1}`
      });
      requests.push(response.data);
      console.log(`✓ Request ${i + 1} assigned to ${response.data.assigned_agent_id}`);
    } catch (error) {
      console.error(`✗ Request ${i + 1} failed:`, error.response?.data?.detail);
    }
  }
  return requests;
}

async function getStats() {
  const response = await axios.get(`${API_BASE}/stats`);
  return response.data;
}

// Run simulation
async function runSimulation() {
  console.log('Creating agents...');
  await setupAgents(3, 2);
  
  console.log('\nSubmitting 10 requests...');
  await submitRequests(10);
  
  console.log('\nFinal statistics:');
  const stats = await getStats();
  console.log(JSON.stringify(stats, null, 2));
}

runSimulation();
```

## 🌍 Real-World Use Cases

### Scenario 8: Customer Support Center

**Context**: E-commerce company with 24/7 support team.

**Setup**:
- Tier 1: 10 agents, capacity 3 (general inquiries)
- Tier 2: 5 agents, capacity 2 (technical issues)
- Tier 3: 2 agents, capacity 1 (escalations)

**Workflow**:
1. Customer submits ticket via website
2. System assigns to most available Tier 1 agent
3. If Tier 1 full, holds in queue
4. When request completed, capacity frees up
5. Next request auto-assigned

**Benefits**:
- Even workload distribution
- No agent overload
- Automatic queue management
- Real-time capacity monitoring

### Scenario 9: IT Help Desk

**Context**: Corporate IT department serving 500 employees.

**Agent Configuration**:
```json
[
  {"name": "Desktop Support", "max_requests": 5},
  {"name": "Network Team", "max_requests": 3},
  {"name": "Security Team", "max_requests": 2},
  {"name": "Database Team", "max_requests": 2}
]
```

**Request Types**:
- Password resets → Desktop Support
- Network issues → Network Team
- Security incidents → Security Team
- Database queries → Database Team

**Extension Needed**: 
Add request categorization to route to specific teams.

### Scenario 10: Food Delivery Service

**Context**: Restaurant managing delivery orders.

**Agent Configuration**:
```
Driver 1: capacity 2 (can handle 2 deliveries simultaneously)
Driver 2: capacity 3 (larger vehicle)
Driver 3: capacity 1 (motorcycle)
```

**Usage**:
1. Order comes in
2. Assigned to driver with most capacity
3. Driver completes delivery
4. Driver capacity increases
5. Next order assigned

## 🧪 Testing Scenarios

### Scenario 11: Capacity Limits

**Test**: Verify system handles capacity correctly.

```bash
# Setup
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "Agent 1", "max_requests": 1}'

# Test 1: Within capacity
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test", "description": "Test 1"}'
# Expected: Success

# Test 2: Exceed capacity
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test", "description": "Test 2"}'
# Expected: Error "No available agents"
```

### Scenario 12: Agent Deletion

**Test**: Ensure agents with active requests can't be deleted.

```bash
# Create agent
AGENT_ID=$(curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "max_requests": 2}' | jq -r '.id')

# Assign request
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test", "description": "Test"}'

# Try to delete agent
curl -X DELETE http://localhost:8000/agents/$AGENT_ID
# Expected: Error "Cannot delete agent with active requests"
```

### Scenario 13: Load Testing

**Test**: Performance under load.

```python
import concurrent.futures
import requests
import time

API_BASE = "http://localhost:8000"

def create_request(i):
    try:
        response = requests.post(
            f"{API_BASE}/requests",
            json={
                "customer_name": f"Load Test {i}",
                "description": f"Test request {i}"
            },
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        return False

# Create 10 agents
for i in range(10):
    requests.post(
        f"{API_BASE}/agents",
        json={"name": f"Agent {i}", "max_requests": 5}
    )

# Submit 100 requests concurrently
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(create_request, range(100)))

end_time = time.time()

success_count = sum(results)
print(f"Successfully created: {success_count}/100 requests")
print(f"Time taken: {end_time - start_time:.2f} seconds")
print(f"Requests per second: {100 / (end_time - start_time):.2f}")
```

## 📊 Monitoring Scenario

### Scenario 14: Real-Time Dashboard

**Goal**: Monitor system health in real-time.

**Bash script for continuous monitoring**:

```bash
#!/bin/bash

while true; do
    clear
    echo "=== Agent Load Balancer Monitor ==="
    echo "==================================="
    echo ""
    
    # Get stats
    STATS=$(curl -s http://localhost:8000/stats)
    
    echo "Total Agents: $(echo $STATS | jq '.total_agents')"
    echo "Total Requests: $(echo $STATS | jq '.total_requests')"
    echo "Active Requests: $(echo $STATS | jq '.active_requests')"
    echo "Completed: $(echo $STATS | jq '.completed_requests')"
    echo "Utilization: $(echo $STATS | jq '.utilization')%"
    echo ""
    
    # Get agents
    echo "Agent Status:"
    curl -s http://localhost:8000/agents | jq -r '.[] | 
        "\(.name): \(.current_requests | length)/\(.max_requests)"'
    
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 3
done
```

## 🎓 Learning Scenarios

### Scenario 15: Understanding Load Balancing

**Educational walkthrough**:

1. **Start clean**: Reset application
2. **Create two agents**:
   - Agent A: capacity 1
   - Agent B: capacity 2

3. **Submit Request 1**:
   - Question: Which agent receives it?
   - Answer: Agent B (higher capacity)
   - Verification: Check `/agents` endpoint

4. **Submit Request 2**:
   - Question: Which agent now?
   - Answer: Agent B (still has more: 2 vs 1)
   - New state: B has 2/2

5. **Submit Request 3**:
   - Question: Which agent now?
   - Answer: Agent A (B is full)
   - New state: A has 1/1, B has 2/2

6. **Submit Request 4**:
   - Question: What happens?
   - Answer: Error - no capacity!

7. **Complete Request on B**:
   - New state: A has 1/1, B has 1/2

8. **Submit Request 5**:
   - Question: Which agent?
   - Answer: Agent B (has 1 free slot)

---

These scenarios demonstrate the flexibility and power of the Agent Load Balancer system for various use cases and workflows.
