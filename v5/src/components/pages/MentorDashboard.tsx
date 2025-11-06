import React, { useState, useMemo } from "react";
import {
  User,
  Mentor as MentorType,
  Student as StudentType,
  NavLink,
  SessionRequest,
  IssueReport,
} from "../../types";
import Layout from "../Layout";
import {
  HomeIcon,
  UsersIcon,
  UploadCloudIcon,
  MessageSquareIcon,
  CheckSquareIcon,
  CheckIcon,
  XIcon,
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
} from "../UI";
import {
  USERS,
  MOCK_STUDENTS,
  MOCK_SESSION_REQUESTS,
  MOCK_ISSUE_REPORTS,
} from "../../constants";
import { getSessionPrepTips } from "../../services/geminiService";
import {
  FunnelChart,
  Funnel,
  Tooltip,
  LabelList,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

const Welcome: React.FC<{
  mentor: MentorType;
  onNavigate: (component: React.ComponentType) => void;
  menteesComponent: React.ComponentType;
}> = ({ mentor, onNavigate, menteesComponent }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <Card className="md:col-span-2">
      <CardContent className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
        <img
          src={mentor.avatar}
          alt={mentor.name}
          className="w-24 h-24 rounded-full border-4 border-primary-500"
        />
        <div>
          <h2 className="text-2xl font-bold">Welcome, {mentor.name}!</h2>
          <p className="text-gray-600 dark:text-gray-400">
            You have {mentor.menteeIds.length} assigned mentee(s).
          </p>
          <p className="text-sm mt-2 text-gray-500 dark:text-gray-300">
            Your expertise:{" "}
            <span className="font-semibold text-primary-600 dark:text-primary-400">
              {mentor.expertise.join(", ")}
            </span>
            .
          </p>
        </div>
      </CardContent>
    </Card>
    <Card onClick={() => onNavigate(menteesComponent)}>
      <CardContent>
        <UsersIcon className="w-8 h-8 text-primary-500 mb-2" />
        <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
          Total Mentees
        </h4>
        <p className="text-3xl font-bold">{mentor.menteeIds.length}</p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          Click to view all mentees
        </p>
      </CardContent>
    </Card>
    <Card className="md:col-span-3">
      <CardHeader>
        <CardTitle>My Profile</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm font-semibold">
          Contact:{" "}
          <a
            href={`mailto:${mentor.email}`}
            className="text-primary-600 hover:underline"
          >
            {mentor.email}
          </a>
        </p>
        <p className="text-sm mt-2">
          <span className="font-semibold">Bio:</span> {mentor.bio}
        </p>
      </CardContent>
    </Card>
  </div>
);

const MyMentees: React.FC<{ mentor: MentorType }> = ({ mentor }) => {
  const [selectedStudent, setSelectedStudent] = useState<StudentType | null>(
    null
  );
  const [prepTips, setPrepTips] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isReportModalOpen, setReportModalOpen] = useState(false);
  const [issueReports, setIssueReports] =
    useState<IssueReport[]>(MOCK_ISSUE_REPORTS);

  const mentees = useMemo(
    () => MOCK_STUDENTS.filter((s) => mentor.menteeIds.includes(s.id)),
    [mentor.menteeIds]
  );

  const handleResolveIssue = (issueId: string) => {
    setIssueReports((prev) =>
      prev.map((issue) =>
        issue.id === issueId ? { ...issue, status: "RESOLVED" } : issue
      )
    );
  };

  const handleGetPrepTips = async (student: StudentType) => {
    setIsLoading(true);
    setPrepTips(null);
    try {
      const tips = await getSessionPrepTips(student);
      setPrepTips(tips);
    } catch (error) {
      setPrepTips("Failed to generate preparation tips.");
    } finally {
      setIsLoading(false);
    }
  };

  if (selectedStudent) {
    const studentIssues = issueReports.filter(
      (ir) => ir.studentId === selectedStudent.id
    );
    return (
      <>
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Profile: {selectedStudent.name}</CardTitle>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSelectedStudent(null);
                    setPrepTips(null);
                  }}
                >
                  Back to Mentees
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p>
                    <strong>Major:</strong> {selectedStudent.major}
                  </p>
                  <p>
                    <strong>Strengths:</strong>{" "}
                    {selectedStudent.strengths.join(", ")}
                  </p>
                  <p>
                    <strong>Weaknesses:</strong>{" "}
                    {selectedStudent.weaknesses.join(", ")}
                  </p>
                  <div className="flex space-x-2 mt-4">
                    <Button
                      onClick={() => handleGetPrepTips(selectedStudent)}
                      disabled={isLoading}
                    >
                      {isLoading ? "Generating..." : "Get AI Session Prep Tips"}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => setReportModalOpen(true)}
                    >
                      Log Session Report
                    </Button>
                  </div>
                </div>
                <div>
                  {isLoading && <Spinner />}
                  {prepTips && (
                    <div className="bg-primary-50 dark:bg-primary-900/30 p-4 rounded-lg">
                      <h4 className="font-bold mb-2 text-primary-800 dark:text-primary-300">
                        AI Preparation Tips
                      </h4>
                      <div
                        className="prose prose-sm dark:prose-invert max-w-none"
                        dangerouslySetInnerHTML={{
                          __html: prepTips.replace(/\n/g, "<br />"),
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>
              {selectedStudent.careerAssessmentStatus ===
                "PENDING_VERIFICATION" && (
                <div className="mt-6 p-4 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg">
                  <h4 className="font-bold text-yellow-800 dark:text-yellow-300">
                    Action Required: Verify Career Report
                  </h4>
                  <p className="text-sm text-yellow-700 dark:text-yellow-200">
                    {selectedStudent.name} has completed a career assessment.
                    Please review the AI-generated report before it is released.
                  </p>
                  <Button size="sm" className="mt-2">
                    Review Report
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Student Issue Reports</CardTitle>
            </CardHeader>
            <CardContent>
              {studentIssues.length > 0 ? (
                <div className="space-y-4">
                  {studentIssues.map((issue) => (
                    <div
                      key={issue.id}
                      className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg flex justify-between items-start"
                    >
                      <div>
                        <p className="text-sm font-semibold">
                          {issue.description}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Reported: {new Date(issue.date).toLocaleDateString()}
                        </p>
                      </div>
                      {issue.status === "OPEN" ? (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleResolveIssue(issue.id)}
                        >
                          <CheckIcon className="w-4 h-4 mr-2" /> Mark as
                          Resolved
                        </Button>
                      ) : (
                        <span className="text-sm font-semibold text-green-600 dark:text-green-400 flex items-center">
                          <CheckSquareIcon className="w-4 h-4 mr-2" /> Resolved
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400">
                  No issues reported by this student.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
        <Modal
          isOpen={isReportModalOpen}
          onClose={() => setReportModalOpen(false)}
          title={`Log Session with ${selectedStudent.name}`}
        >
          <div className="space-y-4">
            <Textarea
              placeholder="Summary of the session, key discussion points, and student progress."
              rows={5}
            />
            <Textarea
              placeholder="Action items for the student to complete before the next session."
              rows={3}
            />
            <Button
              className="w-full"
              onClick={() => setReportModalOpen(false)}
            >
              Save Report
            </Button>
          </div>
        </Modal>
      </>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {mentees.map((student) => (
        <Card key={student.id} onClick={() => setSelectedStudent(student)}>
          <CardContent className="text-center">
            <img
              src={student.avatar}
              alt={student.name}
              className="w-20 h-20 rounded-full mx-auto mb-4"
            />
            <h3 className="font-bold text-lg">{student.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {student.major}
            </p>
            <p className="text-xs text-primary-600 dark:text-primary-400 mt-2">
              View Profile
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

const MarksUploadSystem: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
      setUploadStatus("");
    }
  };

  const handleUpload = () => {
    if (file) {
      setUploadStatus(`Uploading ${file.name}...`);
      // Simulate upload
      setTimeout(() => {
        setUploadStatus(
          `Successfully uploaded ${file.name}. Student profiles will be updated.`
        );
        setFile(null);
      }, 2000);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Marks Upload System</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
          <UploadCloudIcon className="w-12 h-12 text-gray-400" />
          <label htmlFor="file-upload" className="mt-4 cursor-pointer">
            <span className="text-primary-600 font-semibold">
              {file ? file.name : "Click to upload a CSV or Excel file"}
            </span>
          </label>
          <input
            id="file-upload"
            name="file-upload"
            type="file"
            className="sr-only"
            onChange={handleFileChange}
            accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
          />
          <p className="text-xs text-gray-500 mt-1">
            CSV, XLS, or XLSX up to 10MB
          </p>
        </div>
        {file && (
          <Button onClick={handleUpload} className="mt-4 w-full">
            Upload File
          </Button>
        )}
        {uploadStatus && (
          <p className="mt-4 text-sm text-center">{uploadStatus}</p>
        )}
      </CardContent>
    </Card>
  );
};

const SessionManagement: React.FC<{ mentor: MentorType }> = ({ mentor }) => {
  const [requests, setRequests] = useState<SessionRequest[]>(
    MOCK_SESSION_REQUESTS.filter((r) => r.mentorId === mentor.id)
  );

  const handleRequest = (
    requestId: string,
    status: "APPROVED" | "REJECTED"
  ) => {
    setRequests(
      requests.map((r) => (r.id === requestId ? { ...r, status } : r))
    );
  };

  const pendingRequests = requests.filter((r) => r.status === "PENDING");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Session Requests</CardTitle>
      </CardHeader>
      <CardContent>
        {pendingRequests.length > 0 ? (
          <div className="space-y-4">
            {pendingRequests.map((req) => {
              const student = USERS[req.studentId] as StudentType;
              return (
                <div
                  key={req.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                >
                  <div>
                    <p className="font-semibold">{student.name}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Topic: {req.topic}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      onClick={() => handleRequest(req.id, "APPROVED")}
                      className="!p-2"
                    >
                      <CheckIcon className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => handleRequest(req.id, "REJECTED")}
                      className="!p-2"
                    >
                      <XIcon className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-center text-gray-500 dark:text-gray-400">
            No pending session requests.
          </p>
        )}
      </CardContent>
    </Card>
  );
};

const MentorDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const mentor = useMemo(() => USERS[user.id] as MentorType, [user.id]);

  const navLinks: NavLink[] = useMemo(
    () => [
      { name: "Dashboard", icon: HomeIcon, component: Welcome },
      { name: "My Mentees", icon: UsersIcon, component: MyMentees },
      {
        name: "Session Requests",
        icon: MessageSquareIcon,
        component: SessionManagement,
      },
      {
        name: "Upload Marks",
        icon: UploadCloudIcon,
        component: MarksUploadSystem,
      },
    ],
    []
  );

  const [ActiveComponent, setActiveComponent] = useState<
    React.ComponentType<any>
  >(() => navLinks[0].component);

  const handleNavClick = (component: React.ComponentType) => {
    setActiveComponent(() => component);
  };

  const CurrentComponent = ActiveComponent;

  return (
    <Layout
      user={user}
      navLinks={navLinks}
      activeComponent={ActiveComponent}
      onNavClick={handleNavClick}
      onLogout={onLogout}
    >
      <CurrentComponent
        mentor={mentor}
        onNavigate={handleNavClick}
        menteesComponent={MyMentees}
      />
    </Layout>
  );
};

export default MentorDashboard;
