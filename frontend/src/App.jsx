import { useCallback, useEffect, useState } from "react";
import {
  createCriminal,
  getCases,
  getCriminals,
  linkCriminalToCase,
} from "./api";
import "./App.css";

const EMPTY_CRIMINAL_FORM = {
  FullName: "",
  DateOfBirth: "",
  Address: "",
};

const EMPTY_LINK_FORM = {
  CriminalID: "",
  CaseID: "",
  PersonRole: "Suspect",
};

function formatDate(value) {
  return value ? String(value).slice(0, 10) : "—";
}

function statusClass(status) {
  return String(status || "")
    .toLowerCase()
    .replaceAll(" ", "-");
}

function App() {
  const [cases, setCases] = useState([]);
  const [criminals, setCriminals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [criminalSearch, setCriminalSearch] = useState("");
  const [caseStatusFilter, setCaseStatusFilter] = useState("All");
  const [form, setForm] = useState(EMPTY_CRIMINAL_FORM);
  const [showLinkForm, setShowLinkForm] = useState(false);
  const [linking, setLinking] = useState(false);
  const [linkMessage, setLinkMessage] = useState("");
  const [linkMessageType, setLinkMessageType] = useState("");
  const [linkForm, setLinkForm] = useState(EMPTY_LINK_FORM);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [caseData, criminalData] = await Promise.all([
        getCases(),
        getCriminals(),
      ]);

      setCases(caseData);
      setCriminals(criminalData);
    } catch (err) {
      setError(err.message || "Could not load records.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleSubmit(event) {
    event.preventDefault();
    const fullName = form.FullName.trim();

    if (!fullName) {
      setError("Enter a full name to create a criminal record.");
      return;
    }

    setSaving(true);
    setError("");

    try {
      await createCriminal({
        FullName: fullName,
        DateOfBirth: form.DateOfBirth || null,
        Address: form.Address.trim() || null,
      });

      setForm(EMPTY_CRIMINAL_FORM);
      setShowForm(false);
      await loadData();
    } catch (err) {
      setError(err.message || "Could not save the record.");
    } finally {
      setSaving(false);
    }
  }

  async function handleLinkSubmit(event) {
    event.preventDefault();
    setLinking(true);
    setLinkMessage("");

    try {
      const result = await linkCriminalToCase({
        CriminalID: Number(linkForm.CriminalID),
        CaseID: Number(linkForm.CaseID),
        PersonRole: linkForm.PersonRole,
      });

      setLinkMessage(result.message || "Criminal linked successfully.");
      setLinkMessageType("success");
      setLinkForm(EMPTY_LINK_FORM);
    } catch (err) {
      setLinkMessage(err.message || "Could not link criminal to case.");
      setLinkMessageType("error");
    } finally {
      setLinking(false);
    }
  }

  const openCases = cases.filter((item) => item.CaseStatus === "Open").length;
  const investigatingCases = cases.filter(
    (item) => item.CaseStatus === "Under Investigation",
  ).length;
  const closedCases = cases.filter(
    (item) => item.CaseStatus === "Closed",
  ).length;
  const search = criminalSearch.trim().toLowerCase();
  const filteredCriminals = criminals.filter((criminal) => {
    const name = String(criminal.FullName || "").toLowerCase();
    const id = String(criminal.CriminalID);
    return name.includes(search) || id.includes(search);
  });
  const filteredCases = cases.filter(
    (item) =>
      caseStatusFilter === "All" || item.CaseStatus === caseStatusFilter,
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="CDBMS dashboard">
          <span className="brand-mark" aria-hidden="true">C</span>
          <span className="brand-copy">
            <strong>CDBMS</strong>
            <span>Records &amp; Intelligence</span>
          </span>
        </a>
        <div className="topbar-meta">
          <span className="system-status">
            <span className="status-dot" />
            System online
          </span>
          <span className="topbar-divider" />
          <span className="secure-label">Secure workspace</span>
        </div>
      </header>

      <div className="dashboard">
        <section className="page-heading">
          <div>
            <p className="eyebrow">OVERVIEW</p>
            <h1>Dashboard</h1>
            <p className="page-description">
              A clear view of active cases and criminal records.
            </p>
          </div>
          <button
            className="button button-secondary refresh-button"
            type="button"
            onClick={loadData}
            disabled={loading || saving}
          >
            <span className={loading ? "refresh-icon is-spinning" : "refresh-icon"} aria-hidden="true">
              ↻
            </span>
            {loading ? "Refreshing…" : "Refresh data"}
          </button>
        </section>

        {error && (
          <p className="feedback feedback-error" role="alert">
            <span aria-hidden="true">!</span>
            {error}
          </p>
        )}

        <section className="stats-grid" aria-label="Case statistics">
          <article className="stat-card stat-card-total">
            <div className="stat-topline">
              <span className="stat-label">Total cases</span>
              <span className="stat-icon" aria-hidden="true">#</span>
            </div>
            <strong className="stat-value">{cases.length}</strong>
            <span className="stat-caption">Across all case statuses</span>
          </article>
          <article className="stat-card stat-card-open">
            <div className="stat-topline">
              <span className="stat-label">Open cases</span>
              <span className="stat-icon" aria-hidden="true">↗</span>
            </div>
            <strong className="stat-value">{openCases}</strong>
            <span className="stat-caption">Awaiting investigation</span>
          </article>
          <article className="stat-card stat-card-investigating">
            <div className="stat-topline">
              <span className="stat-label">Under investigation</span>
              <span className="stat-icon" aria-hidden="true">⌕</span>
            </div>
            <strong className="stat-value">{investigatingCases}</strong>
            <span className="stat-caption">Currently in progress</span>
          </article>
          <article className="stat-card stat-card-closed">
            <div className="stat-topline">
              <span className="stat-label">Closed cases</span>
              <span className="stat-icon" aria-hidden="true">✓</span>
            </div>
            <strong className="stat-value">{closedCases}</strong>
            <span className="stat-caption">Resolved and archived</span>
          </article>
        </section>

        <section className="content-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">PEOPLE</p>
              <h2>Criminal records</h2>
              <p className="section-description">
                {filteredCriminals.length} of {criminals.length} records
              </p>
            </div>
            <button
              className="button button-primary"
              type="button"
              onClick={() => setShowForm((open) => !open)}
              disabled={saving}
              aria-expanded={showForm}
            >
              {showForm ? "Cancel" : <><span aria-hidden="true">＋</span> Add criminal</>}
            </button>
          </div>

          {showForm && (
            <form className="record-form" onSubmit={handleSubmit}>
              <label>
                Full name <span className="required">*</span>
                <input
                  type="text"
                  value={form.FullName}
                  onChange={(event) =>
                    setForm({ ...form, FullName: event.target.value })
                  }
                  maxLength={100}
                  required
                  placeholder="Enter full name"
                  autoComplete="name"
                />
              </label>
              <label>
                Date of birth
                <input
                  type="date"
                  value={form.DateOfBirth}
                  onChange={(event) =>
                    setForm({ ...form, DateOfBirth: event.target.value })
                  }
                />
              </label>
              <label>
                Address
                <input
                  type="text"
                  value={form.Address}
                  onChange={(event) =>
                    setForm({ ...form, Address: event.target.value })
                  }
                  maxLength={200}
                  placeholder="Enter address"
                  autoComplete="street-address"
                />
              </label>
              <button className="button button-primary form-submit" type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save record"}
              </button>
            </form>
          )}

          <div className="table-toolbar">
            <label className="search-field">
              <span className="search-icon" aria-hidden="true">⌕</span>
              <input
                type="search"
                placeholder="Search by name or ID"
                value={criminalSearch}
                onChange={(event) => setCriminalSearch(event.target.value)}
                aria-label="Search criminal records by name or ID"
              />
              {criminalSearch && (
                <button
                  className="clear-search"
                  type="button"
                  onClick={() => setCriminalSearch("")}
                  aria-label="Clear search"
                >
                  ×
                </button>
              )}
            </label>
            <span className="result-count">{filteredCriminals.length} results</span>
          </div>

          {loading ? (
            <p className="empty-state">Loading criminal records…</p>
          ) : filteredCriminals.length === 0 ? (
            <p className="empty-state">
              {criminals.length === 0
                ? "No criminal records found. Add a record to get started."
                : "No records match your search. Try another name or ID."}
            </p>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Record ID</th>
                    <th scope="col">Full name</th>
                    <th scope="col">Date of birth</th>
                    <th scope="col">Address</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCriminals.map((criminal) => (
                    <tr key={criminal.CriminalID}>
                      <td><span className="record-id">CR-{criminal.CriminalID}</span></td>
                      <td className="person-name">{criminal.FullName}</td>
                      <td>{formatDate(criminal.DateOfBirth)}</td>
                      <td>{criminal.Address || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="content-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">INVESTIGATIONS</p>
              <h2>Case records</h2>
              <p className="section-description">
                {filteredCases.length} of {cases.length} cases
              </p>
            </div>
            <label className="filter-field">
              <span>Status</span>
              <select
                value={caseStatusFilter}
                onChange={(event) => setCaseStatusFilter(event.target.value)}
                aria-label="Filter cases by status"
              >
                <option value="All">All cases</option>
                <option value="Open">Open</option>
                <option value="Under Investigation">Under investigation</option>
                <option value="Closed">Closed</option>
              </select>
            </label>
          </div>

          {loading ? (
            <p className="empty-state">Loading case records…</p>
          ) : filteredCases.length === 0 ? (
            <p className="empty-state">
              {cases.length === 0
                ? "No case records found."
                : "No cases match this status filter."}
            </p>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Case ID</th>
                    <th scope="col">FIR number</th>
                    <th scope="col">Crime type</th>
                    <th scope="col">Officer</th>
                    <th scope="col">Status</th>
                    <th scope="col">Opened</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCases.map((item) => (
                    <tr key={item.CaseID}>
                      <td><span className="record-id">CS-{item.CaseID}</span></td>
                      <td>{item.FIRNumber}</td>
                      <td className="person-name">{item.CrimeType}</td>
                      <td>{item.OfficerName}</td>
                      <td>
                        <span className={`case-status ${statusClass(item.CaseStatus)}`}>
                          <span className="status-dot" />
                          {item.CaseStatus}
                        </span>
                      </td>
                      <td>{formatDate(item.OpenedDate)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="content-section link-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">CASE MANAGEMENT</p>
              <h2>Link a person to a case</h2>
              <p className="section-description">
                Associate an existing criminal record with a case.
              </p>
            </div>
            <button
              className="button button-secondary"
              type="button"
              onClick={() => {
                setShowLinkForm((open) => !open);
                setLinkMessage("");
              }}
              aria-expanded={showLinkForm}
            >
              {showLinkForm ? "Cancel" : "＋ Link to case"}
            </button>
          </div>

          {showLinkForm && (
            <form className="record-form link-form" onSubmit={handleLinkSubmit}>
              <label>
                Criminal <span className="required">*</span>
                <select
                  required
                  value={linkForm.CriminalID}
                  onChange={(event) =>
                    setLinkForm({ ...linkForm, CriminalID: event.target.value })
                  }
                >
                  <option value="">Select a criminal</option>
                  {criminals.map((criminal) => (
                    <option key={criminal.CriminalID} value={criminal.CriminalID}>
                      {criminal.FullName} (ID: {criminal.CriminalID})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Case <span className="required">*</span>
                <select
                  required
                  value={linkForm.CaseID}
                  onChange={(event) =>
                    setLinkForm({ ...linkForm, CaseID: event.target.value })
                  }
                >
                  <option value="">Select a case</option>
                  {cases.map((item) => (
                    <option key={item.CaseID} value={item.CaseID}>
                      Case {item.CaseID} — FIR {item.FIRNumber}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Role <span className="required">*</span>
                <select
                  value={linkForm.PersonRole}
                  onChange={(event) =>
                    setLinkForm({ ...linkForm, PersonRole: event.target.value })
                  }
                >
                  <option value="Suspect">Suspect</option>
                  <option value="Accused">Accused</option>
                  <option value="Witness">Witness</option>
                  <option value="Convicted">Convicted</option>
                </select>
              </label>
              <button
                className="button button-primary form-submit"
                type="submit"
                disabled={linking || criminals.length === 0 || cases.length === 0}
              >
                {linking ? "Linking…" : "Save link"}
              </button>
            </form>
          )}

          {linkMessage && (
            <p className={`feedback feedback-${linkMessageType}`} role="status" aria-live="polite">
              {linkMessage}
            </p>
          )}
        </section>

        <footer className="page-footer">
          <span>CDBMS <span aria-hidden="true">·</span> Records &amp; Intelligence</span>
          <span>Authorized access only</span>
        </footer>
      </div>
    </main>
  );
}

export default App;
