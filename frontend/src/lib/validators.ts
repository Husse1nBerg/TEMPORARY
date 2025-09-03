import { z } from 'zod';

// Validator for the login form
export const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address.'),
  password: z.string().min(6, 'Password must be at least 6 characters.'),
});

// Validator for the registration form
export const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address.'),
  username: z.string().min(3, 'Username must be at least 3 characters.'),
  fullName: z.string().min(3, 'Full name is required.'),
  password: z.string().min(6, 'Password must be at least 6 characters.'),
});

// Type definitions inferred from schemas
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;