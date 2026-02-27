import StatusWidget from "../status-widget";

export default function WelcomePage() {
  return (
    <div className="page">
      <div className="container">
        <nav className="nav">
          <div className="brand">
            <span className="dot" />
            HireUs
          </div>
          <div className="cta">
            <a className="btn ghost" href="/">
              Home
            </a>
            <a className="btn primary" href="http://127.0.0.1:8000/docs">
              API Docs
            </a>
          </div>
        </nav>

        <section className="hero">
          <div>
            <h1>Welcome, founder.</h1>
            <p>
              This page gives you the minimum steps to start using the platform
              today. Follow the checklist, then return to the main page when
              you’re done.
            </p>
            <div className="cta">
              <a className="btn primary" href="#steps">
                Founder Checklist
              </a>
              <a className="btn ghost" href="/">
                Main Page
              </a>
            </div>
          </div>
          <div className="floating">
            <span className="badge">System Status</span>
            <StatusWidget />
            <div style={{ marginTop: "12px" }}>
              API Base: {process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000"}
            </div>
            <div className="floaty one" />
            <div className="floaty two" />
          </div>
        </section>

        <section className="section" id="steps">
          <h2>Founder checklist</h2>
          <div className="steps">
            <div className="step">1. Register founder and create organization.</div>
            <div className="step">2. Invite interviewers.</div>
            <div className="step">3. Create role and competencies.</div>
            <div className="step">4. Generate interview kit.</div>
            <div className="step">5. Create candidate workflow.</div>
            <div className="step">6. Review evaluations and signals.</div>
            <div className="step">7. Generate brief and record decision.</div>
          </div>
        </section>

        <section className="section">
          <h2>Quick API shortcuts</h2>
          <div className="grid">
            <div className="card">
              <div className="tag">Auth</div>
              <div>POST /api/auth/register</div>
              <div>POST /api/auth/login</div>
            </div>
            <div className="card">
              <div className="tag">Roles</div>
              <div>POST /api/roles</div>
              <div>GET /api/roles</div>
            </div>
            <div className="card">
              <div className="tag">Kits</div>
              <div>POST /api/interview-kits/generate</div>
              <div>GET /api/interview-kits/role/:roleId</div>
            </div>
            <div className="card">
              <div className="tag">Workflow</div>
              <div>POST /api/workflows</div>
              <div>PUT /api/workflows/:id/stages</div>
            </div>
          </div>
        </section>

        <footer className="footer">
          HireUs • Welcome page for founders
        </footer>
      </div>
    </div>
  );
}
