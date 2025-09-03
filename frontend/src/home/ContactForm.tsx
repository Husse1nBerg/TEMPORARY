'use client';

import { motion } from 'framer-motion';
import { Globe, Clock, Users } from 'lucide-react';

export default function ContactForm() {
    return (
        <section id="contact" className="py-20 bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="max-w-5xl mx-auto">
                    <div className="grid lg:grid-cols-2 gap-12">
                        {/* Contact Info */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <h2 className="text-4xl font-bold text-gray-900 mb-6">
                                Get in Touch
                            </h2>
                            <p className="text-xl text-gray-600 mb-8">
                                Contact SPC for inquiries about the CROPS Price Tracker.
                            </p>
                            <div className="space-y-6">
                                <div className="flex items-start space-x-4">
                                    <div className="p-3 bg-green-100 rounded-lg">
                                        <Globe className="w-6 h-6 text-green-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">Address</h3>
                                        <p className="text-gray-600">
                                            12, El-fardous St., El-mohandseen, Giza, Egypt
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-start space-x-4">
                                    <div className="p-3 bg-green-100 rounded-lg">
                                        <Users className="w-6 h-6 text-green-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">Contact</h3>
                                        <p className="text-gray-600">
                                            info@spcagri.com<br />
                                            +201000931333
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        {/* Form */}
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            className="bg-gray-50 rounded-2xl p-8"
                        >
                            <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                                Send us a Message
                            </h3>
                            <form action="#" method="POST" className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                                    <input type="text" className="w-full px-4 py-3 rounded-lg border border-gray-200" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                                    <input type="email" className="w-full px-4 py-3 rounded-lg border border-gray-200" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                                    <textarea rows={4} className="w-full px-4 py-3 rounded-lg border border-gray-200 resize-none" />
                                </div>
                                <button
                                    type="submit"
                                    className="w-full py-4 bg-green-600 text-white rounded-lg font-semibold"
                                >
                                    Send Message
                                </button>
                            </form>
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    );
}