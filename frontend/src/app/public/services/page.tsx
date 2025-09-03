'use client';

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Check } from 'lucide-react';

const services = [
  {
    title: "Real-Time Price Tracking",
    description: "Our core service. Get live price data from over 10 major Egyptian grocery stores, updated automatically.",
    features: ["Automated Scraping", "Multi-Store Comparison", "Stock Availability Alerts"]
  },
  {
    title: "Market Trend Analysis",
    description: "Leverage historical data and AI to understand market dynamics and predict future price movements.",
    features: ["Historical Price Charts", "AI-Powered Insights", "Seasonal Trend Reports"]
  },
  {
    title: "API Access",
    description: "Integrate our powerful pricing data directly into your own systems and applications.",
    features: ["RESTful API", "WebSocket for Live Data", "Comprehensive Documentation"]
  }
];

export default function ServicesPage() {
  return (
    <div className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
          Our Services
        </h1>
        <p className="mt-4 text-xl text-gray-600">
          Comprehensive solutions to keep you ahead of the market.
        </p>
      </div>

      <div className="mt-16 max-w-5xl mx-auto grid gap-8 md:grid-cols-1 lg:grid-cols-3">
        {services.map((service) => (
          <Card key={service.title}>
            <CardHeader>
              <CardTitle>{service.title}</CardTitle>
              <CardDescription>{service.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {service.features.map((feature) => (
                  <li key={feature} className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}