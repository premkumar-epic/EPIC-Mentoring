// Fix: Import React to resolve namespace errors for React types.
import React from 'react';

export enum Role {
  STUDENT = 'STUDENT',
  MENTOR = 'MENTOR',
  ADMIN = 'ADMIN',
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatar: string;
}

export interface Student extends User {
  major: string;
  weaknesses: string[];
  strengths: string[];
  assignedMentorId: string | null;
  performanceData: Mark[];
  careerAssessmentStatus: 'NOT_STARTED' | 'IN_PROGRESS' | 'PENDING_VERIFICATION' | 'COMPLETED';
  careerReport: string | null;
}

export interface Mentor extends User {
  expertise: string[];
  menteeIds: string[];
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  bio: string;
}

export interface Admin extends User {}

export interface Mark {
  subject: string;
  score: number;
  date: string; // YYYY-MM-DD
}

export interface Feedback {
    id: string;
    mentorId: string;
    studentId: string; // Will be anonymized in views
    rating: number; // 1-5
    comment: string;
    date: string;
}

export interface SessionRequest {
    id: string;
    studentId: string;
    mentorId: string;
    topic: string;
    status: 'PENDING' | 'APPROVED' | 'COMPLETED' | 'REJECTED';
    date: string;
}

export interface SessionReport {
    id: string;
    sessionId: string;
    mentorId: string;
    studentId: string;
    notes: string;
    actionItems: string;
    date: string;
}

export interface IssueReport {
    id: string;
    studentId: string;
    description: string;
    status: 'OPEN' | 'RESOLVED';
    date: string;
}

export interface ActivityLogEntry {
  id: string;
  user: {
    id: string;
    name: string;
    role: Role;
  };
  action: string;
  timestamp: string; // ISO 8601 format
}

export interface NavLink {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  component: React.ComponentType<any>; // Allow components to accept props
}

export type QuestionType = 'TEXT' | 'MCQ' | 'SCALE';

export interface CareerQuestion {
    id: string;
    type: QuestionType;
    text: string;
    options?: string[];
    labels?: { [key: number]: string };
}

export type AllUsers = Student | Mentor | Admin;