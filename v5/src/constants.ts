import {
  Role,
  Student,
  Mentor,
  Admin,
  AllUsers,
  Feedback,
  SessionRequest,
  CareerQuestion,
  ActivityLogEntry,
  IssueReport,
} from "../src/types";

// More extensive student data
export const MOCK_STUDENTS: Student[] = [
  {
    id: "student-1",
    name: "Alex Johnson",
    email: "alex.j@university.edu",
    role: Role.STUDENT,
    major: "Computer Science",
    weaknesses: ["Advanced Algorithms", "Database Management"],
    strengths: ["Frontend Development", "UI/UX Design"],
    assignedMentorId: "mentor-1",
    avatar: "https://i.pravatar.cc/150?u=student-1",
    performanceData: [
      { subject: "Algorithms", score: 65, date: "2023-09-15" },
      { subject: "Databases", score: 72, date: "2023-09-20" },
      { subject: "Web Dev", score: 88, date: "2023-09-25" },
      { subject: "Algorithms", score: 75, date: "2023-10-15" },
      { subject: "Databases", score: 78, date: "2023-10-20" },
      { subject: "Web Dev", score: 92, date: "2023-10-25" },
    ],
    careerAssessmentStatus: "NOT_STARTED",
    careerReport: null,
  },
  {
    id: "student-2",
    name: "Maria Garcia",
    email: "maria.g@university.edu",
    role: Role.STUDENT,
    major: "Data Science",
    weaknesses: ["Machine Learning Theory"],
    strengths: ["Python Programming", "Data Visualization"],
    assignedMentorId: "mentor-2",
    avatar: "https://i.pravatar.cc/150?u=student-2",
    performanceData: [
      { subject: "Statistics", score: 85, date: "2023-09-15" },
      { subject: "ML Theory", score: 70, date: "2023-09-20" },
      { subject: "Python", score: 95, date: "2023-09-25" },
      { subject: "Statistics", score: 88, date: "2023-10-15" },
      { subject: "ML Theory", score: 78, date: "2023-10-20" },
      { subject: "Python", score: 97, date: "2023-10-25" },
    ],
    careerAssessmentStatus: "COMPLETED",
    careerReport: `
### Suggested Career Path: Data Scientist

**Strengths Alignment:**
Your high scores in Analytical Thinking and proficiency in Python and Data Visualization make you an excellent candidate for a career in data science. You have a natural aptitude for uncovering insights from complex datasets.

**Areas for Development:**
Your assessment indicates a need to strengthen your foundational knowledge in Machine Learning Theory. A deeper theoretical understanding will complement your practical skills.

**Recommended Actions:**
1.  **Advanced Coursework:** Enroll in a graduate-level course on Statistical Learning or Advanced Machine Learning.
2.  **Kaggle Competitions:** Participate in Kaggle competitions to apply your skills to real-world problems and learn from the community.
3.  **Contribute to Open Source:** Find a data science library on GitHub and contribute to its development. This will improve your coding skills and expose you to production-level code.
    `,
  },
  {
    id: "student-3",
    name: "Chen Wei",
    email: "chen.w@university.edu",
    role: Role.STUDENT,
    major: "Electrical Engineering",
    weaknesses: ["Signal Processing", "Circuit Design"],
    strengths: ["Physics", "Mathematics"],
    assignedMentorId: "mentor-1",
    avatar: "https://i.pravatar.cc/150?u=student-3",
    performanceData: [
      { subject: "Circuits", score: 70, date: "2023-09-15" },
      { subject: "Signals", score: 68, date: "2023-09-20" },
      { subject: "Physics", score: 90, date: "2023-09-25" },
      { subject: "Circuits", score: 75, date: "2023-10-15" },
      { subject: "Signals", score: 72, date: "2023-10-20" },
      { subject: "Physics", score: 94, date: "2023-10-25" },
    ],
    careerAssessmentStatus: "NOT_STARTED",
    careerReport: null,
  },
  {
    id: "student-4",
    name: "Fatima Al-Sayed",
    email: "fatima.a@university.edu",
    role: Role.STUDENT,
    major: "Cybersecurity",
    weaknesses: ["Cryptography"],
    strengths: ["Networking", "Ethical Hacking"],
    assignedMentorId: "mentor-3",
    avatar: "https://i.pravatar.cc/150?u=student-4",
    performanceData: [
      { subject: "Networking", score: 92, date: "2023-10-01" },
      { subject: "Cryptography", score: 75, date: "2023-10-08" },
      { subject: "Pen Testing", score: 88, date: "2023-10-15" },
    ],
    careerAssessmentStatus: "PENDING_VERIFICATION",
    careerReport: `AI analysis pending mentor review.`,
  },
  {
    id: "student-5",
    name: "Ben Carter",
    email: "ben.c@university.edu",
    role: Role.STUDENT,
    major: "Business Administration",
    weaknesses: ["Financial Accounting"],
    strengths: ["Marketing", "Public Speaking"],
    assignedMentorId: "mentor-4",
    avatar: "https://i.pravatar.cc/150?u=student-5",
    performanceData: [
      { subject: "Marketing", score: 95, date: "2023-10-05" },
      { subject: "Accounting", score: 72, date: "2023-10-12" },
      { subject: "Management", score: 85, date: "2023-10-19" },
    ],
    careerAssessmentStatus: "NOT_STARTED",
    careerReport: null,
  },
];

export const MOCK_MENTORS: Mentor[] = [
  {
    id: "mentor-1",
    name: "Dr. Evelyn Reed",
    email: "e.reed@faculty.edu",
    role: Role.MENTOR,
    expertise: ["Algorithms", "Data Structures", "System Design"],
    menteeIds: ["student-1", "student-3"],
    status: "APPROVED",
    avatar: "https://i.pravatar.cc/150?u=mentor-1",
    bio: "15+ years of experience in software engineering and a passion for demystifying complex algorithms. My goal is to build strong foundational knowledge in my mentees.",
  },
  {
    id: "mentor-2",
    name: "Prof. David Chen",
    email: "d.chen@faculty.edu",
    role: Role.MENTOR,
    expertise: ["Machine Learning", "AI Ethics", "Python"],
    menteeIds: ["student-2"],
    status: "APPROVED",
    avatar: "https://i.pravatar.cc/150?u=mentor-2",
    bio: "Researcher in the field of ethical AI. I help students navigate the technical and moral complexities of machine learning.",
  },
  {
    id: "mentor-3",
    name: "Dr. Sarah Banks",
    email: "s.banks@faculty.edu",
    role: Role.MENTOR,
    expertise: ["Cybersecurity", "Networking"],
    menteeIds: ["student-4"],
    status: "APPROVED",
    avatar: "https://i.pravatar.cc/150?u=mentor-3",
    bio: "Cybersecurity expert with a focus on ethical hacking and network defense. I enjoy preparing students for the fast-paced world of digital security.",
  },
  {
    id: "mentor-4",
    name: "Mr. Tom Powell",
    email: "t.powell@industry.com",
    role: Role.MENTOR,
    expertise: [
      "Software Engineering",
      "Agile Methodologies",
      "Business Strategy",
    ],
    menteeIds: ["student-5"],
    status: "APPROVED",
    avatar: "https://i.pravatar.cc/150?u=mentor-4",
    bio: "Industry veteran with experience in scaling tech startups. I mentor students on the intersection of technology and business.",
  },
  {
    id: "mentor-5",
    name: "Dr. Angela Merkel",
    email: "a.merkel@faculty.edu",
    role: Role.MENTOR,
    expertise: ["Quantum Computing", "Physics"],
    menteeIds: [],
    status: "PENDING",
    avatar: "https://i.pravatar.cc/150?u=mentor-5",
    bio: "Theoretical physicist exploring the boundaries of quantum computing. Looking to mentor students with a strong background in mathematics and physics.",
  },
  {
    id: "mentor-6",
    name: "Mr. John Smith",
    email: "j.smith@industry.com",
    role: Role.MENTOR,
    expertise: ["Product Management", "Marketing"],
    menteeIds: [],
    status: "REJECTED",
    avatar: "https://i.pravatar.cc/150?u=mentor-6",
    bio: "Product manager with a focus on user-centric design.",
  },
];

export const MOCK_ADMIN: Admin = {
  id: "admin-1",
  name: "Dean Thompson",
  email: "dean.t@university.edu",
  role: Role.ADMIN,
  avatar: "https://i.pravatar.cc/150?u=admin-1",
};

export const MOCK_FEEDBACK: Feedback[] = [
  {
    id: "f-1",
    mentorId: "mentor-1",
    studentId: "student-1",
    rating: 5,
    comment: "Dr. Reed is amazing! She explains complex topics so clearly.",
    date: "2023-10-28",
  },
  {
    id: "f-2",
    mentorId: "mentor-2",
    studentId: "student-2",
    rating: 4,
    comment:
      "Prof. Chen is very knowledgeable, but sometimes the sessions feel a bit rushed.",
    date: "2023-10-29",
  },
  {
    id: "f-3",
    mentorId: "mentor-1",
    studentId: "student-3",
    rating: 4,
    comment: "Great session, really helped me with my project planning.",
    date: "2023-11-01",
  },
  {
    id: "f-4",
    mentorId: "mentor-3",
    studentId: "student-4",
    rating: 5,
    comment:
      "Dr. Banks provided incredible insights into the cybersecurity industry.",
    date: "2023-11-02",
  },
  {
    id: "f-5",
    mentorId: "mentor-2",
    studentId: "student-2",
    rating: 5,
    comment:
      "Follow-up session was much better paced. Prof. Chen is a fantastic mentor!",
    date: "2023-11-05",
  },
  {
    id: "f-6",
    mentorId: "mentor-4",
    studentId: "student-5",
    rating: 4,
    comment: "Mr. Powell gave me great advice on my business plan.",
    date: "2023-11-06",
  },
  {
    id: "f-7",
    mentorId: "mentor-1",
    studentId: "student-1",
    rating: 5,
    comment: "Helped me debug a very tricky algorithm problem. Lifesaver!",
    date: "2023-11-10",
  },
];

export const MOCK_SESSION_REQUESTS: SessionRequest[] = [
  {
    id: "sr-1",
    studentId: "student-1",
    mentorId: "mentor-1",
    topic: "Help with my final year project",
    status: "PENDING",
    date: "2023-11-05",
  },
  {
    id: "sr-2",
    studentId: "student-2",
    mentorId: "mentor-2",
    topic: "Career advice and resume review",
    status: "APPROVED",
    date: "2023-11-03",
  },
  {
    id: "sr-3",
    studentId: "student-3",
    mentorId: "mentor-1",
    topic: "Confused about signal processing concepts",
    status: "PENDING",
    date: "2023-11-08",
  },
];

export const MOCK_ISSUE_REPORTS: IssueReport[] = [
  {
    id: "ir-1",
    studentId: "student-1",
    description:
      "The score for my 'Algorithms' test on 2023-10-15 is incorrect. It should be 78, not 75.",
    status: "OPEN",
    date: "2023-11-01",
  },
  {
    id: "ir-2",
    studentId: "student-3",
    description:
      "My 'Circuits' score from September is missing from the dashboard.",
    status: "OPEN",
    date: "2023-11-04",
  },
  {
    id: "ir-3",
    studentId: "student-2",
    description: "Typo in 'ML Theory' subject name.",
    status: "RESOLVED",
    date: "2023-10-30",
  },
];

export const MOCK_ACTIVITY_LOG: ActivityLogEntry[] = [
  {
    id: "log-1",
    user: { id: "admin-1", name: "Dean Thompson", role: Role.ADMIN },
    action: "Logged in",
    timestamp: "2023-11-12T10:00:00Z",
  },
  {
    id: "log-2",
    user: { id: "mentor-1", name: "Dr. Evelyn Reed", role: Role.MENTOR },
    action: "Logged in",
    timestamp: "2023-11-12T10:05:00Z",
  },
  {
    id: "log-3",
    user: { id: "student-1", name: "Alex Johnson", role: Role.STUDENT },
    action: "Requested a session with Dr. Evelyn Reed",
    timestamp: "2023-11-12T10:15:23Z",
  },
  {
    id: "log-4",
    user: { id: "admin-1", name: "Dean Thompson", role: Role.ADMIN },
    action: "Approved mentor application for Dr. Sarah Banks",
    timestamp: "2023-11-12T11:30:10Z",
  },
  {
    id: "log-5",
    user: { id: "mentor-2", name: "Prof. David Chen", role: Role.MENTOR },
    action: "Submitted a session report for Maria Garcia",
    timestamp: "2023-11-12T14:00:55Z",
  },
  {
    id: "log-6",
    user: { id: "student-2", name: "Maria Garcia", role: Role.STUDENT },
    action: "Submitted feedback for Prof. David Chen",
    timestamp: "2023-11-12T14:25:18Z",
  },
  {
    id: "log-7",
    user: { id: "admin-1", name: "Dean Thompson", role: Role.ADMIN },
    action: "Rejected mentor application for Mr. John Smith",
    timestamp: "2023-11-12T15:00:00Z",
  },
];

export const USERS: { [id: string]: AllUsers } = {
  ...MOCK_STUDENTS.reduce((acc, u) => ({ ...acc, [u.id]: u }), {}),
  ...MOCK_MENTORS.reduce((acc, u) => ({ ...acc, [u.id]: u }), {}),
  [MOCK_ADMIN.id]: MOCK_ADMIN,
};

export const CAREER_ASSESSMENT_QUESTIONS: CareerQuestion[] = [
  {
    id: "q1",
    type: "TEXT",
    text: "Describe a project or accomplishment, either in or out of school, that you are particularly proud of. What did you do, and what did you enjoy about it?",
  },
  {
    id: "q2",
    type: "MCQ",
    text: "Which of these work environments sounds most appealing to you?",
    options: [
      "A fast-paced, collaborative office with lots of team projects.",
      "A quiet, independent setting where I can focus deeply on my own tasks.",
      "A flexible, remote environment where I can manage my own schedule.",
      "A hands-on workshop or lab where I can build or experiment with things.",
    ],
  },
  {
    id: "q3",
    type: "TEXT",
    text: "What kind of problems do you enjoy solving? (e.g., puzzles, helping people with their issues, organizing complex systems, building things)",
  },
  {
    id: "q4",
    type: "SCALE",
    text: "On a scale of 1 to 5, how much do you enjoy leading a team or project?",
    labels: { 1: "Strongly Dislike", 5: "Strongly Enjoy" },
  },
  {
    id: "q5",
    type: "MCQ",
    text: "When learning something new, you prefer:",
    options: [
      "Reading books and theoretical articles.",
      "Watching tutorials and practical demonstrations.",
      "Jumping right in and learning by doing.",
      "Discussing concepts with others.",
    ],
  },
  {
    id: "q6",
    type: "TEXT",
    text: "What are three things you value most in a career? (e.g., financial security, creativity, helping others, work-life balance, leadership)",
  },
];
