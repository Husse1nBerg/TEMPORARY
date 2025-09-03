'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Check } from 'lucide-react';

const pricingPlans = [
    {
      name: "Starter",
      price: "599",
      period: "month",
      features: ["Track up to 50 products", "3 store integrations", "Daily price updates"],
      popular: false
    },
    {
      name: "Professional",
      price: "1,499",
      period: "month",
      features: ["Track up to 200 products", "All store integrations", "Real-time updates", "Price alerts", "API access"],
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      features: ["Unlimited products", "Custom integrations", "Dedicated support"],
      popular: false
    }
];

export default function PricingSection() {
    return (
        <section id="pricing" className="py-20 bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">
                        Simple, Transparent Pricing
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Choose the perfect plan for your business needs.
                    </p>
                </motion.div>

                <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
                    {pricingPlans.map((plan, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className={`relative border rounded-2xl p-8 ${plan.popular ? 'border-green-500 border-2' : 'border-gray-200'}`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-green-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                                    Most Popular
                                </div>
                            )}
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                            <div className="flex items-baseline mb-6">
                                <span className="text-4xl font-bold text-gray-900">
                                    {plan.price === "Custom" ? "" : "EGP "}
                                    {plan.price}
                                </span>
                                {plan.period && (
                                    <span className="text-gray-600 ml-2">/{plan.period}</span>
                                )}
                            </div>
                            <ul className="space-y-3 mb-8">
                                {plan.features.map((feature, fIndex) => (
                                    <li key={fIndex} className="flex items-start">
                                        <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                                        <span className="text-gray-700">{feature}</span>
                                    </li>
                                ))}
                            </ul>
                            <Link href="/auth/register">
                                <button className={`w-full py-3 rounded-lg font-semibold transition-all ${plan.popular ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
                                    {plan.price === "Custom" ? "Contact Sales" : "Start Free Trial"}
                                </button>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}