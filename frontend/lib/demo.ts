/** Demo sign-in. The password is also documented in the repository README. */
export const DEMO_PASSWORD = "demo-ftos-2026";

export const DEMO_ACCOUNTS = [
  {
    role: "Learner",
    email: "learner@demo.ftos",
    detail: "Alex Chen has finished AI101 and has a forecast submission waiting for review.",
  },
  {
    role: "Employer",
    email: "employer@demo.ftos",
    detail: "Jordan Lam at Harbour Frontier Labs can publish missions and certify submissions.",
  },
  {
    role: "Admin",
    email: "admin@demo.ftos",
    detail: "Sam Wu can add, edit, and remove skill modules.",
  },
] as const;
