'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Leaf, 
  TrendingUp, 
  ShoppingCart, 
  BarChart3, 
  RefreshCw, 
  Bell,
  Check,
  ArrowRight,
  Menu,
  X,
  ChevronDown,
  Globe,
  Zap,
  Shield,
  Users,
  Clock,
  DollarSign
} from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activeTestimonial, setActiveTestimonial] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      icon: <RefreshCw className="w-6 h-6" />,
      title: "Real-Time Price Updates",
      description: "Get live updates on grocery prices from multiple stores across Egypt",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Price Trend Analysis",
      description: "Track historical price changes and identify the best times to buy",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: <Bell className="w-6 h-6" />,
      title: "Stock Alerts",
      description: "Get notified when products are back in stock or prices drop",
      color: "from-orange-500 to-red-500"
    },
    {
      icon: <Leaf className="w-6 h-6" />,
      title: "Organic Tracking",
      description: "Easily identify and compare organic vs regular produce prices",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: <ShoppingCart className="w-6 h-6" />,
      title: "Multi-Store Comparison",
      description: "Compare prices across Gourmet, Metro, Spinneys, and more",
      color: "from-indigo-500 to-purple-500"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Automated Scraping",
      description: "Daily automated data collection ensures always fresh information",
      color: "from-yellow-500 to-orange-500"
    }
  ];

  const testimonials = [
    {
      name: "Ahmed Hassan",
      role: "Agricultural Supply Manager",
      content: "CROPS Price Tracker has revolutionized how we monitor market prices. The real-time updates save us hours of manual work.",
      avatar: "AH"
    },
    {
      name: "Sarah Mohamed",
      role: "Procurement Director",
      content: "The trend analysis feature helps us make data-driven purchasing decisions. We've reduced costs by 15% in just 3 months.",
      avatar: "SM"
    },
    {
      name: "Khaled Ibrahim",
      role: "Operations Manager",
      content: "Having all store prices in one dashboard is a game-changer. The automated alerts ensure we never miss a good deal.",
      avatar: "KI"
    }
  ];

  const pricingPlans = [
    {
      name: "Starter",
      price: "599",
      period: "month",
      features: [
        "Track up to 50 products",
        "3 store integrations",
        "Daily price updates",
        "Basic analytics",
        "Email support"
      ],
      popular: false
    },
    {
      name: "Professional",
      price: "1,499",
      period: "month",
      features: [
        "Track up to 200 products",
        "All store integrations",
        "Real-time updates",
        "Advanced analytics",
        "Price alerts",
        "API access",
        "Priority support"
      ],
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      features: [
        "Unlimited products",
        "Custom integrations",
        "Real-time WebSocket",
        "Custom analytics",
        "White-label option",
        "Dedicated support",
        "SLA guarantee"
      ],
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled ? 'bg-white/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
      }`}>
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg blur-lg opacity-70"></div>
                <div className="relative bg-gradient-to-r from-green-500 to-emerald-600 p-2 rounded-lg">
                  <Leaf className="w-8 h-8 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  CROPS
                </h1>
                <p className="text-xs text-gray-600">Price Tracker</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-8">
              <Link href="#features" className="text-gray-700 hover:text-green-600 transition-colors">
                Features
              </Link>
              <Link href="#how-it-works" className="text-gray-700 hover:text-green-600 transition-colors">
                How It Works
              </Link>
              <Link href="#pricing" className="text-gray-700 hover:text-green-600 transition-colors">
                Pricing
              </Link>
              <Link href="#testimonials" className="text-gray-700 hover:text-green-600 transition-colors">
                Testimonials
              </Link>
              <Link href="#contact" className="text-gray-700 hover:text-green-600 transition-colors">
                Contact
              </Link>
            </div>

            {/* CTA Buttons */}
            <div className="hidden lg:flex items-center space-x-4">
              <Link href="/auth/login">
                <button className="px-6 py-2 text-gray-700 hover:text-green-600 transition-colors">
                  Sign In
                </button>
              </Link>
              <Link href="/auth/login">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transition-shadow"
                >
                  Get Started
                </motion.button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden bg-white border-t"
            >
              <div className="container mx-auto px-4 py-4 space-y-4">
                <Link href="#features" className="block py-2 text-gray-700">Features</Link>
                <Link href="#pricing" className="block py-2 text-gray-700">Pricing</Link>
                <Link href="#contact" className="block py-2 text-gray-700">Contact</Link>
                <Link href="/auth/login" className="block">
                  <button className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium">
                    Sign In / Get Started
                  </button>
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-green-50 via-emerald-50/30 to-transparent"></div>
        <div className="absolute top-20 right-10 w-72 h-72 bg-green-200 rounded-full blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute bottom-20 left-10 w-96 h-96 bg-emerald-200 rounded-full blur-3xl opacity-30 animate-pulse"></div>

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center space-x-2 bg-green-100 px-4 py-2 rounded-full mb-6">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-700 font-medium">Live Price Tracking Active</span>
              </div>

              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                Track Egyptian <br />
                <span className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  Grocery Prices
                </span>
                <br />
                in Real-Time
              </h1>

              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Monitor prices across major Egyptian grocery stores. 
                Get instant updates, track trends, and never miss out on the best deals 
                for your agricultural products.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <Link href="/auth/login">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold text-lg shadow-xl hover:shadow-2xl transition-all flex items-center justify-center space-x-2"
                  >
                    <span>Start Free Trial</span>
                    <ArrowRight className="w-5 h-5" />
                  </motion.button>
                </Link>
                <button className="px-8 py-4 border-2 border-gray-200 text-gray-700 rounded-xl font-semibold text-lg hover:border-green-500 hover:text-green-600 transition-all">
                  Watch Demo
                </button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <h3 className="text-3xl font-bold text-gray-900">10+</h3>
                  <p className="text-gray-600">Stores Tracked</p>
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-gray-900">500+</h3>
                  <p className="text-gray-600">Products</p>
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-gray-900">24/7</h3>
                  <p className="text-gray-600">Monitoring</p>
                </div>
              </div>
            </motion.div>

            {/* Hero Image/Animation */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="relative bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl p-8 shadow-2xl">
                {/* Mock Dashboard */}
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Live Prices</h3>
                    <RefreshCw className="w-4 h-4 text-green-600 animate-spin" />
                  </div>
                  
                  {/* Price Cards */}
                  <div className="space-y-3">
                    <motion.div
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.5 }}
                      className="flex items-center justify-between p-3 bg-green-50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-green-200 rounded-full flex items-center justify-center">
                          🥒
                        </div>
                        <div>
                          <p className="font-medium">Cucumbers</p>
                          <p className="text-sm text-gray-600">Gourmet Egypt</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">25 EGP/kg</p>
                        <p className="text-xs text-green-500">↓ 5%</p>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.7 }}
                      className="flex items-center justify-between p-3 bg-red-50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-red-200 rounded-full flex items-center justify-center">
                          🍅
                        </div>
                        <div>
                          <p className="font-medium">Tomatoes</p>
                          <p className="text-sm text-gray-600">Metro Market</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">18 EGP/kg</p>
                        <p className="text-xs text-red-500">↑ 3%</p>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.9 }}
                      className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-yellow-200 rounded-full flex items-center justify-center">
                          🌶️
                        </div>
                        <div>
                          <p className="font-medium">Bell Peppers</p>
                          <p className="text-sm text-gray-600">Spinneys</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">45 EGP/kg</p>
                        <p className="text-xs text-gray-500">—</p>
                      </div>
                    </motion.div>
                  </div>
                </div>

                {/* Floating Elements */}
                <motion.div
                  animate={{
                    y: [0, -10, 0],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute -top-4 -right-4 bg-white rounded-lg shadow-lg p-3"
                >
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium">15% Savings</span>
                  </div>
                </motion.div>

                <motion.div
                  animate={{
                    y: [0, 10, 0],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 1
                  }}
                  className="absolute -bottom-4 -left-4 bg-white rounded-lg shadow-lg p-3"
                >
                  <div className="flex items-center space-x-2">
                    <Bell className="w-4 h-4 text-orange-600" />
                    <span className="text-sm font-medium">Stock Alert</span>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
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
              Everything you need to monitor grocery prices efficiently and make data-driven decisions
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
                whileHover={{ y: -5 }}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-10 transition-opacity rounded-2xl"
                  style={{
                    backgroundImage: `linear-gradient(135deg, ${feature.color.split(' ')[1]}, ${feature.color.split(' ')[3]})`
                  }}
                ></div>
                <div className="relative bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color} text-white mb-4`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Simple, automated, and powerful price tracking in three easy steps
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Connect Stores",
                description: "Link your preferred grocery stores and marketplaces to track",
                icon: <Globe className="w-8 h-8" />
              },
              {
                step: "02",
                title: "Select Products",
                description: "Choose which products you want to monitor from our extensive catalog",
                icon: <ShoppingCart className="w-8 h-8" />
              },
              {
                step: "03",
                title: "Track & Save",
                description: "Get real-time updates and analytics to optimize your purchasing",
                icon: <TrendingUp className="w-8 h-8" />
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index === 0 ? -20 : index === 2 ? 20 : 0 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="relative"
              >
                <div className="bg-white rounded-2xl p-8 shadow-lg relative overflow-hidden">
                  <div className="absolute top-4 right-4 text-6xl font-bold text-gray-100">
                    {item.step}
                  </div>
                  <div className="relative z-10">
                    <div className="inline-flex p-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl mb-4">
                      {item.icon}
                    </div>
                    <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                      {item.title}
                    </h3>
                    <p className="text-gray-600">
                      {item.description}
                    </p>
                  </div>
                </div>
                {index < 2 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-20">
                    <ArrowRight className="w-8 h-8 text-green-500" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
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
              Choose the perfect plan for your business needs
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
                className={`relative ${plan.popular ? 'scale-105' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-5 left-0 right-0 mx-auto w-fit bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}
                <div className={`bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow p-8 ${
                  plan.popular ? 'border-2 border-green-500' : 'border border-gray-200'
                }`}>
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
                    <button className={`w-full py-3 rounded-lg font-semibold transition-all ${
                      plan.popular
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}>
                      {plan.price === "Custom" ? "Contact Sales" : "Start Free Trial"}
                    </button>
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by Agricultural Leaders
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See what our customers say about CROPS Price Tracker
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTestimonial}
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  className="bg-white rounded-2xl shadow-lg p-8 md:p-12"
                >
                  <div className="flex items-start space-x-1 mb-6">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"/>
                      </svg>
                    ))}
                  </div>
                  <p className="text-xl text-gray-700 mb-8 italic">
                    "{testimonials[activeTestimonial].content}"
                  </p>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                      {testimonials[activeTestimonial].avatar}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">
                        {testimonials[activeTestimonial].name}
                      </p>
                      <p className="text-gray-600">
                        {testimonials[activeTestimonial].role}
                      </p>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>

              {/* Navigation dots */}
              <div className="flex justify-center space-x-2 mt-8">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setActiveTestimonial(index)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === activeTestimonial
                        ? 'w-8 bg-gradient-to-r from-green-500 to-emerald-600'
                        : 'bg-gray-300 hover:bg-gray-400'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
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
                  Have questions about CROPS Price Tracker? We're here to help you optimize your agricultural procurement.
                </p>

                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <Globe className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Visit Us</h3>
                      <p className="text-gray-600">
                        Cairo, Egypt<br />
                        New Administrative Capital
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <Clock className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Business Hours</h3>
                      <p className="text-gray-600">
                        Sunday - Thursday: 9:00 AM - 6:00 PM<br />
                        Friday - Saturday: Closed
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <Users className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Support</h3>
                      <p className="text-gray-600">
                        support@cropsegypt.com<br />
                        +20 123 456 7890
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Contact Form */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 shadow-lg"
              >
                <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                  Send us a Message
                </h3>
                <form className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        First Name
                      </label>
                      <input
                        type="text"
                        className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                        placeholder="John"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Last Name
                      </label>
                      <input
                        type="text"
                        className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                        placeholder="Doe"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                      placeholder="john@company.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                      placeholder="Your Company"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Message
                    </label>
                    <textarea
                      rows={4}
                      className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all resize-none"
                      placeholder="Tell us about your needs..."
                    />
                  </div>

                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all"
                  >
                    Send Message
                  </motion.button>
                </form>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            {/* Logo & Description */}
            <div className="md:col-span-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-2 rounded-lg">
                  <Leaf className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold">CROPS</h3>
              </div>
              <p className="text-gray-400 text-sm">
                Advanced agricultural price tracking for Egyptian markets.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">API</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="#contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Cookie Policy</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm mb-4 md:mb-0">
                © 2024 CROPS Egypt. All rights reserved.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}