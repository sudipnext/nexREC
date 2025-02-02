import { useState } from "react";
import type { User } from "~/types/user";

// This would come from your backend
const mockUser: User = {
  id: "1",
  email: "user@example.com",
  username: "moviebuff",
  preferences: {
    favoriteGenres: ["Action", "Sci-Fi"],
    watchlist: [],
    darkMode: true,
    emailNotifications: true,
  },
  createdAt: new Date().toISOString(),
};

export default function Profile() {
  const [user, setUser] = useState<User>(mockUser);

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
          {/* Profile Header */}
          <div className="relative h-48 bg-purple-600">
            <div className="absolute bottom-0 left-0 right-0 px-6 py-4 bg-gradient-to-t from-black/60">
              <div className="flex items-center space-x-4">
                <div className="h-24 w-24 rounded-full bg-gray-300 border-4 border-gray-800">
                  {/* Profile image would go here */}
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">{user.username}</h1>
                  <p className="text-gray-300">Member since {new Date(user.createdAt).getFullYear()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Profile Content */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Personal Information */}
              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-white">Personal Information</h2>
                <div className="space-y-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-400">Username</label>
                    <input
                      type="text"
                      value={user.username}
                      className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
                      readOnly
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400">Email</label>
                    <input
                      type="email"
                      value={user.email}
                      className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
                      readOnly
                    />
                  </div>
                </div>
              </section>

              {/* Preferences */}
              <section className="space-y-4">
                <h2 className="text-xl font-semibold text-white">Movie Preferences</h2>
                <div className="space-y-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-400">Favorite Genres</label>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {user.preferences.favoriteGenres.map((genre) => (
                        <span
                          key={genre}
                          className="px-3 py-1 rounded-full text-sm bg-purple-600 text-white"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 