import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  NavLink
} from "@remix-run/react";
import type { LinksFunction } from "@remix-run/node";

import "./tailwind.css";

export const links: LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body className="bg-gray-950 text-white">
        <nav className="fixed top-0 w-full bg-gray-900/80 backdrop-blur-sm z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <NavLink to="/" className="text-2xl font-bold text-purple-500">
                  CineMatch
                </NavLink>
              </div>
              <div className="flex items-center space-x-6">
                <div className="flex space-x-4">
                  <NavLink 
                    to="/discover" 
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium ${
                        isActive ? 'text-purple-500' : 'text-gray-300 hover:text-purple-400'
                      }`
                    }
                  >
                    Discover
                  </NavLink>
                  <NavLink 
                    to="/recommendations" 
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium ${
                        isActive ? 'text-purple-500' : 'text-gray-300 hover:text-purple-400'
                      }`
                    }
                  >
                    Recommendations
                  </NavLink>
                </div>
                <div className="flex items-center space-x-2">
                  <NavLink
                    to="/auth/login"
                    className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-purple-400"
                  >
                    Login
                  </NavLink>
                  <NavLink
                    to="/auth/signup"
                    className="px-4 py-2 text-sm font-medium bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                  >
                    Sign Up
                  </NavLink>
                </div>
              </div>
            </div>
          </div>
        </nav>
        <main className="pt-16">
          {children}
        </main>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}
