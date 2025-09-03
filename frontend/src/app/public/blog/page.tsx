'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

// Dummy data for blog posts
const posts = [
  {
    slug: 'q3-market-report',
    title: 'Q3 2025 Agricultural Market Report for Egypt',
    description: 'A deep dive into the price trends of key vegetables and fruits in the third quarter.',
    date: 'September 1, 2025',
  },
  {
    slug: 'optimizing-procurement',
    title: 'How to Optimize Procurement with Real-Time Data',
    description: 'Learn how timely data can help you reduce costs and improve your supply chain efficiency.',
    date: 'August 15, 2025',
  }
];

export default function BlogPage() {
  return (
    <div className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
          Our Blog
        </h1>
        <p className="mt-4 text-xl text-gray-600">
          Insights and analysis on the Egyptian agricultural market.
        </p>
      </div>
      <div className="mt-12 max-w-3xl mx-auto grid gap-8">
        {posts.map((post) => (
          <Card key={post.slug}>
            <CardHeader>
              <CardTitle>{post.title}</CardTitle>
              <CardDescription>{post.date}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="mb-4">{post.description}</p>
              <Link href={`/blog/${post.slug}`}>
                <Button variant="link">Read More &rarr;</Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}