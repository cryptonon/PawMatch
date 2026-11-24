import { useEffect, useState } from "react";
import "./index.css";

type Cat = {
  id: number;
  name: string;
  age: number;
  breed: string;
  arrival_date: string;
  temperament: string;
  good_with_dogs: boolean;
  good_with_children: boolean;
  status: string;
};

type Ranked = { cat: Cat; score: number; reason: string };

type Dashboard = {
  cats_in_shelter: number;
  average_stay_days: number;
  adoption_rate: number;
  longest_waiting: Cat[];
};

type WatchEntry = {
  cat: Cat;
  probability: number;
  flagged: boolean;
  reason: string;
};

const API = "http://localhost:8000";

function initials(name: string) {
  return name.slice(0, 1).toUpperCase();
}

export default function App() {
  const [cats, setCats] = useState<Cat[]>([]);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [ranked, setRanked] = useState<Ranked[]>([]);
  const [hasDog, setHasDog] = useState(false);
  const [hasChildren, setHasChildren] = useState(false);
  const [temperament, setTemperament] = useState("calm");
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");
  const [watchlist, setWatchlist] = useState<WatchEntry[]>([]);
  const [bioCatId, setBioCatId] = useState("");
  const [bioNotes, setBioNotes] = useState("");
  const [bioText, setBioText] = useState("");
  const [bioState, setBioState] = useState("");
  const [bioError, setBioError] = useState("");

  function bioAction(action: string) {
    if (!bioCatId) return;
    setBioError("");
    const url = `${API}/cats/${bioCatId}/bio/${action}`;
    const options: RequestInit =
      action === "draft"
        ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ notes: bioNotes || null }) }
        : { method: "POST" };
    fetch(url, options)
      .then((r) => {
        if (!r.ok) throw new Error("That step is not allowed for this bio yet.");
        return r.json();
      })
      .then((body) => {
        setBioText(body.text);
        setBioState(body.state);
      })
      .catch((e) => setBioError(e.message));
  }

  useEffect(() => {
    fetch(`${API}/cats`)
      .then((r) => r.json())
      .then((all: Cat[]) => setCats(all.filter((c) => c.status === "available")))
      .catch(() => setError("Could not reach the PawMatch API on port 8000."));
    fetch(`${API}/dashboard`)
      .then((r) => r.json())
      .then(setDashboard)
      .catch(() => {});
    fetch(`${API}/watchlist`)
      .then((r) => r.json())
      .then(setWatchlist)
      .catch(() => {});
  }, []);

  function search() {
    const params = new URLSearchParams({
      has_dog: String(hasDog),
      has_children: String(hasChildren),
      temperament,
    });
    fetch(`${API}/match?${params}`)
      .then((r) => r.json())
      .then((body) => {
        setRanked(body.ranked ?? []);
        setSearched(true);
      })
      .catch(() => setError("Search failed. Is the backend running?"));
  }

  return (
    <>
      <header className="nav">
        <div className="nav-inner">
          <span className="nav-brand">PawMatch</span>
          <a href="#cats">Cats</a>
          <a href="#match">Find a match</a>
          <a href="#watchlist">Watchlist</a>
          <a href="#bios">Bios</a>
          <a href="#shelter">Shelter</a>
          <a className="nav-cta" href="#match">Find a match</a>
        </div>
      </header>

      <main className="page">
        <section className="hero">
          <h1>Find the cat that fits your home.</h1>
          <p>
            PawMatch tracks every shelter cat from intake to adoption, then
            ranks the cats that fit your home, with the reason shown for each one.
          </p>
          <a className="hero-cta" href="#match">Find your match</a>
        </section>

        {dashboard && (
          <section className="stats" id="shelter" aria-label="Shelter numbers">
            <div className="stat">
              <div className="stat-value">{dashboard.cats_in_shelter}</div>
              <div className="stat-label">Cats at the shelter</div>
            </div>
            <div className="stat">
              <div className="stat-value">{dashboard.average_stay_days} days</div>
              <div className="stat-label">Average length of stay</div>
            </div>
            <div className="stat">
              <div className="stat-value">
                {Math.round(dashboard.adoption_rate * 100)}%
              </div>
              <div className="stat-label">Adoption rate</div>
            </div>
          </section>
        )}

        {error && <p className="notice">{error}</p>}

        <section id="cats">
          <h2 className="section-title">Cats at the shelter</h2>
          <p className="section-sub">
            {cats.length} available now. The longest waiting cat is{" "}
            {dashboard?.longest_waiting?.[0]?.name ?? "shown in the dashboard"}.
          </p>
          <div className="cat-grid">
            {cats.map((c) => (
              <article className="cat-card" key={c.id}>
                <div className={`avatar ${c.temperament}`}>{initials(c.name)}</div>
                <h3>{c.name}</h3>
                <p className="cat-meta">
                  {c.age} {c.age === 1 ? "year" : "years"} &middot; {c.breed}
                  <br />
                  Arrived {c.arrival_date}
                </p>
                <span className="pill">{c.temperament}</span>
                {c.good_with_dogs && <span className="pill good">Good with dogs</span>}
                {c.good_with_children && (
                  <span className="pill good">Good with children</span>
                )}
              </article>
            ))}
          </div>
        </section>

        <section id="match">
          <h2 className="section-title">Find a match</h2>
          <p className="section-sub">
            Tell us about your home. Every result shows its score and why the cat fits.
          </p>
          <div className="match-card">
            <div className="match-controls">
              <label className={`toggle ${hasDog ? "on" : ""}`}>
                <input
                  type="checkbox"
                  checked={hasDog}
                  onChange={(e) => setHasDog(e.target.checked)}
                />
                Dog at home
              </label>
              <label className={`toggle ${hasChildren ? "on" : ""}`}>
                <input
                  type="checkbox"
                  checked={hasChildren}
                  onChange={(e) => setHasChildren(e.target.checked)}
                />
                Children at home
              </label>
              <select
                value={temperament}
                onChange={(e) => setTemperament(e.target.value)}
                aria-label="Preferred temperament"
              >
                <option value="calm">Calm temperament</option>
                <option value="energetic">Energetic temperament</option>
              </select>
              <button className="btn" onClick={search}>Search</button>
            </div>

            {searched && ranked.length === 0 && (
              <p className="section-sub">No cats match those filters yet.</p>
            )}
            <ol className="ranked">
              {ranked.map((entry, i) => (
                <li key={entry.cat.id}>
                  <span className="rank-num">{i + 1}</span>
                  <div className="rank-body">
                    <div className="rank-name">{entry.cat.name}</div>
                    <div className="rank-reason">{entry.reason}</div>
                  </div>
                  <div className="score">
                    <div className="score-num">{entry.score}</div>
                    <div className="score-label">out of 100</div>
                    <div className="score-bar">
                      <div style={{ width: `${entry.score}%` }} />
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="watchlist">
          <h2 className="section-title">Long-stay watchlist</h2>
          <p className="section-sub">
            Available cats most likely to wait too long, highest risk first.
            Flagged cats need staff attention now.
          </p>
          <div className="match-card">
            <ol className="ranked">
              {watchlist.map((entry) => (
                <li key={entry.cat.id}>
                  <div className="rank-body">
                    <div className="rank-name">
                      {entry.cat.name}{" "}
                      {entry.flagged && <span className="pill good">Needs attention</span>}
                    </div>
                    <div className="rank-reason">{entry.reason}</div>
                  </div>
                  <div className="score">
                    <div className="score-num">{Math.round(entry.probability * 100)}%</div>
                    <div className="score-label">long-stay chance</div>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="bios">
          <h2 className="section-title">Adoption bios</h2>
          <p className="section-sub">
            Draft a bio from the cat profile and staff notes. Staff approve
            it before it can be published. A draft can never publish.
          </p>
          <div className="match-card">
            <div className="match-controls">
              <select
                value={bioCatId}
                onChange={(e) => setBioCatId(e.target.value)}
                aria-label="Cat for the bio"
              >
                <option value="">Choose a cat</option>
                {cats.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
              <button className="btn" onClick={() => bioAction("draft")}>Draft bio</button>
              <button className="btn" onClick={() => bioAction("approve")}>Approve</button>
              <button className="btn" onClick={() => bioAction("publish")}>Publish</button>
            </div>
            <textarea
              value={bioNotes}
              onChange={(e) => setBioNotes(e.target.value)}
              placeholder="Staff notes for the bio, optional"
              rows={2}
              style={{ width: "100%", font: "inherit", fontSize: 14, padding: 10, borderRadius: 12, border: "1px solid #d2d2d7", marginTop: 8 }}
            />
            {bioError && <p className="notice">{bioError}</p>}
            {bioText && (
              <>
                <p style={{ fontSize: 15, lineHeight: 1.6 }}>{bioText}</p>
                <span className="pill">{bioState}</span>
              </>
            )}
          </div>
        </section>

        <footer className="footer">
          PawMatch &middot; A smart cat adoption tracker for shelters
        </footer>
      </main>
    </>
  );
}
