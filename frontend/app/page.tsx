import StatusWidget from "./status-widget";

export default function Page() {
  return (
    <div className="page">
      <div className="container">
        <nav className="nav">
          <div className="brand">
            <span className="dot" />
            HireUs
          </div>
          <div className="cta">
            <a className="btn ghost" href="/welcome">
              Welcome
            </a>
            <a className="btn ghost" href="/console">
              Console
            </a>
            <a className="btn ghost" href="#how">
              How It Works
            </a>
            <a className="btn primary" href="#start">
              Start Now
            </a>
          </div>
        </nav>

        <section className="hero" id="start">
          <div>
            <h1>Structured hiring that founders can run in one afternoon.</h1>
            <p>
              HireUs turns your hiring process into a repeatable system. Define
              a role once, generate interview kits with AI, and collect
              consistent evaluations that lead to confident decisions.
            </p>
            <div className="cta">
              <a className="btn primary" href="/console">
                Open Console
              </a>
              <a className="btn ghost" href="#workflow">
                See Workflow
              </a>
            </div>
          </div>
          <div className="floating">
            <span className="badge">Founders View</span>
            <h3>Role: Backend Engineer</h3>
            <p>Competencies: Python, System Design, Ownership</p>
            <div className="grid">
              <div className="card">
                <div className="tag">AI Kit</div>
                <div>12 interview questions</div>
              </div>
              <div className="card">
                <div className="tag">Signals</div>
                <div>Weighted score: 4.2</div>
              </div>
              <div className="card">
                <div className="tag">Decision</div>
                <div>Recommendation: Hire</div>
              </div>
            </div>
            <div className="floaty one" />
            <div className="floaty two" />
          </div>
        </section>

        <section className="section">
          <div className="floating">
            <h2>Live API status</h2>
            <p>Frontend checks the backend health endpoint.</p>
            <ApiStatus />
            <div className="floaty one" />
            <div className="floaty two" />
          </div>
        </section>

        <section className="section" id="how">
          <h2>How founders use it</h2>
          <div className="steps">
            <div className="step">1. Define the role and competencies.</div>
            <div className="step">2. Generate interview kits with AI.</div>
            <div className="step">3. Run workflows with staged interviews.</div>
            <div className="step">4. Collect structured scorecards.</div>
            <div className="step">5. Review signals and record a decision.</div>
          </div>
        </section>

        <section className="section" id="workflow">
          <h2>Workflow pipeline</h2>
          <div className="grid">
            <div className="card">
              <div className="tag">Stage 1</div>
              <div>Screening interview</div>
            </div>
            <div className="card">
              <div className="tag">Stage 2</div>
              <div>Technical deep dive</div>
            </div>
            <div className="card">
              <div className="tag">Stage 3</div>
              <div>System design</div>
            </div>
            <div className="card">
              <div className="tag">Stage 4</div>
              <div>Final decision</div>
            </div>
          </div>
        </section>

        <section className="section">
          <h2>Backend API flow (simple view)</h2>
          <div className="grid">
            <div className="card">
              <div className="tag">1. Auth</div>
              <div>POST /api/auth/register</div>
              <div>POST /api/auth/login</div>
            </div>
            <div className="card">
              <div className="tag">2. Roles</div>
              <div>POST /api/roles</div>
              <div>GET /api/roles</div>
            </div>
            <div className="card">
              <div className="tag">3. Interview Kits</div>
              <div>POST /api/interview-kits/generate</div>
              <div>GET /api/interview-kits/role/:roleId</div>
            </div>
            <div className="card">
              <div className="tag">4. Workflows</div>
              <div>POST /api/workflows</div>
              <div>PUT /api/workflows/:id/stages</div>
            </div>
            <div className="card">
              <div className="tag">5. Evaluations</div>
              <div>POST /api/evaluations</div>
              <div>GET /api/evaluations/workflow/:id</div>
            </div>
            <div className="card">
              <div className="tag">6. Decisions</div>
              <div>POST /api/decisions/generate-brief</div>
              <div>POST /api/decisions</div>
            </div>
            <div className="card">
              <div className="tag">7. Signals</div>
              <div>GET /api/signals/candidate/:cid/role/:rid</div>
            </div>
            <div className="card">
              <div className="tag">Org Ops</div>
              <div>POST /api/auth/invite</div>
              <div>POST /api/auth/accept-invite</div>
            </div>
          </div>
          <div className="steps">
            <div className="step">Founders create roles → AI generates kits → workflows assign interviewers.</div>
            <div className="step">Interviewers submit evaluations → signals aggregate scores.</div>
            <div className="step">AI briefs + final decisions lock workflows (reopen allowed by founders).</div>
            <div className="step">LLM limits: if AI fails, API returns 503. Retry or use Ollama fallback.</div>
          </div>
        </section>

        <section className="section">
          <h2>What makes it different</h2>
          <div className="grid">
            <div className="card">
              <div className="tag">Consistency</div>
              <div>Every candidate is scored on the same competencies.</div>
            </div>
            <div className="card">
              <div className="tag">Speed</div>
              <div>Generate kits in minutes, not weeks.</div>
            </div>
            <div className="card">
              <div className="tag">Transparency</div>
              <div>Audit trail for decisions and workflow changes.</div>
            </div>
            <div className="card">
              <div className="tag">AI + Control</div>
              <div>Ollama and OpenAI options with strict validation.</div>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="floating">
            <h2>Ready to run your next hire?</h2>
            <p>
              Start with a role definition, invite your interviewers, and let
              the system handle consistency.
            </p>
            <div className="cta">
              <a className="btn primary" href="http://127.0.0.1:8000/docs">
                API Docs
              </a>
              <a className="btn ghost" href="/welcome">
                Founder Welcome
              </a>
            </div>
            <div className="floaty one" />
            <div className="floaty two" />
          </div>
        </section>

        <footer className="footer">
          HireUs • Structured Hiring for Founders
        </footer>
      </div>
    </div>
  );
}

function ApiStatus() {
  return (
    <div className="card" style={{ marginTop: "12px" }}>
      <div className="tag">Backend</div>
      <StatusWidget />
    </div>
  );
}
