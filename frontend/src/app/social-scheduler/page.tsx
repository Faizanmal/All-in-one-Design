"use client";

import React from 'react';
import { SocialSchedulerPanel } from '@/components/features/social-scheduler/SocialSchedulerPanel';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';

export default function SocialSchedulerPage() {
    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <DashboardSidebar />

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-screen overflow-hidden">
                <MainHeader />

                <main className="flex-1 overflow-auto">
                    <div className="p-6 h-full">
                        <div className="mb-6 flex justify-between items-center">
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900">Social Media Scheduler</h1>
                                <p className="text-gray-500 mt-1">Connect your accounts and auto-publish your AI-generated designs.</p>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                            <SocialSchedulerPanel />
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
