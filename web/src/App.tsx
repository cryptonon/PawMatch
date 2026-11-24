import { useEffect, useState } from "react";

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

const API = "http://localhost:8000";

export default function App() {
  const [cats, setCats] = useState<Cat[]>([]);
  const [ranked, setRanked] = useState<Ranked[]>([]);
  const [hasDog, setHasDog] = useState(false);
  const [hasChildren, setHasChildren] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/cats`)
      .then((r) => r.json())
      .then(setCats)
      .catch(() => setError("Could not reach the PawMatch API on port 8000."));
  }, []);

  function search() {
    const params = new URLSearchParams({
      has_dog: String(hasDog),
      has_children: String(hasChildren),
      temperament: "calm",
    });
    fetch(`${API}/match?${params}`)
      .then((r) => r.json())
      .then((body) => setRanked(body.ranked ?? []))
      .catch(() => setError("Search failed. Is the backend running?"));
  }

  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 640, margin: "0 auto", padding: 24 }}>
      <h1>PawMatch</h1>
      <p>A smart cat adoption tracker for shelters.</p>
      {error && <p>{error}</p>}
      <h2>Cats at the shelter</h2>
      <ul>
        {cats
          .filter((c) => c.status === "available")
          .map((c) => (
            <li key={c.id}>
              {c.name}, {c.age} years, {c.breed}, arrived {c.arrival_date} ({c.temperament})
            </li>
          ))}
      </ul>
      <h2>Find a match</h2>
      <label>
        <input type="checkbox" checked={hasDog} onChange={(e) => setHasDog(e.target.checked)} />
        Dog at home
      </label>{" "}
      <label>
        <input
          type="checkbox"
          checked={hasChildren}
          onChange={(e) => setHasChildren(e.target.checked)}
        />
        Children at home
      </label>{" "}
      <button onClick={search}>Search</button>
      <ol>
        {ranked.map((entry) => (
          <li key={entry.cat.id}>
            {entry.cat.name}: {entry.score}/100. {entry.reason}
          </li>
        ))}
      </ol>
    </main>
  );
}
