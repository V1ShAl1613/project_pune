"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import type { Resolver } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button, Checkbox, Input } from "@/components/ui/controls";
import { Card } from "@/components/ui/surfaces";
import { login, register, forgotPassword, resetPassword } from "@/services/api/auth-api";
import { sessionStore } from "@/store/session-store";
import { setSessionCookie } from "@/utils/session-cookie";

const loginSchema = z.object({ identifier: z.string().min(1), password: z.string().min(8), remember: z.boolean() });
const registerSchema = z.object({ email: z.string().email(), username: z.string().min(3), displayName: z.string().min(3), password: z.string().min(12), phoneNumber: z.string().optional() });
const forgotSchema = z.object({ email: z.string().email() });
const resetSchema = z.object({ token: z.string().min(1), newPassword: z.string().min(12) });

export function LoginForm(): React.JSX.Element {
  const [error, setError] = useState<string | null>(null);
  const setSession = sessionStore((state) => state.setSession);
  const router = useRouter();
  type LoginFormValues = z.input<typeof loginSchema>;
  const form = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) as Resolver<LoginFormValues>, defaultValues: { identifier: "", password: "", remember: true } });

  return <Card className="w-full max-w-md"><form className="space-y-4" onSubmit={form.handleSubmit(async (values) => { try { const response = await login({ identifier: values.identifier, password: values.password }); setSession(response.user, { accessToken: response.tokens.accessToken, refreshToken: response.tokens.refreshToken, tokenType: response.tokens.tokenType, accessExpiresIn: response.tokens.accessExpiresIn, refreshExpiresIn: response.tokens.refreshExpiresIn }); setSessionCookie(); router.push("/dashboard"); } catch (error_) { setError(error_ instanceof Error ? error_.message : "Unable to sign in"); } })}><div><h1 className="text-2xl font-semibold text-text">Sign in</h1><p className="mt-1 text-sm text-muted">Access the enterprise control plane.</p></div><div className="space-y-2"><label className="text-sm font-medium">Email or username</label><Input {...form.register("identifier")} autoComplete="username" /></div><div className="space-y-2"><label className="text-sm font-medium">Password</label><Input type="password" {...form.register("password")} autoComplete="current-password" /></div><label className="flex items-center gap-2 text-sm text-muted"><Checkbox {...form.register("remember")} /> Remember this device</label>{error ? <div className="rounded-xl bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}<Button className="w-full" type="submit">Sign in</Button></form></Card>;
}

export function RegisterForm(): React.JSX.Element {
  const form = useForm<z.infer<typeof registerSchema>>({ resolver: zodResolver(registerSchema) });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  return <Card className="w-full max-w-md"><form className="space-y-4" onSubmit={form.handleSubmit(async (values) => { try { setError(null); setMessage(null); const response = await register(values); setMessage(response.message); } catch (error_: any) { setError(error_?.response?.data?.message || error_?.message || "Registration failed"); } })}><h1 className="text-2xl font-semibold text-text">Create account</h1><Input placeholder="Email" {...form.register("email")} /><Input placeholder="Username" {...form.register("username")} /><Input placeholder="Display name" {...form.register("displayName")} /><Input placeholder="Phone number" {...form.register("phoneNumber")} /><Input placeholder="Password" type="password" {...form.register("password")} />{message ? <div className="rounded-xl bg-success/10 p-3 text-sm text-success">{message}</div> : null}{error ? <div className="rounded-xl bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}<Button className="w-full" type="submit">Create account</Button></form></Card>;
}

export function ForgotPasswordForm(): React.JSX.Element {
  const form = useForm<z.infer<typeof forgotSchema>>({ resolver: zodResolver(forgotSchema) });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  return <Card className="w-full max-w-md"><form className="space-y-4" onSubmit={form.handleSubmit(async (values) => { try { setError(null); setMessage(null); const response = await forgotPassword(values); setMessage(response.message); } catch (error_: any) { setError(error_?.response?.data?.message || error_?.message || "Failed to send reset link"); } })}><h1 className="text-2xl font-semibold text-text">Forgot password</h1><Input placeholder="Email" {...form.register("email")} />{message ? <div className="rounded-xl bg-success/10 p-3 text-sm text-success">{message}</div> : null}{error ? <div className="rounded-xl bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}<Button className="w-full" type="submit">Send reset link</Button></form></Card>;
}

export function ResetPasswordForm(): React.JSX.Element {
  const form = useForm<z.infer<typeof resetSchema>>({ resolver: zodResolver(resetSchema) });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  return <Card className="w-full max-w-md"><form className="space-y-4" onSubmit={form.handleSubmit(async (values) => { try { setError(null); setMessage(null); const response = await resetPassword(values); setMessage(response.message); } catch (error_: any) { setError(error_?.response?.data?.message || error_?.message || "Failed to reset password"); } })}><h1 className="text-2xl font-semibold text-text">Reset password</h1><Input placeholder="Reset token" {...form.register("token")} /><Input placeholder="New password" type="password" {...form.register("newPassword")} />{message ? <div className="rounded-xl bg-success/10 p-3 text-sm text-success">{message}</div> : null}{error ? <div className="rounded-xl bg-danger/10 p-3 text-sm text-danger">{error}</div> : null}<Button className="w-full" type="submit">Update password</Button></form></Card>;
}
