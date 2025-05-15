# NowGo-LLM

## Project Overview

NowGo-LLM is an advanced AI system designed to address the lack of contextualization and adaptive intelligence in generic corporate AI solutions. Unlike standard LLMs that operate generically, NowGo-LLM personalizes AI behavior according to each organization's specific profile, stage, sector, strategic objectives, and real-time data. It functions as an intelligent consultant, ready to assist in strategic, operational, and regulatory decision-making, providing a unique and tailored AI experience for every business.

## Objectives

*   Provide a highly contextualized and adaptive AI assistant for corporate use.
*   Enable businesses to leverage LLM capabilities tailored to their unique operational context.
*   Offer a modular and scalable platform that can integrate with various LLMs and enterprise systems.
*   Support diverse use cases, including document analysis, automated reporting, content creation, and strategic/regulatory support.
*   Deliver a personalized user experience through adaptive agent personas.

## Technologies Used

*   **Backend:** Python, FastAPI
*   **LLM Interaction:** OpenAI API (initially GPT-4-turbo, designed for LLaMA 3 interoperability)
*   **Orchestrator & Middleware (Conceptual - to be potentially split or integrated):** Logic primarily in Python backend; Node.js/Next.js considered for specific middleware tasks if needed.
*   **Frontend (Conceptual):** React (or Lovable)
*   **Vector Database (for Multi-RAG):** Pinecone (or similar)
*   **Document Processing & Embedding:** LangChain or LlamaIndex
*   **Environment Management:** Python Virtual Environments, Docker (for deployment)

## Architecture & Flow

The NowGo-LLM system is built on a modular architecture:

1.  **Frontend:** (Conceptual) A user-facing dashboard (React/Lovable) for interaction, onboarding, and displaying results.
2.  **Orchestrator (Python Backend):** This core component, residing within the Python backend, is responsible for:
    *   **Context Collection:** Gathering user profile, company profile (sector, stage), interaction history, and module accessed via the `ContextManager`.
    *   **Persona Selection:** Dynamically selecting the most appropriate `AgentPersona` (e.g., Strategy Consultant, Legal Expert) based on the collected context.
    *   **Request Handling:** Managing the overall flow of a user request to an agent response.
3.  **Agents (Python Backend):**
    *   **`AgentPersona`:** Defines various expert personas with specific system prompts and descriptions.
    *   **`BaseAgent`:** A foundational class that takes a persona and user prompt, incorporates context and conversation history, and interacts with the chosen LLM to generate a response.
    *   Specialized agents (e.g., `StrategicAgent`, `LegalAgent`) can inherit from `BaseAgent` for more tailored behavior.
4.  **LLM Backend (Python Backend):**
    *   **`openai_client`:** Manages communication with the OpenAI API (GPT-4-turbo).
    *   Designed to be model-agnostic, allowing future integration of other LLMs like LLaMA 3.
5.  **Multi-RAG System (Python Backend - Conceptual for initial RAG):**
    *   Manages retrieval-augmented generation using a vector database (e.g., Pinecone).
    *   Handles document loading, embedding, and contextual information retrieval to enhance LLM responses.
    *   Designed to support multiple RAG strategies or sources.
6.  **Analytics Layer (Conceptual):** For monitoring usage, satisfaction, and enabling continuous learning.

**Simplified Flow:**

*   User interacts via Frontend/API.
*   Request hits the FastAPI backend (`/v1/chat/interactive` endpoint).
*   The `Orchestrator` (`handle_user_request` function) is invoked.
*   `ContextManager` collects user, company, and interaction context.
*   `Orchestrator` selects an `AgentPersona`.
*   `Orchestrator` prepares context for the agent.
*   An instance of `BaseAgent` (with the selected persona) is used.
*   `BaseAgent` crafts a detailed prompt (including system message, history, user query, and injected context) and calls the LLM (e.g., GPT-4-turbo) via `openai_client`.
*   The LLM response is returned through the layers to the user.
*   Interaction is logged by `ContextManager`.

## Key Features & Use Cases

*   **Contextual Understanding:** Adapts to company-specific data, sector, and strategic goals.
*   **Adaptive Agent Personas:** Provides specialized assistance (Strategy, Legal, Data Analysis, Content Creation).
*   **Multi-RAG Capability:** Enhances responses with information retrieved from company documents and knowledge bases.
*   **Document Analysis:** Understands and summarizes internal documents (contracts, policies).
*   **Automated Reporting:** Generates management reports and insights.
*   **Content Creation:** Assists with institutional content, marketing materials, and emails.
*   **Strategic & Regulatory Support:** Provides context-aware assistance for growth, ESG, and compliance.
*   **Scalable & Modular:** Designed for SaaS multi-tenancy and integration with various LLMs.

## Getting Started / How to Run Locally

### Prerequisites

*   Python 3.11+
*   An OpenAI API Key

### Setup

1.  **Clone the repository (once it's on GitHub):**
    ```bash
    git clone <repository-url>
    cd NowGo-LLM
    ```
2.  **Create and activate a Python virtual environment (from the `NowGo-LLM/backend` directory):**
    ```bash
    cd backend
    python3.11 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies (from the `NowGo-LLM/backend` directory):**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    *   Navigate to the root of the project: `cd ..` (to be in `NowGo-LLM/`)
    *   Create a `.env` file by copying the example: `cp .env.example .env`
    *   Edit the `.env` file and add your actual OpenAI API key:
        ```env
        OPENAI_API_KEY=sk-yourActualOpenAIapiKeyGoesHere
        ```
        You can also adjust other settings like `BACKEND_PORT` if needed.

### Running the Backend Server

1.  **Ensure you are in the `NowGo-LLM/backend` directory and the virtual environment is activated.**
2.  **Start the Uvicorn server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    (The port can be configured in your `.env` file or overridden here).

3.  **Access the API:**
    *   **Health Check:** Open your browser or use curl: `http://localhost:8000/health`
    *   **API Documentation (Swagger UI):** `http://localhost:8000/docs`
        From the Swagger UI, you can test the `/v1/chat/interactive` endpoint.

### Example API Call (using curl)

```bash
curl -X POST "http://localhost:8000/v1/chat/interactive" \
-H "Content-Type: application/json" \
-d 
ginx
{
  "user_id": "user123",
  "company_id": "comp456",
  "prompt": "What are the main ESG goals for a tech company in its growth phase?",
  "module_accessed": "strategy_dashboard"
}

```

## Project Structure

```
NowGo-LLM/
├── .github/             # GitHub Actions workflows (CI/CD, etc.)
│   └── workflows/
├── .vscode/             # VSCode specific settings (optional)
├── backend/             # Main Python backend (FastAPI)
│   ├── app/             # Core application logic
│   │   ├── agents/      # Adaptive agent logic (personas.py, base_agent.py)
│   │   ├── core/        # Core utilities (openai_client.py)
│   │   ├── orchestration/ # Orchestration logic (orchestrator.py, context_manager.py)
│   │   ├── apis/        # (If API endpoints grow and need separation)
│   │   ├── rag/         # Multi-RAG system components
│   │   └── utils/       # General utility functions
│   ├── data/            # Sample data, data processing scripts
│   ├── notebooks/       # Jupyter notebooks for experimentation
│   ├── tests/           # Backend unit and integration tests
│   ├── venv/            # Python virtual environment (ignored by Git)
│   ├── Dockerfile       # For containerizing the backend
│   └── requirements.txt # Python dependencies
├── docs/                # Project documentation
│   ├── architecture.md
│   ├── setup_guide.md
│   └── api_reference.md
├── frontend/            # (Conceptual) React/Lovable frontend application
│   ├── public/
│   ├── src/
│   └── package.json
├── orchestrator/        # (Conceptual) Node/Next.js middleware if separated from backend
│   ├── src/
│   └── package.json
├── scripts/             # Utility scripts (deployment, setup, etc.)
├── tests/               # End-to-end tests covering multiple components
├── .env                 # Local environment variables (ignored by Git)
├── .env.example         # Example environment variables file
├── .gitignore           # Files and folders ignored by Git
├── LICENSE.md           # Project license file (e.g., MIT)
└── README.md            # This file: main project overview and instructions
```

## Contributing

(Details to be added - e.g., coding standards, branch strategy, pull request process).
We welcome contributions! Please refer to `CONTRIBUTING.md` (to be created) for more details.

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.

## Contact

(Details to be added if desired)

=======
# NowGo-LLM
