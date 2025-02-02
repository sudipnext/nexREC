import { useState } from "react";

export default function Recommendations() {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  const categories = [
    "Action & Adventure",
    "Comedy",
    "Drama",
    "Sci-Fi & Fantasy",
    "Horror",
    "Romance",
    "Thriller",
    "Animation",
  ];

  const toggleCategory = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  return (
    <div className="min-h-screen pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-white mb-4">
            Personalize Your Movie Experience
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Select your favorite genres and let our AI create the perfect movie recommendations for you
          </p>
        </div>

        {/* Genre Selection */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => toggleCategory(category)}
              className={`p-4 rounded-lg text-left transition-colors ${
                selectedCategories.includes(category)
                  ? "bg-purple-600 text-white"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
            >
              <span className="text-lg font-medium">{category}</span>
            </button>
          ))}
        </div>

        {/* Recommendation Settings */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Fine-tune Your Recommendations
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Release Year Range
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="number"
                  placeholder="From"
                  className="w-24 px-3 py-2 bg-gray-700 rounded-md text-white"
                  min="1900"
                  max="2024"
                />
                <span className="text-gray-400">to</span>
                <input
                  type="number"
                  placeholder="To"
                  className="w-24 px-3 py-2 bg-gray-700 rounded-md text-white"
                  min="1900"
                  max="2024"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Minimum Rating
              </label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                className="w-full accent-purple-600"
              />
            </div>
          </div>
        </div>

        <button className="w-full md:w-auto px-8 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors">
          Get Recommendations
        </button>
      </div>
    </div>
  );
} 