import Link from "next/link";
import type { Metadata } from "next";
import { Frame } from "@/components/site-header";
import { TRACKS } from "@/lib/tracks";

export const metadata: Metadata = {
  title: "Hong Kong Frontier Talent Operating System",
};

const JOURNEY = [
  {
    title: "Modular skills",
    body: "Finish a short self-check. The completion is written onto your Skills Passport, not stored as another course badge.",
  },
  {
    title: "Skills Passport",
    body: "A public page of modules, missions, and employer certifications. Copy one link and send it.",
  },
  {
    title: "Mission experience",
    body: "Join a live brief from an employer and submit a deliverable URL with notes about what you actually did.",
  },
  {
    title: "Employer validation",
    body: "The mission owner reviews the evidence and issues a competency certification back onto the passport.",
  },
];

export default function HomePage() {
  return (
    <Frame variant="home">
      <section className="hero">
        <p className="eyebrow">Hong Kong · Frontier talent</p>
        <h1>Show the work. Get it certified.</h1>
        <p className="lede">
          FTOS pairs modular skills with live industry missions across AI, NewSpace, Robotics, and the Low
          Altitude Economy. Employers certify what a person demonstrated, instead of collecting another
          course certificate.
        </p>
        <div className="actions">
          <Link className="button" href="/login">
            Sign in
          </Link>
          <Link className="button secondary" href="/passport/alex-chen">
            View a demo passport
          </Link>
        </div>
      </section>
      <ol className="journey">
        {JOURNEY.map((step, index) => (
          <li key={step.title}>
            <span>0{index + 1}</span>
            <h2>{step.title}</h2>
            <p>{step.body}</p>
          </li>
        ))}
      </ol>
      <section className="section-block">
        <h2>Four tracks</h2>
        <div className="track-grid">
          {TRACKS.map((track) => (
            <Link key={track.code} className={`card track-card track-${track.code}`} href={`/missions?track=${track.code}`}>
              <h3>{track.label}</h3>
              <p>{track.summary}</p>
            </Link>
          ))}
        </div>
      </section>
      <section className="demo-note">
        <h2>The demo is already in motion</h2>
        <p>
          Alex Chen has finished AI101 and submitted evidence for Port Community Demand Forecast. Jordan Lam
          at Harbour Frontier Labs can certify it. Sam Wu looks after the module catalogue.
        </p>
        <Link className="button secondary" href="/login">
          Use a demo account
        </Link>
      </section>
    </Frame>
  );
}
