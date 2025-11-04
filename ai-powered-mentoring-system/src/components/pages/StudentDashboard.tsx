import React, { useState, useMemo } from "react";
import {
  User,
  Student as StudentType,
  NavLink,
  CareerQuestion,
} from "../../types";
import Layout from "../Layout";
import {
  HomeIcon,
  BarChartIcon,
  BriefcaseIcon,
  BookOpenIcon,
  SendIcon,
  MessageSquareIcon,
  AlertCircleIcon,
} from "../Icons";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Spinner,
  Modal,
  Textarea,
  Alert,
  ChartSkeleton,
} from "../UI";
import {
  getAcademicAdvice,
  getCareerInsights,
} from "../../services/geminiService";
import {
  USERS,
  CAREER_ASSESSMENT_QUESTIONS,
  MOCK_MENTORS,
} from "../../constants";
import {
  FunnelChart,
  Funnel,
  Tooltip,
  LabelList,
  ResponsiveContainer,
  Cell,
} from "recharts";

// Recharts components from global scope
declare const Recharts: any;

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

const Welcome: React.FC<{
  student: StudentType;
  onActionClick: (action: string) => void;
}> = ({ student, onActionClick }) => {
  const mentor = USERS[student.assignedMentorId || ""];
  return (
    <Card>
      <CardContent className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
        <img
          src={student.avatar}
          alt={student.name}
          className="w-24 h-24 rounded-full border-4 border-primary-500"
        />
        <div className="flex-1">
          <h2 className="text-2xl font-bold">
            Welcome back, {student.name.split(" ")[0]}!
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Ready to excel in your studies today?
          </p>
          {mentor && (
            <p className="text-sm mt-2 text-gray-500 dark:text-gray-300">
              Your mentor is{" "}
              <span className="font-semibold text-primary-600 dark:text-primary-400">
                {mentor.name}
              </span>
              .
            </p>
          )}
        </div>
        <div className="flex flex-col space-y-2">
          <Button size="sm" onClick={() => onActionClick("requestSession")}>
            <MessageSquareIcon className="w-4 h-4 mr-2" /> Request Session
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onActionClick("giveFeedback")}
          >
            <MessageSquareIcon className="w-4 h-4 mr-2" /> Give Feedback
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const AIAdvisor: React.FC = () => {
  const [messages, setMessages] = useState<
    { text: string; sender: "user" | "ai" }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const newMessages = [
      ...messages,
      { text: input, sender: "user" as "user" },
    ];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const aiResponse = await getAcademicAdvice(input);
      setMessages([...newMessages, { text: aiResponse, sender: "ai" as "ai" }]);
    } catch (error) {
      setMessages([
        ...newMessages,
        { text: "An error occurred. Please try again.", sender: "ai" as "ai" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-[70vh]">
      <CardHeader>
        <CardTitle>AI Academic Advisor</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-lg p-3 rounded-lg prose prose-sm dark:prose-invert ${
                msg.sender === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-gray-200 dark:bg-gray-700"
              }`}
            >
              <div
                dangerouslySetInnerHTML={{
                  __html: msg.text
                    .replace(/\n/g, "<br />")
                    .replace(/---/g, "<hr />"),
                }}
              />
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <Spinner />
          </div>
        )}
      </CardContent>
      <div className="p-4 border-t dark:border-gray-700 flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSend()}
          placeholder="Ask for academic help..."
          className="flex-1 p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
          disabled={isLoading}
        />
        <Button onClick={handleSend} className="ml-2" disabled={isLoading}>
          <SendIcon className="w-5 h-5" />
        </Button>
      </div>
    </Card>
  );
};

const PerformanceDashboard: React.FC<{
  student: StudentType;
  onReportIssue: () => void;
}> = ({ student, onReportIssue }) => {
  // FIX: Recharts was not rendering because the data format was incorrect for multiple lines.
  // This transforms the data into the correct shape for the LineChart component.
  const chartData = useMemo(() => {
    const dataByDate: {
      [date: string]: { date: string; [subject: string]: any };
    } = {};
    student.performanceData.forEach((mark) => {
      if (!dataByDate[mark.date]) {
        dataByDate[mark.date] = { date: mark.date };
      }
      dataByDate[mark.date][mark.subject] = mark.score;
    });
    return Object.values(dataByDate).sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [student.performanceData]);

  const subjects = useMemo(
    () => Array.from(new Set(student.performanceData.map((d) => d.subject))),
    [student.performanceData]
  );
  const colors = useMemo(
    () => subjects.map((_, index) => `hsl(${(index * 137.5) % 360}, 70%, 50%)`),
    [subjects]
  );

  if (typeof Recharts === "undefined") {
    return (
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Performance Dashboard</CardTitle>
            <Button variant="secondary" size="sm" onClick={onReportIssue}>
              <AlertCircleIcon className="w-4 h-4 mr-2" /> Report an Issue
            </Button>
          </div>
        </CardHeader>
        <CardContent className="h-96">
          <ChartSkeleton />
        </CardContent>
      </Card>
    );
  }
  const {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
  } = Recharts;

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Performance Dashboard</CardTitle>
          <Button variant="secondary" size="sm" onClick={onReportIssue}>
            <AlertCircleIcon className="w-4 h-4 mr-2" /> Report an Issue
          </Button>
        </div>
      </CardHeader>
      <CardContent className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              className="stroke-gray-200 dark:stroke-gray-700"
            />
            <XAxis dataKey="date" className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1f2937",
                border: "none",
                borderRadius: "0.5rem",
              }}
            />
            <Legend />
            {subjects.map((subject, index) => (
              <Line
                key={subject}
                type="monotone"
                dataKey={subject}
                stroke={colors[index]}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

const CareerAssessment: React.FC<{ student: StudentType }> = ({ student }) => {
  const [answers, setAnswers] = useState<{ [key: string]: string }>({});
  const [studentState, setStudentState] = useState(student);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnswerChange = (id: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    const report = await getCareerInsights(
      answers,
      CAREER_ASSESSMENT_QUESTIONS
    );
    setTimeout(() => {
      setStudentState((prev) => ({
        ...prev,
        careerAssessmentStatus: "PENDING_VERIFICATION",
        careerReport: report,
      }));
      setIsLoading(false);
    }, 2000);
  };

  const renderQuestion = (q: CareerQuestion) => {
    switch (q.type) {
      case "TEXT":
        return (
          <Textarea
            id={q.id}
            value={answers[q.id] || ""}
            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
            rows={4}
            placeholder="Type your answer here..."
            required
          />
        );
      case "MCQ":
        return (
          <div className="space-y-2">
            {q.options?.map((option, index) => (
              <label
                key={index}
                className="flex items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 cursor-pointer"
              >
                <input
                  type="radio"
                  name={q.id}
                  value={index}
                  checked={answers[q.id] === String(index)}
                  onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                  className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                />
                <span className="ml-3 text-sm">{option}</span>
              </label>
            ))}
          </div>
        );
      case "SCALE":
        return (
          <div className="flex flex-col items-center">
            <input
              type="range"
              id={q.id}
              min="1"
              max="5"
              value={answers[q.id] || "3"}
              onChange={(e) => handleAnswerChange(q.id, e.target.value)}
              className="w-full"
            />
            <div className="flex justify-between w-full text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>{q.labels?.[1]}</span>
              <span>{q.labels?.[5]}</span>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="text-center p-8">
          <Spinner /> <p className="mt-4">Analyzing your responses...</p>
        </CardContent>
      </Card>
    );
  }

  if (studentState.careerAssessmentStatus === "PENDING_VERIFICATION") {
    return (
      <Card>
        <CardContent className="text-center p-8">
          <h3 className="font-bold text-lg">Analysis Complete</h3>
          <p>
            Your career report is being verified by your mentor. This may take
            up to 24 hours. You will be notified once it's available.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (
    studentState.careerAssessmentStatus === "COMPLETED" &&
    studentState.careerReport
  ) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your Career Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className="prose prose-sm dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{
              __html: studentState.careerReport.replace(/\n/g, "<br />"),
            }}
          />
          <Button
            onClick={() =>
              setStudentState((prev) => ({
                ...prev,
                careerAssessmentStatus: "NOT_STARTED",
              }))
            }
            className="mt-4"
            variant="secondary"
          >
            Retake Assessment
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Career Path Assessment</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <p>
          Answer the following questions thoughtfully. Your detailed responses
          will help the AI provide a personalized and accurate career path
          analysis.
        </p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <div className="space-y-6">
            {CAREER_ASSESSMENT_QUESTIONS.map((q) => (
              <div key={q.id}>
                <label className="block font-medium mb-2">{q.text}</label>
                {renderQuestion(q)}
              </div>
            ))}
            <Button
              type="submit"
              disabled={
                Object.keys(answers).length < CAREER_ASSESSMENT_QUESTIONS.length
              }
            >
              Generate My Career Report
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

const StudentDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const student = useMemo(() => USERS[user.id] as StudentType, [user.id]);
  const [isFeedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [isSessionModalOpen, setSessionModalOpen] = useState(false);
  const [isIssueModalOpen, setIssueModalOpen] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const navLinks: NavLink[] = useMemo(
    () => [
      { name: "Dashboard", icon: HomeIcon, component: Welcome },
      { name: "AI Advisor", icon: BookOpenIcon, component: AIAdvisor },
      {
        name: "Performance",
        icon: BarChartIcon,
        component: PerformanceDashboard,
      },
      { name: "Career Path", icon: BriefcaseIcon, component: CareerAssessment },
    ],
    []
  );

  const [ActiveComponent, setActiveComponent] = useState<
    React.ComponentType<any>
  >(() => navLinks[0].component);

  const handleActionClick = (action: string) => {
    if (action === "giveFeedback") setFeedbackModalOpen(true);
    if (action === "requestSession") setSessionModalOpen(true);
  };

  const showNotification = (message: string) => {
    setNotification(message);
    setTimeout(() => setNotification(null), 3000);
  };

  const mentor = useMemo(
    () => MOCK_MENTORS.find((m) => m.id === student.assignedMentorId),
    [student.assignedMentorId]
  );

  const CurrentComponent = ActiveComponent;

  return (
    <>
      <Layout
        user={user}
        navLinks={navLinks}
        activeComponent={ActiveComponent}
        onNavClick={(component: React.ComponentType) =>
          setActiveComponent(() => component)
        }
        onLogout={onLogout}
      >
        {notification && (
          <div className="mb-4">
            <Alert message={notification} type="success" />
          </div>
        )}
        <CurrentComponent
          student={student}
          onActionClick={handleActionClick}
          onReportIssue={() => setIssueModalOpen(true)}
        />
      </Layout>
      <Modal
        isOpen={isFeedbackModalOpen}
        onClose={() => setFeedbackModalOpen(false)}
        title="Give Anonymous Feedback"
      >
        <div className="space-y-4">
          <p>
            Your feedback for{" "}
            <span className="font-semibold">{mentor?.name}</span> is anonymous
            and helps us improve our mentoring program.
          </p>
          <div>
            <label>Rating (1-5)</label>
            <input
              type="range"
              min="1"
              max="5"
              defaultValue="4"
              className="w-full"
            />
          </div>
          <Textarea placeholder="Your comments..." rows={4} />
          <Button
            className="w-full"
            onClick={() => {
              setFeedbackModalOpen(false);
              showNotification("Thank you for your feedback!");
            }}
          >
            Submit Feedback
          </Button>
        </div>
      </Modal>
      <Modal
        isOpen={isSessionModalOpen}
        onClose={() => setSessionModalOpen(false)}
        title="Request a Session"
      >
        <div className="space-y-4">
          <Textarea
            placeholder="What would you like to discuss? (e.g., project help, career advice)"
            rows={4}
          />
          <Button
            className="w-full"
            onClick={() => {
              setSessionModalOpen(false);
              showNotification(
                "Your session request has been sent to your mentor."
              );
            }}
          >
            Send Request
          </Button>
        </div>
      </Modal>
      <Modal
        isOpen={isIssueModalOpen}
        onClose={() => setIssueModalOpen(false)}
        title="Report Issue with Marks"
      >
        <div className="space-y-4">
          <p>
            Please describe the issue with your marks. Your mentor will be
            notified.
          </p>
          <Textarea
            placeholder="e.g., The score for my 'Algorithms' test on 2023-10-15 is incorrect."
            rows={4}
          />
          <Button
            className="w-full"
            onClick={() => {
              setIssueModalOpen(false);
              showNotification("Your issue report has been submitted.");
            }}
          >
            Submit Report
          </Button>
        </div>
      </Modal>
    </>
  );
};

export default StudentDashboard;
