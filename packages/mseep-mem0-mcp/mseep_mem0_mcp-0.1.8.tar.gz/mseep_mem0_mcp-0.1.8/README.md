# mem0 MCP Server for project management

mem0 MCP Server is a bridge between MCP Host applications and the mem0 cloud service, providing memory capabilities for MCP Host AI.

This is forked in order to change the scope from coding to project management.
The forked deals more higher level context related with project management topics.

Additionally, this forked experimentally integrate cording format into high level context like human protocol.

## Features

- Forked in order to change the usage from original coding scope to project management scope.
- Project memory storage and retrieval
- Semantic search for finding relevant project information
- Structured project management data handling

## Installation and usage

### Pre-condition and requirement

- Python 12.0 or newer,
- mcp-proxy (in case Cline or Roo code)


### Details

1. Clone the repository and move into.

2. Set up virtual environment using `uv`.

```bash
uv venv --python 3.12
```
3. Activate virtual environment using `uv`.

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`.

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Create .gitignore in repo root.

```bash
touch .gitignore
```

6. Update .gitignore

```sample
# Python
__pycache__/
*.py[cod]
*.egg-info/

# Environment variables
.env

# Egg info
mem0_mcp.egg-info/
```

7. Create .env in repo root.

```bash
touch .env
```

8. Update .env

```
MEM0_API_KEY={your API Key}
```

9. Clone and install the following OSS.

https://github.com/sparfenyuk/mcp-proxy

10. Add MCP Server settings.

- Cline

```cline_mcp_settings.json
"mem0": {
      "command": "PATH_TO/mcp-proxy", # ex: /home/{user}/.local/bin/mcp-proxy
      "args": [
        "http://127.0.0.1:6789/sse" # configure port as you need
      ]
    }
```

11. Launch MCP Server (activated virtual env required)

```bash
python main.py --host 127.0.0.1 --port 6789
```

12. Check the functionality by MCP Host (like Cline)

```
Hey, can you get all memories on mem0?
```

## Operation

- Ensure run MCP Server fast.
- There are several ways automatic run server, like adding script .bashrc
- Set up automatic as your environment is easier usage.

## Available Tools

- add_project_memory: Add new project management information
- get_all_project_memories: Retrieve all stored project information
- search_project_memories: Search for specific project information

## Technical details

The uniqueness of this forked is the structured format between MCP Host and mem0 is expected in coding format like Javascript object.
Make sure you set the custom instruction to be able to handle better.

## Custom instruction

In order to make mem0 working as fitting to project management purpose, this forked has the following instruction for AI.

### For mem0

- Check the source code.

### For MCP Host

- The following is just sample, find the best by yourself !!

---

# mem0 Guide for Effective Project Memory (Enhanced)

This guide outlines strategies and templates for effectively managing project information using mem0. The aim is to improve searchability and reusability of project data through structured templates and metadata management.

## Information Structure and Templates

mem0 can effectively manage the following types of information. Using structured templates improves searchability and reusability. Note that the templates provided are examples and should be adapted to fit specific project needs.

### 1. Project Status Management

**Template**:
```javascript
// [PROJECT: project-name] [TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00] [TYPE: Project Status]
const projectStatus = {
  overview: {
    name: "Project Name",      // Required
    purpose: "Project Purpose", // Required
    version: "1.2.0",          // Optional
    phase: "development"       // Optional
  },
  progress: {
    completionLevel: 0.65,    // Completion rate (value between 0 and 1)
    milestones: [
      { name: "Planning Phase", status: "completed", date: "2025-02-15" },
      { name: "Development Phase", status: "in-progress", progress: 0.70 }
    ]
  },
  currentFocus: ["Implementing Feature X", "Optimizing Component Y"],
  risks: ["Concerns about API stability", "Resource shortage"]
};
```

### 2. Task Management

**Template**:
```javascript
// [PROJECT: project-name] [TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00] [TYPE: Task Management]
const taskManagement = {
  highPriority: [
    {
      description: "Implement Feature X",     // Required
      status: "in-progress",                 // Required
      deadline: "2025-03-15",                // Optional
      assignee: "Team A",                    // Optional
      dependencies: "Component Y"            // Optional
    }
  ],
  mediumPriority: [],
  completedTasks: [
    {
      description: "Setup Development Environment",
      status: "completed"
    }
  ]
};
```

### 3. Meeting Summary

**Template**:
```javascript
// [PROJECT: project-name] [TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00] [TYPE: Meeting Summary]
const meetingMinutes = {
  title: "Weekly Progress Meeting",
  date: "2025-03-23",
  attendees: [
    { department: "Development", members: ["Sato", "Suzuki"] },
    { department: "Design", members: ["Tanaka"] }
  ],
  topics: ["Progress Report", "Risk Management", "Next Week's Plan"],
  decisions: [
    "Approve additional resource allocation",
    "Delay release date by one week"
  ],
  actionItems: [
    { description: "Procedure for adding resources", assignee: "Sato", dueDate: "2025-03-25" },
    { description: "Revise test plan", assignee: "Suzuki", dueDate: "2025-03-24" }
  ]
};
```

## Effective Information Management Techniques

### 1. Context Management (run_id)

Using mem0's `run_id` parameter, you can logically group related information. This helps maintain specific conversation flows or project contexts.

**Recommended Format**:
```
project:project-name:category:subcategory
```

**Usage Example**:
```javascript
// Managing information related to a specific feature
add_project_memory(
  "// [PROJECT: Member System] [TYPE: Technical Specification]\nconst authSpec = {...};",
  run_id="project:member-system:feature:authentication",
  metadata={"type": "specification"}
);

// Adding a task for the same feature
add_project_memory(
  "// [PROJECT: Member System] [TYPE: Task Management]\nconst authTasks = {...};",
  run_id="project:member-system:feature:authentication",
  metadata={"type": "task"}
);

// Searching for related information
search_project_memories("authentication", {
  "run_id": "project:member-system:feature:authentication"
});
```

### 2. Effective Use of Metadata

Using metadata can enhance the searchability of information. We recommend using the following schema:
```javascript
{
  "type": "meeting|task|decision|status|risk", // Type of information
  "priority": "high|medium|low",               // Priority
  "tags": ["frontend", "backend", "design"],   // Related tags
  "status": "pending|in-progress|completed"    // Status
}
```

**Usage Example**:
```javascript
// Registering a high-priority task
add_project_memory(
  "// [PROJECT: Member System] [TYPE: Task Management]\nconst task = {...};",
  metadata={
    "type": "task",
    "priority": "high",
    "tags": ["frontend", "authentication"]
  }
);

// Searching for tasks with a specific tag
search_project_memories("task", {
  "metadata": {
    "tags": ["frontend"]
  }
});
```

### 3. Information Lifecycle Management

Using the `immutable` and `expiration_date` parameters, you can manage the lifecycle of information.

**Usage Example**:
```javascript
// Recording an immutable decision
add_project_memory(
  "// [PROJECT: Member System] [TYPE: Decision Record]\nconst decision = {...};",
  immutable=True,  // Set as immutable
  metadata={"type": "decision"}
);

// Information with an expiration date
add_project_memory(
  "// [PROJECT: Member System] [TYPE: Meeting Summary]\nconst meeting = {...};",
  expiration_date="2025-06-30",  // Expires on this date
  metadata={"type": "meeting"}
);
```

## Practical Usage Patterns

### 1. Sprint Management Example
```javascript
// Registering the sprint plan at the start
add_project_memory(
  "// [PROJECT: Member System] [TIMESTAMP: 2025-05-01T10:00:00+09:00] [TYPE: Project Status]\n" +
  "const sprintPlan = {\n" +
  "  sprint: \"Sprint-2025-05\",\n" +
  "  duration: \"2 weeks\",\n" +
  "  goals: [\"Implement authentication feature\", \"Improve UI\"],\n" +
  "  tasks: [\n" +
  "    { description: \"Implement login screen\", assignee: \"Tanaka\", estimate: \"3 days\" },\n" +
  "    { description: \"API integration\", assignee: \"Sato\", estimate: \"2 days\" }\n" +
  "  ]\n" +
  "};",
  run_id="project:member-system:sprint:2025-05",
  metadata={"type": "status", "tags": ["sprint-planning"]}
);

// Mid-sprint progress report
add_project_memory(
  "// [PROJECT: Member System] [TIMESTAMP: 2025-05-08T15:00:00+09:00] [TYPE: Project Status]\n" +
  "const progress = {\n" +
  "  sprint: \"Sprint-2025-05\",\n" +
  "  completionLevel: 0.4,\n" +
  "  status: [\n" +
  "    { task: \"Implement login screen\", progress: 0.7, status: \"in-progress\" },\n" +
  "    { task: \"API integration\", progress: 0.2, status: \"in-progress\" }\n" +
  "  ],\n" +
  "  blockers: [\"Change in API response specification\"]\n" +
  "};",
  run_id="project:member-system:sprint:2025-05",
  metadata={"type": "status", "tags": ["sprint-progress"]}
);
```

### 2. Risk Management Example
```javascript
// Registering a risk
add_project_memory(
  "// [PROJECT: Member System] [TIMESTAMP: 2025-05-03T11:00:00+09:00] [TYPE: Risk Assessment]\n" +
  "const risk = {\n" +
  "  description: \"Concerns about external API stability\",\n" +
  "  impact: \"High\",\n" +
  "  probability: \"Medium\",\n" +
  "  mitigation: \"Implement fallback mechanism\",\n" +
  "  owner: \"Development Lead\"\n" +
  "};",
  run_id="project:member-system:risk:api-stability",
  metadata={"type": "risk", "priority": "high"}
);

// Updating the risk status
add_project_memory(
  "// [PROJECT: Member System] [TIMESTAMP: 2025-05-10T16:30:00+09:00] [TYPE: Risk Assessment]\n" +
  "const riskUpdate = {\n" +
  "  description: \"Concerns about external API stability\",\n" +
  "  status: \"Resolved\",\n" +
  "  resolution: \"Fallback mechanism implementation completed\"\n" +
  "};",
  run_id="project:member-system:risk:api-stability",
  metadata={"type": "risk", "priority": "medium"}
);
```

## Important Points

- **Standard Metadata**: Always include the project name and timestamp.
- **Data Format**: Use structured data (JavaScript objects, JSON, YAML).
- **Context Management**: Use `run_id` hierarchically to maintain information relevance.
- **Search Efficiency**: Consistent metadata and structure improve search efficiency.

## 4. Implementation Strategy

To implement the above improvements, we recommend the following steps:

1. **Enhance the `add_project_memory` Method**:
   - Update documentation strings: Improve usage examples and parameter descriptions.
   - Error handling: Provide more detailed error information.
   - Response format: Explicitly state the parameters used.

2. **Update Custom Instructions**:
   - Enrich template examples.
   - Clarify recommended usage of `run_id` (introduce hierarchical structure).
   - Standardize metadata schema.
   - Provide practical usage examples.

These improvements will enhance the usability and efficiency of information management while maintaining compatibility with existing APIs.

## 5. Summary

The proposed improvements provide value in the following ways while maintaining compatibility with existing mem0 MCP server functions:

1. **Enhanced Structured Information Management**: Templates and standardized metadata promote consistent information structure.
2. **Improved Context Management**: Hierarchical use of `run_id` makes managing related information easier.
3. **Improved Usability**: Detailed documentation and practical examples reduce the learning curve.

These enhancements will further increase the effectiveness of the mem0 MCP server as a project management tool.