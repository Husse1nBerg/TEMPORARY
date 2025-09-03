'use client';

// This is a dynamic page for a single blog post.
export default function BlogPostPage({ params }: { params: { slug: string } }) {
  return (
    <div className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
          Blog Post Title for: {params.slug}
        </h1>
        <p className="text-gray-500 mb-8">Published on September 2, 2025 by Admin</p>
        <div className="prose lg:prose-xl">
          <p>This is the full content of the blog post. In a real application, you would fetch this content from a CMS or a database based on the slug.</p>
          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet.</p>
        </div>
      </div>
    </div>
  );
}