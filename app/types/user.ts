export interface User {
  id: string;
  email: string;
  username: string;
  preferences: {
    favoriteGenres: string[];
    watchlist: string[];
    darkMode: boolean;
    emailNotifications: boolean;
  };
  createdAt: string;
} 