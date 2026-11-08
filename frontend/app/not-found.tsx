import Link from "next/link";
import { Frame } from "@/components/site-header";

export default function NotFound() {
  return (
    <Frame>
      <h1>That page is not in FTOS.</h1>
      <p>The skills catalogue and the mission board are the two ways back in.</p>
      <div className="actions">
        <Link className="button" href="/skills">
          Browse skills
        </Link>
        <Link className="button secondary" href="/missions">
          Browse missions
        </Link>
      </div>
    </Frame>
  );
}
