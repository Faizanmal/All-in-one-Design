'use client';

import { useState, useEffect, useCallback } from 'react';
import { notificationsApi, userPreferencesApi, webhooksApi, Notification, Webhook, UserPreference } from '@/lib/notifications-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Bell, 
  BellOff, 
  Webhook as WebhookIcon, 
  Settings, 
  Check, 
  X,
  Trash2,
  Plus
} from 'lucide-react';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [preferences, setPreferences] = useState<UserPreference | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [newWebhookName, setNewWebhookName] = useState('');
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const { toast } = useToast();

  // Load notifications
  const loadNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const response = await notificationsApi.list();
      setNotifications(response.data);
      
      const unreadResponse = await notificationsApi.unread();
      setUnreadCount(unreadResponse.data.count);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load notifications',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  // Load webhooks
  const loadWebhooks = useCallback(async () => {
    try {
      const response = await webhooksApi.list();
      setWebhooks(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load webhooks',
        variant: 'destructive',
      });
    }
  }, [toast]);

  // Load preferences
  const loadPreferences = useCallback(async () => {
    try {
      const response = await userPreferencesApi.get();
      setPreferences(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load preferences',
        variant: 'destructive',
      });
    }
  }, [toast]);

  useEffect(() => {
    loadNotifications();
    loadWebhooks();
    loadPreferences();
  }, [loadNotifications, loadWebhooks, loadPreferences]);

  // Mark notification as read
  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await notificationsApi.markRead(notificationId);
      loadNotifications();
      toast({
        title: 'Success',
        description: 'Notification marked as read',
      });
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to mark notification as read',
        variant: 'destructive',
      });
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    try {
      await notificationsApi.markAllRead();
      loadNotifications();
      toast({
        title: 'Success',
        description: 'All notifications marked as read',
      });
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to mark all notifications as read',
        variant: 'destructive',
      });
    }
  };

  // Clear all notifications
  const handleClearAll = async () => {
    try {
      await notificationsApi.clearAll();
      loadNotifications();
      toast({
        title: 'Success',
        description: 'All notifications cleared',
      });
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to clear notifications',
        variant: 'destructive',
      });
    }
  };

  // Delete notification
  const handleDeleteNotification = async (notificationId: number) => {
    try {
      await notificationsApi.delete(notificationId);
      loadNotifications();
      toast({
        title: 'Success',
        description: 'Notification deleted',
      });
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to delete notification',
        variant: 'destructive',
      });
    }
  };

  // Create webhook
  const handleCreateWebhook = async () => {
    if (!newWebhookName.trim() || !newWebhookUrl.trim()) return;
    
    try {
      await webhooksApi.create({
        name: newWebhookName,
        url: newWebhookUrl,
        events: ['*'], // Subscribe to all events
      });
      setNewWebhookName('');
      setNewWebhookUrl('');
      toast({
        title: 'Success',
        description: 'Webhook created successfully',
      });
      loadWebhooks();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to create webhook',
        variant: 'destructive',
      });
    }
  };

  // Test webhook
  const handleTestWebhook = async (webhookId: number) => {
    try {
      await webhooksApi.test(webhookId);
      toast({
        title: 'Success',
        description: 'Test webhook sent',
      });
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to send test webhook',
        variant: 'destructive',
      });
    }
  };

  // Delete webhook
  const handleDeleteWebhook = async (webhookId: number) => {
    try {
      await webhooksApi.delete(webhookId);
      toast({
        title: 'Success',
        description: 'Webhook deleted',
      });
      loadWebhooks();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to delete webhook',
        variant: 'destructive',
      });
    }
  };

  // Update preferences
  const handleUpdatePreferences = async (updates: Partial<UserPreference>) => {
    try {
      await userPreferencesApi.update(updates);
      toast({
        title: 'Success',
        description: 'Preferences updated',
      });
      loadPreferences();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to update preferences',
        variant: 'destructive',
      });
    }
  };

  // Get notification icon
  const getNotificationIcon = () => {
    return <Bell className="w-4 h-4" />;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Notifications</h1>
            <p className="text-muted-foreground">Manage your notifications and webhooks</p>
          </div>
          {unreadCount > 0 && (
            <Badge variant="destructive">{unreadCount} unread</Badge>
          )}
        </div>
      </div>

      <Tabs defaultValue="notifications" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="notifications">
            <Bell className="w-4 h-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="webhooks">
            <WebhookIcon className="w-4 h-4 mr-2" />
            Webhooks
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>All Notifications</CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={handleMarkAllAsRead}>
                    <Check className="w-4 h-4 mr-2" />
                    Mark All Read
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleClearAll}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear All
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading notifications...</p>
              ) : notifications.length === 0 ? (
                <div className="text-center py-8">
                  <BellOff className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
                  <p className="text-muted-foreground">No notifications</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {notifications.map((notification) => (
                    <Card key={notification.id} className={notification.read ? 'opacity-60' : ''}>
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between">
                          <div className="flex gap-3 flex-1">
                            {getNotificationIcon()}
                            <div className="flex-1">
                              <h3 className="font-semibold">{notification.title}</h3>
                              <p className="text-sm text-muted-foreground">{notification.message}</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                {new Date(notification.created_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {!notification.read && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleMarkAsRead(notification.id)}
                              >
                                <Check className="w-4 h-4" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteNotification(notification.id)}
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="webhooks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create Webhook</CardTitle>
              <CardDescription>Add a new webhook endpoint</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Webhook name"
                value={newWebhookName}
                onChange={(e) => setNewWebhookName(e.target.value)}
              />
              <Input
                placeholder="Webhook URL"
                value={newWebhookUrl}
                onChange={(e) => setNewWebhookUrl(e.target.value)}
              />
              <Button onClick={handleCreateWebhook}>
                <Plus className="w-4 h-4 mr-2" />
                Create Webhook
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Active Webhooks</CardTitle>
            </CardHeader>
            <CardContent>
              {webhooks.length === 0 ? (
                <p className="text-muted-foreground">No webhooks configured</p>
              ) : (
                <div className="space-y-2">
                  {webhooks.map((webhook) => (
                    <Card key={webhook.id}>
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-semibold">{webhook.name}</h3>
                            <p className="text-sm text-muted-foreground">{webhook.url}</p>
                            <div className="flex gap-2 mt-2">
                              <Badge variant={webhook.is_active ? 'default' : 'secondary'}>
                                {webhook.is_active ? 'Active' : 'Inactive'}
                              </Badge>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleTestWebhook(webhook.id)}
                            >
                              Test
                            </Button>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteWebhook(webhook.id)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Configure how you receive notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {preferences && (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">Email Notifications</p>
                      <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                    </div>
                    <Switch
                      checked={preferences.email_notifications}
                      onCheckedChange={(checked) => 
                        handleUpdatePreferences({ email_notifications: checked })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">Push Notifications</p>
                      <p className="text-sm text-muted-foreground">Receive browser push notifications</p>
                    </div>
                    <Switch
                      checked={preferences.push_notifications}
                      onCheckedChange={(checked) => 
                        handleUpdatePreferences({ push_notifications: checked })
                      }
                    />
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
