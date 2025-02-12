import { useState, useEffect } from "react";
import axios from "axios";

interface Movie {
  id: number;
  title: string;
  original_title: string;
  synopsis: string;
  poster_path: string | null;
  audience_score: string | null;
  critics_score: string | null;
  vote_average: string | number;
  rating: string;
  runtime: string;
  status: string;
  release_date: string | null;
  release_date_theaters: string | null;
  release_date_streaming: string | null;
  box_office: string;
}

interface MovieResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Movie[];
}

export default function Discover() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  const fetchMovies = async (page: number, search?: string) => {
    setLoading(true);
    setError(null);
    try {
      const baseUrl = "http://54.172.171.231/api/movies/";
      const url = search 
        ? `${baseUrl}search/?title=${encodeURIComponent(search)}`
        : `${baseUrl}?page=${page}`;
      
      const response = await axios.get<MovieResponse>(url);
      if (response.data && Array.isArray(response.data.results)) {
        setMovies(response.data.results);
        setTotalPages(Math.ceil(response.data.count / 20));
      } else {
        setError("Invalid response format from server");
      }
    } catch (err) {
      console.error("Error fetching movies:", err);
      setError("Failed to fetch movies. Please try again later.");
      setMovies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    try {
      fetchMovies(currentPage);
    } catch (err) {
      console.error("Error in useEffect:", err);
      setError("Failed to load movies");
    }
  }, [currentPage]);

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await fetchMovies(1, searchQuery);
    } catch (err) {
      console.error("Error in search:", err);
      setError("Search failed. Please try again.");
    }
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  return (
    <div className="min-h-screen py-8 bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Search Section */}
        <form onSubmit={handleSearch} className="mb-10">
          <div className="flex gap-4">
            <input
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search movies..."
              className="w-full md:w-96 px-4 py-2 rounded-lg bg-gray-800/50 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Search
            </button>
          </div>
        </form>

        {/* Error State */}
        {error && (
          <div className="text-red-500 text-center mb-8 p-4 bg-red-100 rounded">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
          </div>
        )}

        {/* Movies Grid with better spacing */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>

        {/* No Results */}
        {!loading && movies.length === 0 && !error && (
          <div className="text-center text-gray-400 py-12">
            No movies found
          </div>
        )}

        {/* Pagination */}
        {!loading && movies.length > 0 && (
          <div className="mt-10 flex justify-center gap-2">
            <button
              onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 rounded-lg bg-gray-800 text-white disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-white">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 rounded-lg bg-gray-800 text-white disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function MovieCard({ movie }: { movie: Movie }) {
  if (!movie) return null;

  const year = movie.release_date 
    ? new Date(movie.release_date).getFullYear() 
    : "N/A";
  
  const audienceScore = movie.audience_score ? Number(movie.audience_score).toFixed(0) : null;
  const criticsScore = movie.critics_score ? Number(movie.critics_score).toFixed(0) : null;

  return (
    <div className="group relative bg-gray-900 rounded-lg overflow-hidden shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl">
      {/* Movie Poster */}
      <div className="relative aspect-[2/3]">
        <img
          src={movie.poster_path || '/placeholder-movie.jpg'}
          alt={movie.title}
          className="w-full h-full object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder-movie.jpg';
          }}
        />
        
        {/* Dark overlay that appears on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent opacity-100" />

        {/* Content Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-4">
          {/* Title and Year */}
          <div className="mb-2">
            <h3 className="text-xl font-bold text-white mb-1">{movie.title}</h3>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-300">{year}</span>
              <span className="text-sm text-gray-300">{movie.runtime}</span>
            </div>
          </div>

          {/* Scores */}
          <div className="flex items-center gap-4 mb-3">
            {audienceScore && (
              <div className="flex flex-col items-center">
                <span className="text-xs text-gray-400">Audience</span>
                <div className={`text-sm font-bold ${Number(audienceScore) >= 70 ? 'text-green-400' : Number(audienceScore) >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {audienceScore}%
                </div>
              </div>
            )}
            {criticsScore && (
              <div className="flex flex-col items-center">
                <span className="text-xs text-gray-400">Critics</span>
                <div className={`text-sm font-bold ${Number(criticsScore) >= 70 ? 'text-green-400' : Number(criticsScore) >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {criticsScore}%
                </div>
              </div>
            )}
          </div>

          {/* Status and Rating Pills */}
          <div className="flex flex-wrap gap-2 mb-3">
            <span className="px-2 py-1 text-xs rounded-full bg-purple-600/80 text-white">
              {movie.status}
            </span>
            {movie.rating && (
              <span className="px-2 py-1 text-xs rounded-full bg-gray-700/80 text-white">
                {movie.rating}
              </span>
            )}
          </div>

          {/* Synopsis */}
          <p className="text-sm text-gray-300 line-clamp-2 mb-4">
            {movie.synopsis}
          </p>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button className="flex-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition-colors">
              Watch Now
            </button>
            <button className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
              </svg>
            </button>
            <button className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 