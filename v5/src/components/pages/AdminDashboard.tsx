import React, { useState, useMemo } from 'react';
import { User, Admin as AdminType, NavLink, Mentor, Student, AllUsers, Role, ActivityLogEntry } from '../../types';
import Layout from '../Layout';
import { HomeIcon, BarChartIcon, CheckSquareIcon, MessageSquareIcon, UsersIcon, ClipboardListIcon } from '../Icons';
import { Card, CardContent, CardHeader, CardTitle, Button, Spinner, Select, Modal, ChartSkeleton } from '../UI';
import { MOCK_STUDENTS, MOCK_MENTORS, MOCK_FEEDBACK, MOCK_ACTIVITY_LOG } from '../../constants';
import { analyzeFeedbackForAdmin } from '../../services/geminiService';

import { FunnelChart, Funnel, Tooltip, LabelList, ResponsiveContainer, Cell } from "recharts";


interface DashboardProps {
  user: User;
  onLogout: () => void;
}

// Recharts components from global scope
declare const Recharts: any;

const Welcome: React.FC<{ onNavigate: (view: string) => void }> = ({ onNavigate }) => {
    const totalStudents = MOCK_STUDENTS.length;
    const approvedMentors = MOCK_MENTORS.filter(m => m.status === 'APPROVED').length;
    const pendingMentors = MOCK_MENTORS.filter(m => m.status === 'PENDING').length;

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card onClick={() => onNavigate('user_management')}>
                <CardContent>
                    <UsersIcon className="w-8 h-8 text-primary-500 mb-2"/>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Users</h4>
                    <p className="text-3xl font-bold">{totalStudents + approvedMentors}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Click to manage students & mentors</p>
                </CardContent>
            </Card>
            <Card onClick={() => onNavigate('mentor_approval')}>
                <CardContent>
                    <CheckSquareIcon className="w-8 h-8 text-yellow-500 mb-2"/>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Pending Applications</h4>
                    <p className="text-3xl font-bold">{pendingMentors}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Click to review</p>
                </CardContent>
            </Card>
             <Card onClick={() => onNavigate('analytics')}>
                <CardContent>
                    <BarChartIcon className="w-8 h-8 text-green-500 mb-2"/>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">System Analytics</h4>
                    <p className="text-3xl font-bold">View Charts</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Click to view performance</p>
                </CardContent>
            </Card>
        </div>
    );
};

const SystemAnalytics: React.FC = () => {
    if (typeof Recharts === 'undefined') {
        return (
            <Card>
                <CardHeader><CardTitle>Mentor Performance</CardTitle></CardHeader>
                <CardContent className="h-96">
                    <ChartSkeleton />
                </CardContent>
            </Card>
        );
    }
    const { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } = Recharts;

    const mentorPerformanceData = MOCK_MENTORS
        .filter(m => m.status === 'APPROVED')
        .map(m => {
            const feedback = MOCK_FEEDBACK.filter(f => f.mentorId === m.id);
            const avgRating = feedback.length > 0 ? feedback.reduce((acc, f) => acc + f.rating, 0) / feedback.length : 0;
            return {
                name: m.name.split(' ').slice(0,2).join(' '),
                'Average Rating': parseFloat(avgRating.toFixed(2)),
                mentees: m.menteeIds.length
            };
        });

    return (
        <Card>
            <CardHeader><CardTitle>Mentor Performance</CardTitle></CardHeader>
            <CardContent className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={mentorPerformanceData}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                        <XAxis dataKey="name" className="text-xs" />
                        <YAxis domain={[0, 5]} className="text-xs" />
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '0.5rem' }} />
                        <Legend />
                        <Bar dataKey="Average Rating" fill="#3b82f6" />
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
};

const MentorApproval: React.FC = () => {
    const [mentors, setMentors] = useState<Mentor[]>(MOCK_MENTORS);

    const handleApproval = (mentorId: string, status: 'APPROVED' | 'REJECTED') => {
        setMentors(mentors.map(m => m.id === mentorId ? { ...m, status } : m));
    };

    const pendingMentors = mentors.filter(m => m.status === 'PENDING');

    return (
        <Card>
            <CardHeader><CardTitle>Mentor Approval System</CardTitle></CardHeader>
            <CardContent>
                {pendingMentors.length > 0 ? (
                    <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th scope="col" className="px-6 py-3">Name</th>
                                <th scope="col" className="px-6 py-3 hidden md:table-cell">Expertise</th>
                                <th scope="col" className="px-6 py-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pendingMentors.map(mentor => (
                                <tr key={mentor.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                                    <td className="px-6 py-4 font-medium whitespace-nowrap">{mentor.name}</td>
                                    <td className="px-6 py-4 hidden md:table-cell">{mentor.expertise.join(', ')}</td>
                                    <td className="px-6 py-4 flex space-x-2">
                                        <Button size="sm" onClick={() => handleApproval(mentor.id, 'APPROVED')}>Approve</Button>
                                        <Button size="sm" variant="danger" onClick={() => handleApproval(mentor.id, 'REJECTED')}>Reject</Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    </div>
                ) : (
                    <p className="text-center text-gray-500 dark:text-gray-400">No pending mentor applications.</p>
                )}
            </CardContent>
        </Card>
    );
};

const FeedbackDashboard: React.FC = () => {
    const [report, setReport] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedMentorId, setSelectedMentorId] = useState<string>('all');

    const approvedMentors = MOCK_MENTORS.filter(m => m.status === 'APPROVED');

    const handleAnalyze = async () => {
        setIsLoading(true);
        setReport(null);
        let feedbackToAnalyze = MOCK_FEEDBACK;
        let mentorName: string | undefined = undefined;

        if (selectedMentorId !== 'all') {
            feedbackToAnalyze = MOCK_FEEDBACK.filter(f => f.mentorId === selectedMentorId);
            mentorName = approvedMentors.find(m => m.id === selectedMentorId)?.name;
        }

        const result = await analyzeFeedbackForAdmin(feedbackToAnalyze, mentorName);
        setReport(result);
        setIsLoading(false);
    };

    const { filteredFeedback, averageRating } = useMemo(() => {
        if (selectedMentorId === 'all') {
            return { filteredFeedback: MOCK_FEEDBACK, averageRating: null };
        }
        const feedback = MOCK_FEEDBACK.filter(f => f.mentorId === selectedMentorId);
        const avg = feedback.length > 0
            ? (feedback.reduce((acc, f) => acc + f.rating, 0) / feedback.length).toFixed(2)
            : null;
        return { filteredFeedback: feedback, averageRating: avg };
    }, [selectedMentorId]);


    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
                <Card>
                     <CardHeader>
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                            <CardTitle>Feedback Analysis Report</CardTitle>
                            <div className="flex items-center gap-2 w-full md:w-auto">
                                <Select value={selectedMentorId} onChange={e => setSelectedMentorId(e.target.value)} className="w-full md:w-48">
                                    <option value="all">All Mentors</option>
                                    {approvedMentors.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                                </Select>
                                <Button onClick={handleAnalyze} disabled={isLoading}>{isLoading ? "Analyzing..." : "Analyze"}</Button>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {averageRating && (
                            <div className="mb-4 p-3 bg-primary-50 dark:bg-primary-900/30 rounded-lg">
                                <span className="font-semibold text-primary-800 dark:text-primary-300">Average Rating: </span>
                                <span className="text-xl font-bold text-primary-600 dark:text-primary-400">{averageRating}</span>
                                <span className="text-yellow-500"> / 5.00</span>
                            </div>
                        )}
                        {isLoading && <Spinner />}
                        {report ? (
                            <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: report.replace(/\n/g, '<br />') }} />
                        ) : (
                            <p className="text-gray-500 dark:text-gray-400">Select a mentor (or all) and click "Analyze" to generate an AI summary of their feedback.</p>
                        )}
                    </CardContent>
                </Card>
            </div>
            <div>
                 <Card>
                    <CardHeader><CardTitle>Recent Feedback</CardTitle></CardHeader>
                    <CardContent className="space-y-3 max-h-96 overflow-y-auto">
                        {filteredFeedback.length > 0 ? filteredFeedback.slice(0).reverse().map(fb => (
                            <div key={fb.id} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                                <div className="flex justify-between items-center">
                                    <span className="font-semibold text-sm">Mentor: {MOCK_MENTORS.find(m=>m.id === fb.mentorId)?.name}</span>
                                    <span className="text-xs font-bold text-yellow-500">{'★'.repeat(fb.rating)}{'☆'.repeat(5-fb.rating)}</span>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">"{fb.comment}"</p>
                            </div>
                        )) : <p className="text-center text-sm text-gray-500">No feedback for this mentor.</p>}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

const ActivityLog: React.FC = () => {
    return (
        <Card>
            <CardHeader><CardTitle>User Activity Log</CardTitle></CardHeader>
            <CardContent>
                 <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                            <tr>
                                <th scope="col" className="px-6 py-3">User</th>
                                <th scope="col" className="px-6 py-3">Action</th>
                                <th scope="col" className="px-6 py-3">Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {MOCK_ACTIVITY_LOG.map(log => (
                                <tr key={log.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                                    <td className="px-6 py-4 font-medium whitespace-nowrap">
                                        {log.user.name} ({log.user.role})
                                    </td>
                                    <td className="px-6 py-4">{log.action}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
}

const UserManagementPage: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'students' | 'mentors'>('students');
    const [mentors, setMentors] = useState<Mentor[]>(MOCK_MENTORS);
    const [students, setStudents] = useState<Student[]>(MOCK_STUDENTS);

    // Mentor filter/sort state
    const [expertiseFilter, setExpertiseFilter] = useState('all');
    const [sortKey, setSortKey] = useState('name');

    // Deletion state
    const [userToDelete, setUserToDelete] = useState<AllUsers | null>(null);

    const expertiseAreas = useMemo(() => {
        const allAreas = new Set(MOCK_MENTORS.flatMap(m => m.expertise));
        return ['all', ...Array.from(allAreas)];
    }, []);

    const filteredAndSortedMentors = useMemo(() => {
        return mentors
            .filter(m => expertiseFilter === 'all' || m.expertise.includes(expertiseFilter))
            .sort((a, b) => {
                if (sortKey === 'name') {
                    return a.name.localeCompare(b.name);
                }
                if (sortKey === 'mentees') {
                    return b.menteeIds.length - a.menteeIds.length;
                }
                return 0;
            });
    }, [mentors, expertiseFilter, sortKey]);

    const handleDeleteConfirm = () => {
        if (!userToDelete) return;
        if (userToDelete.role === Role.STUDENT) {
            setStudents(students.filter(s => s.id !== userToDelete.id));
        } else {
            setMentors(mentors.filter(m => m.id !== userToDelete.id));
        }
        setUserToDelete(null);
    }

    const renderUserTable = (users: AllUsers[], type: 'students' | 'mentors') => (
        <>
        {/* Desktop Table */}
        <div className="hidden md:block">
            <table className="w-full text-left">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                    <tr>
                        <th scope="col" className="px-6 py-3">Name</th>
                        <th scope="col" className="px-6 py-3">Email</th>
                        {type === 'mentors' && <th scope="col" className="px-6 py-3">Status</th>}
                        <th scope="col" className="px-6 py-3">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map(user => (
                        <tr key={user.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                            <td className="px-6 py-4 font-medium whitespace-nowrap flex items-center">
                                <img src={user.avatar} className="w-8 h-8 rounded-full mr-3" alt={user.name}/>
                                {user.name}
                            </td>
                            <td className="px-6 py-4">{user.email}</td>
                             {type === 'mentors' && (
                                <td className="px-6 py-4">
                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                        (user as Mentor).status === 'APPROVED' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                                        (user as Mentor).status === 'PENDING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' :
                                        'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                    }`}>{(user as Mentor).status}</span>
                                </td>
                            )}
                            <td className="px-6 py-4">
                                <Button size="sm" variant="danger" onClick={() => setUserToDelete(user)}>Delete</Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
        {/* Mobile Cards */}
        <div className="md:hidden space-y-4">
            {users.map(user => (
                <div key={user.id} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <div className="flex items-center justify-between">
                         <div className="flex items-center">
                            <img src={user.avatar} className="w-10 h-10 rounded-full mr-3" alt={user.name}/>
                            <div>
                                <p className="font-semibold">{user.name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
                            </div>
                        </div>
                        <Button size="sm" variant="danger" onClick={() => setUserToDelete(user)}>Delete</Button>
                    </div>
                </div>
            ))}
        </div>
        </>
    );

    return (
        <>
        <Card>
            <CardHeader>
                <CardTitle>User Management</CardTitle>
                <div className="border-b border-gray-200 dark:border-gray-700">
                    <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                        <button onClick={() => setActiveTab('students')} className={`${activeTab === 'students' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>
                            Students
                        </button>
                        <button onClick={() => setActiveTab('mentors')} className={`${activeTab === 'mentors' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>
                            Mentors
                        </button>
                    </nav>
                </div>
            </CardHeader>
            <CardContent>
                {activeTab === 'mentors' && (
                    <div className="flex flex-col md:flex-row gap-4 mb-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-1">Filter by Expertise</label>
                            <Select value={expertiseFilter} onChange={e => setExpertiseFilter(e.target.value)}>
                                {expertiseAreas.map(area => <option key={area} value={area} className="capitalize">{area}</option>)}
                            </Select>
                        </div>
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-1">Sort by</label>
                            <Select value={sortKey} onChange={e => setSortKey(e.target.value)}>
                                <option value="name">Name</option>
                                <option value="mentees">Number of Mentees</option>
                            </Select>
                        </div>
                    </div>
                )}
                {activeTab === 'students' ? renderUserTable(students, 'students') : renderUserTable(filteredAndSortedMentors, 'mentors')}
            </CardContent>
        </Card>
        <Modal isOpen={!!userToDelete} onClose={() => setUserToDelete(null)} title="Confirm Deletion">
             <p>Are you sure you want to delete <span className="font-semibold">{userToDelete?.name}</span>? This action cannot be undone.</p>
             <div className="flex justify-end space-x-2 mt-4">
                 <Button variant="secondary" onClick={() => setUserToDelete(null)}>Cancel</Button>
                 <Button variant="danger" onClick={handleDeleteConfirm}>Delete</Button>
             </div>
         </Modal>
        </>
    );
}


const AdminDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
    const [ActivePageComponent, setActivePageComponent] = useState<React.ComponentType<any>>(() => Welcome);

    const navLinks: NavLink[] = useMemo(() => [
        { name: 'Dashboard', icon: HomeIcon, component: Welcome },
        { name: 'User Management', icon: UsersIcon, component: UserManagementPage },
        { name: 'Mentor Approval', icon: CheckSquareIcon, component: MentorApproval },
        { name: 'Feedback', icon: MessageSquareIcon, component: FeedbackDashboard },
        { name: 'Analytics', icon: BarChartIcon, component: SystemAnalytics },
        { name: 'Activity Log', icon: ClipboardListIcon, component: ActivityLog },
    ], []);

    const handleNavigate = (viewName: string) => {
        const link = navLinks.find(l => l.name.toLowerCase().replace(/ /g, '_') === viewName);
        if (link) {
            setActivePageComponent(() => link.component);
        }
    };

    const activeComponentForLayout = navLinks.find(l => l.component === ActivePageComponent)?.component ?? Welcome;

    return (
        <Layout
            user={user}
            navLinks={navLinks}
            activeComponent={activeComponentForLayout}
            onNavClick={(component: React.ComponentType) => setActivePageComponent(() => component)}
            onLogout={onLogout}
        >
          <ActivePageComponent onNavigate={handleNavigate} />
        </Layout>
    );
};

export default AdminDashboard;
