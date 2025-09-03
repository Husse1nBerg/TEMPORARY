'use client';

import { Leaf, BarChart3, Users } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
          About CROPS Price Tracker
        </h1>
        <p className="mt-4 text-xl text-gray-600">
          Empowering agricultural businesses in Egypt with real-time data and actionable insights.
        </p>
      </div>

      <div className="mt-16 max-w-7xl mx-auto grid gap-12 lg:grid-cols-3">
        <div className="text-center p-8 border rounded-lg">
          <Leaf className="w-12 h-12 mx-auto text-green-600 mb-4" />
          <h2 className="text-2xl font-bold">Our Mission</h2>
          <p className="mt-2 text-gray-600">
            To bring transparency and efficiency to the agricultural supply chain by providing the most accurate and timely grocery price data in the market.
          </p>
        </div>
        <div className="text-center p-8 border rounded-lg">
          <BarChart3 className="w-12 h-12 mx-auto text-green-600 mb-4" />
          <h2 className="text-2xl font-bold">Our Vision</h2>
          <p className="mt-2 text-gray-600">
            To become the leading platform for agricultural market intelligence in the MENA region, driving data-driven decisions for businesses of all sizes.
          </p>
        </div>
        <div className="text-center p-8 border rounded-lg">
          <Users className="w-12 h-12 mx-auto text-green-600 mb-4" />
          <h2 className="text-2xl font-bold">Our Team</h2>
          <p className="mt-2 text-gray-600">
            We are a passionate team of developers, data scientists, and agricultural experts dedicated to solving real-world challenges with technology.
          </p>
        </div>
      </div>
    </div>
  );
}