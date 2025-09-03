'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function ContactPage() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Thank you for your message!');
  };

  return (
    <div className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
          Contact Us
        </h1>
        <p className="mt-4 text-xl text-gray-600">
          We’d love to hear from you. Reach out with any questions or inquiries.
        </p>
      </div>

      <div className="mt-12 max-w-lg mx-auto">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-y-6">
          <div>
            <Label htmlFor="full-name">Full Name</Label>
            <Input type="text" id="full-name" name="full-name" required />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input type="email" id="email" name="email" required />
          </div>
          <div>
            <Label htmlFor="message">Message</Label>
            <textarea
              id="message"
              name="message"
              rows={4}
              required
              className="block w-full shadow-sm py-3 px-4 placeholder-gray-500 focus:ring-green-500 focus:border-green-500 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <Button type="submit" className="w-full">
              Send Message
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}