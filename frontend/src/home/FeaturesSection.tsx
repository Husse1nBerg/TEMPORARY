'use client';

import { motion } from 'framer-motion';
import { RefreshCw, BarChart3, Bell, Leaf, ShoppingCart, Zap } from 'lucide-react';

const features = [
    {
      icon: <RefreshCw className="w-6 h-6" />,
      title: "Real-Time Price Updates",
      description: "Get live updates from multiple stores across Egypt.",
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Price Trend Analysis",
      description: "Track historical price changes to identify the best times to buy.",
    },
    {
      icon: <ShoppingCart className="w-6 h-6" />,
      title: "Multi-Store Comparison",
      description: "Compare prices across Gourmet, Metro, Spinneys, and more.",
    }
];

export default function FeaturesSection() {
    return (
        <section id="features" className="py-20 bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">
                        Powerful Features for Smart Tracking
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Everything you need to monitor grocery prices efficiently.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-gray-50 p-8 rounded-2xl"
                        >
                            <div className="inline-flex p-3 rounded-lg bg-green-200 text-green-800 mb-4">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}