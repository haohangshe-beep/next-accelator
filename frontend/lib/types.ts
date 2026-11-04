export type Role = "learner" | "employer" | "admin";

export type Organization = {
  id: number;
  name: string;
  summary: string;
};

export type User = {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  slug: string;
  headline: string;
  bio: string;
  interests: string[];
  organization: Organization | null;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type ModuleSummary = {
  code: string;
  title: string;
  track: string;
  level: string;
  summary: string;
  estimated_hours: number;
  prerequisites: string[];
  completed: boolean;
  completed_at: string | null;
};

export type ModuleDetail = ModuleSummary & {
  learning_outcomes: string[];
  checklist: string[];
  missing_prerequisites: string[];
};

export type CompletionResult = {
  code: string;
  title: string;
  completed_at: string;
  already_completed: boolean;
  passport_slug: string;
};

export type Certification = {
  id: number;
  mission_id: number;
  mission_title: string;
  organization_name: string;
  issuer_name: string;
  competency_tags: string[];
  statement: string;
  issued_at: string;
};

export type Submission = {
  id: number;
  mission_id: number;
  mission_title: string;
  mission_track: string;
  organization_name: string;
  status: string;
  deliverable_url: string;
  notes: string;
  feedback: string;
  learner_name: string;
  learner_slug: string;
  created_at: string;
  updated_at: string;
  can_review: boolean;
  suggested_competencies: string[];
  certification: Certification | null;
};

export type MissionSummary = {
  id: number;
  title: string;
  organization_name: string;
  track: string;
  difficulty: string;
  summary: string;
  required_skill_codes: string[];
  deadline: string | null;
  status: string;
  membership_status: string | null;
};

export type MissionDetail = MissionSummary & {
  problem_statement: string;
  deliverables: string;
  suggested_competencies: string[];
  missing_skill_codes: string[];
  my_submission: Submission | null;
  submissions: Submission[];
};

export type ReviewResult = {
  submission: Submission;
  certification: Certification | null;
};

export type Passport = {
  profile: {
    full_name: string;
    slug: string;
    headline: string;
    bio: string;
    interests: string[];
  };
  modules: Array<{
    code: string;
    title: string;
    track: string;
    level: string;
    estimated_hours: number;
    completed_at: string;
  }>;
  missions: Array<{
    id: number;
    title: string;
    track: string;
    organization_name: string;
    status: string;
    deliverable_url: string | null;
    joined_at: string;
  }>;
  certifications: Certification[];
};

export type Recommendation = {
  id: string;
  kind: "module" | "mission" | "passport" | "submission";
  title: string;
  reason: string;
  action_label: string;
  href: string;
};

export type NavigatorResponse = {
  summary: string;
  recommendations: Recommendation[];
};

export type Dashboard = {
  user: User;
  learner: {
    completed_modules: number;
    missions_joined: number;
    certifications: number;
    passport_slug: string;
    submissions: Array<{
      id: number;
      mission_id: number;
      mission_title: string;
      status: string;
      updated_at: string;
    }>;
  } | null;
  employer: {
    organization_name: string;
    missions: Array<{
      id: number;
      title: string;
      track: string;
      status: string;
      submission_count: number;
      pending_count: number;
    }>;
    pending_reviews: Array<{
      id: number;
      mission_id: number;
      mission_title: string;
      learner_name: string;
      learner_slug: string;
      submitted_at: string;
    }>;
  } | null;
  admin: {
    module_count: number;
    mission_count: number;
    user_count: number;
    waitlist_count: number;
  } | null;
};

export type WaitlistResult = {
  recorded: boolean;
  already_registered: boolean;
};
