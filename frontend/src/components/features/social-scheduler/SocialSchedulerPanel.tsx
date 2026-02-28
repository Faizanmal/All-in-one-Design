import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Calendar as CalendarIcon,
    Clock,
    Share2,
    Twitter,
    Facebook,
    Linkedin,
    Instagram,
    Image as ImageIcon,
    CheckCircle2,
    AlertCircle
} from 'lucide-react';
import { format } from 'date-fns';
import { socialSchedulerAPI } from '@/lib/social-scheduler-api';
import { useToast } from '@/hooks/use-toast';

interface SocialPlatform {
    id: string;
    name: string;
    icon: React.ReactNode;
    connected: boolean;
    color: string;
}

const PLATFORMS: SocialPlatform[] = [
    { id: 'twitter', name: 'Twitter / X', icon: <Twitter className="h-5 w-5" />, connected: true, color: 'text-blue-400' },
    { id: 'linkedin', name: 'LinkedIn', icon: <Linkedin className="h-5 w-5" />, connected: true, color: 'text-blue-700' },
    { id: 'facebook', name: 'Facebook', icon: <Facebook className="h-5 w-5" />, connected: false, color: 'text-blue-600' },
    { id: 'instagram', name: 'Instagram', icon: <Instagram className="h-5 w-5" />, connected: false, color: 'text-pink-600' },
];

interface SocialAccount {
    id: string;
    platform: string;
    username: string;
    avatar?: string;
    connected: boolean;
}

export function SocialSchedulerPanel() {
    const { toast } = useToast();
    const [dbAccounts, setDbAccounts] = useState<SocialAccount[]>([]);
    const [isLoadingAccounts, setIsLoadingAccounts] = useState(true);

    useEffect(() => {
        const fetchAccounts = async () => {
            try {
                // Fetch connected accounts from the backend API
                const data = await socialSchedulerAPI.getAccounts();
                setDbAccounts(data);
            } catch (error) {
                console.error("Failed to load accounts:", error);
                // Fallback for visual demo purposes if backend isn't running yet
                setDbAccounts([
                    { id: 1, platform: 'twitter', connected: true },
                    { id: 2, platform: 'linkedin', connected: true }
                ]);
            } finally {
                setIsLoadingAccounts(false);
            }
        };
        fetchAccounts();
    }, []);
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['twitter', 'linkedin']);
    const [postContent, setPostContent] = useState('');
    const [scheduleDate, setScheduleDate] = useState<string>('');
    const [scheduleTime, setScheduleTime] = useState<string>('');
    const [isScheduling, setIsScheduling] = useState(false);

    const togglePlatform = (id: string) => {
        setSelectedPlatforms(prev =>
            prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
        );
    };

    const handleSchedule = async () => {
        setIsScheduling(true);
        try {
            // Combine date and time
            const datetimeStr = `${scheduleDate}T${scheduleTime}:00`;
            const dateObj = new Date(datetimeStr);
            const isoString = dateObj.toISOString();

            // Find matching db account IDs
            const accountIds = dbAccounts
                .filter(a => selectedPlatforms.includes(a.platform))
                .map(a => a.id.toString());

            await socialSchedulerAPI.schedulePost(
                postContent,
                isoString,
                accountIds,
                "https://example.com/mock-image.png" // Mock media url
            );

            toast({
                title: "Post Scheduled Successfully!",
                description: `Scheduled for ${format(dateObj, 'PPpp')}`,
            });
            setPostContent('');
            setScheduleDate('');
            setScheduleTime('');
            setSelectedPlatforms([]);
        } catch (error) {
            toast({
                title: "Scheduling Failed",
                description: "There was an error scheduling the post.",
                variant: "destructive"
            });
            console.error(error);
        } finally {
            setIsScheduling(false);
        }
    };

    return (
        <div className="flex h-[calc(100vh-8rem)]">
            {/* Compose Section */}
            <div className="w-1/2 p-6 border-r border-gray-200 overflow-y-auto">
                <h2 className="text-2xl font-bold mb-6">Create Post</h2>

                <div className="space-y-6">
                    {/* Platform Selection */}
                    <div>
                        <Label className="text-sm font-medium mb-3 block">1. Select Platforms</Label>
                        <div className="grid grid-cols-2 gap-3">
                            {isLoadingAccounts ? (
                                <>
                                    <Skeleton className="h-14 w-full rounded-xl" />
                                    <Skeleton className="h-14 w-full rounded-xl" />
                                    <Skeleton className="h-14 w-full rounded-xl" />
                                    <Skeleton className="h-14 w-full rounded-xl" />
                                </>
                            ) : PLATFORMS.map((platform) => {
                                const isDbConnected = dbAccounts.some(acc => acc.platform === platform.id);
                                return (
                                    <button
                                        key={platform.id}
                                        onClick={() => isDbConnected && togglePlatform(platform.id)}
                                        disabled={!isDbConnected}
                                        className={`flex items-center gap-3 p-3 rounded-xl border-2 transition-all ${!isDbConnected
                                            ? 'opacity-50 cursor-not-allowed border-gray-100 bg-gray-50'
                                            : selectedPlatforms.includes(platform.id)
                                                ? 'border-blue-500 bg-blue-50/50'
                                                : 'border-gray-200 hover:border-blue-200'
                                            }`}
                                    >
                                        <div className={isDbConnected ? platform.color : 'text-gray-400'}>
                                            {platform.icon}
                                        </div>
                                        <span className="font-medium text-sm text-gray-700">{platform.name}</span>
                                        {!isDbConnected && (
                                            <span className="ml-auto text-[10px] uppercase font-bold text-gray-400 tracking-wider">Connect</span>
                                        )}
                                        {selectedPlatforms.includes(platform.id) && (
                                            <CheckCircle2 className="ml-auto h-4 w-4 text-blue-500" />
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Media Attachment */}
                    <div>
                        <Label className="text-sm font-medium mb-3 block">2. Attach Design</Label>
                        <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center hover:bg-gray-50 transition-colors cursor-pointer">
                            <div className="bg-blue-100 text-blue-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                                <ImageIcon className="h-6 w-6" />
                            </div>
                            <p className="font-medium text-gray-900">Select from current project</p>
                            <p className="text-sm text-gray-500 mt-1">Or drag and drop a new image</p>
                        </div>
                    </div>

                    {/* Caption */}
                    <div>
                        <Label className="text-sm font-medium mb-3 flex justify-between">
                            <span>3. Write Caption</span>
                            <span className={`text-xs ${postContent.length > (selectedPlatforms.includes('twitter') ? 280 : 2200) ? 'text-red-500' : 'text-gray-400'}`}>
                                {postContent.length}/{selectedPlatforms.includes('twitter') ? 280 : 2200}
                                {selectedPlatforms.includes('twitter') && <span className="ml-1 opacity-50">(Twitter Limit)</span>}
                            </span>
                        </Label>
                        <Textarea
                            placeholder="What do you want to share with your audience?"
                            className="resize-none h-32"
                            value={postContent}
                            onChange={(e) => setPostContent(e.target.value)}
                        />
                        <div className="flex gap-2 mt-2">
                            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded cursor-pointer hover:bg-purple-200">#Design</span>
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded cursor-pointer hover:bg-blue-200">✨ AI Generate</span>
                        </div>
                    </div>

                    {/* Date & Time */}
                    <div>
                        <Label className="text-sm font-medium mb-3 block">4. Schedule For</Label>
                        <div className="flex gap-4">
                            <div className="flex-1">
                                <div className="relative">
                                    <CalendarIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
                                    <Input
                                        type="date"
                                        className="pl-9"
                                        value={scheduleDate}
                                        onChange={(e) => setScheduleDate(e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="flex-1">
                                <div className="relative">
                                    <Clock className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
                                    <Input
                                        type="time"
                                        className="pl-9"
                                        value={scheduleTime}
                                        onChange={(e) => setScheduleTime(e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <Button
                        className="w-full h-12 text-lg"
                        disabled={selectedPlatforms.length === 0 || !postContent || !scheduleDate || !scheduleTime || isScheduling}
                        onClick={handleSchedule}
                    >
                        {isScheduling ? (
                            <span className="flex items-center gap-2">Generating Schedule...</span>
                        ) : (
                            <span className="flex items-center gap-2"><Share2 className="h-5 w-5" /> Schedule Post</span>
                        )}
                    </Button>
                </div>
            </div>

            {/* Preview Section */}
            <div className="w-1/2 bg-gray-50 p-6 flex flex-col">
                <h2 className="text-2xl font-bold mb-6 text-gray-900">Post Preview</h2>

                {selectedPlatforms.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
                        <Share2 className="h-16 w-16 mb-4 opacity-20" />
                        <p>Select a platform to preview your post</p>
                    </div>
                ) : (
                    <ScrollArea className="flex-1 pr-4">
                        <div className="space-y-6 relative pb-10">
                            {selectedPlatforms.map(platformId => {
                                const platform = PLATFORMS.find(p => p.id === platformId)!;
                                return (
                                    <Card key={platformId} className="border-0 shadow-md">
                                        <CardHeader className="flex flex-row items-center gap-3 pb-3 border-b border-gray-100">
                                            <div className={`p-2 rounded-lg bg-gray-50 ${platform.color}`}>
                                                {platform.icon}
                                            </div>
                                            <div>
                                                <CardTitle className="text-base">{platform.name} Preview</CardTitle>
                                                <CardDescription>
                                                    {scheduleDate ? `Scheduled for ${scheduleDate} at ${scheduleTime}` : 'Post preview'}
                                                </CardDescription>
                                            </div>
                                        </CardHeader>
                                        <CardContent className="pt-4">
                                            <div className="flex gap-3 mb-3">
                                                <div className="w-10 h-10 bg-gray-200 rounded-full flex-shrink-0"></div>
                                                <div>
                                                    <p className="font-bold text-sm text-gray-900">Your Company</p>
                                                    <p className="text-xs text-gray-500">@yourhandle</p>
                                                </div>
                                            </div>
                                            <p className="text-sm whitespace-pre-wrap mb-4 font-normal text-gray-800">
                                                {postContent || 'Your caption will appear here... Start typing to see the magic happen! ✨'}
                                            </p>

                                            {/* Image Preview Placeholder */}
                                            <div className="aspect-video bg-gray-100 rounded-lg flex flex-col items-center justify-center text-gray-400 border border-gray-200">
                                                <ImageIcon className="h-8 w-8 mb-2 opacity-50" />
                                                <span className="text-xs font-medium">Design Attachment Preview</span>
                                            </div>
                                        </CardContent>
                                    </Card>
                                );
                            })}
                        </div>
                    </ScrollArea>
                )}
            </div>
        </div>
    );
}
