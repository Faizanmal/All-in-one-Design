"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/design-api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Palette, Loader2, Mail, Shield } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/lib/auth-context';

// Social login icons
const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

const GitHubIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
  </svg>
);

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<string | null>(null);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const router = useRouter();
  const { toast } = useToast();
  const { loginWithGoogle, loginWithGitHub, isAuthenticated } = useAuth();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleGoogleSignup = async () => {
    if (!agreedToTerms) {
      toast({
        title: 'Terms Required',
        description: 'Please agree to the Terms of Service and Privacy Policy',
        variant: 'destructive',
      });
      return;
    }
    try {
      setSocialLoading('google');
      await loginWithGoogle();
    } catch {
      toast({
        title: 'Signup Failed',
        description: 'Failed to connect with Google',
        variant: 'destructive',
      });
      setSocialLoading(null);
    }
  };

  const handleGitHubSignup = async () => {
    if (!agreedToTerms) {
      toast({
        title: 'Terms Required',
        description: 'Please agree to the Terms of Service and Privacy Policy',
        variant: 'destructive',
      });
      return;
    }
    try {
      setSocialLoading('github');
      await loginWithGitHub();
    } catch {
      toast({
        title: 'Signup Failed',
        description: 'Failed to connect with GitHub',
        variant: 'destructive',
      });
      setSocialLoading(null);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !email || !password || !confirmPassword) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all fields',
        variant: 'destructive',
      });
      return;
    }

    if (!agreedToTerms) {
      toast({
        title: 'Terms Required',
        description: 'Please agree to the Terms of Service and Privacy Policy',
        variant: 'destructive',
      });
      return;
    }

    if (password !== confirmPassword) {
      toast({
        title: 'Validation Error',
        description: 'Passwords do not match',
        variant: 'destructive',
      });
      return;
    }

    // Password strength validation
    const passwordChecks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    if (!passwordChecks.length) {
      toast({
        title: 'Weak Password',
        description: 'Password must be at least 8 characters',
        variant: 'destructive',
      });
      return;
    }

    if (!passwordChecks.uppercase || !passwordChecks.lowercase) {
      toast({
        title: 'Weak Password',
        description: 'Password must contain both uppercase and lowercase letters',
        variant: 'destructive',
      });
      return;
    }

    if (!passwordChecks.number) {
      toast({
        title: 'Weak Password',
        description: 'Password must contain at least one number',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      const response = await authAPI.register(username, email, password);
      
      // Store token in localStorage
      localStorage.setItem('auth_token', response.token);
      
      toast({
        title: 'Success',
        description: 'Account created successfully',
      });

      router.push('/dashboard');
    } catch (error) {
      const err = error as { response?: { data?: { error?: string; detail?: string } } };
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || 'Failed to create account';
      
      toast({
        title: 'Signup Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 bg-linear-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Palette className="h-6 w-6 text-white" />
          </div>
          <CardTitle className="text-2xl">Create Account</CardTitle>
          <CardDescription>
            Join AI Design Tool and start creating
          </CardDescription>
        </CardHeader>

        {/* Social Signup Buttons */}
        <CardContent className="space-y-3">
          <Button
            type="button"
            variant="outline"
            className="w-full flex items-center justify-center gap-3 h-11"
            onClick={handleGoogleSignup}
            disabled={loading || socialLoading !== null}
          >
            {socialLoading === 'google' ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <GoogleIcon />
            )}
            <span>Sign up with Google</span>
          </Button>

          <Button
            type="button"
            variant="outline"
            className="w-full flex items-center justify-center gap-3 h-11"
            onClick={handleGitHubSignup}
            disabled={loading || socialLoading !== null}
          >
            {socialLoading === 'github' ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <GitHubIcon />
            )}
            <span>Sign up with GitHub</span>
          </Button>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-4 text-gray-500">Or sign up with email</span>
            </div>
          </div>
        </CardContent>

        <form onSubmit={handleSignup}>
          <CardContent className="space-y-4 pt-0">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading || socialLoading !== null}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading || socialLoading !== null}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading || socialLoading !== null}
              />
              {/* Password strength indicator */}
              {password && (
                <div className="mt-2 space-y-1">
                  <div className="flex gap-1">
                    {[
                      password.length >= 8,
                      /[A-Z]/.test(password),
                      /[a-z]/.test(password),
                      /\d/.test(password),
                      /[!@#$%^&*(),.?":{}|<>]/.test(password),
                    ].map((check, i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full transition-colors ${
                          check ? 'bg-green-500' : 'bg-gray-200'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-gray-500">
                    Use 8+ characters with uppercase, lowercase, numbers, and symbols
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading || socialLoading !== null}
              />
              {confirmPassword && password !== confirmPassword && (
                <p className="text-xs text-red-500">Passwords do not match</p>
              )}
            </div>

            {/* Terms and Privacy Agreement */}
            <div className="flex items-start gap-2 mt-4">
              <input
                type="checkbox"
                id="terms"
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                disabled={loading || socialLoading !== null}
              />
              <label htmlFor="terms" className="text-sm text-gray-600">
                I agree to the{' '}
                <Link href="/terms" className="text-blue-600 hover:underline">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/privacy" className="text-blue-600 hover:underline">
                  Privacy Policy
                </Link>
              </label>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading || socialLoading !== null || !agreedToTerms}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  <Mail className="mr-2 h-4 w-4" />
                  Create Account
                </>
              )}
            </Button>

            <div className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-600 hover:underline font-medium">
                Sign in
              </Link>
            </div>

            {/* Security Notice */}
            <div className="flex items-center justify-center gap-2 text-xs text-gray-400 mt-4">
              <Shield className="h-4 w-4" />
              <span>Your data is protected with enterprise-grade encryption</span>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

export const dynamic = 'force-dynamic';
