import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function DiscoveryBoard() {
    const [upcomingFlights, setUpcomingFlights] = useState([]);
    const [loading, setLoading] = useState(true); // Tracks the loading state
    const [error, setError] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUpcoming = async () => {
            try {
                const response = await apiClient.get('flights/upcoming/');
                setUpcomingFlights(response.data);
            } catch (error) {
                console.error("Error fetching discovery flights", error);
                setError(true);
            } finally {
                // This guarantees the loading text disappears even if the database is empty or errors out
                setLoading(false); 
            }
        };
        fetchUpcoming();
    }, []);

    if (loading) {
        return <div className="text-center py-12 text-gray-500 font-medium">Loading upcoming routes...</div>;
    }

    if (error) {
        return <div className="text-center py-12 text-red-500 font-medium">Failed to connect to the server. Is Django running?</div>;
    }

    if (upcomingFlights.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500 font-medium text-lg">No upcoming flights found.</p>
                <p className="text-gray-400 text-sm mt-2">Your database is empty. Please add flights from the Django admin!</p>
            </div>
        );
    }

    return (
        <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Upcoming Flights</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {upcomingFlights.map(flight => (
                    <div key={flight.id} className="bg-white p-6 rounded-2xl shadow-sm border-t-4 border-julianna flex flex-col justify-between">
                        <div>
                            <h3 className="font-bold text-lg">{flight.source} to {flight.destination}</h3>
                            <p className="text-gray-500 text-sm mt-1">{new Date(flight.departure_time).toLocaleDateString()}</p>
                            <p className="text-gray-800 font-medium mt-2">{flight.airline}</p>
                        </div>
                        <button 
                            onClick={() => navigate(`/flight/${flight.id}/seats`)}
                            className="mt-4 bg-pastelBlue text-gray-900 px-4 py-2 rounded-lg font-semibold hover:bg-opacity-80 transition-all text-sm w-full cursor-pointer"
                        >
                            View Seats
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}