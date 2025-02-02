import type { MetaFunction } from "@remix-run/node";
import { Link } from "@remix-run/react";

export const meta: MetaFunction = () => {
  return [
    { title: "CineMatch - Find Your Perfect Movie Match" },
    { name: "description", content: "Discover movies tailored to your taste with CineMatch's intelligent recommendation system" },
  ];
};

export default function Index() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/90 to-gray-900/90 z-10" />
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1536440136628-849c177e76a1?ixlib=rb-1.2.1&auto=format&fit=crop&w=2850&q=80"
            alt="Cinema Background"
            className="w-full h-full object-cover"
          />
        </div>
        
        <div className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Find Your Perfect Movie Match
            </h1>
            <p className="text-xl text-gray-200 mb-8 max-w-2xl mx-auto">
              Let our AI-powered recommendation engine guide you to your next favorite film
            </p>
            <div className="flex justify-center space-x-4">
              <Link
                to="/discover"
                className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-8 py-4 rounded-lg transition-colors"
              >
                Start Discovering
              </Link>
              <Link
                to="/auth/signup"
                className="bg-gray-800 hover:bg-gray-700 text-white font-semibold px-8 py-4 rounded-lg transition-colors"
              >
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <FeatureCard
              icon="🎯"
              title="Personalized Matches"
              description="Get movie recommendations tailored to your unique taste and preferences"
            />
            <FeatureCard
              icon="🌟"
              title="Curated Collections"
              description="Explore hand-picked collections of movies across different genres and themes"
            />
            <FeatureCard
              icon="🤖"
              title="Smart AI Engine"
              description="Our advanced AI learns from your choices to make better recommendations"
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-gray-800 p-6 rounded-xl">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}
